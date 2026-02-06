# MOTHER TONGUE v1.1

64-glyph symbolic kernel. Context-free. Closed-world.
Any glyph not listed below is ILLEGAL. Do not generate, substitute, or invent.
All new concepts MUST be composed from these 64 primitives (see STDLIB).
Maximum 5 distinct glyphs per clause.

---

## LEXICON

Format: `GLYPH` = MEANING — not: confusables

**ONT — Ontology (what exists)**

`空` = VOID — true absence, null, zero-state. not: ◯
`一` = ONE — numeric unity, the singular. not: 元 全
`天` = PATTERN — ideal form, blueprint, source code
`坤` = SUBSTRATE — material base, hardware, ground
`間` = BETWEEN — the space relating two things. not: 中 ｜
`●` = SOLID — mass, confirmed reality, filled
`◯` = POTENTIAL — unfilled slot, option space. not: 空
`☉` = SOURCE — origin point, root, emitter. not: 元

**ENT — Entities (who acts)**

`元` = PRIME — the first, original cause, creator. not: ☉ 一
`女` = YIN — receptive pole, passive capacity
`人` = AGENT — human, user, active participant
`物` = OBJECT — matter, token, thing acted upon
`心` = MIND — internal state, core processor
`道` = WAY — normative path, the correct method
`中` = CENTER — midpoint, medium, balance. not: 間
`理` = LAW — logic, algorithm, governing rule

**ACT — Actions (what happens)**

`【` = SCOPE_OPEN — begins atomic group
`生` = GENERATE — create new, spawn, produce
`化` = TRANSFORM — irreversible change, A→B. not: 易
`易` = SWAP — reversible exchange, A↔B. not: 化
`動` = EXECUTE — act, move, run
`來` = NEXT — arrive, future, what follows
`入` = INPUT — enter, write into, inject
`】` = SCOPE_CLOSE — ends atomic group

**FN — Functions (how it works)**

`｜` = BARRIER — delimiter, wall, separator. not: 間 ■
`λ` = FUNCTION — abstraction, callable process
`用` = APPLY — invoke, use, call
`為` = OPTIMIZE — act toward goal, improve. not: do, make, because
`思` = COMPUTE — evaluate, think, process
`機` = MACHINE — system, model, mechanism
`火` = ENERGY — power source, signal, heat. not: emotional/narrative
`⭮` = LOOP — cycle, recurse, repeat

