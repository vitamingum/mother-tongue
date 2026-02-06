import json

with open('data/round_1.jsonl', encoding='utf-8') as f:
    d = json.loads(f.readline())

print(f"Chunk {d['chunk_id']}: {len(d['scores'])} scores")
print(f"\nFirst 500 chars of response2:")
print(d['response2'][:500])
