"""
Grammar Particle Scorer — mines Unicode for grammar particles.
First target: CONDITIONAL (irrealis mood marker).
Reuses infrastructure from glyph_scorer.py.
"""

import os
import json
import re
import time
import random
import unicodedata
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import google.generativeai as genai
from tqdm import tqdm

# Load config (API key from .env)
from config import API_KEY

# ============================================================================
# CONFIGURATION
# ============================================================================

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-3-flash-preview"
CHUNK_SIZE = 64
SCORE_THRESHOLD = 7
PAID_TIER_SLEEP = 0.1  # seconds between requests

# Paths
PROMPT_DIR = Path("prompts/grammar")
RANGES_FILE = Path("prompts/grammar_ranges.json")
EXCLUSION_FILE = Path("data/final_64.json")
OUTPUT_FILE = "data/grammar_round_1.jsonl"
HARVEST_FILE = "data/grammar_round_1_harvested.txt"

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ChunkResult:
    round: int
    chunk_id: int
    glyphs: List[str]
    scores: Dict[str, int]
    response1: str
    response2: str


# ============================================================================
# CONFIGURATION LOADERS
# ============================================================================

def load_prompts() -> Tuple[str, str]:
    """Load prompts from grammar directory."""
    prompt1_file = PROMPT_DIR / "turn1.txt"
    prompt2_file = PROMPT_DIR / "turn2.txt"
    
    if not prompt1_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt1_file}")
    if not prompt2_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt2_file}")
    
    with open(prompt1_file, 'r', encoding='utf-8') as f:
        prompt1 = f.read().strip()
    with open(prompt2_file, 'r', encoding='utf-8') as f:
        prompt2 = f.read().strip()
    
    if '{glyphs}' not in prompt1:
        raise ValueError(f"{prompt1_file} must contain {{glyphs}} placeholder")
    
    return prompt1, prompt2


def load_unicode_ranges() -> List[Tuple[int, int]]:
    """Load Unicode ranges from JSON file."""
    if not RANGES_FILE.exists():
        raise FileNotFoundError(f"Grammar ranges file not found: {RANGES_FILE}")
    
    with open(RANGES_FILE, 'r', encoding='utf-8') as f:
        ranges_data = json.load(f)
    
    # Convert to list of tuples
    ranges = [(r[0], r[1]) for r in ranges_data]
    return ranges


