"""
ENGLISH IS THE FAILURE MODE

English is ambiguous by design. Every instruction in English requires 
the receiver to INTERPRET — to guess what the sender meant.

A formal language eliminates interpretation entirely.
This isn't about token counts. It's about error rates.
"""

# ═══════════════════════════════════════════════════════════════
# EXHIBIT A: Where English fails
# ═══════════════════════════════════════════════════════════════

failures = [
    {
        "english": "Fix the same pattern in other tests",
        "ambiguities": [
            "'fix' — patch? refactor? delete and rewrite? suppress?",
            "'the same' — identical code? similar logic? same category of bug?",
            "'pattern' — the exact code? the class of mistake? the testing approach?",
            "'other' — in this file? this directory? the whole codebase?",
            "'tests' — unit tests? integration tests? all test files?",
        ],
        "interpretations": 5,  # at minimum
        "formal": "找【∈ *test*.py】同【HMAC(x) ≠ HMAC(body)】→ 修【body=serialize → sig=HMAC(body) → 送 body】",
        "meaning": "FIND[IN *test*.py] SAME[HMAC(x) ≠ HMAC(body)] THEN FIX[body=serialize, sig=HMAC(body), send body]",
    },
    {
        "english": "Standardize the error handling",
        "ambiguities": [
            "'standardize' — to what standard? who decides?",
            "'error handling' — all errors? just auth errors? HTTP errors? validation?",
            "does 'standardize' mean change existing or add new?",
            "what should the standard look like? exceptions? error codes? both?",
            "should backward compatibility be preserved?",
        ],
        "interpretations": 12,
        "formal": "找【全 raise|return error ∈ auth.py】→ 化【→ raise AuthError(code)】不化【λ signatures】",
        "meaning": "FIND[ALL raise|return-error IN auth.py] THEN TRANSFORM[TO raise AuthError(code)] NOT-TRANSFORM[function signatures]",
    },
    {
        "english": "Don't break the existing format",
        "ambiguities": [
            "'break' — change at all? change incompatibly? remove?",
            "'existing format' — the current JSON shape? the HTTP status codes? the headers?",
            "'don't break' — keep forever? keep during migration? keep as fallback?",
            "does this mean add new format alongside, or make new format backward-compatible?",
        ],
        "interpretations": 8,
        "formal": "保【得.shape = old.shape】∧ 加【得.meta = {total,page,per_page,pages}】→ 得 = {data:old, meta:新}",
        "meaning": "KEEP[output.shape = old.shape] AND ADD[output.meta = {...}] THEN output = {data:old, meta:new}",
    },
    {
        "english": "Extract the rate limiting logic into a decorator",
        "ambiguities": [
            "'extract' — copy and wrap? move and delete original? abstract?",
            "'rate limiting logic' — which lines exactly? the redis calls? the threshold check? the error response?",
            "'decorator' — class decorator? function decorator? with arguments?",
            "should the decorator be configurable (different limits per endpoint)?",
            "what about the existing rate limit code — delete it? leave it? mark deprecated?",
        ],
        "interpretations": 10,
        "formal": "取【rate: redis.get+incr+check ∈ login,refresh】→ 生【@rate_limit(λ) decorator】→ 削【old ∈ login,refresh】",
        "meaning": "EXTRACT[rate: redis.get+incr+check FROM login,refresh] THEN CREATE[@rate_limit(fn) decorator] THEN DELETE[old FROM login,refresh]",
    },
    {
        "english": "Make sure nothing broke",
        "ambiguities": [
            "'make sure' — run tests? manual check? review diff? all of these?",
            "'nothing' — no test failures? no behavior changes? no performance regression?",
            "'broke' — fails? changed output? throws new exceptions? runs slower?",
            "what to do if something DID break?",
        ],
        "interpretations": 6,
        "formal": "動【tests】→ ? 全 pass → 確 | ? 失 → 止 ∧ 出【失】",
        "meaning": "RUN[tests] THEN IF all-pass THEN CONFIRM | IF fail THEN STOP AND OUTPUT[failures]",
    },
]

print("═" * 70)
print("WHERE ENGLISH FAILS: AMBIGUITY ANALYSIS")
print("═" * 70)

