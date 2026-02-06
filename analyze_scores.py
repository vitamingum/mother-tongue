import json

# Read JSONL and analyze scores
all_scores = []
for line in open('data/round_1.jsonl', 'r', encoding='utf-8'):
    data = json.loads(line)
    scores = list(data['scores'].values())
    all_scores.extend(scores)

print(f"Total glyphs scored: {len(all_scores)}")
print(f"Score range: {min(all_scores)} to {max(all_scores)}")
print(f"Average score: {sum(all_scores)/len(all_scores):.2f}")
print(f"\nScore distribution:")
for threshold in [0, 3, 5, 7, 9]:
    count = sum(1 for s in all_scores if s >= threshold)
    print(f"  >= {threshold}: {count} ({100*count/len(all_scores):.1f}%)")