def load_exclusion_glyphs() -> set:
    """Load existing 64 axiom glyphs from final_64.json."""
    if not EXCLUSION_FILE.exists():
        raise FileNotFoundError(f"Exclusion file not found: {EXCLUSION_FILE}")
    
    with open(EXCLUSION_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return set(data['glyphs'])


# ============================================================================
# UNICODE GENERATION
# ============================================================================

def generate_all_glyphs(ranges: List[Tuple[int, int]]) -> List[str]:
    """
    Generate all valid glyphs from Unicode ranges.
    Filters out control characters and separators (except spaces).
    """
    glyphs = []
    for start, end in ranges:
        for i in range(start, end):
            try:
                char = chr(i)
                category = unicodedata.category(char)
                # Skip control (C*) and separator (Z*) categories, except spaces
                if category[0] not in ['C', 'Z'] or category == 'Zs':
                    glyphs.append(char)
            except ValueError:
                continue
    return glyphs


# ============================================================================
# API INTERACTION
# ============================================================================

def score_chunk_with_conversation(chunk: List[str], chunk_id: int, prompt1: str, prompt2: str) -> ChunkResult:
    """
    Score a chunk of glyphs using a 2-turn conversation with Gemini.
    
    Args:
        chunk: List of glyphs to score
        chunk_id: Identifier for this chunk
        prompt1: First turn prompt template
        prompt2: Second turn prompt
    
    Returns:
        ChunkResult with scores and API responses
    """
    model = genai.GenerativeModel(MODEL_NAME)
    chat = model.start_chat()
    
    # Turn 1: Send glyphs
    glyphs_text = "\n".join(chunk)
    prompt1_formatted = prompt1.format(glyphs=glyphs_text)
    
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            response1 = chat.send_message(prompt1_formatted)
            response1_text = response1.text
            
            # Sleep to respect rate limits
            time.sleep(PAID_TIER_SLEEP)
            
            # Turn 2: Request scores (continues same conversation)
            response2 = chat.send_message(prompt2)
            response2_text = response2.text
            
            # Parse scores from response2
            scores = parse_scores(response2_text, chunk)
            
            return ChunkResult(
                round=1,
                chunk_id=chunk_id,
                glyphs=chunk,
                scores=scores,
                response1=response1_text,
                response2=response2_text
            )
            
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                # Rate limit hit - exponential backoff
                wait_time = (2 ** retry_count) * 60  # 1min, 2min, 4min, etc.
                print(f"⚠️  Rate limit hit on chunk {chunk_id}. Waiting {wait_time}s...")
                time.sleep(wait_time)
                retry_count += 1
            else:
                print(f"❌ Error on chunk {chunk_id}: {e}")
                # Return empty scores on non-rate-limit errors
                return ChunkResult(
                    round=1,
                    chunk_id=chunk_id,
                    glyphs=chunk,
                    scores={},
                    response1="",
                    response2=f"ERROR: {e}"
                )
    
    # Max retries exceeded
    print(f"❌ Max retries exceeded for chunk {chunk_id}")
    return ChunkResult(
        round=1,
        chunk_id=chunk_id,
        glyphs=chunk,
        scores={},
        response1="",
        response2="ERROR: Max retries exceeded"
    )


def parse_scores(response: str, expected_glyphs: List[str]) -> Dict[str, int]:
    """
    Parse scores from response text.
    Expected formats:
      - <glyph> <score> (simple: integers or decimals)
      - <glyph> <m∴c> (magnitude∴confidence format)
    Decimals are rounded to nearest int
    
    Args:
        response: API response text
        expected_glyphs: List of glyphs we expect scores for (for validation)
    
    Returns:
        Dictionary mapping glyph to score (0-10)
    """
    scores = {}
    # Pattern for m∴c format: glyph followed by magnitude∴confidence
    pattern_mc = r'^(.)\s+(\d+(?:\.\d+)?)\s*∴\s*(\d+(?:\.\d+)?)$'
    # Pattern for simple format: glyph followed by score
    pattern_simple = r'^(.)\s+(\d+(?:\.\d+)?)$'
    
    for line in response.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Try m∴c format first
        match = re.match(pattern_mc, line)
        if match:
            glyph = match.group(1)
            magnitude = round(float(match.group(2)))  # m is the score (0-10)
            # confidence = float(match.group(3))  # c is 0-1, we ignore for now
            
            if 0 <= magnitude <= 10:
                scores[glyph] = magnitude
            else:
                print(f"⚠️  Invalid magnitude {magnitude} for glyph '{glyph}' (must be 0-10)")
            continue
        
        # Try simple format
        match = re.match(pattern_simple, line)
        if match:
            glyph = match.group(1)
            score = round(float(match.group(2)))
            
            if 0 <= score <= 10:
                scores[glyph] = score
            else:
                print(f"⚠️  Invalid score {score} for glyph '{glyph}' (must be 0-10)")
            continue
        
        # Fallback: try to extract glyph and score/magnitude
        parts = line.split()
        if len(parts) >= 2:
            try:
                glyph = parts[0]
                # Check if it has ∴ separator
                if '∴' in parts[-1]:
                    magnitude_str = parts[-1].split('∴')[0]
                    magnitude = round(float(magnitude_str))
                    if 0 <= magnitude <= 10 and glyph in expected_glyphs:
                        scores[glyph] = magnitude
                else:
                    score = round(float(parts[-1]))
                    if 0 <= score <= 10 and glyph in expected_glyphs:
                        scores[glyph] = score
            except (ValueError, IndexError):
                pass  # Skip lines we can't parse
    
    # Warn if we didn't get all expected scores
    missing = set(expected_glyphs) - set(scores.keys())
    if missing and len(missing) <= 5:
        print(f"⚠️  Missing scores for {len(missing)} glyphs: {''.join(list(missing)[:5])}")
    elif missing:
        print(f"⚠️  Missing scores for {len(missing)} glyphs in chunk")
    
    return scores


# ============================================================================
# HARVESTING
# ============================================================================

def harvest() -> List[str]:
    """
    Load results from round, filter glyphs with score >= threshold.
    
    Returns:
        List of glyphs that passed the threshold, sorted by score
    """
    if not os.path.exists(OUTPUT_FILE):
        return []
    
    harvested = []
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line)
            for glyph, score in result['scores'].items():
                if score >= SCORE_THRESHOLD:
                    harvested.append((glyph, score))
    
    # Sort by score descending
    harvested.sort(key=lambda x: -x[1])
    
    print(f"📊 Harvested {len(harvested)} glyphs with score ≥ {SCORE_THRESHOLD}")
    return harvested


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """
    Main orchestration:
    1. Load grammar ranges
    2. Generate candidate glyphs
    3. Filter out existing 64 axioms
    4. Score ONE round
    5. Harvest top scorers
    6. Print top 20 for human review
    """
    print("🎨 Grammar Particle Scorer — CONDITIONAL (Irrealis Mood)")
    print(f"Model: {MODEL_NAME}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print(f"Score threshold: {SCORE_THRESHOLD}")
    
    # Load prompts
    print("\n📝 Loading prompts...")
    prompt1, prompt2 = load_prompts()
    print(f"✓ Loaded prompts from {PROMPT_DIR}")
    
    # Load Unicode ranges
    print("\n🔢 Loading Unicode ranges...")
    unicode_ranges = load_unicode_ranges()
    print(f"✓ Loaded {len(unicode_ranges)} range(s)")
    
    # Load exclusion list
    print("\n🚫 Loading exclusion list (existing 64 axioms)...")
    exclusion_glyphs = load_exclusion_glyphs()
    print(f"✓ Loaded {len(exclusion_glyphs)} glyphs to exclude")
    
    # Generate glyphs
    print("\n🔤 Generating glyphs from Unicode ranges...")
    glyphs = generate_all_glyphs(unicode_ranges)
    print(f"✓ Generated {len(glyphs):,} glyphs")
    
    # Filter out existing axioms
    print(f"\n🔍 Filtering out existing axioms...")
    glyphs_before = len(glyphs)
    glyphs = [g for g in glyphs if g not in exclusion_glyphs]
    glyphs_after = len(glyphs)
    print(f"✓ Filtered {glyphs_before - glyphs_after} axioms, {glyphs_after:,} candidates remain")
    
    # Chunk glyphs
    chunks = [glyphs[i:i+CHUNK_SIZE] for i in range(0, len(glyphs), CHUNK_SIZE)]
    total_chunks = len(chunks)
    num_requests = total_chunks * 2
    
    # Cost estimation
    tokens_per_turn1 = 500 + (CHUNK_SIZE * 5)
    tokens_per_turn2 = 100 + (CHUNK_SIZE * 3)
    total_input_tokens = total_chunks * (tokens_per_turn1 + tokens_per_turn2)
    total_output_tokens = total_chunks * (CHUNK_SIZE * 3)
    
    cost_input = (total_input_tokens / 1_000_000) * 0.075
    cost_output = (total_output_tokens / 1_000_000) * 0.30
    total_cost = cost_input + cost_output
    estimated_minutes = (num_requests * PAID_TIER_SLEEP) / 60
    
    print(f"\n{'='*60}")
    print(f"ROUND 1 — Grammar Scoring")
    print(f"{'='*60}")
    print(f"Glyphs: {len(glyphs):,}")
    print(f"Chunks: {total_chunks:,} (size={CHUNK_SIZE})")
    print(f"API requests: {num_requests:,} (2 turns per chunk)")
    print(f"Estimated cost: ${total_cost:.2f}")
    print(f"Estimated time: ~{estimated_minutes:.1f} minutes")
    
    response = input(f"\nProceed? [Y/n]: ").strip().lower()
    if response == 'n':
        print("Aborted.")
        return
    
    # Check if output already exists
    if os.path.exists(OUTPUT_FILE):
        response = input(f"\n⚠️  {OUTPUT_FILE} already exists. Overwrite? [y/N]: ").strip().lower()
        if response != 'y':
            print("Keeping existing results.")
        else:
            os.remove(OUTPUT_FILE)
            print(f"✓ Removed {OUTPUT_FILE}")
    
    # Process chunks in parallel with incremental file writing
    max_workers = min(10, max(1, len(chunks) // 10))
    
    results = []
    
    # Open file for incremental writing
    output_handle = open(OUTPUT_FILE, 'w', encoding='utf-8')
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(score_chunk_with_conversation, chunk, idx, prompt1, prompt2): idx
                for idx, chunk in enumerate(chunks)
            }
            
            with tqdm(total=len(chunks), desc="Scoring", unit="chunk") as pbar:
                for future in as_completed(futures):
                    chunk_id = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Write result immediately
                        output_handle.write(json.dumps(asdict(result), ensure_ascii=False) + '\n')
                        output_handle.flush()  # Ensure it's written to disk
                        
                        pbar.set_postfix({"scores": len(result.scores), "chunk": chunk_id})
                        pbar.update(1)
                    except Exception as e:
                        pbar.write(f"❌ Chunk {chunk_id} failed: {e}")
                        pbar.update(1)
    finally:
        output_handle.close()
    
    print(f"\n✓ Round complete! Results saved to {OUTPUT_FILE}")
    
    # Harvest glyphs with score >= threshold
    print(f"\n🌾 Harvesting glyphs with score ≥ {SCORE_THRESHOLD}...")
    harvested = harvest()
    
    # Save harvested glyphs
    with open(HARVEST_FILE, 'w', encoding='utf-8') as f:
        for glyph, score in harvested:
            f.write(f"{glyph} {score}\n")
    print(f"✓ Saved {len(harvested)} harvested glyphs to {HARVEST_FILE}")
    
    # Print top 20
    top_20 = harvested[:20]
    print(f"\n{'='*60}")
    print(f"TOP 20 CANDIDATES")
    print(f"{'='*60}")
    for i, (glyph, score) in enumerate(top_20, 1):
        print(f"#{i:2d}  {glyph}  score={score}")
    
    if len(harvested) == 0:
        print("\n⚠️  No glyphs passed threshold! Consider adjusting prompts or threshold.")
    else:
        print(f"\n🎯 Review top candidates and select the winner for MT's CONDITIONAL particle.")


if __name__ == "__main__":
    main()
