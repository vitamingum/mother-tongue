"""Sample rare CJK glyphs and check their meanings."""
import tiktoken

# Test specific rare CJK glyphs
test_glyphs = """
禁 露 危 決 創 減
築 鍵 競 層 績 複
織 臓 燃 蔵 継 獲
層 績 複 封 鍵 築
態 幅 識 略 績 域
築 層 績 織 複 封
"""

enc = tiktoken.get_encoding("o200k_base")

results = []
for line in test_glyphs.strip().split('\n'):
    for g in line.split():
        if g:
            tokens = enc.encode(g)
            if len(tokens) == 1:
                results.append((g, tokens[0]))

# Sort by token ID
results.sort(key=lambda x: x[1])

# Remove duplicates
seen = set()
unique = []
for g, tid in results:
    if g not in seen:
        seen.add(g)
        unique.append((g, tid))

print("Sample Rare CJK Glyphs (Token ID Analysis):\n")
for g, tid in unique:
    range_label = ""
    if tid < 20000:
        range_label = "ULTRA-COMMON"
    elif tid < 50000:
        range_label = "COMMON"
    elif tid < 80000:
        range_label = "MODERATE"
    elif tid < 120000:
        range_label = "RARE"
    else:
        range_label = "VERY RARE"
    
    print(f"{g}  {tid:>6}  {range_label}")
