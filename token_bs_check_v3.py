"""
REAL BS CHECK: Opus reasoning -> Sonnet execution
The question: Can glyphs compress REASONING OUTPUT, not just instructions?

Scenario: Opus analyzes a complex task, produces a plan.
Sonnet receives that plan and executes it.

Compare: English plan vs Glyph plan as Opus->Sonnet handoff.
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def tok(text):
    return len(enc.encode(text))

print("=" * 70)
print("SCENARIO: Opus reasons about a task, hands off to Sonnet")
print("=" * 70)

# ─────────────────────────────────────────────
# CASE 1: "Refactor this module"
# ─────────────────────────────────────────────
english_plan_1 = """TASK: Refactor the authentication module.

STEP 1: Read auth.py and identify all public functions.
STEP 2: Extract the token validation logic into a separate validate_token() function.
STEP 3: The rate limiting code is duplicated in login() and refresh() — extract to a decorator.
STEP 4: The error handling is inconsistent. Standardize: all auth errors should raise AuthError with a code.
STEP 5: Add type hints to all public functions.
STEP 6: Do NOT change the function signatures — other modules depend on them.
STEP 7: Run the existing tests to verify nothing broke.

CONSTRAINTS:
- Preserve all existing behavior
- Keep backward compatibility
- No new dependencies"""

glyph_plan_1 = """【auth.py】→ 分
取【token検】→ 新λ validate_token
取【rate制】∈ login,refresh → 新 decorator
統【error】→ 全 AuthError(code)
加 type hints → 全 public λ
不化 signatures
動 tests ∧ 不失"""

print("\nCASE 1: Refactor authentication module")
print(f"  English plan: {tok(english_plan_1):4d} tokens")
print(f"  Glyph plan:   {tok(glyph_plan_1):4d} tokens")
print(f"  Savings:      {tok(english_plan_1) - tok(glyph_plan_1):4d} tokens ({(1 - tok(glyph_plan_1)/tok(english_plan_1))*100:.0f}%)")

# ─────────────────────────────────────────────
# CASE 2: "Debug this failing test"
# ─────────────────────────────────────────────
english_plan_2 = """TASK: Debug why test_payment_webhook is failing.

ANALYSIS: The test expects a 200 response but gets 422.
The webhook handler validates the signature first, then parses the payload.
The test is sending a valid payload but the signature check is failing.

ROOT CAUSE: The test is computing HMAC with the raw body bytes, but the handler 
is computing HMAC with the JSON-serialized body (which may reorder keys).

FIX PLAN:
STEP 1: In test_payment_webhook, change the signature computation to use the exact 
        raw bytes that will be sent in the request body, not json.dumps(payload).
STEP 2: Specifically, compute the body first: body = json.dumps(payload, separators=(',', ':'))
STEP 3: Then compute signature from that exact body string.
STEP 4: Send body as the request data (not payload dict).
STEP 5: Verify the test passes.
STEP 6: Check if any other webhook tests have the same pattern — fix those too."""

glyph_plan_2 = """【test_payment_webhook】失 → 422 不 200
因: HMAC(raw bytes) ≠ HMAC(json.dumps) — key order
修:
body = json.dumps(payload, separators=(',',':'))
sig = HMAC(body)
送 body 不 payload dict
動 test → 確
找 同 pattern ∈ 他 webhook tests → 修"""

print("\nCASE 2: Debug failing webhook test")
print(f"  English plan: {tok(english_plan_2):4d} tokens")
print(f"  Glyph plan:   {tok(glyph_plan_2):4d} tokens")
print(f"  Savings:      {tok(english_plan_2) - tok(glyph_plan_2):4d} tokens ({(1 - tok(glyph_plan_2)/tok(english_plan_2))*100:.0f}%)")

# ─────────────────────────────────────────────
# CASE 3: "Implement a feature"
# ─────────────────────────────────────────────
english_plan_3 = """TASK: Add pagination to the /api/users endpoint.

CURRENT STATE: Returns all users in one response. Works fine with 50 users, 
will collapse at 10,000.

