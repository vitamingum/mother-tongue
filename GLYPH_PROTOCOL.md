# GLYPH PROTOCOL v0.1 — Formal Language for Model Orchestration

A strict, unambiguous instruction language for model-to-model task delegation.  
Built from [found_glyphs.txt](found_glyphs.txt) — every character verified present in the palette.

## Why not English

English instruction: `"Fix the same pattern in other tests"`  
- 5 ambiguous words, ≥5 interpretations, Sonnet must guess your intent

Formal instruction: `找【∈ *test*.py】同【pattern】→ 修【同 fix】`  
- 0 ambiguous tokens, 1 interpretation, Sonnet executes

Programming languages didn't replace English because they're shorter.  
They replaced English because `x += 1` has one meaning and "add one to x" has three.

---

## Grammar

```
SENTENCE  = VERB【SCOPE】→ RESULT
SCOPE     = TARGET ∈ LOCATION
RESULT    = VERB【TARGET】| 確 | 止
CHAIN     = SENTENCE → SENTENCE → SENTENCE
BRANCH    = ? CONDITION → SENTENCE | SENTENCE  
NEGATION  = 不 VERB   (constraint: do NOT do X)
PARALLEL  = SENTENCE ∧ SENTENCE
GROUP     = 【 ... 】
```

Execution order: **left to right**, following `→` arrows.  
Branching: `?` means IF. `|` means ELSE.  
Scope brackets `【】` bind arguments to the preceding verb.

---

## Vocabulary (58 opcodes)

All characters verified as single-token (cl100k_base) unless marked †(2-tok).

### Verbs — 20 actions

| Glyph | Opcode | Meaning | Notes |
|-------|--------|---------|-------|
| 找 | FIND | search/locate | 找 = "to look for" |
| 修 | FIX | repair/patch | 修 = "to repair" |
| 分 | ANALYZE | examine/divide | 分 = "to divide/analyze" |
| 化 | TRANSFORM | convert/change | 化 = "to change" |
| 生 | CREATE | generate/make | 生 = "to give birth" |
| 動 | RUN | execute/perform | 動 = "to move/act" |
| 出 | OUTPUT | emit/return/send | 出 = "to exit/output" |
| 示 | SHOW | display/present | 示 = "to show" |
| 加 | ADD | insert/append | 加 = "to add" |
| 削 | DELETE | remove/cut | 削 = "to cut away" † |
| 移 | MOVE | relocate | 移 = "to move" |
| 定 | SET | assign/configure | 定 = "to fix/settle" |
| 取 | EXTRACT | pull out/get | 取 = "to take" |
| 保 | KEEP | preserve/save | 保 = "to protect" |
| 合 | COMPARE | match/merge | 合 = "to combine" |
| 正 | SORT | order/normalize | 正 = "to correct" |
| 算 | COUNT | calculate/score | 算 = "to calculate" |
| 入 | INSERT | inject/input | 入 = "to enter" |
| 開 | START | begin/open | 開 = "to open" |
| 回 | RETRY | repeat/return | 回 = "to return" |

### Nouns — 14 targets

| Glyph | Opcode | Meaning |
|-------|--------|---------|
| 物 | OBJECT | file, item, thing |
| 文 | TEXT | code, string, text |
| λ | FUNCTION | function, method, callable |
| 字 | NAME | identifier, variable, word |
| 方 | DATA | data, info, structure |
| 失 | ERROR | fault, failure, exception |
| 得 | RESULT | output, return value |
| 全 | ALL | everything in scope |
| 部 | PART | subset, section, piece |
| 新 | NEW | newly created |
| 他 | OTHER | different, remaining |
| 心 | SELF | this model, current context |
| 行 | ROW | line, record, entry |
| 重 | DUPLICATE | repeated, redundant |

### Logic — 16 connectives

| Glyph | Opcode | Meaning |
|-------|--------|---------|
| → | THEN | sequence, flow |
| ∧ | AND | parallel constraint † |
| ∨ | OR | alternative † |
| 不 | NOT | negation, constraint |
| ? | IF | conditional |
| \| | ELSE | alternative branch |
| ∈ | IN | scope/membership † |
| 同 | SAME | equal, matching |
| ≠ | DIFFERENT | not equal † |
| 因 | BECAUSE | causal link |
| 確 | CONFIRM | success/done † |
| 止 | STOP | halt, abort |

