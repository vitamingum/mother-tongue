"""Sampling and slate generation."""
import random


def shuffle_pool(pool, seed, pass_num):
    """Deterministically shuffle pool based on seed and pass.
    
    Args:
        pool: list of codepoints
        seed: int - base seed
        pass_num: int - current pass number (φ in spec)
    
    Returns:
        Shuffled copy of pool
    """
    # φ (phi/golden ratio approximation) = 1.618
    phi = 1.618
    combined_seed = int(seed + pass_num * phi)
    
    pool_copy = pool.copy()
    rng = random.Random(combined_seed)
    rng.shuffle(pool_copy)
    
    return pool_copy


def create_slate(pool, k, round_num=0):
    """Create slate of K glyphs from pool, cycling by round.
    
    Args:
        pool: list of codepoints
        k: int - slate size
        round_num: int - round number for cycling through pool
    
    Returns:
        List of k codepoints from pool (no duplicates)
    """
    if len(pool) < k:
        raise ValueError(f"Pool size {len(pool)} < slate size {k}")
    
    # Cycle through pool based on round
    start = (round_num * k) % len(pool)
    indices = [(start + i) % len(pool) for i in range(k)]
    slate = [pool[i] for i in indices]
    
    # Deduplicate (only matters if k > len(pool))
    if len(set(slate)) != len(slate):
        slate = list(dict.fromkeys(slate))
    
    return slate


def format_slate(slate):
    """Format slate as string of characters for model input."""
    return ''.join(chr(cp) for cp in slate)


if __name__ == "__main__":
    # Test
    test_pool = list(range(0x4E00, 0x4E00 + 1000))  # CJK sample
    
    print(f"Original pool size: {len(test_pool)}")
    print(f"First 5: {test_pool[:5]}")
    
    # Shuffle for pass 1
    shuffled1 = shuffle_pool(test_pool, seed=42, pass_num=1)
    print(f"\nShuffled pass 1, first 5: {shuffled1[:5]}")
    
    # Shuffle for pass 2
    shuffled2 = shuffle_pool(test_pool, seed=42, pass_num=2)
    print(f"Shuffled pass 2, first 5: {shuffled2[:5]}")
    
    # Different results
    print(f"Pass 1 != Pass 2: {shuffled1[:5] != shuffled2[:5]}")
    
    # Deterministic: same seed+pass = same result
    shuffled1_repeat = shuffle_pool(test_pool, seed=42, pass_num=1)
    print(f"Deterministic: {shuffled1[:5] == shuffled1_repeat[:5]}")
    
    # Create slate
    slate = create_slate(shuffled1, k=64)
    print(f"\nSlate size: {len(slate)}")
    print(f"No duplicates: {len(set(slate)) == len(slate)}")
    print(f"Slate chars: {format_slate(slate[:10])}...")
