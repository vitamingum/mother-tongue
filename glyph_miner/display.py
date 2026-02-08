"""Live progress display for glyph mining."""


def print_leaderboard(state, stage, pass_num, round_num, 
                      total_rounds, pool_size, valid_count, 
                      prev_top=None, top_k=20):
    """Print leaderboard with top glyphs and progress.
    
    Args:
        state: State object with current scores
        stage: str - stage name ('A', 'B', 'C')
        pass_num: int - current pass
        round_num: int - current round
        total_rounds: int - total rounds in pass
        pool_size: int - current pool size
        valid_count: int - successful inference count
        prev_top: list - previous top codepoints (for diff)
        top_k: int - number of top glyphs to display
    
    Returns:
        list - current top K codepoints
    """
    sorted_items = state.get_sorted_by_score()
    top = sorted_items[:top_k]
    
    # Header
    valid_pct = (valid_count / max(round_num, 1)) * 100
    print(f"\n── Stage {stage}  Pass {pass_num}/{5 if stage == 'A' else 4}  "
          f"Round {round_num}/{total_rounds}  "
          f"Pool: {pool_size}  Valid: {valid_pct:.0f}% ──\n")
    
    # Table header
    print(f" {'#':>3}  glyph  {'score':>6}  {'seen':>5}  {'picked':>6}  {'bytes':>5}")
    
    # Top entries
    for i, item in enumerate(top):
        cp, score, seen, picked, byte_len = item
        print(f" {i+1:>3}   {chr(cp):>1}    {score:.3f}  {seen:>5}  {picked:>6}  {byte_len:>5}")
    
    # Progress bar
    pct = round_num / total_rounds
    filled = int(pct * 30)
    bar = '▰' * filled + '▱' * (30 - filled)
    print(f"\n  {bar} {pct*100:.0f}%")
    
    # Diff from previous
    if prev_top is not None:
        current_cps = {cp for cp, _, _, _, _ in top}
        prev_cps = set(prev_top)
        new = current_cps - prev_cps
        dropped = prev_cps - current_cps
        
        if new or dropped:
            if new:
                new_chars = ' '.join(chr(cp) for cp in list(new)[:10])  # Limit display
                print(f"  NEW: {new_chars}")
            if dropped:
                dropped_chars = ' '.join(chr(cp) for cp in list(dropped)[:10])  # Limit display
                print(f"  DROPPED: {dropped_chars}")
    
    # Return current top codepoints for next comparison
    return [cp for cp, _, _, _, _ in top]
