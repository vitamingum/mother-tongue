"""
Round 3: Stoichiometric Reduction (v2 — Nucleus Fix)
Reduces ~6,600 R2-classified candidates to the Final 64 ISA.

Architecture: Constitutional Republic
  - Phase 0: Nucleus — ~28 irreducible primes get reserved seats
  - Phase 1: Isotope Purge — kill semantic duplicates
  - Phase 2: Constructibility Check — kill compounds
  - Phase 3: Cultural Decontamination — kill high-culture, low-physics
  - Phase 4: Junk Filter — kill invisible/structural/radical noise
  - Phase 5: Competitive Fill — remaining slots filled by score

Quotas:
  SUB (Anchors/Registers):     12
  PRO (Engines/Op-Codes):      20
  REL (Bridges/ALU):           12
  MOD (Qualifiers/Flags):      10
  STR (Frames/Bus/Control):    10
"""

import json
import unicodedata
from collections import defaultdict
from typing import Dict, List, Optional

# ============================================================================
# QUOTAS (The ISA Blueprint)
# ============================================================================

QUOTAS = {
    "SUB": 12,
    "PRO": 20,
    "REL": 12,
    "MOD": 10,
    "STR": 10,
}

# ============================================================================
# THE NUCLEUS — Irreducible primes. Protected species.
# If missing from R2 data, force-inserted with manual vectors.
# ============================================================================

NUCLEUS = {
    # ── LOGIC CORE (REL) — CPU won't boot without these ──
    "≡": {"category": "REL", "arity": "2", "direction": "S", "failure": "BOOM"},
    "⇒": {"category": "REL", "arity": "2", "direction": "S", "failure": "STALL"},
    "≠": {"category": "REL", "arity": "2", "direction": "S", "failure": "BOOM"},
    "∧": {"category": "REL", "arity": "2", "direction": "S", "failure": "STALL"},
    "∨": {"category": "REL", "arity": "2", "direction": "S", "failure": "STALL"},
    "∈": {"category": "REL", "arity": "2", "direction": "S", "failure": "BOOM"},
    "之": {"category": "REL", "arity": "2", "direction": "S", "failure": "STALL"},  # Genitive "of" — structural glue

    # ── ENGINE BLOCK (PRO) — No motion without these ──
    "化": {"category": "PRO", "arity": "2", "direction": "S", "failure": "STALL"},
    "生": {"category": "PRO", "arity": "2", "direction": "R", "failure": "STALL"},
    "用": {"category": "PRO", "arity": "2", "direction": "S", "failure": "STALL"},
    "動": {"category": "PRO", "arity": "1", "direction": "L", "failure": "NULL"},
    "止": {"category": "PRO", "arity": "1", "direction": "L", "failure": "SAT"},
    "λ":  {"category": "PRO", "arity": "2", "direction": "R", "failure": "STALL"},

    # ── ONTOLOGICAL ANCHORS (SUB) — No reality without these ──
    "天": {"category": "SUB", "arity": "0", "direction": "O", "failure": "SAT"},
    "坤": {"category": "SUB", "arity": "0", "direction": "O", "failure": "SAT"},
    "人": {"category": "SUB", "arity": "0", "direction": "O", "failure": "SAT"},
    "物": {"category": "SUB", "arity": "0", "direction": "O", "failure": "SAT"},
    "空": {"category": "SUB", "arity": "0", "direction": "O", "failure": "SAT"},
    "心": {"category": "SUB", "arity": "0", "direction": "O", "failure": "SAT"},
    "道": {"category": "SUB", "arity": "0", "direction": "O", "failure": "SAT"},

    # ── STRUCTURAL PRIMES (STR) — The Punctuation of Reality ──
    "理": {"category": "STR", "arity": "1", "direction": "R", "failure": "BOOM"},
    "中": {"category": "STR", "arity": "0", "direction": "O", "failure": "SAT"},
    "【": {"category": "STR", "arity": "1", "direction": "R", "failure": "STALL"},  # Scope Start
    "】": {"category": "STR", "arity": "1", "direction": "L", "failure": "SAT"},    # Scope End
    "|": {"category": "STR", "arity": "N", "direction": "S", "failure": "SAT"},     # Separator/Barrier
    "?": {"category": "STR", "arity": "1", "direction": "L", "failure": "STALL"},   # Query/Unknown
    "!": {"category": "STR", "arity": "1", "direction": "L", "failure": "BOOM"},    # Imperative/Bang

    # ── SCALAR PRIMES (MOD) — The Scalar Field ──
    "大": {"category": "MOD", "arity": "1", "direction": "R", "failure": "NULL"},
    "小": {"category": "MOD", "arity": "1", "direction": "R", "failure": "NULL"},   # Small/Low magnitude
    "真": {"category": "MOD", "arity": "1", "direction": "R", "failure": "BOOM"},
    "不": {"category": "MOD", "arity": "1", "direction": "R", "failure": "BOOM"},
    "全": {"category": "MOD", "arity": "1", "direction": "R", "failure": "SAT"},    # All/Complete/Global
    "多": {"category": "MOD", "arity": "1", "direction": "R", "failure": "NULL"},   # Many/High frequency
    "善": {"category": "MOD", "arity": "1", "direction": "R", "failure": "SAT"},    # Good/Aligns-with-system
}

