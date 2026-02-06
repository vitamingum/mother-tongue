"""
Glyph Scorer - Multi-round Unicode glyph scoring using Gemini API
Uses 2-turn conversations to score glyphs, filtering top performers across rounds
"""

import os
import json
import re
import time
import random
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
import google.generativeai as genai


# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Set GEMINI_API_KEY environment variable")

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-3-flash-preview"
CHUNK_SIZE = 64
SCORE_THRESHOLD = 7
FINAL_COUNT = 64
FREE_TIER_RPD = 1500  # requests per day
SLEEP_BETWEEN_REQUESTS = 4  # seconds (for free tier)

# TODO: User to provide actual Unicode ranges
# Format: list of (start, end) tuples
UNICODE_RANGES = [
    (0x0000, 0x6400),  # PLACEHOLDER - user will provide actual ranges
]

# TODO: User to provide actual prompts
PROMPT1 = """
TODO: User prompt for turn 1
Should include {glyphs} placeholder for formatting
Example:
Rate the visual complexity of these glyphs from 0-10:
{glyphs}
"""

PROMPT2 = """
TODO: User prompt for turn 2
Should request output in format: <glyph> <score>
Example:
Now provide scores in format: <glyph> <score> (one per line)
"""


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

def score_chunk_with_conversation(chunk: List[str], chunk_id: int, round_num: int) -> ChunkResult:
    """
    Score a chunk of glyphs using a 2-turn conversation with Gemini.
    
    Args:
        chunk: List of glyphs to score
        chunk_id: Identifier for this chunk
        round_num: Current round number
    
    Returns:
        ChunkResult with scores and API responses
    """
    model = genai.GenerativeModel(MODEL_NAME)
    chat = model.start_chat()
    
    # Turn 1: Send glyphs
    glyphs_text = "\n".join(chunk)
    prompt1_formatted = PROMPT1.format(glyphs=glyphs_text)
    
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            response1 = chat.send_message(prompt1_formatted)
            response1_text = response1.text
            
            # Sleep to respect rate limits
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            
            # Turn 2: Request scores (continues same conversation)
            response2 = chat.send_message(PROMPT2)
            response2_text = response2.text
            
            # Parse scores from response2
            scores = parse_scores(response2_text, chunk)
            
            return ChunkResult(
                round=round_num,
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
                    round=round_num,
                    chunk_id=chunk_id,
                    glyphs=chunk,
                    scores={},
                    response1="",
                    response2=f"ERROR: {e}"
                )
    
    # Max retries exceeded
    print(f"❌ Max retries exceeded for chunk {chunk_id}")
    return ChunkResult(
        round=round_num,
        chunk_id=chunk_id,
        glyphs=chunk,
        scores={},
        response1="",
        response2="ERROR: Max retries exceeded"
    )


def parse_scores(response: str, expected_glyphs: List[str]) -> Dict[str, int]:
    """
    Parse scores from response text.
    Expected format: <glyph> <score> (one per line)
    
    Args:
        response: API response text
        expected_glyphs: List of glyphs we expect scores for (for validation)
    
    Returns:
        Dictionary mapping glyph to score (0-10)
    """
    scores = {}
    pattern = r'^(.)\s+(\d+)$'
    
    for line in response.strip().split('\n'):
        line = line.strip()
        match = re.match(pattern, line)
        if match:
            glyph = match.group(1)
            score = int(match.group(2))
            
            # Validate score range
            if 0 <= score <= 10:
                scores[glyph] = score
            else:
                print(f"⚠️  Invalid score {score} for glyph '{glyph}' (must be 0-10)")
    
    # Warn if we didn't get all expected scores
    missing = set(expected_glyphs) - set(scores.keys())
    if missing:
        print(f"⚠️  Missing scores for {len(missing)} glyphs in chunk")
    
    return scores


# ============================================================================
# ROUND PROCESSING
# ============================================================================