IMPLEMENTATION PLAN:
STEP 1: Add query parameters: page (default 1), per_page (default 20, max 100).
STEP 2: Modify the database query to use LIMIT and OFFSET.
STEP 3: Add response metadata: total_count, page, per_page, total_pages.
STEP 4: Add Link headers for next/prev/first/last pages (RFC 5988).
STEP 5: Update the OpenAPI spec with the new parameters and response shape.
STEP 6: Add tests for: first page, middle page, last page, out of range, 
        per_page > max, per_page = 0.
STEP 7: Update the frontend UserList component to use pagination — it currently 
        calls fetchAll(). Change to fetchPage(page, perPage).

CONSTRAINTS:
- Don't break the existing response format — wrap in { data: [...], meta: {...} }
- The frontend must keep working during migration (support both formats temporarily)
- Add a deprecation warning header when the old format is used"""

glyph_plan_3 = """【/api/users】加 pagination

加 params: page=1, per_page=20 (max 100)
DB: 加 LIMIT per_page OFFSET (page-1)*per_page
応 meta: {total_count, page, per_page, total_pages}
加 Link headers (RFC 5988): next/prev/first/last
更新 OpenAPI spec
加 tests: first/mid/last/overflow/max/zero
更新 frontend: fetchAll → fetchPage(page, perPage)

制:
応 → {data:[...], meta:{...}} — 不破 old format
両 format 同時 (migration)
加 deprecation header → old format"""

print("\nCASE 3: Add pagination feature")
print(f"  English plan: {tok(english_plan_3):4d} tokens")
print(f"  Glyph plan:   {tok(glyph_plan_3):4d} tokens")
print(f"  Savings:      {tok(english_plan_3) - tok(glyph_plan_3):4d} tokens ({(1 - tok(glyph_plan_3)/tok(english_plan_3))*100:.0f}%)")

# ─────────────────────────────────────────────
# CASE 4: Multi-step pipeline with branching
# ─────────────────────────────────────────────
english_plan_4 = """TASK: Process the uploaded CSV, validate it, transform it, and load into the database.