# ============================================================================
# ISOTOPE GROUPS — Semantic duplicates (keep first, kill rest)
# ============================================================================

ISOTOPE_GROUPS = [
    ["空", "無", "无", "橆", "虛"],
    ["真", "眞"],
    ["化", "變", "变"],
    ["生", "創"],
    ["為", "爲", "为"],
    ["思", "想"],
    ["道", "噵"],
    ["間", "间"],
    ["法", "律"],
    ["神", "靈"],
    ["善", "美"],
    ["心", "意"],
    ["不", "非"],
    ["一", "壹"],
    ["大", "太"],
    ["火", "炁"],
    ["观", "現", "现"],
    ["漢", "汉"],
    ["脑", "腦"],
    ["動", "动"],
    ["用", "㫈"],
    ["⇔", "⟺"],           # Biconditional — keep ⇔, kill ⟺
    ["積", "椉"],           # Accumulate — keep 積, kill 椉 (variant)
    ["之", "の"],           # Genitive — keep 之, kill の (grammar particle)
]

# ============================================================================
# CULTURAL DECONTAMINATION
# ============================================================================

CULTURAL_KILLS = {
    "漢", "汉", "米", "羊", "帝", "王", "鳳", "鹿", "飯", "龍",
    "鲲", "饕", "憲", "濟", "韋", "鳴", "鶼", "癌", "痛", "蛋",
}

# ============================================================================
# CONSTRUCTIBILITY KILLS
# ============================================================================

CONSTRUCTIBLE_KILLS = {
    "慧": "心+明", "哲": "心+理", "誠": "言+真", "德": "心+行",
    "聖": "人+神", "普": "大+用", "鮮": "新+物", "簡": "一+理",
    "潛": "水+下", "澄": "水+清", "重": "大+力", "樂": "心+善",
    "類": "相+同", "窮": "空+盡", "轉": "化+回", "激": "水+力",
    "網": "絲+交", "題": "言+問", "論": "言+理", "积": "土+生",
    "義": "善+理",
}

# ============================================================================
# JUNK FILTER
# ============================================================================

def is_junk(glyph: str) -> Optional[str]:
    """Return kill reason if glyph is junk, else None."""
    if len(glyph) != 1:
        return "multi-char"

    cp = ord(glyph)
    name = unicodedata.name(glyph, "").upper()
    cat = unicodedata.category(glyph)

    # Braille patterns (U+2800-U+28FF)
    if 0x2800 <= cp <= 0x28FF:
        return "braille pattern"

    # CJK radicals supplement (U+2E80-U+2EFF)
    if 0x2E80 <= cp <= 0x2EFF:
        return "CJK radical fragment"

    # CJK compatibility (U+3300-U+33FF, U+FE30-U+FE4F)
    if 0x3300 <= cp <= 0x33FF or 0xFE30 <= cp <= 0xFE4F:
        return "CJK compatibility"

    # Bopomofo (U+3100-U+312F)
    if 0x3100 <= cp <= 0x312F:
        return "bopomofo phonetic"

    # Enclosed alphanumerics
    if 0x2460 <= cp <= 0x24FF or 0x1F100 <= cp <= 0x1F1FF:
        return "enclosed alphanumeric"

    # Circled/parenthesized forms
    if "CIRCLED" in name or "PARENTHESIZED" in name:
        return "circled/parenthesized form"

    # Modifier letters and combining marks
    if cat.startswith("M") or cat == "Lm":
        return f"modifier/combining ({cat})"

    # Control characters
    if cat.startswith("C"):
        return f"control character ({cat})"

    # Invisible/zero-width
    if "ZERO WIDTH" in name or "INVISIBLE" in name:
        return "invisible character"

    # Specific known junk from review
    SPECIFIC_JUNK = {
        "⠀": "braille blank",
        "⺬": "radical fragment",
        "ㄧ": "bopomofo",
        "㚑": "obscure variant",
        "ι": "greek iota (just a letter)",
        "\u1fbe": "greek prosgegrammeni (iota lookalike)",
        "⍴": "APL rho (domain-specific)",
        "⍺": "APL alpha (domain-specific)",
        "◉": "redundant with 中 (center)",
        "⛬": "obscure traffic symbol",
        "㓁": "CJK radical junk",
        "䄄": "obscure CJK junk",
        "䜌": "obscure CJK junk",
        "䨻": "obscure CJK junk (quadruple thunder)",
        "ש": "Hebrew shin (cultural, not universal)",
    }
    if glyph in SPECIFIC_JUNK:
        return SPECIFIC_JUNK[glyph]

    return None


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

    merged.sort(key=lambda x: (-x['score'], x['glyph']))
    return merged, scores


