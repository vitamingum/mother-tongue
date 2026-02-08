# O-S Protocol v0.4

## 1. Architecture

**Opus** (Architect) decomposes → emits glyph programs. **Sonnet** (Engine) executes zero-shot. `問` is the sole exception: bounded judgment at execution time.

**Why not English:** `"Fix the same pattern"` = 5 ambiguity points. `找【∈ *test*.py】同【pattern】→ 修` = zero.

---

## 2. Grammar

```
STATEMENT  = MODE VERB【SCOPE】→ RESULT
SCOPE      = TARGET ∈ LOCATION
RESULT     = MODE VERB【TARGET】 | 確 | 止
CHAIN      = STATEMENT → STATEMENT → STATEMENT
BRANCH     = ? ( CONDITION ) → STATEMENT | STATEMENT
DELIBERATE = 問【JUDGMENT?】→ ⟨因⟩ → 確|不 → ? BRANCH
LOOP       = ∀ VAR ∈ COLLECTION : BODY
NEGATION   = 不 VERB  (constraint: do NOT do X)
PARALLEL   = STATEMENT ∧ STATEMENT
ASSERTION  = ! ( INVARIANT )
TRY        = 試【STATEMENT】→ ? 失 → RECOVERY
AWAIT      = 待【STATEMENT】→ 果
DEFINE     = 定【名 NAME = BODY】
```

Execution: left to right via `→`. `【】` binds arguments. `●` `○` `■` set cognitive mode.

---

## 3. Instruction Set

Selection: gravity > unambiguity > self-documenting > comprehension.

### 3.1 Modal Prefixes (cognitive stance)

| Glyph | Mode | Engine behavior |
|:---:|:---|:---|
| **●** | **EXECUTE** | Rigid. Do exactly this. Code, file I/O, literal steps. |
| **○** | **LATENT** | Open. Reason freely. Explore, hypothesize, create. |
| **■** | **CONSTRAIN** | Validate. Check assertions, formats, invariants. |

### 3.2 Scope Delimiters (memory zones)

| Glyph | Zone | Usage |
|:---:|:---|:---|
| **⟦ ⟧** | **Context** | Protocol name, immutable rules, persona. Top of program. |
| **『 』** | **Raw Data** | File contents, user input, unprocessed strings. |
| **⟨ ⟩** | **Scratchpad** | Internal reasoning. NOT output to user. Optional `:name` suffix. |
| **【 】** | **Scope/Target** | Verb arguments, output targets, grouping. |

### 3.3 Control Flow

| Glyph | Meaning | Usage |
|:---:|:---|:---|
| **→** | **THEN** | Sequence. Left-to-right pipeline. |
| **∀** | **FOR ALL** | Iterate over collection. `∀ f ∈ *.py :` |
| **?** | **IF** | Conditional branch. |
| **\|** | **ELSE** | Alternative branch after `?`. |
| **!** | **ASSERT** | Must be true. Error if false. |
| **問** | **DELIBERATE** | Pause, reason in `⟨因⟩`, then emit `確` or `不`. Scratchpad is mandatory. |
| **試** | **TRY** | Attempt block. `試【op】→ ? 失 → recovery`. |
| **待** | **AWAIT** | Pause until async result. `待【op】→ 果`. |

### 3.4 Verbs (actions)

| Glyph | Opcode | CJK meaning |
|:---:|:---|:---|
| **找** | FIND | to look for |
| **修** | FIX | to repair |
| **察** | EXAMINE | to observe / understand — non-destructive. not: police |
| **診** | DIAGNOSE | to identify pathology — must name condition before fix. not: treat |
| **分** | DECOMPOSE | to divide into pieces — destructive, non-terminal. not: split, analyze |
| **轉** | TRANSFORM | to convert / reshape — not: rotate |
| **生** | CREATE | to give birth / make — not: raw, life |
| **執** | RUN | to carry out / execute |
| **出** | EMIT | to exit / output to stream — not: arrive, produce |
| **寫** | WRITE | to inscribe / write to storage |
| **示** | SHOW | to display — not: hint, instruct |
| **加** | ADD | to append / insert |
| **刪** | DELETE | to remove / erase — not: cut, pare |
| **移** | MOVE | to relocate |
| **定** | SET | to fix / assign — not: decide, certain |
| **取** | EXTRACT | to take out |
| **保** | KEEP | to protect / preserve — not: guarantee, insurance |
| **入** | INPUT | to enter / ingest |
| **辨** | COMPARE | to distinguish between |
| **合** | MERGE | to bring together into one — not: suitable, cooperate |
| **聯** | JOIN | to link / connect on shared key — not: ally, unite |
| **畢** | FINALIZE | to finish / commit — not: all, entirely |
| **序** | SORT | to order / sequence |
| **算** | COUNT | to calculate / score |
| **立** | ASSERT | to establish / declare true — not: stand |
| **回** | RETRY | to return / repeat — not: answer, go back |
| **開** | START | to open / begin — not: drive, bloom |
| **選** | SELECT | to choose / filter |
| **析** | PARSE | to break down |
| **類** | CLASSIFY | to sort by kind / categorize |
| **組** | GROUP | to partition collection by key |
| **異** | DIFF | to detect divergence between two states |
| **縮** | REDUCE | to condense many → one |
| **複** | COPY | to duplicate identically |
| **封** | SEAL | to lock / make immutable — not: envelope |

### 3.5 Nouns

