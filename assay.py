"""
Assay — Round 2 Valence Extraction Pipeline
Takes R1 harvest (~6,600 glyphs ≥ 7) and classifies each into a 4D vector:
  Category (SUB/PRO/REL/MOD/STR)
  Arity (0/1/2/N)
  Direction (L/R/S/O)
  Failure (SAT/STALL/BOOM/NULL)

Output: data/round_2_assay.jsonl (one JSON object per chunk)
"""

import os
import sys
import json
import re
import time
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple
import google.generativeai as genai
from tqdm import tqdm

from config import API_KEY

# ============================================================================
# CONFIGURATION
# ============================================================================

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-3-flash-preview"
CHUNK_SIZE = 64
PAID_TIER_SLEEP = 0.1
FREE_TIER_SLEEP = 4
USE_PAID_TIER = os.getenv("GEMINI_PAID_TIER", "true").lower() == "true"
SLEEP_BETWEEN_REQUESTS = PAID_TIER_SLEEP if USE_PAID_TIER else FREE_TIER_SLEEP

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
TEST_GLYPHS_LIMIT = 128

PROMPT_DIR = Path("prompts/round2")
R1_HARVEST_FILE = "data/round_1_harvested.txt"
OUTPUT_FILE = "data/round_2_assay.jsonl"

# Valid values for each dimension
VALID_CATEGORIES = {"SUB", "PRO", "REL", "MOD", "STR"}
VALID_ARITIES = {"0", "1", "2", "N"}
VALID_DIRECTIONS = {"L", "R", "S", "O"}
VALID_FAILURES = {"SAT", "STALL", "BOOM", "NULL"}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class GlyphAssay:
    """Classification vector for a single glyph."""
    glyph: str
    category: str   # SUB | PRO | REL | MOD | STR
    arity: str      # 0 | 1 | 2 | N
    direction: str  # L | R | S | O
    failure: str    # SAT | STALL | BOOM | NULL


@dataclass
class AssayChunkResult:
    """Result from assaying one chunk of glyphs."""
    chunk_id: int
    glyphs: List[str]
    assays: List[Dict]         # List of GlyphAssay as dicts
    unparsed: List[str]        # Lines that failed to parse
    response1: str
    response2: str


# ============================================================================
# PROMPT LOADING
# ============================================================================

def load_prompts() -> Tuple[str, str]:
    """Load Round 2 prompts."""
    turn1_file = PROMPT_DIR / "turn1.txt"
    turn2_file = PROMPT_DIR / "turn2.txt"

    if not turn1_file.exists():
        raise FileNotFoundError(f"R2 prompt not found: {turn1_file}")
    if not turn2_file.exists():
        raise FileNotFoundError(f"R2 prompt not found: {turn2_file}")

    with open(turn1_file, 'r', encoding='utf-8') as f:
        turn1 = f.read().strip()
    with open(turn2_file, 'r', encoding='utf-8') as f:
        turn2 = f.read().strip()

    if '{glyphs}' not in turn1:
        raise ValueError(f"{turn1_file} must contain {{glyphs}} placeholder")

    return turn1, turn2


# ============================================================================
# PARSER
# ============================================================================

# Primary pattern:  化 | C:PRO | A:2 | D:R | F:STALL
ASSAY_PATTERN = re.compile(
    r'^(.)\s*\|\s*C:(\w+)\s*\|\s*A:(\w)\s*\|\s*D:(\w)\s*\|\s*F:(\w+)\s*$'
)

# Relaxed pattern: allows missing C:/A:/D:/F: prefixes
# e.g.  化 | PRO | 2 | R | STALL
ASSAY_PATTERN_RELAXED = re.compile(
    r'^(.)\s*\|\s*(\w+)\s*\|\s*(\w)\s*\|\s*(\w)\s*\|\s*(\w+)\s*$'
)