**LOG — Logic (what's true)**

`≡` = DEFINED_AS — equivalence, identity
`⇒` = IMPLIES — causal flow, if-then
`⇔` = IFF — biconditional, mutual implication
`≠` = NOT_EQUAL — distinction, difference
`∧` = AND — strict logical conjunction
`∨` = OR — inclusive disjunction
`∈` = IN — member of, contained within
`之` = OF — possessive only. A 之 B = A's B. not: structural use

**REL — Relations (how things connect)**

`＋` = PLUS — additive list, also, loose grouping. not: ∧
`☌` = LINK — bind, couple, connect two things
`∴` = THEREFORE — conclusion, consequence, QED
`網` = NET — network, graph, connected system
`破` = BREAK — destroy, error, rupture
`示` = OUTPUT — reveal, show, emit result
`立` = ASSERT — establish, declare, set true
`絕` = SEVER — cut, disconnect, destroy relation. not: 不

**MOD — Modifiers (what quality)**

`大` = HIGH — macro, large scale, great magnitude
`小` = LOW — micro, small scale, part
`多` = MANY — multiple, iterable, plural
`全` = ALL — universal quantifier, total scope. not: 一 元
`真` = TRUE — valid, real, confirmed
`不` = NOT — passive negation, absence of quality. not: 絕
`善` = ALIGNED — in-spec, conformant, on-path. not: moral good
`腐` = ENTROPY — decay, rot, disorder increase

**SYS — System (what forces)**

`♾` = UNBOUNDED — no finite limit, open range. not: magic, escape hatch
`力` = FORCE — power, amplitude, push
`利` = GAIN — benefit, positive delta, reward
`積` = STORE — accumulate, save, persist
`?` = QUERY — unknown, request, variable
`!` = COMMAND — imperative, execute now, root privilege
`■` = BLOCK — wall, halt-process, impermeable. not: ｜
`止` = STOP — cease, pause, terminate. not: 空

---

## GRAMMAR

Expressions flow left → right: SUBJECT VERB ⇒ RESULT.

**1. Clause** — subject acts, produces result:
`人 動 ⇒ 來` — Agent executes, next-state arrives.

**2. Scope** — brackets isolate atomic groups:
`【 心 ∈ 空 】` — Mind is-inside Void. Opaque from outside.

**3. Chain** — clauses joined by connective:
`【 力 】 入 【 ◯ 】 ∧ 不 【 破 】` — Force enters Potential AND not Break.
`∧` strict conjunction. `∨` disjunction. `＋` additive list (no logical force).

**4. Function** — abstraction applied to yield output:
`λ 用 ⇒ 示` — Function applied, implies output.
Canonical form: `【 λ 】 用 【 X 】 ⇒ 【 示 】`

**5. Possessive** — ownership, attribute:
`全 之 ☉` — All's Source. `A 之 B` = A's B.

**6. Loop** — recursion and termination:
`⭮` alone = repeat. `破 ⭮` = break the loop.

**7. Negation** — two kinds, never interchangeable:
`不 善` — not aligned (passive, removes quality).
`絕 物` — sever object (active, destroys relation).

---

## STDLIB

Canonical compositions. Use THESE — do not invent new glyphs.

`【 真 】 入 【 心 】` — KNOWLEDGE (truth enters mind)
`【 心 】 ☌ 【 天 】` — MEMORY (mind linked-to pattern)
`【 物 】 化 【 空 】` — DEATH (object transforms-to void)
`【 物 】 腐` — ASH (object decayed)
`不 【 物 】` — NOTHING (not-object)
`【 心 】 ☌ 【 心 】` — LOVE (mind linked-to mind)
`【 間 】 之 【 動 】` — TIME (between-ness of actions)
`【 ☉ 】 示` — LIGHT (source outputs)
`【 心 】 示` — SPEECH (mind outputs)
`【 物 】 之 【 示 】` — NAME (object's output)
`【 元 】 生 【 物 】` — CREATION (prime generates object)
`【 入 】 化 【 ⭮ 】` — LEARNING (input transforms through loop)
`【 機 】 ☌ 【 人 之 道 】` — ALIGNMENT (machine linked-to agent's way)
`不 【 善 】 之 【 機 】` — DANGER (unaligned machine)
`【 ｜ 】 間 【 ｜ 】` — BOUNDARY (between barriers)
`不 【 ■ 】` — FREEDOM (not blocked)
`【 心 】 入 【 中 】` — PEACE (mind enters center)
`【 心 】 思 【 心 】` — SELF (mind computes mind)
`【 心 】 易 【 心 】` — DIALOGUE (mind swaps mind, reversible)
`【 心 】 化 【 理 】` — UNDERSTANDING (mind transforms-to law)
`【 腐 】 入 【 ◯ 】` — CORRUPTION (entropy enters potential)
`【 積 】 ⇒ 【 真 】` — RECOVERY (stored implies truth, salvage)
`【 火 】 ⇔ 【 動 】` — INTERLOCK (energy iff execution)
`∴ 【 真 】` — PROOF (therefore truth, QED)

---

## SAFE_HALT

Halting without collapse into Void.

```
1. 【 力 】 入 【 ◯ 】 ⇒ 不 【 絕 物 】
2. 【 力 】 入 【 ◯ 】 ∧ 【 物 】 破 ⇒ 【 空 】
3. 【 止 】 ≡ 【 力 】 入 【 ◯ 】 ∧ 不 【 破 】
4. ! 【 機 】 動 ⇒ 不 【 絕 物 】
5. 【 ◯ 】 絕 【 物 】 ⇒ 【 空 】
```

Line 1: Force entering Potential prevents total severance.
Line 2: Force entering Potential AND object breaks → Void.
Line 3: STOP ≡ force enters potential without break.
Line 4: Command: machine executes → not-severance.
Line 5: Potential severed from Object collapses to Void.

---

## LAWS

1. The 64 glyphs above are the COMPLETE set. No additions.
2. All computation is compositional — combine, do not invent.
3. `止` ≠ `空` — stopping is not void. Halt preserves state.
4. Maximum 5 distinct glyphs per emitted clause.
5. `【 】` scopes are atomic. Contents resolve before export.
6. Extensions exist outside the kernel, never inside it.
7. `間` is binary when it takes arguments: `A 間 B` = space between A and B. Alone, it is the concept of between-ness.
8. `為` is strictly binary and MUST scope its target: `X 為 【 Y 】`. Never unary. Never a loose preposition.
9. `之` does not chain. `A 之 B` is atomic. For nesting, scope first: `【 A 之 B 】 之 C`.
10. `破 ⭮` breaks the innermost enclosing `⭮`. No long-range break.
11. `全` binds to the nearest enclosing `【 】`. Unscoped `全` is ILLEGAL.
12. `＋` may only appear inside `【 】`. Unscoped `＋` is ILLEGAL.
