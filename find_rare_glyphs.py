"""Find rare glyphs (token ID > 80k) from single-token list."""
import tiktoken

# Read the single-token glyphs
with open('data/metacog_r1_all_glyphs_single_token_compact.txt', 'r', encoding='utf-8') as f:
    glyphs = f.read()

enc = tiktoken.get_encoding("o200k_base")

# Get token IDs for all glyphs
glyph_tokens = []
for g in glyphs:
    tokens = enc.encode(g)
    if len(tokens) == 1:
        glyph_tokens.append((g, tokens[0]))

# Filter to rare glyphs (token ID > 80k)
rare = [(g, tid) for g, tid in glyph_tokens if tid > 80000]

# Sort by token ID
rare.sort(key=lambda x: x[1])

print(f"Rare glyphs (token ID > 80k): {len(rare)}\n")

# Show ranges
print("Token ID ranges:")
print(f"  80k-90k: {sum(1 for _, t in rare if 80000 <= t < 90000)}")
print(f"  90k-100k: {sum(1 for _, t in rare if 90000 <= t < 100000)}")
print(f"  100k-110k: {sum(1 for _, t in rare if 100000 <= t < 110000)}")
print(f"  110k-120k: {sum(1 for _, t in rare if 110000 <= t < 120000)}")
print(f"  120k+: {sum(1 for _, t in rare if t >= 120000)}")

# Sample from different ranges
print("\n=== 80k-90k range (uncommon) ===")
for g, tid in rare[0:30]:
    print(f"{g}  {tid}")

print("\n=== 100k-110k range (rare) ===")
for g, tid in [(g, t) for g, t in rare if 100000 <= t < 110000][:30]:
    print(f"{g}  {tid}")

print("\n=== 120k+ range (very rare) ===
")
for g, tid in [(g, t) for g, t in rare if t >= 120000][:30]:
    print(f"{g}  {tid}")

# Save to file
with open('data/rare_glyphs_80k_plus.txt', 'w', encoding='utf-8') as f:
    for g, tid in rare:
        f.write(f"{g}\t{tid}\n")

print(f"\nSaved to: data/rare_glyphs_80k_plus.txt")
