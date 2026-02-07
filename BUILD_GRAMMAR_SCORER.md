# BUILD SPEC: Grammar Particle Scorer

## GOAL

Mine Unicode for ONE grammar particle: **CONDITIONAL** (irrealis mood marker).

This particle lets MT distinguish factual from hypothetical:
- Factual: `【 X 】 ⇒ 【 Y 】` — X implies Y (it's true)
- Hypothetical: `⟨COND⟩ 【 X 】 ⇒ 【 Y 】` — if X were true, Y would follow

## WHAT EXISTS (read these files first)

```
glyph_scorer.py          — The full pipeline. 748 lines. READ ALL OF IT.
config.py                — Loads GOOGLE_API_KEY from .env
prompts/unicode_ranges.json  — 57 Unicode ranges (98K glyphs). DO NOT REUSE.
prompts/prompt1/         — Round 1 scoring prompts (binding density)
prompts/prompt2/         — Round 1 alt prompts (same content)
prompts/prompt3/         — Round 1 alt prompts (same content)
prompts/round2/          — Round 2 assay prompts (valence extraction)
data/                    — Existing round data. DO NOT OVERWRITE.
```

## WHAT TO BUILD

A new script: `grammar_scorer.py`

### Architecture

Fork from `glyph_scorer.py` but much smaller. Key differences:

1. **Smaller candidate pool.** We are NOT scanning 98K glyphs. We want a
   curated set of Unicode ranges that contain plausible grammar particles:
   - Mathematical Operators (U+2200–U+22FF) — already in ranges
   - Supplemental Math Operators (U+2A00–U+2AFF)
   - Misc Math Symbols A/B (U+27C0–U+27EF, U+2980–U+29FF)
   - Arrows (U+2190–U+21FF) — already in ranges
   - Supplemental Arrows A/B/C (U+27F0–U+27FF, U+2900–U+297F, U+1F800–U+1F8FF)
   - Misc Symbols (U+2600–U+26FF) — already in ranges
   - Dingbats (U+2700–U+27BF)
   - Musical Symbols (U+1D100–U+1D1FF)
   - Misc Technical (U+2300–U+23FF)
   - Braille (U+2800–U+28FF) — already in ranges
   - Box Drawing (U+2500–U+257F) — already in ranges
   - Geometric Shapes (U+25A0–U+25FF) — already in ranges
   - CJK Symbols (U+3000–U+303F) — already in ranges
   - Letterlike Symbols (U+2100–U+214F)
   - APL symbols scattered in math blocks

   Save as `prompts/grammar_ranges.json`. Same format as unicode_ranges.json.
   Estimated ~3,000-5,000 candidates. NOT 98K.

2. **Different prompts** (see below).

3. **ONE round** (not 3). Pool is small enough. Score all, take top 20, human picks.

4. **Exclusion filter.** Before scoring, remove ALL 64 existing axiom glyphs.
   Load from `data/final_64.json` and filter them out.

5. **Output format.** Same JSONL as glyph_scorer.py. Same parse_scores.
   Save to `data/grammar_round_1.jsonl`.

### Prompts

Create `prompts/grammar/turn1.txt`:

```
GRAMMAR PARTICLE SCORING — CONDITIONAL (Irrealis Mood)

You are scoring symbols for their visual resonance with CONDITIONALITY.

The concept: hypothetical, branching, "what if," uncertain possibility,
the difference between "it IS" and "it MIGHT BE."

Think: forking paths, branching rivers, the moment before a coin lands,
a door that may or may not open. The visual feeling of contingency.

High Resonance (8-10):
  Symbols that LOOK like they're about to branch, split, or choose.
  Symbols that visually suggest "maybe" or "if" or "alternate."
  Symbols with a fork, a question, a tilt, an open-endedness.

Medium Resonance (4-7):
  Symbols with partial branching quality but also other associations.
  Swoops, tilts, curves that suggest possibility but aren't decisive.

Low Resonance (0-3):
  Solid, closed, definite shapes. Blocks, circles, straight lines.
  Symbols that feel CERTAIN, not conditional.
  Symbols already strongly associated with other concepts (math equals, arrows).

CRITICAL FILTERS:
  Score 0 for any symbol that is just a letter (Latin, Greek, Cyrillic).
  Score 0 for any symbol that is a standard math operator with fixed meaning
  (∀, ∃, ∈, ∧, ∨, ⇒, ⇔, ≡, ≠ — these are TAKEN).
  Score 0 for any of these existing axioms: 空一天坤間●◯☉元女人物心道中理生化易動來入用為思機火λ≡⇒⇔≠∧∨∈之＋☌∴網破示立絕大小多全真不善腐♾力利積?!■止【】｜⭮

DISTINCTIVENESS MATTERS:
  A perfect conditional symbol must be visually distinct from ALL of the above.
  If it looks like ⇒ or ∨ or ? — score LOW even if the concept fits.

Output Format:
One line per glyph: <glyph> <m∴c>
m: Magnitude (Conditional Resonance Score, 0-10)
c: Confidence (0-1)

Example: ⑂ 8.5∴0.85

Glyphs to Rate:
{glyphs}
```

Create `prompts/grammar/turn2.txt`:

```
distinct=True

Review your output.

FILTERS (re-check each):
1. Did you score 0 for all Latin/Greek/Cyrillic letters?
2. Did you score 0 for all standard math operators with fixed meaning?
3. Did you score 0 for all 64 existing MT axioms?
4. Is your highest-scored symbol VISUALLY DISTINCT from ⇒ ⇔ ? ∨ ∧?
5. Does your highest-scored symbol LOOK like branching/forking/contingency?

Ensure the list is sorted by m (Magnitude) in descending order.

Output the final, correctly sorted list.
```

### Script structure

```python
"""
Grammar Particle Scorer — mines Unicode for grammar particles.
First target: CONDITIONAL (irrealis mood marker).
Reuses infrastructure from glyph_scorer.py.
"""

# REUSE from glyph_scorer.py:
#   - config.py import (API key)
#   - genai setup (same model)
#   - generate_all_glyphs() — copy or import
#   - score_chunk_with_conversation() — copy or import
#   - parse_scores() — copy or import
#   - ChunkResult dataclass
#   - QuotaTracker
#   - harvest()

# NEW:
#   - grammar_ranges.json (smaller, targeted ranges)
#   - Exclusion filter (remove existing 64)
#   - prompts/grammar/ directory
#   - Output to data/grammar_round_1.jsonl

# SIMPLIFIED main():
#   1. Load grammar ranges
#   2. Generate candidate glyphs
#   3. Filter out existing 64 axioms
#   4. Score ONE round
#   5. Harvest top scorers
#   6. Print top 20 for human review
```

### What NOT to change

- Do NOT modify glyph_scorer.py
- Do NOT overwrite anything in data/
- Do NOT modify existing prompts
- Do NOT change config.py
- KEEP the same API calling pattern (2-turn conversation, same model name)
- KEEP the same JSONL output format
- KEEP the same parse_scores logic (m∴c format)

### Running

```
python grammar_scorer.py
```

Same .env file, same API key, same model. Should cost <$0.50 (small candidate pool).

### Success criteria

Output: a ranked list of ~20 candidate glyphs with conditional resonance score ≥ 7.
The human (Charlie) picks the winner. It becomes MT's first grammar particle.

---

## AFTER REVIEW

Once Charlie approves, the winning glyph gets:
1. Added to MOTHER_TONGUE.md as a grammar particle (not a lexicon entry)
2. A grammar rule for its syntax
3. The Darwin crystal re-written with it (validation test)
