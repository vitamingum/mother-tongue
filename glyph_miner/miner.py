"""Main glyph mining orchestrator."""
import argparse
import random
import time
from pathlib import Path

from unicode import enum_unicode
from checkpoint import Checkpoint
from sampler import shuffle_pool, create_slate, format_slate
from runner_ollama import OllamaRunner
from scorer import State
from prune import prune_with_margin, prune_to_target, aggregate_across_passes
from report import (
    check_stability, write_final_output, 
    write_stability_report, append_log_entry
)
from display import print_leaderboard


class GlyphMiner:
    """Main mining coordinator."""
    
    def __init__(self, model_name, seed, output_dir="output"):
        self.model_name = model_name
        self.seed = seed
        self.output_dir = output_dir
        self.checkpoint = Checkpoint()
        self.runner = OllamaRunner(model_name)
        
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
    
    def run_round(self, pool, state, round_num, k):
        """Execute one mining round.
        
        Args:
            pool: list - current pool
            state: State - current state
            round_num: int - round number
            k: int - slate size
        
        Returns:
            bool - True if valid selection made
        """
        # Create slate
        slate = create_slate(pool, k, round_num)
        slate_chars = format_slate(slate)
        slate_set = set(slate)
        
        # Infer
        choices = self.runner.sample_with_schedule(slate_chars, slate_set)
        
        # Update state
        state.update(slate, choices)
        
        return choices is not None
    
    def run_pass(self, pool, pass_num, stage_name, stage_config):
        """Execute one pass with multiple rounds.
        
        Args:
            pool: list - current pool
            pass_num: int - pass number
            stage_name: str - 'A', 'B', or 'C'
            stage_config: dict - stage parameters
        
        Returns:
            State - state after this pass
        """
        # Initialize state for this pass
        state = State(pool)
        
        # Shuffle pool for this pass
        shuffled = shuffle_pool(pool, self.seed, pass_num)
        
        rounds = stage_config['rounds']
        k = stage_config['k']
        
        print(f"  Pass {pass_num}: {rounds} rounds, K={k}")
        
        prev_top = None
        valid_selections = 0
        for r in range(rounds):
            success = self.run_round(shuffled, state, r, k)
            if success:
                valid_selections += 1
            
            # Display leaderboard every 100 rounds
            if (r + 1) % 100 == 0:
                prev_top = print_leaderboard(
                    state, stage_name, pass_num, r + 1,
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
    
    def run_stage(self, stage_name, initial_pool):
        """Execute complete stage with multiple passes.
        
        Args:
            stage_name: str - 'A', 'B', or 'C'
            initial_pool: list - starting pool
        
        Returns:
            list - final pool after stage
        """
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
            
            # Run this pass
            pass_state = self.run_pass(pool, p, stage_name, config)
            pass_states.append(pass_state)
            
            # Aggregate so far
            aggregated = aggregate_across_passes(pass_states)
            
            # Check min_seen requirement
            min_seen = aggregated.get_min_seen()
            print(f"  Min seen: {min_seen} (required: {config['min_seen']})")
            
            if min_seen < config['min_seen']:
                print(f"  ⚠ Min seen below threshold, continuing...")
            
            # Prune with union margin
            pool = prune_with_margin(
                aggregated, 
                config['keep'], 
                config['union_margin']
            )
            print(f"  Pool after prune: {len(pool)}")
            
            # Track top N for stability (only for final 512)
            if stage_name == 'C':
                top_512 = aggregated.top_n(512)
                top_n_history.append(top_512)
                
                # Check stability
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
        
        # Final aggregation and pruning to target
        final_state = aggregate_across_passes(pass_states)
        final_pool = prune_to_target(final_state, config['keep'])
        
        print(f"\nStage {stage_name} complete: {len(final_pool)} glyphs")
        
        # Save stability data for stage C
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
    
    def run(self):
        """Execute complete mining pipeline: A → B → C → final."""
        print(f"GLYPH_MINER_512 v0.3.1")
        print(f"Model: {self.model_name}")
        print(f"Seed: {self.seed}")
        print(f"Output: {self.output_dir}")
        
        # Initialize with full Unicode
        pool = enum_unicode()
        print(f"\nInitial Unicode pool: {len(pool)}")
        
        # Set global random seed
        random.seed(self.seed)
        
        # Stage A
        pool, state_a = self.run_stage('A', pool)
        
        # Stage B
        pool, state_b = self.run_stage('B', pool)
        
        # Stage C
        pool, state_c = self.run_stage('C', pool)
        
        # Final assertions
        assert len(pool) == 512, f"Final pool has {len(pool)}, expected 512"
        assert len(set(pool)) == len(pool), "Final pool contains duplicates"
        
        # Write outputs
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
        description='GLYPH_MINER_512 v0.3.1 - Deterministic glyph mining'
    )
    parser.add_argument(
        'model',
        help='Ollama model name (e.g., llama2, mistral)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for determinism (default: 42)'
    )
    parser.add_argument(
        '--output',
        default='output',
        help='Output directory (default: output)'
    )
    
    args = parser.parse_args()
    
    miner = GlyphMiner(
        model_name=args.model,
        seed=args.seed,
        output_dir=args.output
    )
    
    miner.run()


if __name__ == "__main__":
    main()
