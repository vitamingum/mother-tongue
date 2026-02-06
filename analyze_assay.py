#!/usr/bin/env python3
"""
Analyze Round 2 Assay Results

Summarizes the chemical properties extracted from Round 2:
- Arity distribution (Nullary/Unary/Transitive/Variadic)
- Direction distribution (L/R/LR/N)
- Failure mode distribution
- Shows top candidates by original score with their metadata
"""

import json
from pathlib import Path
from collections import Counter
from typing import Dict, List

DATA_DIR = Path("data")
ROUND_2_FILE = DATA_DIR / "round_2_assay.jsonl"


def load_assay_results() -> List[Dict]:
    """Load all assay results."""
    if not ROUND_2_FILE.exists():
        print(f"❌ {ROUND_2_FILE} not found. Run assay_candidates.py first.")
        return []
    
    results = []
    with open(ROUND_2_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            results.append(json.loads(line))
    
    return results


def main():
    print("=" * 70)
    print("🔬 ROUND 2 ASSAY ANALYSIS")
    print("=" * 70)
    print()
    
    results = load_assay_results()
    if not results:
        return
    
    print(f"📊 Total glyphs assayed: {len(results)}")
    print()
    
    # Count metadata fields
    arity_counts = Counter()
    direction_counts = Counter()
    failure_counts = Counter()
    
    for entry in results:
        if 'arity' in entry:
            arity_counts[entry['arity']] += 1
        if 'direction' in entry:
            direction_counts[entry['direction']] += 1
        if 'failure' in entry:
            failure_counts[entry['failure']] += 1
    
    # Display distributions
    print("=" * 70)
    print("⚛️  ARITY DISTRIBUTION (Argument Count)")
    print("=" * 70)
    for arity, count in arity_counts.most_common():
        pct = (count / len(results)) * 100
        bar = "█" * int(pct / 2)
        print(f"{arity:12s}: {count:4d} ({pct:5.1f}%) {bar}")
    print()
    
    print("=" * 70)
    print("🧭 DIRECTION DISTRIBUTION (Hunger Direction)")
    print("=" * 70)
    for direction, count in direction_counts.most_common():
        pct = (count / len(results)) * 100
        bar = "█" * int(pct / 2)
        print(f"{direction:12s}: {count:4d} ({pct:5.1f}%) {bar}")
    print()
    
    print("=" * 70)
    print("💥 FAILURE MODE DISTRIBUTION")
    print("=" * 70)
    for failure, count in failure_counts.most_common():
        pct = (count / len(results)) * 100
        bar = "█" * int(pct / 2)
        print(f"{failure:12s}: {count:4d} ({pct:5.1f}%) {bar}")
    print()
    
    # Show top 32 by original score with metadata
    print("=" * 70)
    print("🏆 TOP 32 CANDIDATES (with Chemical Properties)")
    print("=" * 70)
    
    sorted_results = sorted(results, key=lambda x: x.get('round_1_magnitude', 0), reverse=True)
    
    for i, entry in enumerate(sorted_results[:32], 1):
        glyph = entry.get('glyph', '?')
        score = entry.get('round_1_magnitude', 0)
        arity = entry.get('arity', 'UNKNOWN')
        direction = entry.get('direction', '?')
        failure = entry.get('failure', '?')
        
        print(f"#{i:2d}  {glyph}  Score:{score:4.1f}  "
              f"Arity:{arity:11s}  Dir:{direction:2s}  Fail:{failure:10s}")
    
    print()
    
    # Validation checks
    print("=" * 70)
    print("🔍 VALIDATION TARGETS")
    print("=" * 70)
    
    target_glyphs = ['化', '生', '用', '間', '■', '○', '中', '因']
    for target in target_glyphs:
        for entry in results:
            if entry.get('glyph') == target:
                print(f"{target}  Arity:{entry.get('arity', '?'):11s}  "
                      f"Dir:{entry.get('direction', '?'):2s}  "
                      f"Fail:{entry.get('failure', '?'):10s}  "
                      f"Score:{entry.get('round_1_magnitude', 0):.1f}")
                break
    
    print()
    print("✅ Expected:")
    print("   化 (Transform): Transitive | R | Saturate")
    print("   ■ (Square):     Nullary | N | Inert")
    print("   中 (Center):     Nullary or Unary | N or LR | ?")
    print()


if __name__ == "__main__":
    main()
