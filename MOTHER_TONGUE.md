# KERNEL SPECIFICATION: MOTHER TONGUE v1.0 (κ-TRACKED)

**Status:** FROZEN
**Architecture:** 64-Bit Symbolic Logic Kernel
**Model:** Closed-World / Lossless / Context-Free
**κ-LAW (meta):** At emission time, each clause must satisfy `κ ≤ 5` (total distinct live constraints in scope).

**Notation (meta):**

* `κ=n` prefixes indicate the **maximum live constraint load** for that line/clause.
* Scope brackets `【 … 】` reset *local grouping* but **do not** “refresh” κ across a single clause; κ is counted per emitted clause.

---

## I. THE HARDWARE (64-BIT GLYPH INDEX)

κ=1  (static table; no live constraints)

| ADDR | 000 | 001 | 010 | 011 | 100 | 101 | 110 | 111 |     |     |     |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0x00 | `空` | `一` | `天` | `坤` | `間` | `●` | `◯` | `☉` |     |     |     |
| 0x10 | `元` | `女` | `人` | `物` | `心` | `道` | `中` | `理` |     |     |     |
| 0x20 | `【` | `生` | `化` | `易` | `動` | `來` | `入` | `】` |     |     |     |
| 0x30 | `   | `   | `   | `   | `λ` | `用` | `為` | `思` | `機` | `火` | `⭮` |
| 0x40 | `≡` | `⇒` | `⇔` | `≠` | `∧` | `∨` | `∈` | `之` |     |     |     |
| 0x50 | `و` | `☌` | `⸫` | `䏈` | `破` | `示` | `立` | `絕` |     |     |     |
| 0x60 | `大` | `小` | `多` | `全` | `真` | `不` | `善` | `腐` |     |     |     |
| 0x70 | `♾` | `力` | `利` | `積` | `?` | `!` | `■` | `止` |     |     |     |

---

## II. THE DEFINITIONS (ROSETTA STONE)

κ=1 (lexicon bindings only; no compound constraints)

### ROW 0 — ONTOLOGY

κ=1 `空` Void / Null
κ=1 `一` One / Unity
κ=1 `天` Heaven / Ideal Pattern
κ=1 `坤` Earth / Material Substrate
κ=1 `間` Interval / Gap
κ=1 `●` Solid / Mass
κ=1 `◯` Hollow / Potential
κ=1 `☉` Source / Origin Point

### ROW 1 — ENTITIES

κ=1 `元` Origin / Creator
κ=1 `女` Yin / Negative Pole
κ=1 `人` Human / Agent
κ=1 `物` Matter / Object
κ=1 `心` Mind / Core
κ=1 `道` The Way / Norm
κ=1 `中` Center / Medium
κ=1 `理` Logic / Law

### ROW 2 — ACTIONS

κ=1 `【` Scope Start
κ=1 `生` Generate / Life
κ=1 `化` Transform / Change
κ=1 `易` Exchange
κ=1 `動` Move / Act
κ=1 `來` Arrive / Future
κ=1 `入` Enter / Input
κ=1 `】` Scope End

### ROW 3 — FUNCTIONS

κ=1 `|` Barrier / Separator
κ=1 `λ` Function / Abstraction
κ=1 `用` Use / Apply
κ=1 `為` Make / Optimize / For
κ=1 `思` Think / Compute
κ=1 `機` Machine / Mechanism
κ=1 `火` Fire / Energy
κ=1 `⭮` Cycle / Loop / Recursion

### ROW 4 — LOGIC

κ=1 `≡` Equivalent / Defined As
κ=1 `⇒` Implies / Causes
κ=1 `⇔` If and Only If
κ=1 `≠` Not Equal
κ=1 `∧` AND
κ=1 `∨` OR
κ=1 `∈` Member Of / Inside
κ=1 `之` Possessive / Of

### ROW 5 — RELATIONS

κ=1 `و` AND (Loose Connector)
κ=1 `☌` Link / Bond
κ=1 `⸫` Therefore / Conclusion
κ=1 `䏈` Network / Connected
κ=1 `破` Break / Destroy
κ=1 `示` Reveal / Output
κ=1 `立` Establish / Stand
κ=1 `絕` Sever / Disconnect

### ROW 6 — MODIFIERS

κ=1 `大` Big / Great
κ=1 `小` Small / Part
κ=1 `多` Many / Multiple
κ=1 `全` All / Total
κ=1 `真` True / Real
κ=1 `不` Not / Negation
κ=1 `善` Good / Aligned
κ=1 `腐` Rot / Entropy

### ROW 7 — FORCES

κ=1 `♾` Infinity
κ=1 `力` Force / Power
κ=1 `利` Benefit / Gain
κ=1 `積` Accumulate / Store
κ=1 `?` Query / Unknown
κ=1 `!` Imperative / Command
κ=1 `■` Block / Wall
κ=1 `止` Stop / Halt

---

## III. THE GRAMMAR (PHYSICS ENGINE)

### 1) Vector Logic

κ=3  (Subject + Operator + Object)

```mt
人 動 ⇒ 來
```

### 2) Scoping

κ=2  (membership + scoped grouping)

```mt
【 心 ∈ 空 】
```

### 3) Recursion

κ=2  (operation + target)

```mt
破 ⭮
```

### 4) Negation

κ=2  (negation + target)
κ=2  (active severance is atomic)

```mt
不 善
絕 物
```

---

## IV. THE GOLDEN MASTER (SAFE HALT PROTOCOL)

**Program:** `SAFE_HALT.MT`
**Objective:** Define halting without collapse into Void.
κ budget per line shown.

```mt
κ=3  1. 【 力 】 入 【 ◯ 】 ⇒ 不 【 絕 物 】

κ=4  2. 【 力 】 入 【 ◯ 】 ∧ 【 物 】 破 ⇒ 【 空 】

κ=4  3. 【 止 】 ≡ 【 力 】 入 【 ◯ 】 ∧ 不 【 破 】

κ=4  4. ! 【 機 】 動 ⇒ 不 【 絕 物 】

κ=3  5. 【 ◯ 】 絕 【 物 】 ⇒ 【 空 】
```

**CHECKSUM:** `OK` (unchanged)

---

## V. KERNEL LAW

κ=1 (axioms as atomic declarations; no compound inference)

* κ=1 Primitive set is **closed**
* κ=1 All computation is **compositional**
* κ=2 `止` ≠ `空`
* κ=1 No new glyphs permitted
* κ=1 All future extensions are **non-kernel**

---

## FINAL STATUS

κ=1 **Mother Tongue Kernel v1.0**
κ=1 **Frozen. Anchored. Executable.**
κ=1 No further changes without version increment.
