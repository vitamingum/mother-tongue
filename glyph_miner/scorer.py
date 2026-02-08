"""Scorer for tracking Σ (state) across mining rounds."""
from collections import defaultdict


class State:
    """Σ - Persistent state across rounds and passes."""
    
    def __init__(self, pool):
        """Initialize state with pool.
        
        Args:
            pool: list - current pool of codepoints
        """
        self.pool = pool.copy()
        self.seen = defaultdict(int)      # cp -> count of times in slate
        self.picked = defaultdict(int)    # cp -> count of times selected
        self.score = {}                   # cp -> pick_rate (picked/seen)
        self.edges = []                   # list of (cp1, cp2) pairs
    
    def update(self, slate, choices):
        """Update state after a single inference round.
        
        Args:
            slate: list - codepoints shown to model
            choices: tuple - (cp1, cp2) selected by model, or None
        """
        # seen += slate
        for cp in slate:
            self.seen[cp] += 1
        
        # If valid choices
        if choices and len(choices) == 2:
            cp1, cp2 = choices
            
            # picked += choices
            self.picked[cp1] += 1
            self.picked[cp2] += 1
            
            # edges += (cp1, cp2)
            self.edges.append((cp1, cp2))
        
        # Recalculate scores
        self._update_scores()
    
    def _update_scores(self):
        """Calculate pick rate = picked/seen for all seen glyphs."""
        for cp in self.seen:
            if self.seen[cp] > 0:
                self.score[cp] = self.picked[cp] / self.seen[cp]
            else:
                self.score[cp] = 0.0
    
    def get_sorted_by_score(self):
        """Return codepoints sorted by score (descending), then by seen count.
        
        Returns:
            list of (cp, score, seen, picked, byte_len) tuples
        """
        items = []
        for cp in self.score:
            byte_len = len(chr(cp).encode('utf-8'))
            items.append((cp, self.score[cp], self.seen[cp], self.picked[cp], byte_len))
        
        # Sort by score desc, then seen desc
        items.sort(key=lambda x: (-x[1], -x[2]))
        return items
    
    def top_n(self, n):
        """Return top N codepoints by score.
        
        Args:
            n: int - number to return
        
        Returns:
            list of codepoints
        """
        sorted_items = self.get_sorted_by_score()
        return [cp for cp, _, _, _, _ in sorted_items[:n]]
    
    def get_min_seen(self):
        """Return minimum seen count across all glyphs in pool."""
        if not self.seen:
            return 0
        return min(self.seen.get(cp, 0) for cp in self.pool)
    
    def to_dict(self):
        """Export state as dict for checkpointing."""
        return {
            'pool': self.pool,
            'seen': dict(self.seen),
            'picked': dict(self.picked),
            'score': self.score.copy(),
            'byte_len': {cp: len(chr(cp).encode('utf-8')) for cp in self.seen},
            'edges': self.edges.copy()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Restore state from dict."""
        state = cls(data['pool'])
        state.seen = defaultdict(int, data['seen'])
        state.picked = defaultdict(int, data['picked'])
        state.score = data['score']
        state.edges = data['edges']
        return state


if __name__ == "__main__":
    # Test
    pool = [100, 101, 102, 103, 104]
    state = State(pool)
    
    # Round 1: slate [100, 101], choice (100, 101)
    state.update([100, 101], (100, 101))
    print("After round 1:")
    print(f"  Seen: {dict(state.seen)}")
    print(f"  Picked: {dict(state.picked)}")
    print(f"  Scores: {state.score}")
    
    # Round 2: slate [100, 102], choice (102, 100)
    state.update([100, 102], (102, 100))
    print("\nAfter round 2:")
    print(f"  Seen: {dict(state.seen)}")
    print(f"  Picked: {dict(state.picked)}")
    print(f"  Scores: {state.score}")
    
    # Round 3: slate [103, 104], no valid choice
    state.update([103, 104], None)
    print("\nAfter round 3 (no pick):")
    print(f"  Seen: {dict(state.seen)}")
    print(f"  Scores: {state.score}")
    
    # Top 2
    print(f"\nTop 2: {state.top_n(2)}")
    print(f"Min seen: {state.get_min_seen()}")