PIPELINE:
STEP 1: Parse the CSV. If parsing fails, return error with line number.
STEP 2: Validate each row:
  - email must be valid format
  - age must be integer 0-150
  - name must be non-empty, max 200 chars
  - If any row fails, collect all errors (don't stop at first).
STEP 3: If more than 10% of rows have errors, reject the entire upload.
        Return all errors grouped by type.
STEP 4: For valid rows, normalize:
  - emails to lowercase
  - names trimmed, title-cased
  - missing optional fields get defaults
STEP 5: Deduplicate by email. If duplicate emails exist, keep the row with more 
        filled fields.
STEP 6: Batch insert into database (chunks of 500).
STEP 7: Return summary: inserted count, skipped duplicates, rejected rows with reasons."""

glyph_plan_4 = """CSV → parse (失 → error + line#)
行 検:
  email format ∧ age int 0-150 ∧ name 不空 ≤200
  集 全 errors (不止 first)
if errors > 10% → 拒 全 upload + errors by type
正規化 valid:
  email → lower, name → trim+title, 空 optional → default
重複 email → 取 more fields
batch insert 500
応: {inserted, skipped, rejected+reasons}"""

print("\nCASE 4: CSV upload pipeline")
print(f"  English plan: {tok(english_plan_4):4d} tokens")
print(f"  Glyph plan:   {tok(glyph_plan_4):4d} tokens")
print(f"  Savings:      {tok(english_plan_4) - tok(glyph_plan_4):4d} tokens ({(1 - tok(glyph_plan_4)/tok(english_plan_4))*100:.0f}%)")

# ─────────────────────────────────────────────
# CASE 5: Architecture decision
# ─────────────────────────────────────────────
english_plan_5 = """TASK: Migrate the session storage from Redis to PostgreSQL.

REASONING: Redis keeps dying under memory pressure. Sessions are not hot enough 
to justify in-memory storage. PostgreSQL can handle our session load (500 req/s) 
easily with proper indexing.

MIGRATION PLAN:
STEP 1: Create sessions table: id (UUID), user_id (FK), data (JSONB), 
        created_at, expires_at, last_accessed_at.
STEP 2: Add index on expires_at for cleanup job. Add index on user_id for lookups.
STEP 3: Implement SessionStore interface with PostgreSQL backend.
        Methods: create, get, update, delete, cleanup_expired.
STEP 4: Write migration script that copies active sessions from Redis to PostgreSQL.
STEP 5: Deploy with feature flag: SESSION_STORE=postgres (default remains redis).
STEP 6: Monitor for 48 hours. Check: p99 latency < 50ms, no session loss.
STEP 7: If OK, flip default to postgres. Keep redis code for 2 weeks, then remove.
STEP 8: Add cron job: cleanup_expired every 15 minutes."""

glyph_plan_5 = """Redis → PostgreSQL sessions
因: memory pressure, sessions 不 hot

新 table sessions: id UUID, user_id FK, data JSONB, created_at, expires_at, last_accessed_at
index: expires_at (cleanup), user_id (lookup)
実装 SessionStore: create/get/update/delete/cleanup_expired
migration script: Redis active → PG
deploy flag SESSION_STORE=postgres (default=redis)
監視 48h: p99 < 50ms ∧ 不 session loss
OK → default=postgres, 保 redis 2w → 削
cron: cleanup_expired 15min"""

print("\nCASE 5: Architecture migration")
print(f"  English plan: {tok(english_plan_5):4d} tokens")
print(f"  Glyph plan:   {tok(glyph_plan_5):4d} tokens")
print(f"  Savings:      {tok(english_plan_5) - tok(glyph_plan_5):4d} tokens ({(1 - tok(glyph_plan_5)/tok(english_plan_5))*100:.0f}%)")

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY: Opus → Sonnet handoff compression")
print("=" * 70)

cases = [
    ("Refactor module", english_plan_1, glyph_plan_1),
    ("Debug webhook", english_plan_2, glyph_plan_2),
    ("Add pagination", english_plan_3, glyph_plan_3),
    ("CSV pipeline", english_plan_4, glyph_plan_4),
    ("Redis migration", english_plan_5, glyph_plan_5),
]

total_en = total_gl = 0
print(f"\n  {'Case':<20} {'English':>8} {'Glyph':>8} {'Saved':>8} {'%':>6}")
print("  " + "-" * 54)
for name, en, gl in cases:
    e, g = tok(en), tok(gl)
    total_en += e
    total_gl += g
    print(f"  {name:<20} {e:>8} {g:>8} {e-g:>8} {(1-g/e)*100:>5.0f}%")
print("  " + "-" * 54)
print(f"  {'TOTAL':<20} {total_en:>8} {total_gl:>8} {total_en-total_gl:>8} {(1-total_gl/total_en)*100:>5.0f}%")

# Cost estimate
print("\n  COST IMPACT (at Sonnet pricing):")
opus_input = 15.00  # per 1M tokens
sonnet_input = 3.00  # per 1M tokens
en_cost = total_en * sonnet_input / 1_000_000
gl_cost = total_gl * sonnet_input / 1_000_000
print(f"  These 5 handoffs with English:  ~{total_en} input tokens to Sonnet")
print(f"  These 5 handoffs with Glyphs:   ~{total_gl} input tokens to Sonnet")
print(f"  Savings per handoff:            ~{(total_en-total_gl)//5} tokens")
print(f"  At 1000 handoffs/day:           ~{1000 * (total_en-total_gl)//5:,} tokens/day saved")
print(f"  At Sonnet $3/1M input:          ~${1000 * (total_en-total_gl)//5 * 3 / 1_000_000:.2f}/day")

# What fraction is "glyph" vs just "terse English/Japanese mix"
print("\n\n  HONESTY CHECK: How much of the savings is glyphs vs just being terse?")
print("  " + "=" * 60)

terse_plan_1 = """Read auth.py, find public fns.
Extract token validation -> validate_token().
Extract rate limiting from login/refresh -> decorator.
Standardize errors -> AuthError(code).
Add type hints to public fns.
Don't change signatures.
Run tests."""

print(f"\n  Case 1 (Refactor):")
print(f"    Verbose English: {tok(english_plan_1):4d} tokens")
print(f"    Terse English:   {tok(terse_plan_1):4d} tokens")
print(f"    Glyph mix:       {tok(glyph_plan_1):4d} tokens")
print(f"    Terse vs Verbose savings: {(1-tok(terse_plan_1)/tok(english_plan_1))*100:.0f}%")
print(f"    Glyph vs Terse savings:   {(1-tok(glyph_plan_1)/tok(terse_plan_1))*100:.0f}%")
print(f"    -> Most savings from BEING TERSE, not from glyphs specifically")
