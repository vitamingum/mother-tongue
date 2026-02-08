# GLYPH_MINER_512 v0.3.1

Deterministic multi-stage glyph mining using LLM preference signals via Ollama.

## Overview

GLYPH_MINER_512 implements a rigorous three-stage pipeline that distills ~90,000 filtered Unicode codepoints down to exactly 512 glyphs based on model co-selection patterns. The system is fully deterministic: given the same seed and model, outputs are reproducible.

## Architecture

```
Unicode Filter → Stage A → Stage B → Stage C → Final 512
  (~90K)         (10K)      (2K)      (512)
```

### Stages

- **Stage A**: 5 passes × 12000 rounds, K=64 slate size → 10,000 glyphs
- **Stage B**: 4 passes × 3000 rounds, K=64 slate size → 2,000 glyphs  
- **Stage C**: 4 passes × 5000 rounds, K=16 slate size → 512 glyphs

Each pass:
1. Shuffle pool with deterministic seed (seed + pass×φ)
2. Run rounds: create slate (cycling through pool) → infer → parse → update Σ state
3. Aggregate statistics across passes
4. Prune pool with union margin for fairness
5. Check stability (Stage C only)

### Σ (State)

Persistent state tracked across all rounds and passes:

- `pool` - current codepoint pool
- `seen` - per-glyph slate appearance counts
- `picked` - per-glyph model selection counts
- `score` - pick rate (picked/seen) for each glyph
- `edges` - all co-occurrence pairs (g1, g2)
- `byte_len` - UTF-8 byte length (tokenizer proxy)

## Requirements

- Python 3.8+
- Ollama installed and running
- Model pulled in Ollama (e.g., `ollama pull llama2`)

## Installation

```bash
cd glyph_miner
# No pip dependencies required (uses stdlib only)
```

## Usage

```bash
# Basic usage
python miner.py MODEL_NAME

# With custom seed and output directory
python miner.py llama2 --seed 42 --output results/

# Examples
python miner.py mistral
python miner.py llama2:13b --seed 12345
```

## Outputs

All outputs written to `output/` (or `--output` directory):

- `final_512.txt` - One glyph per line
- `final_512.json` - Structured data with scores
- `edges.csv` - All co-occurrence pairs
- `stability.json` - Convergence metrics
- `log.jsonl` - Per-pass execution log

## Guarantees

### Determinism

Given the same seed and model, outputs are **identical**:

```bash
python miner.py llama2 --seed 42
# Produces final_512.json

python miner.py llama2 --seed 42
# Produces identical final_512.json
```

### Assertions

Runtime asserts enforce:

- ✓ Model output = exactly 2 glyphs ∧ ∈ slate
- ✓ No duplicates in slate
- ✓ |final| = 512
- ✓ unique(final) 
- ✓ final ⊂ filtered Unicode
- ✓ No unicode names/blocks/metadata reach model

### Fairness

Multi-pass design with independent shuffles and union margins ensures:

- All glyphs in pool receive fair exposure
- min_seen thresholds enforced before pruning
- Aggregation across passes reduces sampling bias

### Stability

Stage C monitors Jaccard similarity between consecutive passes:

- Threshold: ≥0.98
- Required: 2 consecutive passes
- Early termination when converged

## Components

### `unicode.py`

Filters Unicode scalar values, excluding:
- Surrogates, control chars, format chars
- Marks (nonspacing, spacing, enclosing)
- Spaces, Private Use Area, Variation Selectors
- Unassigned codepoints

NO unicode names or block metadata - just codepoints.

### `sampler.py`

- `shuffle_pool(pool, seed, pass)` - Deterministic shuffling
- `create_slate(pool, k, round_num)` - Extract K glyphs cycling through pool (asserts no dupes)
- `format_slate(slate)` - Convert to character string

### `runner_ollama.py`
that most strongly suggest a specific action or logical operation
- Prompt: "Pick exactly two characters from this set. Output nothing else."
- Sampling: T={0.8→0.6→0.4}, p=0.95, k=50, rp=1.05, n=8
- Parsing: Extract exactly 2 glyphs ∈ slate

### `scorer.py`

Tracks Σ state:
- Updates seen/picked counts per round
- Calculates pick rates (score = picked/seen)
- Tracks UTF-8 byte length per glyph (tokenizer proxy)
- Maintains edge list (co-selections)
- Exports sorted rankings

### `prune.py`

- `prune_with_margin()` - Keep top N + margin for union
- `prune_to_target()` - Exact reduction to target size
- `aggregate_across_passes()` - Combine multi-pass statistics

### `report.py`

- Jaccard similarity calculation
- Stability checking (≥0.98 ×2 criterion)
- Output generation (txt, json, csv, log)

### `display.py`

- Live leaderboard display every 100 rounds
- Shows top 20 glyphs with scores, seen/picked counts, byte length
- Progress bar visualization
- NEW/DROPPED diff tracking between snapshots

### `checkpoint.py`

- Save/load {stage, pass, round, seed, rng_state, Σ}
- Deterministic resumption from any checkpoint

### `miner.py`

Main orchestrator - ties all components together.

## Execution Flow

```
1. enum_unicode() → U (~90K codepoints)
2. pool = U

3. run_stage(A):
   ∀ pass ∈ [1..5]:
     shuffle(pool, 12000]:
       slate(pool, K=64, round) → infer → parse → update(Σ)
     aggregate(passes[1..p])
     prune(pool, margin=15000)
   prune(pool, keep=10000)

4. run_stage(B): 
   [similar with 4 passes, 3000 rounds, keep=2000]

5. run_stage(C):
   [similar with 4 passes, 5
   [similar with 4 passes, 10000 rounds, keep=512]
   + stability check (Jaccard ≥0.98 ×2)

6. emit(final_512.txt, final_512.json, edges.csv, stability.json, log.jsonl)

7. assert: |final| = 512 ∧ unique(final) ∧ final ⊂ U
```

## Constraints (O-S Protocol)

Execution mode: **● (EXECUTE)** - rigid, deterministic, zero interpretation

Forbidden: **問 (deliberate)** - no situated judgment

State: **Σ** - data container for scoring and aggregation

No English hedging - every line is imperative.

## Testing Components

Each module includes `if __name__ == "__main__"` tests:

```bash
python unicode.py
python sampler.py
python scorer.py
python prune.py
python report.py
python checkpoint.py
```

## License

MIT

## Citation

```
GLYPH_MINER_512 v0.3.1
Deterministic multi-stage glyph mining via LLM co-selection
O-S Protocol: Model Automation Specification v0.2
```