def score_round(glyphs: List[str], round_num: int) -> str:
    """
    Score all glyphs in a round using parallel API calls.
    
    Args:
        glyphs: List of glyphs to score
        round_num: Current round number
    
    Returns:
        Path to the output JSONL file
    """
    # Chunk glyphs
    chunks = [glyphs[i:i+CHUNK_SIZE] for i in range(0, len(glyphs), CHUNK_SIZE)]
    total_chunks = len(chunks)
    total_requests = total_chunks * 2  # 2 turns per chunk
    
    print(f"\n{'='*60}")
    print(f"ROUND {round_num}")
    print(f"{'='*60}")
    print(f"Glyphs: {len(glyphs)}")
    print(f"Chunks: {total_chunks} (size={CHUNK_SIZE})")
    print(f"API requests: {total_requests} (2 turns per chunk)")
    print(f"Estimated time: ~{total_requests * SLEEP_BETWEEN_REQUESTS / 60:.1f} minutes")
    
    # Check if we'll hit rate limit
    if total_requests > FREE_TIER_RPD:
        print(f"⚠️  WARNING: {total_requests} requests exceeds free tier limit of {FREE_TIER_RPD} RPD")
        print(f"   Consider splitting into multiple days or using paid tier")
    
    output_file = f"data/round_{round_num}.jsonl"
    
    # Process chunks in parallel
    max_workers = min(10, max(1, FREE_TIER_RPD // (2 * total_chunks)))
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(score_chunk_with_conversation, chunk, idx, round_num): idx
            for idx, chunk in enumerate(chunks)
        }
        
        completed = 0
        for future in as_completed(futures):
            chunk_id = futures[future]
            try:
                result = future.result()
                results.append(result)
                completed += 1
                print(f"✓ Chunk {completed}/{total_chunks} complete (chunk_id={chunk_id}, scores={len(result.scores)})")
            except Exception as e:
                print(f"❌ Chunk {chunk_id} failed: {e}")
                completed += 1
    
    # Write results to JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(asdict(result), ensure_ascii=False) + '\n')
    
    print(f"\n✓ Round {round_num} complete. Results saved to {output_file}")
    return output_file


def harvest(round_num: int) -> List[str]:
    """
    Load results from a round, filter glyphs with score >= threshold, and shuffle.
    
    Args:
        round_num: Round number to harvest from
    
    Returns:
        List of glyphs that passed the threshold, shuffled
    """
    input_file = f"data/round_{round_num}.jsonl"
    
    harvested = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            result = json.loads(line)
            for glyph, score in result['scores'].items():
                if score >= SCORE_THRESHOLD:
                    harvested.append(glyph)
    
    # Shuffle for variety in next round
    random.shuffle(harvested)
    
    print(f"📊 Harvested {len(harvested)} glyphs with score ≥ {SCORE_THRESHOLD} from round {round_num}")
    return harvested


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """
    Main orchestration loop:
    1. Generate all glyphs from Unicode ranges
    2. Run rounds of scoring until we have <= FINAL_COUNT glyphs
    3. Save final glyphs
    """
    print("🎨 Glyph Scorer - Multi-round selection system")
    print(f"Model: {MODEL_NAME}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print(f"Score threshold: {SCORE_THRESHOLD}")
    print(f"Target final count: {FINAL_COUNT}")
    
    # Generate initial glyph set
    print("\n🔤 Generating glyphs from Unicode ranges...")
    glyphs = generate_all_glyphs(UNICODE_RANGES)
    print(f"✓ Generated {len(glyphs)} glyphs")
    
    round_num = 1
    
    # Multi-round scoring
    while len(glyphs) > FINAL_COUNT:
        score_round(glyphs, round_num)
        glyphs = harvest(round_num)
        
        if len(glyphs) == 0:
            print("❌ No glyphs passed threshold! Adjust SCORE_THRESHOLD or prompts.")
            return
        
        round_num += 1
    
    # Save final glyphs
    final_file = "data/final.txt"
    with open(final_file, 'w', encoding='utf-8') as f:
        for glyph in glyphs[:FINAL_COUNT]:
            f.write(glyph + '\n')
    
    print(f"\n{'='*60}")
    print(f"🏆 COMPLETE!")
    print(f"{'='*60}")
    print(f"Final glyphs: {len(glyphs)}")
    print(f"Total rounds: {round_num - 1}")
    print(f"Saved to: {final_file}")
    print(f"\nFinal glyphs: {''.join(glyphs[:FINAL_COUNT])}")


if __name__ == "__main__":
    main()
