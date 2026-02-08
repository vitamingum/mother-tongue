"""Pruning logic for pool reduction."""


def prune_with_margin(state, target_size, margin):
    """Prune pool to target size, keeping union margin for fairness.
    
    Takes top (target_size + margin) glyphs by score to ensure fair
    representation across passes before final reduction.
    
    Args:
        state: State object with scoring data
        target_size: int - final target pool size
        margin: int - extra glyphs to keep for union across passes
    
    Returns:
        list - pruned pool (codepoints)
    """
    keep_size = target_size + margin
    top_glyphs = state.top_n(keep_size)
    
    # If we don't have enough, keep what we have
    if len(top_glyphs) < keep_size:
        return top_glyphs
    
    return top_glyphs[:keep_size]


def prune_to_target(state, target_size):
    """Prune pool to exact target size by score.
    
    Args:
        state: State object with scoring data
        target_size: int - exact target pool size
    
    Returns:
        list - pruned pool (codepoints)
    """
    return state.top_n(target_size)


def aggregate_across_passes(pass_states):
    """Aggregate multiple pass states and compute union.
    
    Args:
        pass_states: list of State objects from different passes
    
    Returns:
        State - aggregated state with combined statistics
    """
    if not pass_states:
        raise ValueError("No pass states to aggregate")
    
    # Start with first pass's pool
    from scorer import State
    aggregated = State(pass_states[0].pool)
    
    # Aggregate seen, picked, edges from all passes
    for pass_state in pass_states:
        for cp, count in pass_state.seen.items():
            aggregated.seen[cp] += count
        
        for cp, count in pass_state.picked.items():
            aggregated.picked[cp] += count
        
        aggregated.edges.extend(pass_state.edges)
    
    # Recalculate scores
    aggregated._update_scores()
    
    return aggregated


if __name__ == "__main__":
    from scorer import State
    
    # Test pruning
    pool = list(range(100, 200))
    state = State(pool)
    
    # Simulate some scoring
    for i in range(100, 110):
        state.seen[i] = 10
        state.picked[i] = 8  # High pick rate
    
    for i in range(110, 150):
        state.seen[i] = 10
        state.picked[i] = 5  # Medium pick rate
    
    for i in range(150, 200):
        state.seen[i] = 10
        state.picked[i] = 1  # Low pick rate
    
    state._update_scores()
    
    print(f"Original pool size: {len(pool)}")
    print(f"Top 10 scores: {[(cp, state.score[cp]) for cp in state.top_n(10)]}")
    
    # Prune with margin
    pruned_margin = prune_with_margin(state, target_size=20, margin=5)
    print(f"\nPruned with margin (20+5): {len(pruned_margin)}")
    
    # Prune to exact target
    pruned_exact = prune_to_target(state, target_size=20)
    print(f"Pruned to exact target (20): {len(pruned_exact)}")
    print(f"Top 5 in pruned: {pruned_exact[:5]}")
