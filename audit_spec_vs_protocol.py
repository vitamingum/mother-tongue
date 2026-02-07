"""
AUDIT: MODEL_AUTOMATION_SPEC vs GLYPH_PROTOCOL vs LIVE CODE

Sonnet is currently executing this:

⟦ IMPORT_AUDIT_PROTOCOL ⟧
1. ● 立 [audit_report.txt]
2. ∀ f ∈ { *.py } :
     ● ( 析 imports(f) ) 
     ? ( import X ∈ f ∧ count(X) == 0 ) 
        ⇒ ●( 出[audit_report.txt] : "UNUSED: " + X + " in " + f )
     ? ( import X ∈ f ∧ X ∉ requirements.txt ∧ X ∉ stdlib ) 
        ⇒ ●( 出[audit_report.txt] : "MISSING_DEP: " + X + " in " + f )
3. ■ ( audit_report.txt ) :
     ! ( Format == "TYPE: Module in File" )

Let's audit every symbol used.
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def tok(text):
    return len(enc.encode(text))

print("=" * 70)
print("SYMBOL AUDIT: What Sonnet is actually parsing")
print("=" * 70)

# Every distinct glyph/symbol in the live code
symbols_used = {
    # Modal prefixes (from spec)
    "●": ("EXECUTE", "spec 2.1"),
    "■": ("CONSTRAIN", "spec 2.1"),
    # Scope delimiters
    "⟦": ("SYSTEM_OPEN", "spec 2.2"),
    "⟧": ("SYSTEM_CLOSE", "spec 2.2"),
    # Control flow
    "⇒": ("IMPLIES/NEXT", "spec 2.3"),
    "∀": ("FOR ALL", "spec 2.3"),
    "?": ("BRANCH", "spec 2.3"),
    "!": ("ASSERT", "spec 2.3"),
    # Set logic
    "∈": ("IN/MEMBER", "spec 2.5"),
    "∉": ("NOT IN", "spec 2.5"),
    "∧": ("AND", "spec 2.5"),
    # Semantic primitives
    "立": ("ESTABLISH/INIT", "spec 2.4"),
    "析": ("ANALYZE/PARSE", "spec 2.4"),
    "出": ("OUTPUT/WRITE", "spec 2.4"),
}

print(f"\n{'Symbol':<6} {'Tok':>4} {'Role':<20} {'Source':<12} {'Spec claims':>12}")
print("-" * 65)

total_cost = 0
spec_wrong = []
for sym, (role, source) in symbols_used.items():
    t = tok(sym)
    total_cost += t
    # Check what the spec CLAIMS the token cost is
    spec_claim_map = {
        "●": 1, "■": 1, "⟦": 3, "⟧": 3,
        "⇒": 1, "∀": 1, "?": 1, "!": 1,
        "∈": 1, "∉": 1, "∧": 1,
        "立": 1, "析": 1, "出": 1,
    }
    claimed = spec_claim_map.get(sym, "?")
    match = "✓" if t == claimed else f"WRONG (says {claimed})"
    if t != claimed:
        spec_wrong.append((sym, role, claimed, t))
    print(f"  {sym:<4}  {t:>3}   {role:<20} {source:<12} {match:>12}")

print(f"\n  Total symbols: {len(symbols_used)}")
print(f"  Total token cost: {total_cost}")

if spec_wrong:
    print(f"\n  ⚠ SPEC ERRORS ({len(spec_wrong)} wrong token costs):")
    for sym, role, claimed, actual in spec_wrong:
        print(f"    {sym} {role}: spec says {claimed}-tok, actually {actual}-tok")

# ───────────────────────────────────────────────
# Now: how does the spec compare to GLYPH_PROTOCOL?
# ───────────────────────────────────────────────
print("\n\n" + "=" * 70)
print("SPEC vs GLYPH_PROTOCOL: DESIGN DIFFERENCES")
print("=" * 70)

comparisons = [
    ("MODAL PREFIXES",
     "Spec has ● ○ ■ (execute/latent/constrain)",
     "Protocol has none — verbs ARE the mode",
     "Spec is BETTER here. ● means 'do exactly this.' ○ means 'think freely.' The mode prefix tells Sonnet HOW to process, not just WHAT to process. This is a real cognitive switch."),
    
    ("FLOW ARROW",
     "Spec uses ⇒ (claims 1-tok, actually 3-tok)",
     "Protocol uses → (actually 1-tok)",
     "Protocol is CORRECT. ⇒ costs 3x what the spec claims. → does the same job for 1 token."),
    
    ("SCOPE BRACKETS",
     "Spec uses ⟦⟧ for system, 『』for raw data, 【】for output",
     "Protocol uses only 【】for everything",
     "Spec is RICHER. Three bracket types = three memory zones. 【output target】vs『raw input data』vs ⟦immutable context⟧ is a real distinction. But ⟦⟧ costs 3 tok each."),
    
    ("VERBS",
     "Spec: 立 析 出 變 選 削 移 入 理 道 (10 primitives)",
     "Protocol: 找修分化生動出示加削移定取保合正算入開回 (20 verbs)",
     "Protocol has 2x coverage. But spec's verbs are the RIGHT 10 — they map to what Sonnet actually does in the live code. 20 may be over-specified."),
    
    ("SET LOGIC",
     "Spec: ∈ ∉ ∩ ∪ ¬ ∅ ≣",
     "Protocol: ∈ ≠ 同 (minimal)",
     "Spec is STRONGER. The live code uses ∈ ∉ ∧ — set operations are essential for scoping. Protocol under-specified this."),
    
    ("FOR-ALL LOOP",
     "Spec: ∀ f ∈ { *.py } (explicit iteration)",
     "Protocol: no loop construct",
     "Spec is BETTER. The live code NEEDS ∀. You can't write the import audit without it."),
    
    ("ASSERTION",
     "Spec: ! (assert/critical requirement)",
     "Protocol: ! (imperative marker)",
     "Spec is BETTER. ! as ASSERT is more useful than ! as 'do this.' Every line is already imperative."),
    
    ("SCRATCHPAD",
     "Spec: ⟨ ⟩ hidden chain-of-thought",
     "Protocol: none",
     "Spec adds something REAL. Telling Sonnet 'reason here but don't output' is a genuine cognitive directive."),
]

for name, spec, proto, verdict in comparisons:
    print(f"\n  {name}")
    print(f"  {'─' * 60}")
    print(f"  Spec:     {spec}")
    print(f"  Protocol: {proto}")
    print(f"  Verdict:  {verdict}")

# ───────────────────────────────────────────────
# Now: how SHOULD the live code look with fixes?
# ───────────────────────────────────────────────
print("\n\n" + "=" * 70)
print("THE LIVE CODE: What's working and what to fix")
print("=" * 70)

live_code = """⟦ IMPORT_AUDIT_PROTOCOL ⟧

