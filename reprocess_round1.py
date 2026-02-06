"""Reprocess existing round_1.jsonl with decimal-aware parser"""
import json
import re

def parse_scores_new(response: str, expected_glyphs: list) -> dict:
    """New parser - accepts decimals"""
    scores = {}
    pattern = r'^(.)\s+(\d+(?:\.\d+)?)$'
    for line in response.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        match = re.match(pattern, line)
        if match:
            glyph = match.group(1)
            score = round(float(match.group(2)))
            if 0 <= score <= 10:
                scores[glyph] = score
        else:
            # Fallback parsing
            parts = line.split()
            if len(parts) >= 2:
                try:
                    glyph = parts[0]
                    score = round(float(parts[-1]))
                    if 0 <= score <= 10 and glyph in expected_glyphs:
                        scores[glyph] = score
                except (ValueError, IndexError):
                    pass
    return scores

# Load and reprocess
data = []
with open('data/round_1.jsonl', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

print("🔧 Reprocessing with decimal-aware parser...")
print("="*60)

old_total = sum(len(d['scores']) for d in data)
recovered = 0

for chunk in data:
    old_count = len(chunk['scores'])
    new_scores = parse_scores_new(chunk['response2'], chunk['glyphs'])
    new_count = len(new_scores)
    
    if new_count > old_count:
        recovered += (new_count - old_count)
        print(f"Chunk {chunk['chunk_id']:3d}: {old_count:2d} → {new_count:2d} scores (+{new_count - old_count})")

new_total = old_total + recovered

print()
print("="*60)
print(f"BEFORE: {old_total:,} / {len(data)*64:,} scores ({old_total/(len(data)*64)*100:.1f}%)")
print(f"AFTER:  {new_total:,} / {len(data)*64:,} scores ({new_total/(len(data)*64)*100:.1f}%)")
print(f"RECOVERED: {recovered:,} glyphs")
print()
print(f"💾 Would you like to rewrite round_1.jsonl with fixed scores?")
print(f"   (This won't affect the live run, only the saved file)")
