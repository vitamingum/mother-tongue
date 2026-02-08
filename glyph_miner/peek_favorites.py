"""Quick peek at current mining favorites by testing a few slates."""
import asyncio
import sys
sys.path.insert(0, '.')

from runner_async import AsyncOllamaRunner
from unicode import enum_unicode
from sampler import create_slate, format_slate
import random

async def peek_favorites():
    """Run a few test slates to see what gets picked."""
    print("🔍 Peeking at model preferences...\n")
    
    # Get filtered unicode pool
    pool = enum_unicode()
    random.seed(42)
    random.shuffle(pool)
    
    # Take diverse samples from different parts of pool
    sample_slates = []
    for i in range(6):
        start = (i * len(pool) // 6)
        slate = pool[start:start+64]
        sample_slates.append(slate)
    
    async with AsyncOllamaRunner('qwen2.5-coder:14b', max_concurrent=6) as runner:
        results = []
        for i, slate in enumerate(sample_slates):
            slate_chars = format_slate(slate)
            slate_set = set(slate)
            output = await runner.infer_one(slate_chars, temperature=0.7)
            result = runner.parse_output(output, slate_set)
            
            if result:
                g1, g2 = chr(result[0]), chr(result[1])
                results.append((g1, g2))
                print(f"  Slate {i+1}: {g1} {g2}")
            else:
                print(f"  Slate {i+1}: [invalid]")
        
        print(f"\n✨ Favorites from {len([r for r in results if r])} valid selections:")
        for g1, g2 in results:
            if g1 and g2:
                print(f"     {g1}  {g2}")

if __name__ == "__main__":
    asyncio.run(peek_favorites())