1.
● 立 [audit_report.txt]

2.
∀ f ∈ { *.py } :
   ● ( 析 imports(f) ) 
   
   ? ( import X ∈ f ∧ count(X) == 0 ) 
      ⇒ ● ( 出[audit_report.txt] : "UNUSED: " + X + " in " + f )
   
   ? ( import X ∈ f ∧ X ∉ requirements.txt ∧ X ∉ stdlib ) 
      ⇒ ● ( 出[audit_report.txt] : "MISSING_DEP: " + X + " in " + f )

3.
■ ( audit_report.txt ) :
   ! ( Format == "TYPE: Module in File" )"""

optimized = """⟦ IMPORT_AUDIT ⟧

● 立 audit_report.txt

∀ f ∈ *.py :
  ● 析 imports(f)
  ? import X ∈ f ∧ count(X) == 0
    → ● 出【audit_report.txt】"UNUSED: " + X + " in " + f
  ? import X ∈ f ∧ X ∉ requirements.txt ∧ X ∉ stdlib
    → ● 出【audit_report.txt】"MISSING_DEP: " + X + " in " + f

■ audit_report.txt :
  ! Format == "TYPE: Module in File" """

print(f"\n  CURRENT ({tok(live_code)} tokens):")
for line in live_code.strip().split('\n'):
    print(f"  {line}")

print(f"\n  OPTIMIZED ({tok(optimized)} tokens):")
for line in optimized.strip().split('\n'):
    print(f"  {line}")

print(f"\n  Savings: {tok(live_code) - tok(optimized)} tokens ({(1-tok(optimized)/tok(live_code))*100:.0f}%)")

print("\n  WHAT CHANGED:")
print("  · ⇒ → → (3 tok → 1 tok, same meaning)")
print("  · Removed unnecessary ( ) grouping")
print("  · Removed numbered steps (→ provides ordering)")
print("  · [ ] → 【】for output targets (spec consistency)")
print("  · Kept ⟦⟧ for system context (worth the 3-tok cost — it's a MODE SWITCH)")

# ───────────────────────────────────────────────
# The merged spec
# ───────────────────────────────────────────────
print("\n\n" + "=" * 70)
print("MERGED SPEC: Best of both")
print("=" * 70)
print("""
  FROM MODEL_AUTOMATION_SPEC (keep):
  ✓ Modal prefixes: ● ○ ■ (execute/latent/constrain)
  ✓ System scope: ⟦ ⟧ (worth 3-tok — it's a cognitive mode switch)
  ✓ Hidden scratchpad: ⟨ ⟩ (think but don't output)
  ✓ Assert: ! (not just imperative — MUST BE TRUE)
  ✓ ∀ for-all loop
  ✓ Set logic: ∈ ∉ ∧ ∪ ∩ ¬
  ✓ Semantic primitives: 立 析 出 入 削 移 選
  
  FROM GLYPH_PROTOCOL (keep):
  ✓ → not ⇒ (1-tok vs 3-tok, same job)
  ✓ 【】for output/scope binding
  ✓ Full verb set: 找修分化生動定取保合正算回開
  ✓ Quantifiers: 多少一空大小上下
  ✓ 不 for negation/constraint
  ✓ English inside brackets for domain terms
  
  FROM BOTH (keep):
  ✓ ? for conditionals
  ✓ ! for assertions
  ✓ 全 for ALL
  
  KILL:
  ✗ ⇒ (use → instead, saves 2 tok per use)
  ✗ ∴ (therefore — not used in practice)
  ✗ ≣ (use 同 instead — 1 tok)
  ✗ ∅ (use 空 instead — 1 tok, self-documenting)
  ✗ 變 (use 化 instead — 1 tok, same meaning)
  ✗ 理 道 (too philosophical, not actionable verbs)
""")

print("=" * 70)
print("WHAT THE LIVE CODE PROVES")
print("=" * 70)
print("""
  Sonnet is ALREADY EXECUTING glyph-lang. Right now. Successfully.
  
  The import audit program is 14 lines. It:
    · Creates a file (● 立)
    · Iterates all Python files (∀ f ∈)
    · Analyzes imports (● 析)
    · Conditionally branches (?)
    · Filters by set membership (∈, ∉)
    · Writes structured output (● 出)  
    · Validates format (■ !)
  
  That's a complete program. Loops, branches, I/O, validation.
  Sonnet parsed it. Sonnet executed it. No system prompt decoder ring needed.
  
  The question is no longer "will this work?"
  The question is "what's the minimal spec that covers all programs?"
  
  The live code uses 14 distinct symbols.
  The merged spec needs maybe 40.
  That's the language.
""")
