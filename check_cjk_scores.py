import json

# CJK characters from previous run
target_glyphs = set('⻱⿏⿐⿑⿒⿓⿔⿕乽亹儇儻儼儽儾兣兾兿冀冁凟劀劎劐劖劗劘劙劚勳勴勵勷勸匶匷卛厴厵叆叇叢嚨嚩嚫嚮嚰嚱嚳嚴嚵嚶嚷嚸嚹嚻嚼嚽嚾嚿囀囁囂囃')

# Load current results
found = {}
with open('data/round_1.jsonl', encoding='utf-8') as f:
    for line in f:
        chunk = json.loads(line)
        for glyph, score in chunk['scores'].items():
            if glyph in target_glyphs:
                found[glyph] = score

print("🔍 Searching for previous top scorers in new Crystalline Gravity run...")
print("="*70)
print(f"Target glyphs: {len(target_glyphs)}")
print(f"Found so far: {len(found)}")
print()

if found:
    print("✨ FOUND GLYPHS (sorted by new score):")
    print("="*70)
    for glyph, score in sorted(found.items(), key=lambda x: -x[1]):
        stars = "⭐" * score
        print(f"{glyph}  Score: {score}  {stars}")
    
    print()
    print("📊 COMPARISON:")
    print("="*70)
    print(f"Old run (complexity): All scored 10")
    print(f"New run (crystalline gravity): Range {min(found.values())}-{max(found.values())}")
    avg = sum(found.values()) / len(found)
    print(f"Average new score: {avg:.1f}")
else:
    print("❌ None found yet - still in early Unicode ranges (math operators, etc.)")
    print(f"   CJK characters likely in later chunks")

print()
print(f"Current progress: ~3% of 105k glyphs")
print(f"CJK ranges come later in Unicode spectrum")
