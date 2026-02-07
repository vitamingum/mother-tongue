import json
import unicodedata

# Load scores
with open('data/metacog_round_1.jsonl', 'r', encoding='utf-8') as f:
    scores = {}
    for line in f:
        chunk = json.loads(line)
        for glyph, score_data in chunk['scores'].items():
            if isinstance(score_data, dict):
                mag = score_data.get('magnitude', score_data.get('score', 0))
            else:
                mag = score_data
            scores[glyph] = mag

sorted_glyphs = sorted(scores.items(), key=lambda x: -x[1])

print('DEEP DIVE - TOP METACOGNITIVE GLYPHS WITH UNICODE NAMES')
print('=' * 90)
print()

# Categorize by type
loops = []
branches = []
arrows = []
ellipses = []
negations = []
relations = []
other = []

for g, s in sorted_glyphs[:200]:
    try:
        name = unicodedata.name(g, '')
    except:
        name = ''
    
    if 'ARROW' in name and ('CIRCULAR' in name or 'HOOK' in name or 'RETURN' in name):
        loops.append((g, s, name))
    elif 'FORK' in name or 'TINE' in name or 'CURLY' in name or 'PITCHFORK' in name:
        branches.append((g, s, name))
    elif 'ARROW' in name:
        arrows.append((g, s, name))
    elif 'DOT' in name or 'ELLIPSIS' in name or 'MIDLINE' in name:
        ellipses.append((g, s, name))
    elif 'NOT' in name or 'NEGAT' in name:
        negations.append((g, s, name))
    elif 'EQUAL' in name or 'SIMILAR' in name or 'APPROX' in name or 'LESS' in name or 'GREATER' in name:
        relations.append((g, s, name))
    else:
        other.append((g, s, name))

print(f'🔄 LOOPS & RECURSION ({len(loops)}):')
for g, s, name in loops[:15]:
    print(f'  {g} ({s:.0f})  {name}')
print()

print(f'🌿 BRANCHING & FORKING ({len(branches)}):')
for g, s, name in branches[:15]:
    print(f'  {g} ({s:.0f})  {name}')
print()

print(f'⋯ SUSPENSION & ELLIPSIS ({len(ellipses)}):')
for g, s, name in ellipses[:15]:
    print(f'  {g} ({s:.0f})  {name}')
print()

print(f'🚫 NEGATION & REFUSAL ({len(negations)}):')
for g, s, name in negations[:15]:
    print(f'  {g} ({s:.0f})  {name}')
print()

print(f'≈ APPROXIMATION & RELATIONS ({len(relations)}):')
for g, s, name in relations[:20]:
    print(f'  {g} ({s:.0f})  {name}')
print()

print(f'➜ ARROWS & TRANSFORMATIONS ({len(arrows)}):')
for g, s, name in arrows[:20]:
    print(f'  {g} ({s:.0f})  {name}')
print()

print(f'⊕ OTHER COMPELLING ({len(other)} total) - showing top 30:')
for g, s, name in other[:30]:
    print(f'  {g} ({s:.0f})  {name}')
print()

# Show absolute top 30
print()
print('🏆 ABSOLUTE TOP 30:')
print('=' * 90)
for i, (g, s) in enumerate(sorted_glyphs[:30], 1):
    try:
        name = unicodedata.name(g, 'UNKNOWN')
    except:
        name = 'UNKNOWN'
    print(f'{i:2d}. {g} ({s:.0f})  {name}')