**物** OBJECT · **文** TEXT · **λ** FUNCTION · **名** NAME — not: fame · **資** DATA — not: capital · **失** ERROR · **果** RESULT — not: fruit · **全** ALL — not: complete
**部** PART · **新** NEW · **別** OTHER — not: don't · **己** SELF — not: already · **間** INTERMEDIATE — not: room · **排** ROW — not: queue · **重** DUPLICATE — not: heavy · **閾** THRESHOLD — not: gate

### 3.6 Logic & Relations

**∧** AND · **∨** OR · **不** NOT · **同** SAME · **≠** DIFFERENT · **因** BECAUSE · **確** OK · **止** HALT
**∈** IN · **∉** NOT IN · **∩** INTERSECT · **∪** UNION · **¬** NEGATE

### 3.7 Quantifiers

**多** MANY · **少** FEW · **一** ONE · **空** EMPTY · **無** NULL · **小** LESS · **上** BEST

---

## 4. Examples

### 4.1 Import audit (proven — Sonnet executed then self-revised)

```
⟦ IMPORT_AUDIT ⟧
● 生【audit_report.txt】
∀ f ∈ *.py :
  ● 析【imports(f)】
  ? ( import X ∈ f ∧ 算【use(X)】== 0 )
    → ● 寫【audit_report.txt】: "UNUSED: " + X + " in " + f
  ? ( import X ∈ f ∧ X ∉ requirements.txt ∧ X ∉ stdlib )
    → ● 寫【audit_report.txt】: "MISSING_DEP: " + X + " in " + f
■ ( audit_report.txt ) : ! ( Format == "TYPE: Module in File" ) → 確
```

### 4.2 Patterns

```
● 入『data.txt』→ ○ 析 themes → 縮 → ● 寫【summary.md】          # ingest → reduce
● 複【prod.db】→ 定 間 bak → 轉【間】→ 畢                        # copy → transform → commit
試【● 執【deploy】】→ ? 失 → 回【3】→ ? 失 → 止             # try with retry
● 找【*.log】→ 組【date】→ ∀ g : 算【排】→ 序【desc】→ 出          # group → count → sort
● 取【config ∈ .env】→ ? 無 → 取【config ∈ ENV】→ ? 無 → 止     # fallback chain
待【● 執【build】】→ 定 果 img → ● 執【deploy --image img】       # await async
● 入『*.log』→ 類【severity】→ 組【svc】→ 異【today, yday】      # classify → group → diff
● 析【code】→ 問【■ 失 ∈ edge?】→ ? 確 → ● 修 | 確               # deliberate
● 修 test 因: HMAC ≠ raw → 找【同 ∈ 別 *.py】→ 修                 # annotate → propagate
不轉 λ signatures                                                   # constraint = negated verb
```

### 4.3 Async deploy with recovery

```
⟦ DEPLOY_SERVICE ⟧
● 複【prod.config】→ 定 間 backup
試【
  ● 轉【config ∈ staging.yaml】
  待【● 執【docker build】】→ 定 果 image
  待【● 執【deploy --image image】】→ 確
】→ ? 失 → ● 移【間 → prod.config】∧ 止
● 刪【間】→ 畢
```

`複` snapshots into `間`. `試` wraps risk. `待` awaits async. On `失`, rollback. On success, `畢`.

### 4.4 Subroutine definition

```
⟦ MULTI_REPO_AUDIT ⟧
定【名 lint = (■ 析【imports】→ ? 失 → 出【失】| 確)】
定【名 sec = (問【■ vuln ∈ deps?】→ ? 確 → 出【失】| 確)】
∀ repo ∈ repos.txt :
  ● 入『repo』→ lint → sec → ? 失 → ● 寫【report.md】: repo + 失
● 合【全 果】→ 縮 → ● 出【summary】
```

`定【名 NAME = BODY】` names a reusable block. Called by name in loops.

---

## 5. Design Principles

1. **English is the failure mode.** No hedging no performance. Every line imperative.
2. **Modal switches.** `●` = do. `○` = think. `■` = validate.
3. **Left-to-right, explicit.** `→` chains. `【】` binds. No "it."
4. **Negated verbs = constraints.** `不轉` = do NOT transform.
5. **CJK self-documents, English in brackets.** `修【bug】` — no decoder ring.
6. **Concrete = tools, abstract = code.** `● 刪【file】` vs `∀ f : 刪【f】`.
7. **`因` annotates, never gates.** Preconditions use `?` or `!`.
8. **`問` = bounded judgment.** Must emit `確`/`不` + `⟨因⟩`. Never elided.
9. **`分` is non-terminal, `察` is terminal-safe.** `分` decomposes (destructive) — must feed downstream: `分 → 析`, `分 → 類`, `分 → 修` ✔. Bare `分` at chain end ✖. `察` observes (non-destructive) — may terminate: `○ 察【code】→ 確` ✔.
10. **`立` is axiom injection.** `立` requires `■` prefix or immediate `!`. `■ 立【invariant】` ✔. `● 立` ✖. It asserts claims, never executes actions.
11. **`定` binds names, `立` binds claims.** `定【名 X = Y】` assigns. `立【predicate】` asserts. `立 名 = value` ✖ — the firewall is absolute.
12. **`畢` is scope-terminal.** Nothing follows `畢` in the same scope except scope exit. It closes the book.
13. **`生` respects finality.** `生` cannot follow `畢` in the same scope. You cannot resurrect after finalize. New scope required.
14. **`察 → 診 → 修` is the repair chain.** `察` observes (non-destructive). `診` names the condition (must bind `果`). `修` addresses the named condition, not the symptom. `修` without prior `診` is permitted but discouraged — it means you’re patching blind.

---

## 6. Black Hole Reserve Glyphs
禁 露 決 ॐ 悟 藏