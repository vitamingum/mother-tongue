# O-S Protocol: Model Automation Specification v0.2

## 1. Architecture

The **O-S Protocol** decouples **Reasoning** from **Execution**.

- **Opus (Architect)** — Decomposes problems. Emits formal programs.
- **Sonnet (Engine)** — Executes programs. Zero re-reasoning.

**Why not English:** `"Fix the same pattern in other tests"` has 5 ambiguity points and ≥5 valid interpretations. Sonnet must guess. `找【∈ *test*.py】同【pattern】→ 修` has zero. Every field is specified.

Programming languages didn't replace English because they're shorter. They replaced English because `x += 1` has one meaning and "add one to x" has three.

**Proven:** Sonnet already executes glyph-lang zero-shot — no decoder ring in system prompt. The import audit protocol ran successfully with 14 symbols.

---

## 2. Grammar

```
STATEMENT  = MODE VERB【SCOPE】→ RESULT
SCOPE      = TARGET ∈ LOCATION
RESULT     = MODE VERB【TARGET】 | 確 | 止
CHAIN      = STATEMENT → STATEMENT → STATEMENT
BRANCH     = ? ( CONDITION ) → STATEMENT | STATEMENT
LOOP       = ∀ VAR ∈ COLLECTION : BODY
NEGATION   = 不 VERB  (constraint: do NOT do X)
PARALLEL   = STATEMENT ∧ STATEMENT
ASSERTION  = ! ( INVARIANT )
```

**Execution:** left to right, following `→`.
**Branching:** `?` = IF, `|` = ELSE.
**Scope:** `【】` binds arguments to preceding verb.
**Mode:** `●` `○` `■` prefix tells Engine HOW to process.

---

## 3. Instruction Set

All token costs verified against `cl100k_base`. Palette: `found_glyphs.txt`.

### 3.1 Modal Prefixes (cognitive stance)

| Glyph | Tok | Mode | Engine behavior |
|:---:|:---:|:---|:---|
| **●** | 1 | **EXECUTE** | Rigid. Do exactly this. Code, file I/O, literal steps. |
| **○** | 2 | **LATENT** | Open. Reason freely. Explore, hypothesize, create. |
| **■** | 1 | **CONSTRAIN** | Validate. Check assertions, formats, invariants. |

### 3.2 Scope Delimiters (memory zones)

| Glyph | Tok | Zone | Usage |
|:---:|:---:|:---|:---|
| **⟦ ⟧** | 2+2 | **Context** | Protocol name, immutable rules, persona. Top of program. |
| **『 』** | 1+1 | **Raw Data** | File contents, user input, unprocessed strings. |
| **⟨ ⟩** | 2+1 | **Scratchpad** | Internal reasoning. NOT output to user. |
| **【 】** | 1+1 | **Scope/Target** | Verb arguments, output targets, grouping. |

### 3.3 Control Flow

| Glyph | Tok | Meaning | Usage |
|:---:|:---:|:---|:---|
| **→** | 1 | **THEN** | Sequence. Left-to-right pipeline. |
| **∀** | 2 | **FOR ALL** | Iterate over collection. `∀ f ∈ *.py :` |
| **?** | 1 | **IF** | Conditional branch. |
| **\|** | 1 | **ELSE** | Alternative branch after `?`. |
| **!** | 1 | **ASSERT** | Must be true. Error if false. |
| **∫** | 2 | **REDUCE** | Summarize, condense many → one. |

### 3.4 Verbs (actions)

