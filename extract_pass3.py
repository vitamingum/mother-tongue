"""Extract top glyphs from mining state."""
import sys
import pickle
from pathlib import Path

# Add glyph_miner to path
sys.path.insert(0, 'glyph_miner')

from scorer import State

def load_checkpoint(checkpoint_dir):
    """Try to load most recent checkpoint."""
    checkpoint_path = Path(checkpoint_dir)
    if not checkpoint_path.exists():
        return None
    
    # Look for checkpoint files
    checkpoints = list(checkpoint_path.glob('*.pkl'))
    if not checkpoints:
        return None
    
    # Load most recent
    latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
    print(f"Loading: {latest}")
    
    with open(latest, 'rb') as f:
        return pickle.load(f)

def main():
    # Try to load checkpoint
    checkpoint_data = load_checkpoint('glyph_miner/checkpoints')
    
    if checkpoint_data:
        print(f"Checkpoint data keys: {checkpoint_data.keys()}")
        
        # Extract state if available
        if 'state' in checkpoint_data:
            state = checkpoint_data['state']
            top_glyphs = state.top_n(1000)  # Get top 1000
            
            # Write to file
            with open('data/pass3_top_glyphs.txt', 'w', encoding='utf-8') as f:
                for cp in top_glyphs:
                    f.write(chr(cp))
            
            print(f"Extracted {len(top_glyphs)} glyphs to data/pass3_top_glyphs.txt")
    else:
        print("No checkpoint found. Mining may still be in progress.")
        print("The miner doesn't save intermediate glyph lists by default.")

if __name__ == "__main__":
    main()