def parse_assay_line(line: str) -> Optional[GlyphAssay]:
    """
    Parse a single assay output line into a GlyphAssay.

    Accepts:
      化 | C:PRO | A:2 | D:R | F:STALL     (strict)
      化 | PRO | 2 | R | STALL               (relaxed)

    Returns None if unparseable or values are invalid.
    """
    line = line.strip()
    if not line:
        return None

    # Try strict pattern first
    m = ASSAY_PATTERN.match(line)
    if not m:
        # Try relaxed pattern
        m = ASSAY_PATTERN_RELAXED.match(line)
    if not m:
        return None

    glyph = m.group(1)
    cat = m.group(2).upper()
    arity = m.group(3).upper()
    direction = m.group(4).upper()
    failure = m.group(5).upper()

    # Validate
    if cat not in VALID_CATEGORIES:
        return None
    if arity not in VALID_ARITIES:
        return None
    if direction not in VALID_DIRECTIONS:
        return None
    if failure not in VALID_FAILURES:
        return None

    return GlyphAssay(
        glyph=glyph,
        category=cat,
        arity=arity,
        direction=direction,
        failure=failure
    )


def parse_assay_response(response: str, expected_glyphs: List[str]) -> Tuple[List[GlyphAssay], List[str]]:
    """
    Parse full assay response. Returns (parsed_assays, unparsed_lines).
    """
    assays = []
    unparsed = []
    seen_glyphs = set()

    for line in response.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        result = parse_assay_line(line)
        if result and result.glyph not in seen_glyphs:
            assays.append(result)
            seen_glyphs.add(result.glyph)
        elif line and not line.startswith('#') and '|' in line:
            # Looks like it tried to be a data line but failed
            unparsed.append(line)

    # Report missing glyphs
    expected_set = set(expected_glyphs)
    parsed_set = seen_glyphs
    missing = expected_set - parsed_set
    extra = parsed_set - expected_set

    if missing and len(missing) <= 5:
        print(f"⚠️  Missing assay for {len(missing)} glyphs: {''.join(list(missing)[:5])}")
    elif missing:
        print(f"⚠️  Missing assay for {len(missing)} glyphs in chunk")
    if extra:
        print(f"⚠️  {len(extra)} unexpected glyphs in response")

    return assays, unparsed


# ============================================================================
# API INTERACTION
# ============================================================================

