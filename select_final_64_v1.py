"""
Round 3: Stoichiometric Reduction
Reduces ~6,600 R2-classified candidates to the Final 64 ISA.

Quotas:
  SUB (Anchors/Registers):     12
  PRO (Engines/Op-Codes):      20
  REL (Bridges/ALU):           12
  MOD (Qualifiers/Flags):      10
  STR (Frames/Bus/Control):    10

Reduction steps:
  1. Isotope Purge — kill semantic duplicates
  2. Constructibility Check — kill compounds
  3. Cultural Decontamination — kill high-culture, low-physics
  4. Stoichiometric Fill — top-N by score per category
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional

# ============================================================================
# QUOTAS (The ISA Blueprint)
# ============================================================================

QUOTAS = {
    "SUB": 12,  # Registers — ontological anchors
    "PRO": 20,  # Op-Codes — transformation engines
    "REL": 12,  # ALU — logic connectives
    "MOD": 10,  # Flags — quality scalars
    "STR": 10,  # Bus/Control — spatial frames
}

# ============================================================================
# ISOTOPE GROUPS — Semantic duplicates (keep first, kill rest)
# ============================================================================

# Format: list of sets. Within each set, first element is the survivor.
# Sorted by: simplicity (stroke count), universality, Unicode stability.
ISOTOPE_GROUPS = [
    # Void/Nothing/Emptiness
    ["空", "無", "无", "橆", "虛"],
    # Truth
    ["真", "眞"],
    # Transform/Change
    ["化", "變", "变"],
    # Create/Generate
    ["生", "創"],
    # Do/Act/Make
    ["為", "爲", "为"],
    # Think/Thought
    ["思", "想"],
    # Way/Path/Principle
    ["道", "噵"],
    # Between/Inter
    ["間", "间"],
    # Law/Pattern
    ["法", "律"],
    # Spirit/Divine
    ["神", "靈"],
    # Beauty/Good
    ["善", "美"],
    # Heart/Mind
    ["心", "意"],
    # Not/Negation
    ["不", "非"],
    # One/Unity
    ["一", "壹"],
    # Great/Large
    ["大", "太"],
    # Fire
    ["火", "炁"],
    # Observe/See
    ["观", "現", "现"],
    # Han/Chinese (cultural, but track for decontam)
    ["漢", "汉"],
    # Brain
    ["脑", "腦"],
]

# ============================================================================
# CULTURAL DECONTAMINATION — High culture, low physics utility
# ============================================================================

CULTURAL_KILLS = {
    "漢", "汉",     # "Han Chinese" — ethnic, not universal
    "米",           # "Rice" — agricultural, not atomic
    "羊",           # "Sheep" — livestock, not primitive
    "帝",           # "Emperor" — political hierarchy
    "王",           # "King" — political hierarchy
    "鳳",           # "Phoenix" — mythological
    "鹿",           # "Deer" — animal, not primitive
    "飯",           # "Rice/meal" — food
    "龍",           # "Dragon" — mythological
    "鲲",           # "Kun fish" — mythological
    "饕",           # "Taotie" — mythological glutton
    "憲",           # "Constitution" — legal document
    "濟",           # "Aid/Ford" — too specific
    "韋",           # Surname-heavy
    "鳴",           # "Cry of bird" — too specific
    "鶼",           # "Lovebirds" — too specific
    "癌",           # "Cancer" — medical, not ontological
    "痛",           # "Pain" — sensation, constructible from body+damage
    "蛋",           # "Egg" — too specific
}

# ============================================================================
# CONSTRUCTIBILITY KILLS — Compounds expressible from primes
# ============================================================================

# These can be built from simpler atoms in the final language
CONSTRUCTIBLE_KILLS = {
    "慧": "心+明 (wisdom = mind + clarity)",
    "哲": "心+理 (philosophy = mind + principle)",
    "誠": "言+真 (sincerity = speech + truth)",
    "德": "心+行 (virtue = mind + action)",
    "聖": "人+神 (holy = person + divine)",
    "普": "大+用 (universal = great + use)",
    "鮮": "新+物 (fresh = new + matter)",
    "簡": "一+理 (simple = one + principle)",
    "潛": "水+下 (latent = water + below)",
    "澄": "水+清 (clear = water + pure)",
    "重": "大+力 (heavy = great + force)",
    "樂": "心+善 (joy = mind + good)",
    "類": "相+同 (classify = mutual + same)",
    "窮": "空+盡 (exhaust = void + end)",
    "轉": "化+回 (rotate = transform + return)",
    "激": "水+力 (excite = water + force)",
    "網": "絲+交 (net = thread + cross)",
    "題": "言+問 (topic = speech + question)",
    "論": "言+理 (theory = speech + principle)",
    "积": "土+生 (accumulate = earth + grow)",
    "義": "善+理 (justice = good + principle)",
}


# ============================================================================
# LOAD DATA
# ============================================================================

def load_merged_data():
    """Load R1 scores + R2 assay, merge, return sorted list."""
    scores = {}
    with open('data/round_1.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            chunk = json.loads(line)
            for g, s in chunk['scores'].items():
                scores[g] = s

    assay = {}
    with open('data/round_2_assay.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            chunk = json.loads(line)
            for a in chunk['assays']:
                assay[a['glyph']] = a

    merged = []
    for g, a in assay.items():
        if g in scores:
            merged.append({**a, 'score': scores[g]})

    # Sort by score descending, then by glyph for stability
    merged.sort(key=lambda x: (-x['score'], x['glyph']))
    return merged


# ============================================================================
# REDUCTION ENGINE
# ============================================================================

def reduce(merged: list) -> dict:
    """
    Execute the 4-step reduction algorithm.
    Returns dict of category -> list of selected glyphs.
    """

    # Build lookup
    by_glyph = {m['glyph']: m for m in merged}
    alive = set(m['glyph'] for m in merged)
    kill_log = []

    def kill(glyph, reason):
        if glyph in alive:
            alive.discard(glyph)
            kill_log.append((glyph, reason))

    # ── Step 1: Isotope Purge ──────────────────────────────────────────
    print("\n🧪 STEP 1: Isotope Purge")
    for group in ISOTOPE_GROUPS:
        # Keep first that's alive, kill rest
        survivor = None
        for g in group:
            if g in alive:
                if survivor is None:
                    survivor = g
                else:
                    kill(g, f"isotope of {survivor}")
        if survivor:
            killed = [g for g in group[1:] if g != survivor and (g, f"isotope of {survivor}") in kill_log]
            if killed:
                print(f"  {survivor} survives, killed: {''.join(killed)}")

    # ── Step 2: Constructibility Check ─────────────────────────────────
    print("\n🔨 STEP 2: Constructibility Check")
    for g, reason in CONSTRUCTIBLE_KILLS.items():
        if g in alive:
            kill(g, f"constructible: {reason}")
            print(f"  ✗ {g} = {reason}")

    # ── Step 3: Cultural Decontamination ───────────────────────────────
    print("\n🧹 STEP 3: Cultural Decontamination")
    for g in CULTURAL_KILLS:
        if g in alive:
            kill(g, "cultural/specific, not atomic")
            print(f"  ✗ {g}")

    # ── Step 4: Stoichiometric Fill ────────────────────────────────────
    print("\n⚗️  STEP 4: Stoichiometric Fill")

    # Bucket survivors by category, score-ordered
    buckets = defaultdict(list)
    for m in merged:
        if m['glyph'] in alive:
            buckets[m['category']].append(m)

    selected = {}
    for cat in ["SUB", "PRO", "REL", "MOD", "STR"]:
        quota = QUOTAS[cat]
        candidates = buckets[cat]
        picked = candidates[:quota]
        selected[cat] = picked
        overflow = len(candidates) - quota
        print(f"  {cat}: {len(candidates)} candidates -> picked {len(picked)}/{quota}" +
              (f" (dropped {overflow})" if overflow > 0 else f" (UNDERFILL by {quota - len(picked)})" if len(picked) < quota else ""))

    return selected, kill_log


# ============================================================================
# DISPLAY
# ============================================================================

def display_final_64(selected: dict):
    """Pretty-print the final 64."""
    print(f"\n{'='*72}")
    print(f"  THE 64-GLYPH INSTRUCTION SET ARCHITECTURE")
    print(f"{'='*72}")

    total = 0
    all_glyphs = []

    for cat, label, analog in [
        ("SUB", "SUBSTANCE (Anchors)", "Registers"),
        ("PRO", "PROCESS (Engines)", "Op-Codes"),
        ("REL", "RELATION (Bridges)", "ALU"),
        ("MOD", "MODIFIER (Qualifiers)", "Flags"),
        ("STR", "STRUCTURE (Frames)", "Bus/Control"),
    ]:
        items = selected[cat]
        total += len(items)
        quota = QUOTAS[cat]

        print(f"\n  ┌─ {label} [{len(items)}/{quota}] ── {analog}")
        print(f"  │")

        for m in items:
            g = m['glyph']
            a = m['arity']
            d = m['direction']
            f = m['failure']
            s = m['score']
            # Direction symbol
            dir_sym = {"L": "←", "R": "→", "S": "↔", "O": "◎"}.get(d, "?")
            # Failure symbol
            f_sym = {"SAT": "●", "STALL": "◐", "BOOM": "✦", "NULL": "○"}.get(f, "?")
            print(f"  │  {g}  A:{a} {dir_sym} {f_sym}  (score {s})")
            all_glyphs.append(g)

        print(f"  └{'─'*40}")

    print(f"\n  TOTAL: {total}/64")
    print(f"\n  THE SET: {''.join(all_glyphs)}")

    return all_glyphs


def display_kill_summary(kill_log):
    """Show what was killed and why."""
    if not kill_log:
        return
    reasons = defaultdict(list)
    for g, r in kill_log:
        reasons[r.split(':')[0] if ':' in r else r].append(g)

    print(f"\n{'='*72}")
    print(f"  KILL LOG ({len(kill_log)} eliminated)")
    print(f"{'='*72}")
    for reason, glyphs in sorted(reasons.items()):
        print(f"  {reason}: {''.join(glyphs[:20])}" +
              (f" +{len(glyphs)-20} more" if len(glyphs) > 20 else ""))


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("⚗️  Round 3: Stoichiometric Reduction")
    print(f"Target: 64 glyphs ({' + '.join(f'{v} {k}' for k, v in QUOTAS.items())})")

    # Load
    merged = load_merged_data()
    print(f"Loaded {len(merged)} classified candidates")

    # Reduce
    selected, kill_log = reduce(merged)

    # Display
    all_glyphs = display_final_64(selected)
    display_kill_summary(kill_log)

    # Save
    with open('data/final_64.json', 'w', encoding='utf-8') as f:
        output = {
            "quotas": QUOTAS,
            "total": len(all_glyphs),
            "glyphs": all_glyphs,
            "details": {cat: items for cat, items in selected.items()},
        }
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Saved to data/final_64.json")

    with open('data/final_64.txt', 'w', encoding='utf-8') as f:
        f.write(''.join(all_glyphs))
    print(f"✓ Saved to data/final_64.txt")


if __name__ == "__main__":
    main()
