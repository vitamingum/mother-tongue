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
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import google.generativeai as genai
from tqdm import tqdm


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
PAID_TIER_SLEEP = 0.1  # seconds (if using paid tier)

# Prompts loaded from files
PROMPT_DIR = Path("prompts")
PROMPT1_FILE = PROMPT_DIR / "turn1.txt"
PROMPT2_FILE = PROMPT_DIR / "turn2.txt"
RANGES_FILE = PROMPT_DIR / "unicode_ranges.json"


# ============================================================================
# CONFIGURATION LOADERS
# ============================================================================

def load_prompts() -> Tuple[str, str]:
    """Load prompts from files."""
    if not PROMPT1_FILE.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT1_FILE}\n"
            f"Create prompts/ directory with turn1.txt and turn2.txt\n"
            f"turn1.txt should include {{glyphs}} placeholder"
        )
    if not PROMPT2_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT2_FILE}")
    
    with open(PROMPT1_FILE, 'r', encoding='utf-8') as f:
        prompt1 = f.read().strip()
    with open(PROMPT2_FILE, 'r', encoding='utf-8') as f:
        prompt2 = f.read().strip()
    
    if '{glyphs}' not in prompt1:
        raise ValueError(f"{PROMPT1_FILE} must contain {{glyphs}} placeholder")
    
    return prompt1, prompt2


def load_unicode_ranges() -> List[Tuple[int, int]]:
    """Load Unicode ranges from JSON file."""
    if not RANGES_FILE.exists():
        raise FileNotFoundError(
            f"Unicode ranges file not found: {RANGES_FILE}\n"
            f"Create {RANGES_FILE} with format: [[start, end], ...]\n"
            f"Example: [[0, 25600], [0x4E00, 0x9FFF]]"
        )
    
    with open(RANGES_FILE, 'r', encoding='utf-8') as f:
        ranges_data = json.load(f)
    
    # Convert to list of tuples
    ranges = [(r[0], r[1]) for r in ranges_data]
    return ranges


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

def score_chunk_with_conversation(chunk: List[str], chunk_id: int, round_num: int, prompt1: str, prompt2: str) -> ChunkResult:
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
    prompt1_formatted = prompt1.format(glyphs=glyphs_text)
    
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            response1 = chat.send_message(prompt1_formatted)
            response1_text = response1.text
            
            # Sleep to respect rate limits
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            
            # Turn 2: Request scores (continues same conversation)
            response2 = chat.send_message(prompt2)
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

def check_existing_round(round_num: int) -> Optional[str]:
    """Check if round results already exist."""
    output_file = f"data/round_{round_num}.jsonl"
    if os.path.exists(output_file):
        return output_file
    return None


def estimate_round_cost(num_glyphs: int, chunk_size: int = CHUNK_SIZE) -> Dict:
    """Estimate cost and time for a round."""
    num_chunks = (num_glyphs + chunk_size - 1) // chunk_size
    num_requests = num_chunks * 2
    
    # Rough estimates (adjust based on actual prompt sizes)
    tokens_per_turn1 = 500 + (chunk_size * 5)  # prompt + glyphs
    tokens_per_turn2 = 100 + (chunk_size * 3)  # prompt + response
    total_input_tokens = num_chunks * (tokens_per_turn1 + tokens_per_turn2)
    total_output_tokens = num_chunks * (chunk_size * 3)  # ~3 tokens per scored glyph
    
    # Free tier timing
    free_tier_minutes = (num_requests * SLEEP_BETWEEN_REQUESTS) / 60
    
    # Paid tier cost (gemini-2.5-flash-lite rates)
    cost_input = (total_input_tokens / 1_000_000) * 0.10
    cost_output = (total_output_tokens / 1_000_000) * 0.40
    total_cost = cost_input + cost_output
    
    return {
        'chunks': num_chunks,
        'requests': num_requests,
        'estimated_minutes': free_tier_minutes,
        'estimated_cost_usd': total_cost,
        'exceeds_free_tier': num_requests > FREE_TIER_RPD
    }


