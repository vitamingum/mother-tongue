"""Quick analysis of R1+R2 merged data for language composition."""
import json
from collections import Counter

# Load R1 scores
scores = {}
with open('data/round_1.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunk = json.loads(line)
        for g, s in chunk['scores'].items():
            scores[g] = s

# Load R2 assay
assay = {}
with open('data/round_2_assay.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunk = json.loads(line)
        for a in chunk['assays']:
            assay[a['glyph']] = a

# Merge
merged = []
for g, a in assay.items():
    if g in scores:
        merged.append({**a, 'score': scores[g]})
merged.sort(key=lambda x: -x['score'])

# Top candidates by category
print("TOP CANDIDATES BY CATEGORY (score-ranked)")
print("=" * 70)
cats = {}
for m in merged:
    c = m['category']
    cats.setdefault(c, []).append(m)

for cat in ['SUB', 'PRO', 'REL', 'MOD', 'STR']:
    items = cats.get(cat, [])[:20]
    line = '  '.join(f"{m['glyph']}" for m in items)
    print(f"\n{cat} ({len(cats.get(cat, []))} total, top 20):")
    print(f"  {line}")

# Cross-tabs for top 200
top200 = merged[:200]
print("\n\nCATEGORY x ARITY (top 200)")
print("=" * 50)
cross = Counter((m['category'], m['arity']) for m in top200)
header = "      " + "    ".join(f"{a:>3}" for a in ['0', '1', '2', 'N'])
print(header)
for cat in ['SUB', 'PRO', 'REL', 'MOD', 'STR']:
    vals = "    ".join(f"{cross.get((cat, a), 0):3d}" for a in ['0', '1', '2', 'N'])
    print(f"  {cat} {vals}")

print("\n\nCATEGORY x FAILURE (top 200)")
print("=" * 50)
cross2 = Counter((m['category'], m['failure']) for m in top200)
header = "      " + "  ".join(f"{f:>5}" for f in ['SAT', 'STALL', 'BOOM', 'NULL'])
print(header)
for cat in ['SUB', 'PRO', 'REL', 'MOD', 'STR']:
    vals = "  ".join(f"{cross2.get((cat, f), 0):5d}" for f in ['SAT', 'STALL', 'BOOM', 'NULL'])
    print(f"  {cat} {vals}")

# Interesting combos
print("\n\nINTERESTING ARCHETYPES")
print("=" * 50)

# Engines: PRO + Arity 2 + STALL (hungry transformers)
engines = [m for m in merged if m['category'] == 'PRO' and m['arity'] == '2' and m['failure'] == 'STALL']
print(f"\nENGINES (PRO + Binary + STALL) = {len(engines)}")
print(f"  Top: {'  '.join(m['glyph'] for m in engines[:30])}")

# Anchors: SUB + Arity 0 + SAT (stable ground)
anchors = [m for m in merged if m['category'] == 'SUB' and m['arity'] == '0' and m['failure'] == 'SAT']
print(f"\nANCHORS (SUB + Nullary + SAT) = {len(anchors)}")
print(f"  Top: {'  '.join(m['glyph'] for m in anchors[:30])}")

# Gates: REL + Arity 2 + BOOM (logic connectives that explode on contradiction)
gates = [m for m in merged if m['category'] == 'REL' and m['arity'] == '2' and m['failure'] == 'BOOM']
print(f"\nGATES (REL + Binary + BOOM) = {len(gates)}")
print(f"  Top: {'  '.join(m['glyph'] for m in gates[:30])}")

# Modifiers: MOD + Arity 1 (quality changers)
mods = [m for m in merged if m['category'] == 'MOD' and m['arity'] == '1']
print(f"\nQUALIFIERS (MOD + Unary) = {len(mods)}")
print(f"  Top: {'  '.join(m['glyph'] for m in mods[:30])}")

# Frames: STR + Symmetric
frames = [m for m in merged if m['category'] == 'STR' and m['direction'] == 'S']
print(f"\nFRAMES (STR + Symmetric) = {len(frames)}")
print(f"  Top: {'  '.join(m['glyph'] for m in frames[:30])}")

# Summary stats
print(f"\n\n{'=' * 50}")
print(f"SUMMARY")
print(f"{'=' * 50}")
print(f"Total assayed: {len(assay)}")
print(f"Merged (score+assay): {len(merged)}")
print(f"Score 10: {sum(1 for m in merged if m['score'] == 10)}")
print(f"Score 9: {sum(1 for m in merged if m['score'] == 9)}")
print(f"Score 8: {sum(1 for m in merged if m['score'] == 8)}")
print(f"Score 7: {sum(1 for m in merged if m['score'] == 7)}")
