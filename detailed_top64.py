import json
from collections import defaultdict

# Read all scored glyphs
all_glyphs = {}
for line in open('data/round_1.jsonl', 'r', encoding='utf-8'):
    data = json.loads(line)
    for glyph, score in data['scores'].items():
        all_glyphs[glyph] = score

# Sort by score descending
sorted_glyphs = sorted(all_glyphs.items(), key=lambda x: (-x[1], x[0]))

print(f"📊 PROGRESS REPORT")
print("=" * 70)
print(f"Glyphs scored: {len(all_glyphs):,} / 105,472 (~{100*len(all_glyphs)/105472:.1f}%)")
print()

# Score distribution
print("📈 SCORE DISTRIBUTION:")
for threshold in [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]:
    count = sum(1 for g, s in all_glyphs.items() if s >= threshold)
    bar = "█" * int(count / len(all_glyphs) * 50)
    print(f"≥{threshold}: {count:4d} ({100*count/len(all_glyphs):5.1f}%) {bar}")

print("\n" + "=" * 70)
print("🏆 TOP 64 RANKED & SORTED")
print("=" * 70)

top_64 = sorted_glyphs[:64]

# Detailed rankings
for rank, (glyph, score) in enumerate(top_64, 1):
    stars = "⭐" * score
    if rank <= 6:
        prefix = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
    else:
        prefix = f"#{rank:2d}"
    print(f"{prefix}  {glyph}  Score: {score}  {stars}")

print("\n" + "=" * 70)
print("✨ VISUAL GROUPINGS:")
print("=" * 70)

score_groups = defaultdict(list)
for glyph, score in top_64:
    score_groups[score].append(glyph)

for score in sorted(score_groups.keys(), reverse=True):
    glyphs = score_groups[score]
    print(f"\n🎯 SCORE {score} ({len(glyphs)} glyphs):")
    # Print in rows of 10
    for i in range(0, len(glyphs), 10):
        print("   " + " ".join(glyphs[i:i+10]))

print("\n" + "=" * 70)
print("📦 ALL TOP 64 (copy-paste ready):")
print(''.join([g for g, s in top_64]))