def assay_chunk(chunk: List[str], chunk_id: int, turn1: str, turn2: str) -> AssayChunkResult:
    """
    Assay a chunk of glyphs using 2-turn conversation.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    chat = model.start_chat()

    glyphs_text = "\n".join(chunk)
    turn1_formatted = turn1.format(glyphs=glyphs_text)

    retry_count = 0
    max_retries = 5

    while retry_count < max_retries:
        try:
            response1 = chat.send_message(turn1_formatted)
            response1_text = response1.text

            time.sleep(SLEEP_BETWEEN_REQUESTS)

            response2 = chat.send_message(turn2)
            response2_text = response2.text

            assays, unparsed = parse_assay_response(response2_text, chunk)

            return AssayChunkResult(
                chunk_id=chunk_id,
                glyphs=chunk,
                assays=[asdict(a) for a in assays],
                unparsed=unparsed,
                response1=response1_text,
                response2=response2_text
            )

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait_time = (2 ** retry_count) * 60
                print(f"⚠️  Rate limit hit on chunk {chunk_id}. Waiting {wait_time}s...")
                time.sleep(wait_time)
                retry_count += 1
            else:
                print(f"❌ Error on chunk {chunk_id}: {e}")
                return AssayChunkResult(
                    chunk_id=chunk_id,
                    glyphs=chunk,
                    assays=[],
                    unparsed=[],
                    response1="",
                    response2=f"ERROR: {e}"
                )

    print(f"❌ Max retries exceeded for chunk {chunk_id}")
    return AssayChunkResult(
        chunk_id=chunk_id,
        glyphs=chunk,
        assays=[],
        unparsed=[],
        response1="",
        response2="ERROR: Max retries exceeded"
    )


# ============================================================================
# HARVEST R1
# ============================================================================

def load_r1_harvest() -> List[str]:
    """Load Round 1 harvested glyphs."""
    # Try harvested file first
    if os.path.exists(R1_HARVEST_FILE):
        with open(R1_HARVEST_FILE, 'r', encoding='utf-8') as f:
            glyphs = list(f.read().strip())
        print(f"✓ Loaded {len(glyphs)} glyphs from {R1_HARVEST_FILE}")
        return glyphs

    # Fall back to re-harvesting from round_1.jsonl
    r1_file = "data/round_1.jsonl"
    if not os.path.exists(r1_file):
        raise FileNotFoundError(
            f"No R1 data found. Run glyph_scorer.py first to complete Round 1."
        )

    print(f"⚠️  {R1_HARVEST_FILE} not found, re-harvesting from {r1_file}...")
    glyphs = []
    with open(r1_file, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line)
            for glyph, score in result['scores'].items():
                if score >= 7:
                    glyphs.append(glyph)

    random.shuffle(glyphs)

    # Save for next time
    with open(R1_HARVEST_FILE, 'w', encoding='utf-8') as f:
        f.write(''.join(glyphs))
    print(f"✓ Harvested and saved {len(glyphs)} glyphs to {R1_HARVEST_FILE}")

    return glyphs


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_assay(glyphs: List[str], turn1: str, turn2: str, resume: bool = True):
    """Run the full assay pipeline."""

    # Check for existing progress
    start_chunk_idx = 0
    if resume and os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            start_chunk_idx = sum(1 for _ in f)
        if start_chunk_idx > 0:
            print(f"🔄 Resuming from chunk {start_chunk_idx}")

    # Chunk glyphs
    chunks = [glyphs[i:i+CHUNK_SIZE] for i in range(0, len(glyphs), CHUNK_SIZE)]
    total_chunks = len(chunks)

    if start_chunk_idx >= total_chunks:
        print(f"✓ Assay already complete ({total_chunks} chunks)")
        return OUTPUT_FILE

    chunks_to_process = chunks[start_chunk_idx:]
    num_requests = len(chunks_to_process) * 2

    # Cost estimate
    cost_est = num_requests * 800 / 1_000_000 * 0.075  # rough input token cost
    cost_est += num_requests * 200 / 1_000_000 * 0.30   # rough output token cost
    time_est_min = num_requests * SLEEP_BETWEEN_REQUESTS / 60

    print(f"\n{'='*60}")
    print(f"ROUND 2: SEMANTIC ASSAY")
    print(f"{'='*60}")
    print(f"Glyphs:     {len(glyphs):,}")
    print(f"Chunks:     {total_chunks} (size={CHUNK_SIZE})")
    print(f"To process: {len(chunks_to_process)} chunks ({num_requests} API calls)")
    print(f"Est. cost:  ${cost_est:.2f}")
    print(f"Est. time:  ~{time_est_min:.1f} min")
    print(f"Output:     {OUTPUT_FILE}")

    # Process
    max_workers = min(10, max(1, len(chunks_to_process) // 10)) if USE_PAID_TIER else 5
    mode = 'a' if start_chunk_idx > 0 else 'w'
    output_handle = open(OUTPUT_FILE, mode, encoding='utf-8')

    total_assayed = 0
    total_unparsed = 0

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    assay_chunk, chunk, start_chunk_idx + idx, turn1, turn2
                ): idx
                for idx, chunk in enumerate(chunks_to_process)
            }

            with tqdm(total=len(chunks_to_process), desc="Assay R2", unit="chunk") as pbar:
                for future in as_completed(futures):
                    chunk_idx = futures[future]
                    try:
                        result = future.result()
                        total_assayed += len(result.assays)
                        total_unparsed += len(result.unparsed)

                        output_handle.write(json.dumps(asdict(result), ensure_ascii=False) + '\n')
                        output_handle.flush()

                        pbar.set_postfix({
                            "parsed": len(result.assays),
                            "miss": len(result.glyphs) - len(result.assays),
                            "chunk": result.chunk_id
                        })
                        pbar.update(1)
                    except Exception as e:
                        pbar.write(f"❌ Chunk {start_chunk_idx + chunk_idx} failed: {e}")
                        pbar.update(1)
    finally:
        output_handle.close()

    # Summary
    parse_rate = total_assayed / len(glyphs) * 100 if glyphs else 0
    print(f"\n{'='*60}")
    print(f"ASSAY COMPLETE")
    print(f"{'='*60}")
    print(f"Glyphs assayed: {total_assayed}/{len(glyphs)} ({parse_rate:.1f}%)")
    if total_unparsed:
        print(f"Unparsed lines: {total_unparsed}")
    print(f"Output: {OUTPUT_FILE}")

    return OUTPUT_FILE


def print_distribution(output_file: str):
    """Print category/arity/direction/failure distributions from assay output."""
    cats = {}
    arities = {}
    dirs = {}
    fails = {}

    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            chunk = json.loads(line)
            for a in chunk['assays']:
                cats[a['category']] = cats.get(a['category'], 0) + 1
                arities[a['arity']] = arities.get(a['arity'], 0) + 1
                dirs[a['direction']] = dirs.get(a['direction'], 0) + 1
                fails[a['failure']] = fails.get(a['failure'], 0) + 1

    total = sum(cats.values())
    print(f"\n📊 Assay Distribution ({total} glyphs)")

    print(f"\n  Category (stoichiometric balance):")
    for k in ["SUB", "PRO", "REL", "MOD", "STR"]:
        n = cats.get(k, 0)
        pct = n / total * 100 if total else 0
        bar = "█" * int(pct / 2)
        print(f"    {k}: {n:5d} ({pct:5.1f}%) {bar}")

    print(f"\n  Arity (valence shell):")
    for k in ["0", "1", "2", "N"]:
        n = arities.get(k, 0)
        pct = n / total * 100 if total else 0
        bar = "█" * int(pct / 2)
        print(f"    {k}: {n:5d} ({pct:5.1f}%) {bar}")

    print(f"\n  Direction (port geometry):")
    for k in ["L", "R", "S", "O"]:
        n = dirs.get(k, 0)
        pct = n / total * 100 if total else 0
        bar = "█" * int(pct / 2)
        print(f"    {k}: {n:5d} ({pct:5.1f}%) {bar}")

    print(f"\n  Failure mode:")
    for k in ["SAT", "STALL", "BOOM", "NULL"]:
        n = fails.get(k, 0)
        pct = n / total * 100 if total else 0
        bar = "█" * int(pct / 2)
        print(f"    {k}: {n:5d} ({pct:5.1f}%) {bar}")


def main():
    print("⚗️  Round 2: Semantic Assay — Valence Extraction")
    print(f"Model: {MODEL_NAME}")
    print(f"Tier: {'PAID 💳' if USE_PAID_TIER else 'FREE 🆓'}")

    # Load prompts
    print(f"\n📝 Loading R2 prompts from {PROMPT_DIR}...")
    turn1, turn2 = load_prompts()
    print("✓ Prompts loaded")

    # Load R1 harvest
    print(f"\n🌾 Loading R1 harvest...")
    glyphs = load_r1_harvest()

    if TEST_MODE:
        glyphs = glyphs[:TEST_GLYPHS_LIMIT]
        print(f"🧪 TEST MODE: Limited to {len(glyphs)} glyphs")

    # Run assay
    output_file = run_assay(glyphs, turn1, turn2)

    # Print distribution
    print_distribution(output_file)


if __name__ == "__main__":
    main()