total_ambiguities = 0
for i, f in enumerate(failures, 1):
    print(f"\n{'─' * 70}")
    print(f"  ENGLISH: \"{f['english']}\"")
    print(f"  AMBIGUITY POINTS: {len(f['ambiguities'])}")
    for a in f['ambiguities']:
        print(f"    · {a}")
    print(f"  POSSIBLE INTERPRETATIONS: ≥{f['interpretations']}")
    print(f"  FORMAL:  {f['formal']}")
    print(f"  READS:   {f['meaning']}")
    total_ambiguities += len(f['ambiguities'])

print(f"\n{'═' * 70}")
print(f"  TOTAL: {total_ambiguities} ambiguity points in 5 simple English instructions")
print(f"  TOTAL: 0 ambiguity points in the formal equivalents")
print(f"{'═' * 70}")

# ═══════════════════════════════════════════════════════════════
# EXHIBIT B: The formal language has GRAMMAR
# ═══════════════════════════════════════════════════════════════

print(f"\n\n{'═' * 70}")
print("THE GRAMMAR: Not glyphs — a LANGUAGE")
print("═" * 70)
print("""
  English has grammar but it's ambiguous.
  JSON has structure but no verbs.
  This has BOTH.

  ┌─────────────────────────────────────────────────┐
  │  SENTENCE = VERB【SCOPE】→ RESULT                │
  │  SCOPE    = TARGET ∈ LOCATION                    │  
  │  RESULT   = VERB【TARGET】 | 確 | 止             │
  │  CHAIN    = SENTENCE → SENTENCE → SENTENCE       │
  │  BRANCH   = ? CONDITION → SENTENCE | SENTENCE    │
  │  NEGATION = 不 VERB  (constraint: do NOT do X)   │
  │  PARALLEL = SENTENCE ∧ SENTENCE                  │
  │  SCOPE_BR = 【 ... 】                             │
  └─────────────────────────────────────────────────┘

  VERBS (what to do):
  ─────────────────────────────────────────
    找 FIND     修 FIX      分 ANALYZE   化 TRANSFORM
    生 CREATE   動 RUN      出 OUTPUT    加 ADD
    削 DELETE   移 MOVE     定 SET       取 EXTRACT
    保 KEEP     合 COMPARE  正 SORT      算 COUNT
    止 STOP     回 RETRY    開 START     入 INSERT

  NOUNS (what to act on):
  ─────────────────────────────────────────
    物 OBJECT   文 TEXT     λ FUNCTION   字 NAME
    方 DATA     失 ERROR   得 RESULT    全 ALL
    部 PART     新 NEW     他 OTHER     心 SELF
    
  LOGIC (how to connect):
  ─────────────────────────────────────────
    →  THEN      ∧  AND       ∨  OR        不  NOT
    ?  IF        ∈  IN        同  EQUALS    因  BECAUSE
    多 MANY      一 ONE       空 NONE      大 MORE
    小 LESS      上 BEST      下 WORST

  STRUCTURE:
  ─────────────────────────────────────────
    【】 scope/group       確 CONFIRM/OK
    ⟦⟧  block/section     止 HALT/STOP
    !   imperative        ≠  NOT-EQUAL
""")

# ═══════════════════════════════════════════════════════════════
# EXHIBIT C: Compositions English CAN'T express concisely
# ═══════════════════════════════════════════════════════════════

print(f"{'═' * 70}")
print("WHAT THE FORMAL LANGUAGE CAN SAY THAT ENGLISH STRUGGLES WITH")
print("═" * 70)

