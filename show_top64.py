import json
from collections import defaultdict

# Read all scored glyphs
all_glyphs = {}
for line in open('data/round_1.jsonl', 'r', encoding='utf-8'):
    data = json.loads(line)
    for glyph, score in data['scores'].items():
        all_glyphs[glyph] = score

# Sort by score (descending), then by glyph
sorted_glyphs = sorted(all_glyphs.items(), key=lambda x: (-x[1], x[0]))

# Top 64
top_64 = sorted_glyphs[:64]

print(f"Total glyphs scored so far: {len(all_glyphs)}")
print(f"\n🏆 TOP 64 GLYPHS (sorted by score)")
print("=" * 60)

# Group by score
score_groups = defaultdict(list)
for glyph, score in top_64:
    score_groups[score].append(glyph)

# Display by score groups
for score in sorted(score_groups.keys(), reverse=True):
    glyphs = score_groups[score]
    print(f"\nScore {score}: {len(glyphs)} glyphs")
    print(''.join(glyphs))

print("\n" + "=" * 60)
print("ALL TOP 64 TOGETHER:")
print(''.join([g for g, s in top_64]))