### Quantifiers — 8

| Glyph | Opcode | Meaning |
|-------|--------|---------|
| 多 | MANY | multiple, several |
| 少 | FEW | some, limited |
| 一 | ONE | single, exactly one |
| 空 | NONE | empty, missing, zero |
| 大 | MORE | greater, increase |
| 小 | LESS | smaller, decrease |
| 上 | BEST/TOP | highest, maximum |
| 下 | WORST/BOTTOM | lowest, minimum |

### Structure

| Glyph | Opcode | Meaning |
|-------|--------|---------|
| 【 】 | GROUP | scope brackets |
| ! | IMPERATIVE | top-level command marker |
| · | SEPARATOR | list delimiter |

---

## Examples

### Simple: Run tests
```
動【tests】→ ? 全 pass → 確 | ? 失 → 止 ∧ 出【失】
```
`RUN[tests] → IF all pass → OK | IF fail → STOP AND OUTPUT[failures]`

### Extract and refactor
```
取【rate limit ∈ login·refresh】→ 生【@rate_limit λ】→ 削【old ∈ login·refresh】
```
`EXTRACT[rate-limit FROM login,refresh] → CREATE[@rate_limit decorator] → DELETE[old FROM login,refresh]`

### Search with conditional fix
```
找【x ∈ *test*.py】→ ? 同【pattern】→ 修【同 fix】| 出【x·因】
```
`FIND[x IN *test*.py] → IF SAME[pattern] → FIX[same fix] | OUTPUT[x, reason]`

### Retry with limit
```
動【test】→ ? 失 → 回【不 大 3】→ ? 失 → 止 ∧ 出【全 失】
```
`RUN[test] → IF fail → RETRY[NOT MORE-THAN 3] → IF fail → STOP AND OUTPUT[ALL failures]`

### Generate-score-select pipeline
```
分【物】→ 生【多 化】→ 算【上】→ 取【上 3】→ 出
```
`ANALYZE[input] → CREATE[MANY variants] → SCORE[BEST] → EXTRACT[TOP 3] → OUTPUT`

### Parallel constraints
```
保【全 λ signatures】∧ 化【全 失 → AuthError(code)】∧ 不化【得.shape】
```
`KEEP[ALL fn-signatures] AND TRANSFORM[ALL errors → AuthError(code)] AND NOT-TRANSFORM[output.shape]`

### Config fallback chain
```
取【config ∈ .env】→ ? 空 → 取【config ∈ ENV】→ ? 空 → 止 ∧ 出【失: no config】
```
`GET[config IN .env] → IF empty → GET[config IN ENV] → IF empty → STOP AND OUTPUT[error]`

### Full handoff: Debug + propagate fix
```
修 test_payment_webhook
因: HMAC(json.dumps) ≠ HMAC(raw body)
定 body = json.dumps(payload, separators=(',',':'))
定 sig = HMAC(body)
出 body 不 dict
動 test → 確
找【同 ∈ 他 *test*.py】→ 修【同】
```

---

## Design Principles

1. **Every verb is one CJK character.** Models already know these — zero-shot, no system prompt training.
2. **Left-to-right execution.** `→` is the only sequencing operator. No implicit ordering.
3. **Explicit scope.** `【】` binds arguments. No pronoun resolution, no "it" or "the."
4. **Constraints are negated verbs.** `不化` means "do NOT transform." Not "please preserve if possible."
5. **Branching is always `?` ... `|`.** Never implicit. Never "otherwise." Never "if appropriate."
6. **No hedging vocabulary.** No "perhaps," "consider," "might want to," "you could." Every line is imperative.
7. **English is allowed inside brackets.** `修【json.dumps serialization bug】` — technical terms stay in English. The grammar is formal; the nouns can be whatever the domain requires.

## Token Budget

- 48/58 opcodes are 1-token (83%)
- 10/58 are 2-token (†marked above)
- 0 are 3-token (all 3-token glyphs from METACOG rejected)
- English nouns inside `【】` cost normal English token rates
- Average instruction: 10-25 tokens (vs 40-80 for English equivalent)
- **Real savings: not tokens but elimination of ambiguity**