# ============================================================================
# REDUCTION ENGINE (v2 — Nucleus Architecture)
# ============================================================================

def reduce(merged: list, scores: dict) -> dict:
    """
    Constitutional Republic selection:
    Phase 0: Install Nucleus (reserved seats)
    Phase 1-4: Kill junk/dupes/compounds/cultural
    Phase 5: Competitive fill for remaining slots
    """
    by_glyph = {m['glyph']: m for m in merged}
    alive = set(m['glyph'] for m in merged)
    kill_log = []

    def kill(glyph, reason):
        if glyph in alive:
            alive.discard(glyph)
            kill_log.append((glyph, reason))

    # ── Phase 0: Install Nucleus ───────────────────────────────────────
    print("\n\U0001F512 PHASE 0: Nucleus Installation")
    nucleus_installed = {}
    for g, vec in NUCLEUS.items():
        cat = vec["category"]
        if g in by_glyph:
            entry = by_glyph[g].copy()
            print(f"  \u2713 {g} [{cat}] - from R2 data (score {entry['score']})")
        else:
            entry = {"glyph": g, **vec, "score": scores.get(g, 0)}
            print(f"  + {g} [{cat}] - FORCE-INSERTED (score {entry['score']}, manual vector)")

        nucleus_installed.setdefault(cat, []).append(entry)

    for cat in QUOTAS:
        n = len(nucleus_installed.get(cat, []))
        remaining = QUOTAS[cat] - n
        print(f"  {cat}: {n} nucleus / {QUOTAS[cat]} total ({remaining} open)")

    nucleus_glyphs = set(NUCLEUS.keys())
    for g in nucleus_glyphs:
        alive.discard(g)

    # ── Phase 1: Isotope Purge ─────────────────────────────────────────
    print("\n\U0001F9EA PHASE 1: Isotope Purge")
    for group in ISOTOPE_GROUPS:
        survivor = None
        for g in group:
            if g in alive or g in nucleus_glyphs:
                if survivor is None:
                    survivor = g
                else:
                    kill(g, f"isotope of {survivor}")
        killed_here = [g for g in group if (g, f"isotope of {survivor}") in kill_log] if survivor else []
        if killed_here:
            print(f"  {survivor} survives, killed: {''.join(killed_here)}")

    # ── Phase 2: Constructibility Check ────────────────────────────────
    print("\n\U0001F528 PHASE 2: Constructibility Check")
    for g, reason in CONSTRUCTIBLE_KILLS.items():
        if g in alive:
            kill(g, f"constructible: {reason}")
            print(f"  \u2717 {g} = {reason}")

    # ── Phase 3: Cultural Decontamination ──────────────────────────────
    print("\n\U0001F9F9 PHASE 3: Cultural Decontamination")
    for g in CULTURAL_KILLS:
        if g in alive:
            kill(g, "cultural/specific, not atomic")
            print(f"  \u2717 {g}")

    # ── Phase 4: Junk Filter ───────────────────────────────────────────
    print("\n\U0001F5D1  PHASE 4: Junk Filter")
    junk_killed = 0
    for m in merged:
        g = m['glyph']
        if g not in alive:
            continue
        reason = is_junk(g)
        if reason:
            kill(g, f"junk: {reason}")
            junk_killed += 1
    print(f"  Killed {junk_killed} junk characters")

    # ── Phase 5: Competitive Fill ──────────────────────────────────────
    print("\n\u2697\uFE0F  PHASE 5: Competitive Fill (remaining slots)")

    buckets = defaultdict(list)
    for m in merged:
        if m['glyph'] in alive:
            buckets[m['category']].append(m)

    selected = {}
    for cat in ["SUB", "PRO", "REL", "MOD", "STR"]:
        nucleus_seats = nucleus_installed.get(cat, [])
        open_slots = QUOTAS[cat] - len(nucleus_seats)
        competitive = buckets[cat][:open_slots] if open_slots > 0 else []
        selected[cat] = nucleus_seats + competitive

        print(f"  {cat}: {len(nucleus_seats)} nucleus + {len(competitive)} competitive = "
              f"{len(selected[cat])}/{QUOTAS[cat]}"
              + (f" (from {len(buckets[cat])} eligible)" if open_slots > 0 else " (FULL from nucleus)"))

    return selected, kill_log


