"""
FOLLOW-UP: What if we restrict to 1-token glyphs only?
Can we build a REAL compression language?
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# Test a bunch of potential replacement glyphs for the 3-token traps
candidates = []
# Common CJK that might be 1-token
test_chars = (
    # Common CJK
    "機器分析變轉移送出入返回始終開關上下左右前後大小多少全部"
    "心身目耳手足口言語文字書讀寫算數形色聲光明暗新舊高低遠近"
    "行走來去取得失敗合分連斷開閉升降增減成敗勝負"
    "看找選定做作用力能力量度數點線面體空時間地方向位置"
    # Arrows and math
    "→←↑↓↔↕⇒⇐⇔∧∨¬∀∃∈∉⊂⊃∪∩≡≠≤≥±×÷√∞∑∏∫"
    # Box drawing / structural
    "│─┌┐└┘├┤┬┴┼║═╔╗╚╝╠╣╦╩╬"
    # Misc useful
    "●○◆◇▲△▼▽◀▶►◄★☆♦♣♠♥"
    "·•‣※†‡§¶©®™°¹²³⁴⁵⁶⁷⁸⁹⁰"
    # Brackets
    "()[]{}⟨⟩《》「」『』【】〔〕〈〉"
)

print("SINGLE-TOKEN GLYPH CANDIDATES")
print("=" * 60)
single = []
double = []
triple = []
for c in test_chars:
    t = len(enc.encode(c))
    if t == 1:
        single.append(c)
    elif t == 2:
        double.append(c)
    else:
        triple.append(c)

print(f"\n1-TOKEN ({len(single)} chars):")
print("  " + " ".join(single))
print(f"\n2-TOKEN ({len(double)} chars):")
print("  " + " ".join(double))
print(f"\n3-TOKEN ({len(triple)} chars):")
print("  " + " ".join(triple))

# Now: build a token-optimized instruction set using ONLY 1-token chars
print("\n\n" + "=" * 70)
print("TOKEN-OPTIMIZED MT: Replace 3-token traps with 1-token equivalents")
print("=" * 70)

swaps = {
    "⇒": "→",   # flow arrow: 3 tok -> check
    "機": "分",   # ANALYZE: 3 tok -> check
    "網": "部",   # SCOPE: 3 tok -> check  
    "破": "失",   # BREAK: 3 tok -> check
    "⭮": "回",   # RETRY: 3 tok -> check
    "善": "上",   # GOOD: 2 tok -> check
}

print("\nProposed swaps:")
for old, new in swaps.items():
    old_t = len(enc.encode(old))
    new_t = len(enc.encode(new))
    print(f"  {old} ({old_t} tok) -> {new} ({new_t} tok)")

# Re-run the test cases with optimized glyphs
print("\n\nRE-TEST WITH OPTIMIZED GLYPHS")
print("=" * 70)

test_cases_opt = [
    ("Read this file and summarize the key points",
     "!分思【物】→示", "basic summarize"),
    ("Transform this Python code to Rust, preserving the logic",
     "!【物】化【物】∧不失理", "code transform"),
    ("Search the codebase for all usages of this function and list them",
     "!分動?【λ】∈【部】→多示", "search usages"),
    ("Generate 5 variations, score each one, return the best 3",
     "!生【多物】∧思→【上小多示】", "generate+filter"),
    ("If the output contains errors, retry with relaxed constraints. Otherwise return it.",
     "!動→示∨【失→回不■】", "conditional retry"),
]

print(f"{'task':<22} {'EN':>4} {'MT_old':>7} {'MT_new':>7} {'ASCII':>6}")
print("-" * 50)

ascii_cases = [
    "S(R(f),K)->O",
    "T(src,py,rs,keep=logic)",
    "FIND(fn,scope=all)->LIST",
    "GEN(5)->SCORE->TOP(3)",
    "IF(err,RETRY(relax),RET)",
]

en_total = mt_old_total = mt_new_total = asc_total = 0
for i, (eng, mt_new, desc) in enumerate(test_cases_opt):
    e = len(enc.encode(eng))
    # old MT from previous test
    old_mts = ["!機思【物】⇒示", "!【物】化【物】∧不破理", 
               "!機動?【λ】∈【網】⇒多示", "!生【多物】∧思⇒【善小多示】",
               "!動⇒示∨【破⇒⭮不■】"]
    m_old = len(enc.encode(old_mts[i]))
    m_new = len(enc.encode(mt_new))
    a = len(enc.encode(ascii_cases[i]))
    en_total += e; mt_old_total += m_old; mt_new_total += m_new; asc_total += a
    print(f"  {desc:<22} {e:3d}  {m_old:5d}  {m_new:5d}  {a:4d}")

n = len(test_cases_opt)
print("-" * 50)
print(f"  {'AVERAGE':<22} {en_total/n:3.0f}  {mt_old_total/n:5.0f}  {mt_new_total/n:5.0f}  {asc_total/n:4.0f}")
print(f"  {'vs English':<22} {'1.0x':>4}  {mt_old_total/en_total:.2f}x  {mt_new_total/en_total:.2f}x  {asc_total/en_total:.2f}x")

print("\n\nFINAL VERDICT")
print("=" * 70)
if mt_new_total <= en_total:
    print(f"  Optimized MT: {en_total - mt_new_total} tokens SAVED vs English ({mt_new_total/en_total:.2f}x)")
else:
    print(f"  Optimized MT: {mt_new_total - en_total} tokens MORE than English ({mt_new_total/en_total:.2f}x)")
print(f"  ASCII codes:  {en_total - asc_total} tokens SAVED vs English ({asc_total/en_total:.2f}x)")
print(f"  Old MT:       {mt_old_total - en_total} tokens MORE than English ({mt_old_total/en_total:.2f}x)")
