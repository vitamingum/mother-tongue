import random

# Read all glyphs
with open('data/metacog_r1_all_glyphs.txt', 'r', encoding='utf-8') as f:
    glyphs = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(glyphs)} glyphs")

# Shuffle randomly
random.shuffle(glyphs)

# Save shuffled version
with open('data/metacog_r1_all_glyphs_shuffled.txt', 'w', encoding='utf-8') as f:
    for glyph in glyphs:
        f.write(f"{glyph}\n")

print(f"Shuffled {len(glyphs)} glyphs")
print(f"Saved to: data/metacog_r1_all_glyphs_shuffled.txt")
print(f"\nFirst 20 after shuffle:")
for i, glyph in enumerate(glyphs[:20], 1):
    print(f"{i:2d}. {glyph}")