| Glyph | Tok | Opcode | CJK meaning |
|:---:|:---:|:---|:---|
| **找** | 1 | FIND | to look for |
| **修** | 1 | FIX | to repair |
| **分** | 1 | ANALYZE | to divide / examine |
| **化** | 1 | TRANSFORM | to change |
| **生** | 1 | CREATE | to give birth / make |
| **動** | 1 | RUN | to move / execute |
| **出** | 1 | EMIT | to exit / output to stream |
| **寫** | 2 | WRITE | to inscribe / write to storage |
| **示** | 1 | SHOW | to display |
| **加** | 1 | ADD | to append / insert |
| **削** | 2 | DELETE | to cut away |
| **移** | 1 | MOVE | to relocate |
| **定** | 1 | SET | to fix / assign |
| **取** | 1 | EXTRACT | to take out |
| **保** | 1 | KEEP | to protect / preserve |
| **入** | 1 | INPUT | to enter / ingest |
| **合** | 1 | COMPARE | to match / merge |
| **正** | 1 | SORT | to order / normalize |
| **算** | 1 | COUNT | to calculate / score |
| **立** | 1 | INIT | to establish |
| **回** | 1 | RETRY | to return / repeat |
| **開** | 1 | START | to open / begin |
| **選** | 2 | SELECT | to choose / filter |
| **析** | 1 | PARSE | to break down |

### 3.5 Nouns (targets)

| Glyph | Tok | Meaning |
|:---:|:---:|:---|
| **物** | 1 | OBJECT — file, item, thing |
| **文** | 1 | TEXT — code, string, document |
| **λ** | 1 | FUNCTION — callable, method |
| **字** | 1 | NAME — identifier, variable |
| **方** | 1 | DATA — info, structure |
| **失** | 1 | ERROR — fault, failure |
| **得** | 1 | RESULT — return value, output |
| **全** | 1 | ALL — everything in scope |
| **部** | 1 | PART — subset, section |
| **新** | 1 | NEW — newly created |
| **他** | 1 | OTHER — remaining, different |
| **心** | 1 | SELF — this model, current context |
| **行** | 1 | ROW — line, record |
| **重** | 1 | DUPLICATE — repeated |

### 3.6 Logic & Relations

| Glyph | Tok | Meaning |
|:---:|:---:|:---|
| **∧** | 2 | AND |
| **∨** | 2 | OR |
| **不** | 1 | NOT — negation, constraint |
| **同** | 1 | SAME — equals, matching |
| **≠** | 2 | DIFFERENT — not equal |
| **因** | 1 | BECAUSE — causal link |
| **確** | 2 | OK — success, confirmed |
| **止** | 1 | HALT — stop, abort |
| **∈** | 2 | IN — membership, scope |
| **∉** | 2 | NOT IN — exclusion |
| **∩** | 2 | INTERSECT — and-filter |
| **∪** | 2 | UNION — or-combine |
| **¬** | 1 | NEGATE — logical not |

### 3.7 Quantifiers

| Glyph | Tok | Meaning |
|:---:|:---:|:---|
| **多** | 1 | MANY |
| **少** | 1 | FEW |
| **一** | 1 | ONE |
| **空** | 1 | NONE / empty |
| **大** | 1 | MORE / greater |
| **小** | 1 | LESS / smaller |
| **上** | 1 | BEST / top |
| **下** | 1 | WORST / bottom |

---

## 4. Examples

### 4.1 Import audit (proven — Sonnet executed then self-revised)

```
⟦ IMPORT_AUDIT ⟧

● 立【audit_report.txt】

∀ f ∈ *.py :
  ● 析【imports(f)】

  ? ( import X ∈ f ∧ 算【use(X)】== 0 )
    → ● 寫【audit_report.txt】: "UNUSED: " + X + " in " + f

  ? ( import X ∈ f ∧ X ∉ requirements.txt ∧ X ∉ stdlib )
    → ● 寫【audit_report.txt】: "MISSING_DEP: " + X + " in " + f

■ ( audit_report.txt ) :
  ! ( Format == "TYPE: Module in File" )
  → 確
```

**Revision notes:** Sonnet's self-critique after execution. `寫` (write-to-file) replaced `出` (emit-to-stream). `算` made the count operation an explicit opcode instead of English `count()`. `確` terminates the `■` validation block. `【】` consistently wraps all verb arguments.

