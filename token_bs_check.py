"""
BS CHECK: Do MT glyphs actually save tokens for inter-model communication?
Compare English, MT, ASCII shortcodes, and JSON function calls.
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

test_cases = [
    ("Read this file and summarize the key points",
     "!機思【物】⇒示", "basic summarize"),
    ("Transform this Python code to Rust, preserving the logic",
     "!【物】化【物】∧不破理", "code transform"),
    ("Search the codebase for all usages of this function and list them",
     "!機動?【λ】∈【網】⇒多示", "search usages"),
    ("Generate 5 variations, score each one, return the best 3",
     "!生【多物】∧思⇒【善小多示】", "generate+filter"),
    ("If the output contains errors, retry with relaxed constraints. Otherwise return it.",
     "!動⇒示∨【破⇒⭮不■】", "conditional retry"),
]

print("TOKEN COUNT COMPARISON: English vs MT Glyphs (cl100k_base)")
print("=" * 70)
for eng, mt, desc in test_cases:
    e = len(enc.encode(eng))
    m = len(enc.encode(mt))
    delta = m - e
    sign = "+" if delta > 0 else ""
    print(f"  {desc:<22}  EN={e:2d}  MT={m:2d}  delta={sign}{delta}")

print()
print("PER-GLYPH TOKEN COST (how many tokens each glyph eats)")
print("=" * 60)
glyphs = list("!?機思物化動入示⇒【】∧∨不λ⭮間網多小善破生全積中理■止☌絕⥎⇼⚖⏸↺⧗⮻⦸⌲≡≋⏽▷◁⨝⊞")
for g in glyphs:
    t = len(enc.encode(g))
    print(f"  {g} = {t} tok")

print()
print("FOUR-WAY COMPARISON FOR THE SAME INSTRUCTION")
print("=" * 70)
comparisons = [
    ("Summarize",
     "Read this file and summarize the key points",
     "!機思【物】⇒示",
     "S(R(f),K)->O",
     '{"op":"summarize","target":"file"}'),
    ("Transform",
     "Transform this Python code to Rust, preserving the logic",
     "!【物】化【物】∧不破理",
     "T(src,py,rs,keep=logic)",
     '{"op":"transform","from":"py","to":"rs","preserve":"logic"}'),
    ("Search",
     "Search the codebase for all usages of this function and list them",
     "!機動?【λ】∈【網】⇒多示",
     "FIND(fn,scope=all)->LIST",
     '{"op":"find_usages","target":"function","scope":"codebase"}'),
]

for label, eng, mt, asc, jsn in comparisons:
    print(f"\n  [{label}]")
    for fmt, text in [("English", eng), ("MT Glyph", mt), ("ASCII", asc), ("JSON", jsn)]:
        t = len(enc.encode(text))
        print(f"    {fmt:<10} {t:2d} tok  |  {text}")

print()
print("VERDICT")
print("=" * 70)
# Calculate averages
en_total = sum(len(enc.encode(e)) for e, _, _ in test_cases)
mt_total = sum(len(enc.encode(m)) for _, m, _ in test_cases)
print(f"  Average EN tokens: {en_total / len(test_cases):.1f}")
print(f"  Average MT tokens: {mt_total / len(test_cases):.1f}")
print(f"  MT/EN ratio: {mt_total / en_total:.2f}x")
if mt_total > en_total:
    print(f"  MT uses {mt_total - en_total} MORE tokens total across {len(test_cases)} tests.")
    print("  >>> GLYPHS ARE MORE EXPENSIVE THAN ENGLISH <<<")
else:
    print(f"  MT saves {en_total - mt_total} tokens total across {len(test_cases)} tests.")
    print("  >>> GLYPHS SAVE TOKENS <<<")
