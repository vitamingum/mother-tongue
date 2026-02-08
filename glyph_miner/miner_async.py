"""Async pipelined miner with batch processing."""
import asyncio
import argparse
import random
import time
from pathlib import Path

from unicode import enum_unicode
from sampler import shuffle_pool, create_slate, format_slate
from runner_async import AsyncOllamaRunner
from scorer import State
from prune import prune_with_margin, prune_to_target, aggregate_across_passes
from report import (
    check_stability, write_final_output,
    write_stability_report, append_log_entry
)
from display import print_leaderboard


class AsyncGlyphMiner:
    """Async mining coordinator with batched inference."""
    
    def __init__(self, model_name, seed, output_dir="output", batch_size=20):
        self.model_name = model_name
        self.seed = seed
        self.output_dir = output_dir
        self.batch_size = batch_size
        
        # Stage configurations
        self.stages = {
            'A': {
                'passes': 5,
                'rounds': 12000,
                'keep': 10000,
                'k': 64,
                'union_margin': 15000,
                'min_seen': 8
            },
            'B': {
                'passes': 4,
                'rounds': 3000,
                'keep': 2000,
                'k': 64,
                'union_margin': 3000,
                'min_seen': 20
            },
            'C': {
                'passes': 4,
                'rounds': 5000,
                'keep': 512,
                'k': 16,
                'union_margin': 800,
                'min_seen': 20
            }
        }
    
    async def run_pass_async(self, pool, pass_num, stage_name, stage_config):
        """Execute one pass with batched async rounds."""
        state = State(pool)
        shuffled = shuffle_pool(pool, self.seed, pass_num)
        
        rounds = stage_config['rounds']
        k = stage_config['k']
        
        print(f"  Pass {pass_num}: {rounds} rounds, K={k}, batch_size={self.batch_size}")
        
        prev_top = None
        valid_selections = 0
        
        async with AsyncOllamaRunner(self.model_name, max_concurrent=10) as runner:
            # Process in batches
            for batch_start in range(0, rounds, self.batch_size):
                batch_end = min(batch_start + self.batch_size, rounds)
                batch_rounds = range(batch_start, batch_end)
                
                # Prepare batch
                batch_data = []
                for r in batch_rounds:
                    slate = create_slate(shuffled, k, r)
                    slate_chars = format_slate(slate)
                    slate_set = set(slate)
                    batch_data.append((slate, slate_chars, slate_set))
                
                # Process batch concurrently
                slate_chars_list = [(sc, ss) for _, sc, ss in batch_data]
                results = await runner.infer_batch(slate_chars_list)
                
                # Update state for all results
                for (slate, _, _), choices in zip(batch_data, results):
                    state.update(slate, choices)
                    if choices is not None:
                        valid_selections += 1
                
                # Display every ~100 rounds
                if (batch_end) % 100 == 0:
                    prev_top = print_leaderboard(
                        state, stage_name, pass_num, batch_end,
                        rounds, len(pool), valid_selections, prev_top
                    )
        
        print(f"  Pass {pass_num} complete: {valid_selections}/{rounds} valid selections")
        
        # Log this pass
        append_log_entry({
            'stage': stage_name,
            'pass': pass_num,
            'rounds': rounds,
            'valid_selections': valid_selections,
            'pool_size': len(pool),
            'timestamp': time.time()
        }, self.output_dir)
        
        return state
    
    async def run_stage_async(self, stage_name, initial_pool):
        """Execute complete stage with async passes."""
        config = self.stages[stage_name]
        print(f"\n{'='*60}")
        print(f"Stage {stage_name}: {config['passes']} passes, "
              f"{config['rounds']} rounds each, K={config['k']}")
        print(f"Initial pool: {len(initial_pool)}")
        print(f"{'='*60}")
        
        pool = initial_pool.copy()
        pass_states = []
        top_n_history = []
        
        for p in range(1, config['passes'] + 1):
            print(f"\nPass {p}/{config['passes']}")
            
            pass_state = await self.run_pass_async(pool, p, stage_name, config)
            pass_states.append(pass_state)
            
            aggregated = aggregate_across_passes(pass_states)
            
            min_seen = aggregated.get_min_seen()
            print(f"  Min seen: {min_seen} (required: {config['min_seen']})")
            
            pool = prune_with_margin(
                aggregated,
                config['keep'],
                config['union_margin']
            )
            print(f"  Pool after prune: {len(pool)}")
            
            if stage_name == 'C':
                top_512 = aggregated.top_n(512)
                top_n_history.append(top_512)
                
                if len(top_n_history) >= 2:
                    is_stable, sims = check_stability(
                        top_n_history,
                        threshold=0.98,
                        consecutive_required=2
                    )
                    print(f"  Stability: {sims[-1]:.4f}")
                    if is_stable:
                        print(f"  ✓ Converged (≥0.98 ×2)")
                        break
        
        final_state = aggregate_across_passes(pass_states)
        final_pool = prune_to_target(final_state, config['keep'])
        
        print(f"\nStage {stage_name} complete: {len(final_pool)} glyphs")
        
        if stage_name == 'C' and top_n_history:
            _, sims = check_stability(top_n_history, threshold=0.98)
            stability_data = {
                'stage': stage_name,
                'passes': len(top_n_history),
                'similarities': sims,
                'final_size': len(final_pool)
            }
            write_stability_report(stability_data, self.output_dir)
        
        return final_pool, final_state
    
    async def run_async(self):
        """Execute complete async mining pipeline."""
        print(f"GLYPH_MINER_512 v0.3.1 (ASYNC)")
        print(f"Model: {self.model_name}")
        print(f"Seed: {self.seed}")
        print(f"Batch size: {self.batch_size}")
        print(f"Output: {self.output_dir}")
        
        pool = enum_unicode()
        print(f"\nInitial Unicode pool: {len(pool)}")
        
        random.seed(self.seed)
        
        pool, state_a = await self.run_stage_async('A', pool)
        pool, state_b = await self.run_stage_async('B', pool)
        pool, state_c = await self.run_stage_async('C', pool)
        
        assert len(pool) == 512, f"Final pool has {len(pool)}, expected 512"
        assert len(set(pool)) == len(pool), "Final pool contains duplicates"
        
        print(f"\n{'='*60}")
        print("Writing final outputs...")
        paths = write_final_output(state_c, self.output_dir)
        
        for key, path in paths.items():
            print(f"  {key}: {path}")
        
        print(f"\n✓ Complete: 512 unique glyphs")
        print(f"  Deterministic: rerun with seed {self.seed} → same result")
        
        return pool


def main():
    parser = argparse.ArgumentParser(
        description='GLYPH_MINER_512 v0.3.1 (ASYNC) - Pipelined glyph mining'
    )
    parser.add_argument('model', help='Ollama model name')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', default='output', help='Output directory')
    parser.add_argument('--batch-size', type=int, default=20, help='Inference batch size')
    
    args = parser.parse_args()
    
    miner = AsyncGlyphMiner(
        model_name=args.model,
        seed=args.seed,
        output_dir=args.output,
        batch_size=args.batch_size
    )
    
    asyncio.run(miner.run_async())


if __name__ == "__main__":
    main()
