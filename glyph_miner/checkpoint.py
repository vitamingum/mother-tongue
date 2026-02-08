"""Checkpoint system for deterministic state persistence."""
import json
import pickle
from pathlib import Path


class Checkpoint:
    """Manages saving and loading of mining state."""
    
    def __init__(self, checkpoint_dir="checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def save(self, stage, pass_num, round_num, seed, rng_state, state):
        """Save complete mining state.
        
        Args:
            stage: str - 'A', 'B', or 'C'
            pass_num: int - current pass
            round_num: int - current round
            seed: int - base seed
            rng_state: tuple - random.getstate()
            state: dict - Σ (pool, seen, picked, score, edges)
        """
        checkpoint_data = {
            'stage': stage,
            'pass': pass_num,
            'round': round_num,
            'seed': seed,
            'rng_state': rng_state,
            'state': state
        }
        
        filename = f"ckpt_{stage}_p{pass_num}_r{round_num}.pkl"
        path = self.checkpoint_dir / filename
        
        with open(path, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        return path
    
    def load(self, checkpoint_path):
        """Load mining state from checkpoint.
        
        Returns tuple: (stage, pass_num, round_num, seed, rng_state, state)
        """
        with open(checkpoint_path, 'rb') as f:
            data = pickle.load(f)
        
        return (
            data['stage'],
            data['pass'],
            data['round'],
            data['seed'],
            data['rng_state'],
            data['state']
        )
    
    def list_checkpoints(self, stage=None):
        """List all checkpoints, optionally filtered by stage."""
        pattern = f"ckpt_{stage}_*.pkl" if stage else "ckpt_*.pkl"
        return sorted(self.checkpoint_dir.glob(pattern))
    
    def latest(self, stage=None):
        """Get most recent checkpoint, optionally for specific stage."""
        ckpts = self.list_checkpoints(stage)
        return ckpts[-1] if ckpts else None


if __name__ == "__main__":
    import random
    
    # Test save/load
    cp = Checkpoint()
    
    # Mock state
    test_state = {
        'pool': [1, 2, 3],
        'seen': {1: 5, 2: 3},
        'picked': {1: 2, 2: 1},
        'score': {1: 0.4, 2: 0.33},
        'edges': [(1, 2)]
    }
    
    random.seed(42)
    rng_state = random.getstate()
    
    # Save
    path = cp.save('A', 1, 100, 42, rng_state, test_state)
    print(f"Saved: {path}")
    
    # Load
    stage, pass_num, round_num, seed, loaded_rng, loaded_state = cp.load(path)
    print(f"Loaded: stage={stage}, pass={pass_num}, round={round_num}, seed={seed}")
    print(f"State matches: {loaded_state == test_state}")
