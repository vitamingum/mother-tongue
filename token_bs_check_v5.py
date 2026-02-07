"""
CORRECT COMPARISON: Opus's actual reasoning output → Sonnet

The question isn't "glyphs vs terse English" (a human wrote that terse English).
The question is: what does Opus ACTUALLY emit when reasoning, and how much 
can the glyph protocol compress that handoff?
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def tok(text):
    return len(enc.encode(text))

print("=" * 70)
print("WHAT OPUS ACTUALLY PRODUCES vs GLYPH PROTOCOL")
print("=" * 70)

# ─────────────────────────────────────────────
# This is what Opus's reasoning looks like in practice.
# Not terse bullets — actual model reasoning output.
# ─────────────────────────────────────────────

opus_reasoning_1 = """Looking at this problem, I need to fix test_payment_webhook which is returning a 422 instead of the expected 200.

Let me trace through the code. The webhook handler in webhook.py first validates the signature by computing HMAC-SHA256 over the raw request body, then compares it to the X-Webhook-Signature header. The test is constructing a payload dict, computing HMAC over json.dumps(payload), and sending the payload as JSON.

The issue is subtle: json.dumps() doesn't guarantee key ordering in all Python versions, and even when it does (Python 3.7+), the handler receives the raw bytes from the HTTP request, which were serialized by the test's HTTP client — which may use different serialization settings (spacing, separators) than the test's json.dumps call.

So the fix is:
1. In the test, serialize the body ONCE: body = json.dumps(payload, separators=(',', ':'))
2. Compute the HMAC from that exact body string
3. Send that body string as the request data (not the dict, which would be re-serialized by the HTTP client)
4. This ensures the bytes used for signature computation match the bytes the handler receives

After fixing this test, I should search for other webhook tests that might have the same pattern — computing HMAC separately from the request body construction."""

# What Opus would compress this to in glyph protocol
glyph_handoff_1 = """修 test_payment_webhook (422 不 200)
因: HMAC(json.dumps) ≠ HMAC(raw body) — serialization
修:
  定 body = json.dumps(payload, separators=(',',':'))
  定 sig = HMAC(body)
  出 body 不 dict
動 test
找 同 pattern ∈ 他 webhook tests → 修"""

# What you'd write in English if you were being concise (but still English)
english_handoff_1 = """Fix test_payment_webhook (getting 422 not 200).
Root cause: test computes HMAC over json.dumps(payload) but handler computes over raw body bytes. Different serialization = different bytes.
Fix: body = json.dumps(payload, separators=(',',':')), sig = HMAC(body), send body string not dict.
Run test to verify.
Search other webhook tests for same HMAC pattern, fix those too."""

o = tok(opus_reasoning_1)
g = tok(glyph_handoff_1) 
e = tok(english_handoff_1)
print(f"\nCASE: Debug webhook test")
print(f"  Opus reasoning:    {o:4d} tokens  (what the model actually produces)")
print(f"  English handoff:   {e:4d} tokens  (human-compressed)")
print(f"  Glyph handoff:     {g:4d} tokens  (protocol)")
print(f"")
print(f"  Glyph vs Opus:     {(1-g/o)*100:.0f}% reduction  ({o-g} tokens saved)")
print(f"  English vs Opus:   {(1-e/o)*100:.0f}% reduction  ({o-e} tokens saved)")
print(f"  Glyph vs English:  {(1-g/e)*100:.0f}% reduction  ({e-g} tokens saved)")

# ─────────────────────────────────────────────
# Case 2: Architecture decision
# ─────────────────────────────────────────────
opus_reasoning_2 = """The user wants to add pagination to the /api/users endpoint. Currently it returns all users in one response, which works fine with their current 50 users but will become a serious performance problem as they scale.

I need to think about what a proper pagination implementation looks like:

First, the API needs query parameters. Standard REST pagination uses `page` and `per_page` (or `limit` and `offset`). I'll go with page/per_page since it's more intuitive. Default page should be 1, default per_page should be 20, and I should cap per_page at 100 to prevent abuse.

For the database query, I need to convert page/per_page into SQL LIMIT and OFFSET. OFFSET = (page - 1) * per_page. I also need a COUNT query to get the total for metadata.

The response format needs to change. Instead of just returning an array, I need to wrap it: { data: [...], meta: { total_count, page, per_page, total_pages } }. But I can't break the existing format — the frontend expects a bare array. So I need to support both formats during migration, maybe with an Accept header or API version parameter.

I should also add Link headers per RFC 5988 for next/prev/first/last pages. This is standard practice and helps automated clients.

For the frontend, the UserList component currently calls fetchAll() which returns all users. I need to change it to fetchPage(page, perPage) and add pagination controls to the UI.

Testing needs to cover: first page, middle page, last page, page beyond range (should return empty data not error), per_page exceeding max (should clamp to 100), per_page of 0 (should error).

