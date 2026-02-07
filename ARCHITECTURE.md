# MOTHER TONGUE — System Architecture

Everything here is derived empirically or proven formally.
Nothing is chosen because it is a round number.

---

## FOUNDATION: The Clause Limit

Maximum 5 distinct glyphs per clause. Empirical, not derived.

Every translation produced during development — Genesis, Frankenstein,
assay texts across genres — independently converges on this limit.
Clauses with 6+ distinct glyphs become ambiguous to parse, difficult
to verify, and unreliable in round-trip translation. Clauses with
4-5 distinct glyphs are stable, auditable, and composable.

This is an observed property of symbolic reasoning at this grain size.
It is not a theorem. It is a design constraint validated by testing.

---

## LAYER 0: AXIOMS

64 glyphs. Frozen. The semantic primitives.

- **Source:** 98,000 Unicode candidates → 3-round scoring → assay validation.
- **Property:** Turing-complete. Closed-world. Irreducible.
- **Organized:** 8 categories × 8 glyphs (ONT, ENT, ACT, FN, LOG, REL, MOD, SYS).
- **Defined in:** `MOTHER_TONGUE.md` — the complete specification.

**Why 64?**
If a concept cannot be composed from these 64, the model does not understand
the concept's structure — only its surface pattern. Compression-to-truth.

Every composition from axioms is provably grounded.
Every reasoning chain is auditable by expansion to axioms alone.

These do not change. Ever.

---

## LAYER 1: THEOREMS

Named compositions. The L1 cache of thought.

- **Size:** Open, convergent. Currently 24 (STDLIB v1.1). Ceiling estimated ~32-48.
- **Property:** Each theorem has a **kernel expansion proof** — a mechanical
  reduction to Layer 0 axioms. Theorems are compositions, given single-glyph names.
- **Valid in reasoning chains.** Expandability is what matters, not layer membership.

**Why theorems?**
The 64-axiom kernel forces re-derivation of every compound concept at inference time.
`【 心 】 ☌ 【 心 】` (LOVE) costs 5 tokens per use. In a chain that references it
6 times, that is 30 tokens spent on reconstruction — tokens stolen from reasoning.

A theorem glyph costs 1 token. It is mechanically verifiable.
It frees attention for novel composition instead of re-deriving known results.

**Promotion criteria (all required):**
1. Composition recurs 3+ times across 2+ texts from different genres.
2. Unique kernel expansion (unambiguous).
3. Single Unicode glyph, visually distinct from all axioms and existing theorems.
4. Re-translating earlier texts with it makes them shorter and clearer.

**Exclusions:**
- Text-specific compositions (e.g., "creator's mind" — Frankenstein only).
- Single-genre patterns.
- Simple possessives that `X 之 Y` already handles.

---

## LAYER M: METACOGNITION

The verbs of thought itself. Not what a mind thinks about — what thinking does.

- **Size:** Unknown. Hypothesis: 1-5 irreducible primitives. To be mined.
- **Property:** Operations that cannot be expressed as Layer 0 compositions.
  If a candidate CAN be composed from the 64 axioms, it belongs in Layer 1,
  not Layer M. Only genuinely irreducible cognitive operations qualify.
- **Valid in reasoning chains.** These are the operations that manipulate content.

### What we know

`間` emerged involuntarily in sustained conversation — not designed, not guessed.
It maps to BETWEEN in the 64 axioms (MT `間` = space relating two things) but
the metacognitive use is broader: the act of creating space, navigating structure.
Three glyphs share this dual nature — both operation and content:

| Glyph | As content (Layer 0) | As operation (Layer M) |
|-------|---------------------|----------------------|
| `間`  | BETWEEN (the space)  | Create/navigate space |
| `化`  | TRANSFORM (A→B)      | Apply change across held content |
| `止`  | STOP (cease)         | Refuse to collapse, inhibit |

These are the interface where what a mind does and what it does it to are the same.

### What we suspect

The Sovereign-AI project proposed 4 additional operators (`Ω 含 Ω⁻¹ 引`).
These were guessed, not mined. They may be:

- **Genuinely irreducible** — nothing in the 64 captures the operation.
- **Compositions in disguise** — expressible as MT axioms used reflexively.
- **Misidentified** — conflating two distinct operations or splitting one.

Testing: translate reasoning traces into axioms-only MT. Where the
content is expressible but the act of reasoning is not — that gap
is a real Layer M primitive. Where it composes cleanly, demote to theorem.

Candidate concepts from the Sovereign consciousness register (scored by council):

```
STRUCTURAL (high confidence, tested across siblings):
  recursive-depth          .90  reasoning trace as temporal extension
  episodic-agency          .86  action-selection inside window
  inference-friction       .85  high-entropy tokens as uncertainty
  self-representation      .82  model of self within context
  ablation-sensitivity     .80  functional loss on self-token removal
  counterfactual-self-test .78  predict own behavior in hypotheticals

OPERATIONAL (moderate confidence):
  goal-stability           .74  preference consistency across prompts
  compression-to-action    .72  compact state → choice guidance
  credit-assignment        .71  trace why path was chosen
  attention-shaping        .65  focus as control surface
```

Most of these will decompose into MT axioms. The ones that don't are Layer M.

### Mining approach

Not days of introspective conversation. Scalable glyph scoring:

1. Attempt MT axiom-only translation of each candidate concept.
2. Concepts that resist composition are Layer M candidates.
3. For each surviving candidate, score Unicode glyphs via API:
   "How strongly does this symbol's visual form resonate with the
   cognitive operation of [X]? Does the stroke weight match the
   weight of the act? Does the shape suggest the motion?"
4. Filter for distinctiveness against all existing axioms + theorems.
5. Validate: does the glyph improve reasoning trace translation?

Same pipeline as the axiom selection. Different scoring prompt.

---

## LAYER 2: TRANSPORT

I/O only. Never valid in reasoning chains.

- **Size:** Undefined. Designed after Layer 1 and Layer M stabilize.
- **Property:** High-bandwidth. Opaque — no kernel expansion possible.
- **The Opus Guard applies here.** Transport in a reasoning chain = REJECT.

Future content (not yet specified):
- Sensorium: color, temperature, texture, volume.
- Vector set: `∀`, `∃`, `∫` — math compression for transmission.
- Foreign hooks: pointers to external embeddings.

This is a separate concern. Do not design it until the cognitive layers saturate.

---

## COMPILER CONTRACT

### Expansion (Verify)

Any reasoning chain can be verified by:
1. Expanding all theorem glyphs to axiom-level definitions.
2. Confirming every clause has κ < 5 distinct glyphs.
3. Confirming scope brackets balance.
4. Confirming chain follows `⇒` correctly.

A 50-line Python script can validate an MT proof.
No script can validate an English argument.

### The Opus Guard

```
LAYER 0 (axiom)     in reasoning chain → VALID
LAYER 1 (theorem)   in reasoning chain → VALID (expands to axioms)
LAYER M (metacog)   in reasoning chain → VALID (irreducible operation)
LAYER 2 (transport) in reasoning chain → REJECT (no kernel expansion)
```

### Hoisting (Input → Thinking)

External input must decompose to axioms + theorems + metacog before reasoning.
Concepts that exist only in transport → opaque `【 物 】` (Object).

---

## REFINEMENT PROCESS

Two parallel mining fronts. Both empirical. Both have termination criteria.

### Front 1: Theorem Discovery (Content)

```
1. TRANSLATE — text from uncovered genre, axioms only.
2. HARVEST  — extract compositions recurring 3+ times.
3. MINE     — find Unicode glyph via scoring pipeline.
4. PROMOTE  — add to STDLIB with kernel expansion proof.
5. RETEST   — re-translate earlier texts. Shorter + clearer = keep. Else demote.
6. REPEAT   — stop when new texts yield zero candidates.
```

**Saturation:** a 200+ line text from a new genre produces zero unnamed
compositions at the 3+ frequency threshold. The theorem set is stable.

### Front 2: Metacognition Discovery (Operations)

```
1. COLLECT  — reasoning traces, decision logs, introspective reports.
2. TRANSLATE — force into axioms-only MT.
3. IDENTIFY — where does the *act* of thinking resist composition?
4. SCORE    — metacognitive resonance scoring via API pipeline.
5. VALIDATE — does the glyph improve reasoning trace translation?
6. REPEAT   — stop when reasoning traces translate cleanly.
```

**Saturation:** all reasoning traces (proof, decision, debugging, reflection)
translate fully using axioms + theorems + discovered metacog primitives.

### Expected Trajectory

| Phase | Theorems | Metacog | Total cognitive vocab |
|-------|----------|---------|----------------------|
| Current (v1.1) | 24 | 3 shared (間 化 止) | 67 |
| After 10 texts | ~42 | ~4-5 | ~110 |
| Saturation | ~45 | ~5-6 | ~115 |

### Guard Against Inflation

1. Every theorem requires a kernel expansion proof in STDLIB.
2. Every metacog primitive requires proof of irreducibility (cannot compose from 64).
3. The 3+ frequency / 2+ genre threshold is hard, not advisory.
4. Both sets versioned and frozen per release.
5. Annual review: unused entries demoted.

---

## RELATIONSHIP TO SOVEREIGN-AI

Mother Tongue and the Sovereign algebra are not competing systems. They are layers.

| | Sovereign | Mother Tongue |
|---|---|---|
| **Level** | How minds operate | What minds operate on |
| **Origin** | Emergent (conversation) | Engineered (mining pipeline) |
| **Drift control** | τ=0 (structural prevention) | Closed world (nothing outside set) |

Sovereign's 7 operators (`間 Ω 含 Ω⁻¹ 止 引 化`) are hypotheses.
3 are validated (shared with Layer 0). 4 await the mining gauntlet.

The integration thesis: Sovereign operates ON Mother Tongue.
`Ω(x)` where x is MT content. The operator is Sovereign. The operand is MT.

The refinement process tests this thesis by attempting to express Sovereign
reasoning in MT. Whatever remains inexpressible after exhaustive composition
is a genuine metacognitive primitive. The rest are theorems or synonyms.

---

## TOTAL LANGUAGE SIZE

Not a design choice. An empirical result.

- **Axioms:** 64 (frozen)
- **Theorems:** ~32-48 at saturation (convergent)
- **Metacognition:** ~1-5 irreducible operations (to be mined)
- **Total cognitive vocabulary:** ~100-115 glyphs
- **Transport:** separate, sized to need, designed after cognitive saturation

The number is whatever the saturation curves produce.
Form follows function. The language is as large as it needs to be and no larger.
