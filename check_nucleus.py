"""Check which nucleus glyphs exist in R1 scores and R2 assay."""
import json

NUCLEUS = list("≡⇒≠∧∨¬不∈化生用動止λ天坤人物空心理道中大真")

# Load R1
scores = {}
with open('data/round_1.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunk = json.loads(line)
        for g, s in chunk['scores'].items():
            scores[g] = s

# Load R2
assay = {}
with open('data/round_2_assay.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunk = json.loads(line)
        for a in chunk['assays']:
            assay[a['glyph']] = a

print(f"{'Glyph':>6} {'R1 Score':>9} {'R2 Cat':>7} {'R2 Arity':>9} {'R2 Dir':>7} {'R2 Fail':>8}")
print("-" * 55)
for g in NUCLEUS:
    s = scores.get(g, "MISSING")
    a = assay.get(g)
    if a:
        print(f"{g:>6} {str(s):>9} {a['category']:>7} {a['arity']:>9} {a['direction']:>7} {a['failure']:>8}")
    else:
        print(f"{g:>6} {str(s):>9}  -- NOT ASSAYED --")