One thing to be careful about: adding a deprecation warning when clients use the old array format. This gives them time to migrate before I remove it."""

glyph_handoff_2 = """加 pagination →【/api/users】
加 params: page=1, per_page=20 (max 100)
DB: LIMIT per_page OFFSET (page-1)*per_page + COUNT
得 → {data:[...], meta:{total, page, per_page, pages}}
不破 old format — 両 format 同時
加 Link headers RFC5988: next/prev/first/last
修 frontend: fetchAll → fetchPage(page, perPage)
加 tests: first/mid/last/overflow/clamp/zero
加 deprecation header → old format"""

english_handoff_2 = """Add pagination to /api/users.
Params: page (default 1), per_page (default 20, max 100).
DB: LIMIT/OFFSET with COUNT for total.
Response: { data: [...], meta: { total_count, page, per_page, total_pages } }.
Don't break existing array format — support both during migration.
Add Link headers (RFC 5988) for next/prev/first/last.
Update frontend UserList: fetchAll() → fetchPage(page, perPage).
Tests: first page, middle, last, beyond range, per_page > max, per_page = 0.
Add deprecation warning header when old format used."""

o = tok(opus_reasoning_2)
g = tok(glyph_handoff_2)
e = tok(english_handoff_2)
print(f"\nCASE: Add pagination")
print(f"  Opus reasoning:    {o:4d} tokens")
print(f"  English handoff:   {e:4d} tokens")
print(f"  Glyph handoff:     {g:4d} tokens")
print(f"")
print(f"  Glyph vs Opus:     {(1-g/o)*100:.0f}% reduction  ({o-g} tokens saved)")
print(f"  English vs Opus:   {(1-e/o)*100:.0f}% reduction  ({o-e} tokens saved)")
print(f"  Glyph vs English:  {(1-g/e)*100:.0f}% reduction  ({e-g} tokens saved)")

# ─────────────────────────────────────────────
# Case 3: Complex multi-step refactoring
# ─────────────────────────────────────────────
opus_reasoning_3 = """I need to refactor the authentication module. Let me look at what needs to change.

The main issues I see in auth.py:
1. Token validation logic is embedded directly in the login() function. It's about 30 lines of JWT decode, expiry check, issuer validation, and scope verification. This should be its own function since it's also needed in the middleware and in the refresh endpoint.

2. Rate limiting is duplicated. Both login() and refresh() have nearly identical rate limiting code — they check Redis for the number of attempts, increment, and raise if over limit. This is a textbook case for a decorator.

3. Error handling is a mess. login() returns {"error": "bad password"}, refresh() raises HTTPException(403), and validate_session() returns None on failure. We need to standardize: every auth failure should raise AuthError with a specific error code.

4. No type hints anywhere. The functions take and return dicts with no documentation of their shape.

The key constraint is that I cannot change the function signatures. Other modules import and call login(username, password), refresh(token), etc. If I change those signatures, I'll break the entire application.

My plan:
- First, read through auth.py and catalog all public functions
- Extract validate_token() as a standalone function
- Create a rate_limit decorator that wraps the Redis check logic
- Define AuthError with error codes and update all error paths
- Add type hints to all public functions
- Run the existing test suite to make sure nothing broke"""

glyph_handoff_3 = """分【auth.py】→ 找 全 public λ
取【token 検: decode+expiry+issuer+scope】→ 生 validate_token λ
取【rate limit ∈ login,refresh】→ 生 rate_limit decorator
定 全 auth error → AuthError(code)
  login: {"error":...} → AuthError
  refresh: HTTPException → AuthError
  validate_session: None → AuthError
加 type hints → 全 public λ
不化 λ signatures (他 modules 用)
動 tests"""

english_handoff_3 = """Read auth.py and identify all public functions.
Extract token validation (JWT decode, expiry, issuer, scope) into validate_token().
Extract rate limiting from login() and refresh() into a rate_limit decorator.
Standardize error handling: all auth failures raise AuthError(code).
  - login: {"error": ...} → AuthError
  - refresh: HTTPException → AuthError
  - validate_session: None → AuthError