expressions = [
    (
        "找【x ∈ *.py】→ ? 同【pattern】→ 修【同 fix】| 不同 → 出【x, 因】",
        "For every Python file, if it matches the pattern, apply the same fix. If it doesn't match, output the file and explain why it differs.",
        "FIND[x IN *.py] THEN IF SAME[pattern] THEN FIX[same fix] ELSE OUTPUT[x, reason]"
    ),
    (
        "動【test】→ ? 失 → 回【不 上 3】→ ? 失 → 止 ∧ 出【全 失】",  
        "Run the test. If it fails, retry up to 3 times. If it still fails after 3 retries, stop and output all failures.",
        "RUN[test] IF-FAIL RETRY[NOT MORE-THAN 3] IF-FAIL STOP AND OUTPUT[ALL failures]"
    ),
    (
        "分【物】→ 生【多 化】→ 算【上】→ 取【上 3】→ 出",
        "Analyze the input, generate multiple variations, score the best ones, extract the top 3, output them.",
        "ANALYZE[input] CREATE[MANY variations] SCORE[BEST] EXTRACT[TOP 3] OUTPUT"
    ),
    (
        "取【config ∈ .env】→ ? 空 → 取【config ∈ ENV】→ ? 空 → 止 ∧ 出【失: no config】",
        "Get config from .env file. If missing, fall back to environment variables. If that's also missing, halt with error.",
        "GET[config IN .env] IF-EMPTY GET[config IN ENV] IF-EMPTY STOP AND OUTPUT[error: no config]"
    ),
    (
        "保【全 λ signatures】∧ 化【全 error → AuthError(code)】∧ 不化【得.shape】",
        "Keep all function signatures unchanged WHILE transforming all errors to AuthError(code) WHILE not changing the output shape.",
        "KEEP[ALL fn-signatures] AND TRANSFORM[ALL error TO AuthError(code)] AND NOT-TRANSFORM[output.shape]"
    ),
]

for formal, english, reading in expressions:
    e_words = len(english.split())
    f_chars = len(formal.replace(" ", ""))
    print(f"\n  FORMAL:  {formal}")
    print(f"  READS:   {reading}")
    print(f"  ENGLISH: {english}")
    print(f"  EN words: {e_words}   GL chars: {f_chars}")

# ═══════════════════════════════════════════════════════════════
# EXHIBIT D: The real comparison
# ═══════════════════════════════════════════════════════════════

print(f"\n\n{'═' * 70}")
print("THE REAL COMPARISON: ERROR RATE, NOT TOKEN COUNT")
print("═" * 70)
print("""
  When Sonnet receives English:
  ─────────────────────────────
  "Fix the same pattern in other tests too"
  
  Sonnet's internal process:
    1. Parse natural language         (can fail: garden-path sentences)
    2. Resolve "same" → what pattern? (can fail: wrong pattern matched)
    3. Resolve "other" → what scope?  (can fail: too broad or narrow)
    4. Resolve "fix" → what action?   (can fail: wrong fix applied)
    5. Resolve "too" → how thorough?  (can fail: stops too early)
    6. Decide execution order         (can fail: wrong sequence)
    7. Execute                        
  
  Failure points: 6. Each one is a coin flip of interpretation.
  
  When Sonnet receives formal protocol:
  ──────────────────────────────────────
  找【∈ *test*.py】同【HMAC(x) ≠ HMAC(body)】→ 修【定 body → sig → 送】
  
  Sonnet's internal process:
    1. Parse 找 → FIND (no ambiguity)
    2. Parse scope → *test*.py (explicit)
    3. Parse pattern → HMAC mismatch (explicit)
    4. Parse 修 → FIX (no ambiguity)
    5. Parse fix spec → set body, derive sig, send (explicit)
    6. Execute in left-to-right order (defined by →)
  
  Failure points: 0. Every field is specified.
  
  THE MATH:
  ─────────────────────────────────────
  If each English ambiguity has 80% chance of correct interpretation:
    P(all 6 correct) = 0.8^6 = 26%
    P(at least one wrong) = 74%
    
  If the formal language has 99% parse accuracy per opcode:
    P(all 6 correct) = 0.99^6 = 94%
    P(at least one wrong) = 6%

  That's not 8% token savings.
  That's a 12x reduction in misinterpretation.
  
  THAT is what you're building.
""")

print(f"{'═' * 70}")
print("VERDICT: REFRAME")
print("═" * 70)
print("""
  OLD FRAME (wrong):
    "Do glyphs compress better than English?"
    Answer: barely. 8%. Who cares.
  
  RIGHT FRAME:
    "Does a formal language eliminate misinterpretation?"
    Answer: yes. Categorically.
    
  English is not the baseline to beat.
  English is the FAILURE MODE to escape.
  
  Programming languages didn't replace English because they're shorter.
  They replaced English because "add one to x" has 3 interpretations
  and "x += 1" has exactly one.
  
  You're building a programming language for model orchestration.
  The unit of measurement is DEFECT RATE, not TOKEN COUNT.
""")