def score_round(glyphs: List[str], round_num: int, prompt1: str, prompt2: str, resume: bool = True) -> str:
    """
    Score all glyphs in a round using parallel API calls.
    
    Args:
        glyphs: List of glyphs to score
        round_num: Current round number
        prompt1: First turn prompt template
        prompt2: Second turn prompt
        resume: Whether to skip if results already exist
    
    Returns:
        Path to the output JSONL file
    """
    output_file = f"data/round_{round_num}.jsonl"
    
    # Check for existing results
    if resume and os.path.exists(output_file):
        print(f"\n✓ Round {round_num} results already exist: {output_file}")
        response = input(f"Resume from existing? [Y/n]: ").strip().lower()
        if response != 'n':
            return output_file
    
    # Chunk glyphs
    chunks = [glyphs[i:i+CHUNK_SIZE] for i in range(0, len(glyphs), CHUNK_SIZE)]
    total_chunks = len(chunks)
    
    # Cost/time estimation
    estimate = estimate_round_cost(len(glyphs))
    
    print(f"\n{'='*60}")
    print(f"ROUND {round_num}")
    print(f"{'='*60}")
    print(f"Glyphs: {len(glyphs):,}")
    print(f"Chunks: {estimate['chunks']} (size={CHUNK_SIZE})")
    print(f"API requests: {estimate['requests']} (2 turns per chunk)")
    print(f"Estimated time: ~{estimate['estimated_minutes']:.1f} minutes (free tier)")
    print(f"Estimated cost: ${estimate['estimated_cost_usd']:.2f} (paid tier)")
    
    if estimate['exceeds_free_tier']:
        print(f"\n⚠️  WARNING: {estimate['requests']} requests exceeds free tier limit of {FREE_TIER_RPD} RPD")
        print(f"   Consider splitting into multiple days or using paid tier")
        response = input(f"\nContinue anyway? [y/N]: ").strip().lower()
        if response != 'y':
            print("Aborted.")
            exit(0)
    
    # Process chunks in parallel
    max_workers = min(10, max(1, FREE_TIER_RPD // (2 * total_chunks)))
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(score_chunk_with_conversation, chunk, idx, round_num, prompt1, prompt2): idx
            for idx, chunk in enumerate(chunks)
        }
        
        with tqdm(total=total_chunks, desc=f"Round {round_num}", unit="chunk") as pbar:
            for future in as_completed(futures):
                chunk_id = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    pbar.set_postfix({"scores": len(result.scores), "chunk": chunk_id})
                    pbar.update(1)
                except Exception as e:
                    pbar.write(f"❌ Chunk {chunk_id} failed: {e}")
                    pbar.update(1)
    
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

def validate_configuration():
    """Validate that all required configuration is present."""
    errors = []
    
    # Check API key
    if not API_KEY:
        errors.append("GEMINI_API_KEY environment variable not set")
    
    # Check prompt files
    if not PROMPT_DIR.exists():
        errors.append(f"Prompts directory not found: {PROMPT_DIR}")
    if not PROMPT1_FILE.exists():
        errors.append(f"Prompt file not found: {PROMPT1_FILE}")
    if not PROMPT2_FILE.exists():
        errors.append(f"Prompt file not found: {PROMPT2_FILE}")
    
    # Check ranges file
    if not RANGES_FILE.exists():
        errors.append(f"Unicode ranges file not found: {RANGES_FILE}")
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   • {error}")
        print("\n📖 Setup instructions:")
        print("   1. Set GEMINI_API_KEY environment variable")
        print("   2. Create prompts/ directory")
        print("   3. Create prompts/turn1.txt (include {glyphs} placeholder)")
        print("   4. Create prompts/turn2.txt")
        print("   5. Create prompts/unicode_ranges.json (format: [[start, end], ...])")
        exit(1)


def main():
    """
    Main orchestration loop:
    1. Validate configuration
    2. Load prompts and Unicode ranges
    3. Generate all glyphs from Unicode ranges
    4. Run rounds of scoring until we have <= FINAL_COUNT glyphs
    5. Save final glyphs
    """
    print("🎨 Glyph Scorer - Multi-round selection system")
    print(f"Model: {MODEL_NAME}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print(f"Score threshold: {SCORE_THRESHOLD}")
    print(f"Target final count: {FINAL_COUNT}")
    
    # Validate configuration
    print("\n📋 Validating configuration...")
    validate_configuration()
    print("✓ Configuration valid")
    
    # Load prompts and ranges
    print("\n📝 Loading prompts...")
    prompt1, prompt2 = load_prompts()
    print(f"✓ Loaded prompts from {PROMPT_DIR}")
    
    print("\n🔢 Loading Unicode ranges...")
    unicode_ranges = load_unicode_ranges()
    print(f"✓ Loaded {len(unicode_ranges)} range(s)")
    
    # Generate initial glyph set
    print("\n🔤 Generating glyphs from Unicode ranges...")
    glyphs = generate_all_glyphs(unicode_ranges)
    print(f"✓ Generated {len(glyphs):,} glyphs")
    
    # Determine starting round
    round_num = 1
    while check_existing_round(round_num):
        print(f"✓ Found existing round_{round_num}.jsonl")
        round_num += 1
    
    if round_num > 1:
        print(f"\n🔄 Resuming from round {round_num}")
        glyphs = harvest(round_num - 1)
    
    # Multi-round scoring
    while len(glyphs) > FINAL_COUNT:
        score_round(glyphs, round_num, prompt1, prompt2)
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