Add type hints to all public functions.
Do NOT change function signatures — other modules depend on them.
Run existing tests to verify."""

o = tok(opus_reasoning_3)
g = tok(glyph_handoff_3)
e = tok(english_handoff_3)
print(f"\nCASE: Refactor auth module")
print(f"  Opus reasoning:    {o:4d} tokens")
print(f"  English handoff:   {e:4d} tokens")
print(f"  Glyph handoff:     {g:4d} tokens")
print(f"")
print(f"  Glyph vs Opus:     {(1-g/o)*100:.0f}% reduction  ({o-g} tokens saved)")
print(f"  English vs Opus:   {(1-e/o)*100:.0f}% reduction  ({o-e} tokens saved)")
print(f"  Glyph vs English:  {(1-g/e)*100:.0f}% reduction  ({e-g} tokens saved)")

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
print("\n\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

cases = [
    ("Debug webhook", opus_reasoning_1, english_handoff_1, glyph_handoff_1),
    ("Add pagination", opus_reasoning_2, english_handoff_2, glyph_handoff_2),
    ("Refactor auth", opus_reasoning_3, english_handoff_3, glyph_handoff_3),
]

print(f"\n  {'Case':<18} {'Opus':>6} {'English':>8} {'Glyph':>6} {'GL/Opus':>8} {'GL/EN':>7}")
print("  " + "-" * 55)
o_total = e_total = g_total = 0
for name, opus, eng, gly in cases:
    o, e, g = tok(opus), tok(eng), tok(gly)
    o_total += o; e_total += e; g_total += g
    print(f"  {name:<18} {o:>6} {e:>8} {g:>6} {g/o:>7.0%} {g/e:>6.0%}")
print("  " + "-" * 55)
print(f"  {'TOTAL':<18} {o_total:>6} {e_total:>8} {g_total:>6} {g_total/o_total:>7.0%} {g_total/e_total:>6.0%}")

print(f"""
  THE THREE-WAY SPLIT:
  ──────────────────────────────────────────────
  Opus reasoning → Sonnet:     {o_total} tokens  (100% — Sonnet re-reasons EVERYTHING)
  English handoff → Sonnet:    {e_total} tokens  ({e_total/o_total:.0%} — compressed, still NL)
  Glyph handoff → Sonnet:     {g_total} tokens  ({g_total/o_total:.0%} — structured opcodes)
  
  Savings: Opus→Glyph = {o_total - g_total} tokens across 3 cases ({(1-g_total/o_total)*100:.0f}%)
  Savings: Opus→English = {o_total - e_total} tokens across 3 cases ({(1-e_total/o_total)*100:.0f}%)
  Extra savings Glyph over English: {e_total - g_total} tokens ({(1-g_total/e_total)*100:.0f}%)
""")

print("  WHERE THE SAVINGS COME FROM:")
print("  " + "─" * 50)
opus_to_eng = o_total - e_total
eng_to_glyph = e_total - g_total
total_savings = o_total - g_total
print(f"  1. Removing Opus's reasoning/analysis:  {opus_to_eng:4d} tokens ({opus_to_eng/total_savings*100:.0f}% of savings)")
print(f"  2. Glyph compression over English:      {eng_to_glyph:4d} tokens ({eng_to_glyph/total_savings*100:.0f}% of savings)")
print(f"  ─────────────────────────────────────── ─────")
print(f"  Total:                                  {total_savings:4d} tokens")

print(f"""
  AT SCALE:
  ──────────────────────────────────────────────
  If Opus hands off 100 tasks/day to Sonnet:
    Without protocol:  ~{100 * o_total // 3:,} tokens/day to Sonnet
    With English:      ~{100 * e_total // 3:,} tokens/day to Sonnet  
    With glyphs:       ~{100 * g_total // 3:,} tokens/day to Sonnet
    
  Daily savings (glyph vs raw): ~{100 * (o_total - g_total) // 3:,} tokens
  At Sonnet $3/1M input: ${100 * (o_total - g_total) // 3 * 3 / 1_000_000:.3f}/day

  Monthly: ${100 * (o_total - g_total) // 3 * 3 / 1_000_000 * 30:.2f}/month for 100 tasks/day
  At 10,000 tasks/day: ${10000 * (o_total - g_total) // 3 * 3 / 1_000_000 * 30:.2f}/month
""")

print("  THE BOTTOM LINE:")
print("  " + "═" * 50)
print(f"""
  Token savings are real but modest (~{(1-g_total/o_total)*100:.0f}% vs Opus output).
  Most of that ({opus_to_eng/total_savings*100:.0f}%) comes from just NOT SENDING REASONING.
  The glyph layer adds {(1-g_total/e_total)*100:.0f}% beyond terse English.
  
  The REAL value isn't tokens. It's this:
  
  Opus reasoning (Sonnet has to RE-UNDERSTAND):
    "The issue is subtle: json.dumps() doesn't guarantee 
     key ordering... the handler receives the raw bytes..."
    → Sonnet reads this, re-derives the same conclusion, THEN acts
  
  Glyph plan (Sonnet just EXECUTES):
    修 test_payment_webhook
    因: HMAC(json.dumps) ≠ HMAC(raw body)
    定 body = json.dumps(payload, separators=(',',':'))
    → Every line is an instruction. No re-reasoning needed.
  
  The protocol's value = ZERO RE-REASONING by Sonnet.
  Opus thinks once. Sonnet executes. No duplicate cognition.
  
  That's not measurable in tokens.
  It's measurable in OUTPUT QUALITY and FEWER ERRORS.
""")