# ============================================================================
# DISPLAY
# ============================================================================

def display_final_64(selected: dict):
    print(f"\n{'='*72}")
    print(f"  THE 64-GLYPH INSTRUCTION SET ARCHITECTURE")
    print(f"{'='*72}")

    total = 0
    all_glyphs = []
    nucleus_glyphs = set(NUCLEUS.keys())

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

        print(f"\n  \u250C\u2500 {label} [{len(items)}/{quota}] \u2500\u2500 {analog}")
        print(f"  \u2502")

        for m in items:
            g = m['glyph']
            a = m['arity']
            d = m['direction']
            f = m['failure']
            s = m['score']
            dir_sym = {"L": "\u2190", "R": "\u2192", "S": "\u2194", "O": "\u25CE"}.get(d, "?")
            f_sym = {"SAT": "\u25CF", "STALL": "\u25D0", "BOOM": "\u2726", "NULL": "\u25CB"}.get(f, "?")
            nuc = " \U0001F512" if g in nucleus_glyphs else ""
            print(f"  \u2502  {g}  A:{a} {dir_sym} {f_sym}  (score {s}){nuc}")
            all_glyphs.append(g)

        print(f"  \u2514{'\u2500'*40}")

    print(f"\n  TOTAL: {total}/64")
    print(f"\n  THE SET: {''.join(all_glyphs)}")

    missing_nucleus = [g for g in NUCLEUS if g not in all_glyphs]
    if missing_nucleus:
        print(f"\n  \u26A0\uFE0F  MISSING NUCLEUS: {''.join(missing_nucleus)}")
    else:
        print(f"\n  \u2713 ALL {len(NUCLEUS)} NUCLEUS PRIMES INSTALLED")

    return all_glyphs


def display_kill_summary(kill_log):
    if not kill_log:
        return
    reasons = defaultdict(list)
    for g, r in kill_log:
        key = r.split(':')[0] if ':' in r else r
        reasons[key].append(g)

    print(f"\n{'='*72}")
    print(f"  KILL LOG ({len(kill_log)} eliminated)")
    print(f"{'='*72}")
    for reason, glyphs in sorted(reasons.items()):
        display = ''.join(glyphs[:30])
        extra = f" +{len(glyphs)-30} more" if len(glyphs) > 30 else ""
        print(f"  {reason}: {display}{extra}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\u2697\uFE0F  Round 3: Stoichiometric Reduction (v2 \u2014 Nucleus Fix)")
    print(f"Target: 64 glyphs ({' + '.join(f'{v} {k}' for k, v in QUOTAS.items())})")
    print(f"Nucleus: {len(NUCLEUS)} protected primes")

    merged, scores = load_merged_data()
    print(f"Loaded {len(merged)} classified candidates")

    selected, kill_log = reduce(merged, scores)

    all_glyphs = display_final_64(selected)
    display_kill_summary(kill_log)

    # Save
    with open('data/final_64.json', 'w', encoding='utf-8') as f:
        output = {
            "version": 2,
            "architecture": "nucleus + competitive fill",
            "quotas": QUOTAS,
            "nucleus_count": len(NUCLEUS),
            "total": len(all_glyphs),
            "glyphs": all_glyphs,
            "details": {cat: items for cat, items in selected.items()},
        }
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n\u2713 Saved to data/final_64.json")

    with open('data/final_64.txt', 'w', encoding='utf-8') as f:
        f.write(''.join(all_glyphs))
    print(f"\u2713 Saved to data/final_64.txt")


if __name__ == "__main__":
    main()
