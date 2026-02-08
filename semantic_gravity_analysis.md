# Semantic Gravity Analysis: Mining vs. Spec

## Already in MODEL_AUTOMATION_SPEC ✓

| Mined Glyph | Status in Spec | Gravity Assessment |
|:---:|:---|:---|
| **加** | ADD (verb) | ✓ Already captured |
| **∧ ∨** | AND / OR (logic) | ✓ Core logical operators |
| **→** | THEN (control flow) | ✓ Primary sequencer |
| **因** | BECAUSE (relation) | ✓ Annotation primitive |
| **果** | RESULT (noun) | ✓ Output binding |
| **【 】** | Scope/Target delimiter | ✓ Primary argument binder |

**Analysis:** Model re-discovered 6/9 core glyphs independently. High validation.

---

## Novel Mining Picks (Not in Spec)

### HIGH GRAVITY (Should Consider)

| Glyph | Meaning | Gravity | Why Strong |
|:---:|:---|:---:|:---|
| **減** | SUBTRACT | 🌑🌑🌑 | Perfect complement to 加. Math operations need both polarities. Spec has ADD but no explicit SUBTRACT. |
| **⊕ ⊗** | XOR / TENSOR | 🌑🌑🌑🌑 | Extremely crisp semantics. ⊕ = exclusive-or (toggle, diff without intersection). ⊗ = tensor product (compose, cross). Model picked this 3/3 times. |
| **因 果** | CAUSE EFFECT | 🌑🌑🌑🌑 | Model chose as PAIR twice. Spec has 因 (BECAUSE) but not 果 as standalone causal marker. The pair encodes bidirectional reasoning. |
| **建** | BUILD | 🌑🌑🌑 | Distinct from 生 (CREATE). 建 = construct incrementally from parts. 生 = bring into existence. Orthogonal. |

### MEDIUM GRAVITY (Interesting but Redundant)

| Glyph | Meaning | Gravity | Why Weaker |
|:---:|:---|:---:|:---|
| **創** | CREATE | 🌑🌑 | Spec already has 生 (CREATE). 創 = innovate/originate. Semantic overlap ~70%. |
| **天 地** | HEAVEN EARTH | 🌑🌑 | Beautiful pair, but abstract nouns. Spec prioritizes verbs > nouns. Universe-scale concepts rarely needed in code automation. |
| **「 」** | CORNER QUOTES | 🌑 | Spec already has 4 delimiter pairs: 【】『』⟦⟧⟨⟩. Fifth pair adds token cost without orthogonal function. |

---

## Comparative Semantic Gravity

### ⊕ ⊗ (HIGHEST)
**Model confidence:** 3/3 identical picks from 64-glyph slate.

**Semantic wells:**
- `⊕` pulls toward: XOR, symmetric difference, toggle, parity, exclusive selection
- `⊗` pulls toward: tensor product, Cartesian product, compose, multiply

**Why gravity is extreme:**
1. **Unambiguous:** Unlike ∪ (union OR intersection?), ⊕ has ONE meaning in math/CS
2. **Paired operators:** Like ∧∨, they form a complementary dyad
3. **Missing primitive:** Spec has ∧∨ (boolean) but no XOR. Spec has no composition operator.
4. **Token efficient:** Single glyph vs `XOR【A, B】` or `∧ 不 ∨`

**O-S use case:**
```
⊕【A, B】           # symmetric diff: (A ∪ B) - (A ∩ B)
資 ⊗ 資 → 資       # compose data transformations
選【changed】⊕ 選【expected】  # what differs between sets
```

---

### 減 (HIGH)

**Model confidence:** 2/3 picks paired with 加.

**Semantic well:**
- Pulls toward: subtract, remove numerically, decrement, reduce by amount

**Why gravity is high:**
1. **Perfect complement:** 加 is in spec. Math needs polarity.
2. **Distinct from 刪:** 刪 = DELETE (remove existence). 減 = subtract (numeric operation).
3. **Natural pairing:** Model consistently picks 加減 together.

**Current spec gap:**
- Has: 加 (ADD), 縮 (REDUCE many→one), 刪 (DELETE)
- Missing: numeric subtraction

**O-S use case:**
```
● 算【errors】→ 減【fixed】→ 算【remaining】
● 加【new_features】∧ 減【deprecated】→ 算【net】
```

---

### 因 果 as CAUSAL PAIR (HIGH)

**Model confidence:** Picked twice as pair.

**Semantic wells:**
- `因` already in spec as BECAUSE (annotation)
- `果` in spec as RESULT (output binding)

**Why pairing adds gravity:**
1. **Bidirectional reasoning:** `因` explains backward, `果` projects forward
2. **Natural language:** "因X故Y" = because X therefore Y
3. **Program flow:** `因` = precondition, `果` = postcondition

**Current spec usage:**
```
● 修 test 因: HMAC ≠ raw    # 因 annotates reason
待【● 執【build】】→ 定 果 img   # 果 captures result
```

**Enhanced with explicit pairing:**
```
問【因 X → 果 Y ?】           # does X cause Y?
● 分 因 → 析 果               # analyze causal chain
```

---

### 建 (BUILD) vs 生 (CREATE)

**Model confidence:** Picked once with 創.

**Semantic distinction:**
- `生` (in spec) = CREATE = bring into existence (birth metaphor)
- `建` = BUILD = construct from components (assembly metaphor)

**Orthogonality:** ~70% overlap, but nuance matters:
- `生【file】` = create new file (conjure)
- `建【project】` = scaffold project from template (build up)

**Spec has both metaphors elsewhere:**
- 合 (MERGE = bring together)
- 組 (GROUP = partition)

**Verdict:** Medium gravity. 建 useful if O-S needs incremental construction semantics distinct from instantiation.

---

## Recommendations by Gravity

### TIER 1: Immediate Activation (breaks semantic gaps)
1. **⊕ ⊗** — XOR and compose operators. Model's strongest signal. Zero ambiguity.
2. **減** — Numeric subtract. Natural complement to 加.

### TIER 2: Deliberate Activation (enhances existing)
3. **因 果 as causal dyad** — Already in spec separately, but formalizing their paired semantics could enable richer reasoning patterns.

### TIER 3: Reserve (beautiful but redundant)
4. **建** — If O-S needs BUILD distinct from CREATE
5. **天 地** — If O-S expands to cosmological/hierarchical concepts
6. **創** — Overlaps 生 too much
7. **「 」** — Fifth delimiter pair, low marginal utility

---

## Gravity Score Summary

```
⊕ ⊗  ████████████ 12/10  (off-scale: model certainty × semantic precision)
減    ████████░░░░  8/10  (completes arithmetic dyad)
因果  ███████░░░░░  7/10  (already in spec, pairing adds formalism)
建    █████░░░░░░░  5/10  (nuanced, but 生 covers 70%)
天地  ███░░░░░░░░░  3/10  (poetic, rarely operational)
創    ██░░░░░░░░░░  2/10  (duplicates 生)
「」  █░░░░░░░░░░░  1/10  (fifth delimiter)
```

---

## Key Insight: Model's XOR Fixation

The fact that qwen2.5-coder picked `⊕ ⊗` with **100% consistency** (3/3 trials) from a 64-glyph slate suggests these symbols activate an extremely deep semantic well in the model's training. Math/CS texts heavily use ⊕ for XOR and ⊗ for tensor/cross products. 

**This is a model telling you what it "thinks" clearly.**

For O-S Protocol: if you want Opus/Sonnet to execute with zero ambiguity, glyphs that models *independently mine* have higher grounding than human-selected symbols.
