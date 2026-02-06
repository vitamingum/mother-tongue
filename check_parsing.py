import json

data = []
with open('data/round_1.jsonl', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

print(f"📊 Parsing Analysis:")
print(f"{'='*60}")
print(f"Total chunks processed: {len(data)}")
print(f"Empty score chunks (0): {sum(1 for d in data if len(d['scores']) == 0)}")
print(f"Partial chunks (1-63): {sum(1 for d in data if 0 < len(d['scores']) < 64)}")
print(f"Full chunks (64): {sum(1 for d in data if len(d['scores']) == 64)}")

total_scores = sum(len(d['scores']) for d in data)
total_possible = len(data) * 64
success_rate = (total_scores / total_possible * 100) if total_possible > 0 else 0

print(f"\nTotal glyphs scored: {total_scores:,} / {total_possible:,} ({success_rate:.1f}%)")

# Show a sample of failed chunk
empty_chunks = [d for d in data if len(d['scores']) == 0]
if empty_chunks:
    print(f"\n❌ Sample failed chunk response:")
    print(f"Chunk ID: {empty_chunks[0]['chunk_id']}")
    print(f"Response2 (first 500 chars):")
    print(empty_chunks[0]['response2'][:500])
