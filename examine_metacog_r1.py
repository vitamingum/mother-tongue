import json
from collections import Counter

# Read all glyphs from metacog_round_1.jsonl
all_glyphs = []
glyph_scores = {}

print("Reading metacog_round_1.jsonl...")
with open('data/metacog_round_1.jsonl', 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        try:
            entry = json.loads(line)
            glyphs_in_chunk = entry.get('glyphs', [])
            scores = entry.get('scores', {})
            
            for glyph in glyphs_in_chunk:
                all_glyphs.append(glyph)
                if glyph in scores:
                    if glyph not in glyph_scores:
                        glyph_scores[glyph] = []
                    glyph_scores[glyph].append(scores[glyph])
        except Exception as e:
            print(f"Error on line {line_num}: {e}")

print(f"\nTotal glyph instances: {len(all_glyphs)}")
print(f"Unique glyphs: {len(set(all_glyphs))}")

# Get unique glyphs
unique_glyphs = sorted(set(all_glyphs))
print(f"\nFirst 20 unique glyphs: {unique_glyphs[:20]}")
print(f"Last 20 unique glyphs: {unique_glyphs[-20:]}")

# Save all unique glyphs to a file for examination
with open('data/metacog_r1_all_glyphs.txt', 'w', encoding='utf-8') as f:
    for glyph in unique_glyphs:
        f.write(f"{glyph}\n")

print(f"\nAll unique glyphs saved to data/metacog_r1_all_glyphs.txt")
print(f"Total unique glyphs to examine: {len(unique_glyphs)}")
