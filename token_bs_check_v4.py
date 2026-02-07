"""
THE REAL QUESTION: Is it structure or terseness?

The v3 test showed glyphs save ~50% vs verbose English.
But the honesty check showed terse English beats glyphs.

So what's the ACTUAL value proposition?
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def tok(text):
    return len(enc.encode(text))

# ─────────────────────────────────────────────
# Three versions of the SAME handoff
# ─────────────────────────────────────────────

# Opus's reasoning output (what it figured out)
reasoning = """The test computes HMAC over json.dumps(payload) but the handler
computes HMAC over the raw request body. json.dumps may reorder keys,
producing different bytes. Fix: compute body once, derive both signature
and request data from that same string."""

# VERSION A: Verbose English handoff
verbose = """TASK: Fix test_payment_webhook.

The root cause is a signature mismatch. The test computes the HMAC signature 
using json.dumps(payload), but the webhook handler computes the HMAC from the 
raw request body bytes. Since json.dumps may reorder dictionary keys, the bytes 
differ even though the payload is logically identical.

To fix this:
1. In the test, compute the body string first: body = json.dumps(payload, separators=(',', ':'))
2. Compute the HMAC signature from that exact body string
3. Send body (the string) as the request data, not the payload dict
4. Verify the test passes
5. Search for other webhook tests with the same pattern and fix those too"""

# VERSION B: Terse English (same info, fewer words)
terse = """Fix test_payment_webhook.
Cause: HMAC(json.dumps(payload)) != HMAC(raw body) — key reorder.
Fix: body = json.dumps(payload, separators=(',',':')), sig = HMAC(body), send body not dict.
Run test. Find same pattern in other webhook tests, fix."""

# VERSION C: Glyph protocol
glyph = """修 test_payment_webhook
因: HMAC(json.dumps) ≠ HMAC(raw body) — key order
修: body=json.dumps(payload,separators=(',',':'))
   sig=HMAC(body), 送 body 不 dict
動 test → 確
找 同 pattern ∈ webhook tests → 修"""

# VERSION D: Structured function call (what APIs actually use)
structured = """{
  "task": "fix_test",
  "target": "test_payment_webhook",
  "root_cause": "hmac_mismatch",
  "detail": "json.dumps reorders keys vs raw body",
  "steps": [
    {"action": "set", "var": "body", "value": "json.dumps(payload, separators=(',',':'))"},
    {"action": "set", "var": "sig", "value": "HMAC(body)"},
    {"action": "replace", "arg": "payload_dict", "with": "body_string"},
    {"action": "run", "target": "test"},
    {"action": "find_and_fix", "pattern": "same_hmac_issue", "scope": "webhook_tests"}
  ]
}"""

print("FOUR FORMATS FOR ONE OPUS→SONNET HANDOFF")
print("=" * 70)
for label, text in [("Verbose English", verbose), ("Terse English", terse), 
                     ("Glyph Protocol", glyph), ("JSON Structured", structured)]:
    t = tok(text)
    print(f"\n  [{label}] — {t} tokens")
    print(f"  {'─' * 60}")
    for line in text.strip().split('\n'):
        print(f"  {line}")

print("\n\n" + "=" * 70)
print("TOKEN COMPARISON")
print("=" * 70)
v, t, g, s = tok(verbose), tok(terse), tok(glyph), tok(structured)
print(f"  Verbose English:  {v:4d} tokens  (baseline)")
print(f"  Terse English:    {t:4d} tokens  ({(1-t/v)*100:+.0f}%)")
print(f"  Glyph Protocol:   {g:4d} tokens  ({(1-g/v)*100:+.0f}%)")
print(f"  JSON Structured:  {s:4d} tokens  ({(1-s/v)*100:+.0f}%)")

print("\n\n" + "=" * 70)
print("THE ACTUAL QUESTION")
print("=" * 70)
print("""
  Token savings: Terse English wins. Glyphs don't compress better.
  
  But that's NOT what this is about.
  
  The question is: which format lets Sonnet EXECUTE with least 
  cognitive overhead? Which one reduces Sonnet's need to RE-REASON?
  
  PARSE DIFFICULTY (what Sonnet has to do):
  ─────────────────────────────────────────
  Verbose English:  Parse NL → extract steps → infer order → execute
                    Risk: Sonnet re-interprets, adds its own reasoning
  
  Terse English:    Parse compressed NL → less context → still ambiguous
                    Risk: "Fix same pattern" — how literally does Sonnet take this?
  
  Glyph Protocol:   Visual scan → each symbol = one operation → execute
                    Risk: Does Sonnet actually know the protocol?
  
  JSON Structured:  Parse schema → execute steps array → deterministic
                    Risk: Verbose, rigid, but ALREADY WORKS (function calling)
  
  THE REAL INSIGHT:
  ─────────────────
  You're not building a compression format. 
  You're building a PROGRAMMING LANGUAGE for model orchestration.
  
  The glyphs aren't tokens to save — they're OPCODES.
  
  修 = FIX (verb/action)
  因 = BECAUSE (causal link)  
  → = THEN (sequence)
  ∈ = IN (scope)
  不 = NOT (negation/constraint)
  找 = FIND (search)
  同 = SAME (pattern match)
  
  That's 7 opcodes. A model that knows these 7 symbols can execute
  ANY plan Opus writes. The savings aren't in tokens — they're in
  REMOVING AMBIGUITY from the handoff.
  
  English: "fix the same pattern in other tests too"
  Glyph:   "找 同 pattern ∈ webhook tests → 修"
  
  The English version Sonnet might interpret as:
    - "look for similar code" (too vague)
    - "fix only exact matches" (too literal)
    - "refactor all webhook tests" (too broad)
  
  The glyph version says:
    FIND(SAME pattern, IN webhook_tests) → FIX
  
  It's function calling with CJK verbs instead of JSON keys.
  And the CJK verbs are self-documenting — 找 MEANS find.
""")

print("=" * 70)
print("VERDICT")
print("=" * 70)
print("""
  WHAT'S REAL:
  ✓ Opus→Sonnet handoff IS a real use case
  ✓ Structured plans DO reduce Sonnet re-reasoning
  ✓ CJK verbs ARE self-documenting (no lookup table)
  ✓ ~50% token savings vs verbose English (real, but from terseness)
  ✓ Reduced ambiguity (real, but hard to quantify)
  
  WHAT'S NOT:
  ✗ Glyphs don't compress better than terse English
  ✗ METACOG's fancy Unicode symbols are 3-tok traps
  ✗ "Shape-meaning resonance" doesn't affect execution
  
  WHAT THIS ACTUALLY IS:
  → A lightweight DSL for model-to-model task delegation
  → Using CJK characters as self-documenting opcodes
  → Competitors: JSON function calls, YAML plans, terse English
  → Advantage over JSON: ~40% fewer tokens, more readable
  → Advantage over English: less ambiguity, more structured
  → Disadvantage: requires both models to know the protocol
""")