### 4.2 Summarize a file

```
⟦ SUMMARY_TASK ⟧
● 入『data.txt』→ ○ 析 themes → ∫ → ● 寫【summary.md】
```

### 4.3 Code validation

```
⟦ PYTHON_STANDARDS ⟧
■ ∀ λ ∈『script.py』: !EdgeCases ∧ !PEP8
? 失 → ● 修
```

### 4.4 Refactor with constraints

```
⟦ REFACTOR_AUTH ⟧
● 分【auth.py】→ 找 全 public λ
● 取【token validation ∈ login】→ 生 validate_token λ
● 取【rate limit ∈ login·refresh】→ 生 @rate_limit λ → 削【old】
● 定 全 error → AuthError(code)
● 加 type hints → 全 public λ
不化 λ signatures
● 動 tests → ? 失 → 止 ∧ 出【失】
```

### 4.5 Debug + propagate fix

```
⟦ WEBHOOK_FIX ⟧
● 修 test_payment_webhook
因: HMAC(json.dumps) ≠ HMAC(raw body)
● 定 body = json.dumps(payload, separators=(',',':'))
● 定 sig = HMAC(body)
● 出 body 不 dict
● 動 test → 確
● 找【同 ∈ 他 *test*.py】→ 修【同】
```

### 4.6 Generate-score-select pipeline

```
● 分【物】→ 生【多 化】→ 算【上】→ 取【上 3】→ 出
```

### 4.7 Config fallback chain

```
● 取【config ∈ .env】→ ? 空 → 取【config ∈ ENV】→ ? 空 → 止 ∧ 出【失】
```

### 4.8 Retry with limit

```
● 動【test】→ ? 失 → 回【不 大 3】→ ? 失 → 止 ∧ 出【全 失】
```

---

## 5. Design Principles

1. **English is the failure mode.** 5 ordinary English instructions contained 23 ambiguity points. The formal equivalents contained 0. The unit of value is defect rate, not token count.
2. **Modal prefixes are cognitive switches.** `●` = do exactly this. `○` = think freely. `■` = validate. These change HOW Sonnet processes, not just WHAT.
3. **Left-to-right execution.** `→` is the only sequencing operator. No implicit ordering.
4. **Explicit scope.** `【】` binds arguments. No pronoun resolution. No "it" or "the."
5. **Constraints are negated verbs.** `不化` = do NOT transform. Not "please preserve if possible."
6. **No hedging vocabulary.** No "perhaps," "consider," "might want to." Every line is imperative.
7. **English inside brackets.** `修【json.dumps serialization bug】` — domain terms stay in English. The grammar is formal; the nouns can be whatever the domain needs.
8. **Zero-shot execution.** Sonnet parses this without a decoder ring. Models already know `∀`, `∈`, `∧`. They already know 立 means establish and 析 means analyze. CJK carries its own documentation.

---

## 6. Token Budget

- 46/59 core opcodes are 1-token (78%)
- 13/59 are 2-token (set logic, some verbs)
- 0 are 3-token — all 3-tok symbols purged (~~⇒~~ → `→`, ~~變~~ → `化`, ~~≣~~ → `同`, ~~∅~~ → `空`)
- English inside `【】` costs normal English token rates
- `⟦⟧` costs 2-tok each — worth it as a program-level mode switch
- Average instruction: 10-25 tokens vs 40-80 for English equivalent

---

## 7. Workflow

1. **User** submits complex request to the system.
2. **Opus (Architect)** reasons about the problem, decomposes it, emits a glyph-lang program.
3. **System** passes the program to Sonnet. No decoder ring needed.
4. **Sonnet (Engine)** parses and executes. Each `●` line is a step. Each `?` is a branch. Each `→` is sequence. No re-reasoning.
5. **Result** returned to user.

The critical insight: Opus reasons once, emits structured instructions. Sonnet executes without re-deriving any conclusions. Zero duplicate cognition.
