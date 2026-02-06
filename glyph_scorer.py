"""
Glyph Scorer - Multi-round Unicode glyph scoring using Gemini API
Uses 2-turn conversations to score glyphs, filtering top performers across rounds
"""

import os
import sys
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
FINAL_COUNT = 64
FREE_TIER_RPD = 1500  # requests per day
FREE_TIER_SLEEP = 4  # seconds between requests
PAID_TIER_SLEEP = 0.1  # seconds between requests

# Paid tier mode (default: True for $6.56 fast processing)
USE_PAID_TIER = os.getenv("GEMINI_PAID_TIER", "true").lower() == "true"
SLEEP_BETWEEN_REQUESTS = PAID_TIER_SLEEP if USE_PAID_TIER else FREE_TIER_SLEEP

# Daily quota tracking
QUOTA_TRACKING_FILE = "data/quota_tracking.json"

# Available prompt strategies
AVAILABLE_STRATEGIES = ["prompt1", "prompt2", "prompt3"]
DEFAULT_STRATEGY = "prompt1"

# Prompts loaded from files
PROMPT_DIR = Path("prompts")
RANGES_FILE = PROMPT_DIR / "unicode_ranges.json"


# ============================================================================
# CONFIGURATION LOADERS
# ============================================================================

def load_prompts(strategy: str = DEFAULT_STRATEGY) -> Tuple[str, str]:
    """Load prompts from strategy directory."""
    strategy_dir = PROMPT_DIR / strategy
    prompt1_file = strategy_dir / "turn1.txt"
    prompt2_file = strategy_dir / "turn2.txt"
    
    if not strategy_dir.exists():
        raise FileNotFoundError(
            f"Strategy directory not found: {strategy_dir}\n"
            f"Available strategies: {', '.join(AVAILABLE_STRATEGIES)}"
        )
    if not prompt1_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt1_file}\n"
            f"Create {strategy_dir}/turn1.txt and turn2.txt\n"
            f"turn1.txt should include {{glyphs}} placeholder"
        )
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


@dataclass
class QuotaTracker:
    date: str
    requests_used: int
    requests_limit: int
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def load(cls) -> 'QuotaTracker':
        """Load quota tracking from file."""
        today = time.strftime("%Y-%m-%d")
        
        if not os.path.exists(QUOTA_TRACKING_FILE):
            return cls(date=today, requests_used=0, requests_limit=FREE_TIER_RPD)
        
        with open(QUOTA_TRACKING_FILE, 'r') as f:
            data = json.load(f)
        
        # Reset if it's a new day
        if data.get('date') != today:
            return cls(date=today, requests_used=0, requests_limit=FREE_TIER_RPD)
        
        return cls(**data)
    
    def save(self):
        """Save quota tracking to file."""
        os.makedirs("data", exist_ok=True)
        with open(QUOTA_TRACKING_FILE, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def add_requests(self, count: int):
        """Add completed requests to tracker."""
        self.requests_used += count
        self.save()
    
    def can_make_requests(self, count: int) -> bool:
        """Check if we can make this many requests today."""
        if USE_PAID_TIER:
            return True
        return (self.requests_used + count) <= self.requests_limit
    
    def remaining_today(self) -> int:
        """Get remaining requests for today."""
        if USE_PAID_TIER:
            return 999999
        return max(0, self.requests_limit - self.requests_used)


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


def estimate_round_cost(num_glyphs: int, chunk_size: int = CHUNK_SIZE, quota: Optional[QuotaTracker] = None) -> Dict:
    """Estimate cost and time for a round."""
    num_chunks = (num_glyphs + chunk_size - 1) // chunk_size
    num_requests = num_chunks * 2
    
    # Rough estimates (adjust based on actual prompt sizes)
    tokens_per_turn1 = 500 + (chunk_size * 5)  # prompt + glyphs
    tokens_per_turn2 = 100 + (chunk_size * 3)  # prompt + response
    total_input_tokens = num_chunks * (tokens_per_turn1 + tokens_per_turn2)
    total_output_tokens = num_chunks * (chunk_size * 3)  # ~3 tokens per scored glyph
    
    # Timing estimation
    estimated_minutes = (num_requests * SLEEP_BETWEEN_REQUESTS) / 60
    
    # Paid tier cost (gemini-3-flash-preview rates: $0.075 per 1M input, $0.30 per 1M output)
    cost_input = (total_input_tokens / 1_000_000) * 0.075
    cost_output = (total_output_tokens / 1_000_000) * 0.30
    total_cost = cost_input + cost_output
    
    # Multi-day calculation for free tier
    if quota:
        remaining_today = quota.remaining_today()
        can_finish_today = num_requests <= remaining_today
        days_needed = (num_requests + FREE_TIER_RPD - 1) // FREE_TIER_RPD if not USE_PAID_TIER else 1
    else:
        remaining_today = FREE_TIER_RPD
        can_finish_today = num_requests <= FREE_TIER_RPD
        days_needed = (num_requests + FREE_TIER_RPD - 1) // FREE_TIER_RPD if not USE_PAID_TIER else 1
    
    return {
        'chunks': num_chunks,
        'requests': num_requests,
        'estimated_minutes': estimated_minutes,
        'estimated_hours': estimated_minutes / 60,
        'estimated_cost_usd': total_cost,
        'exceeds_free_tier': num_requests > FREE_TIER_RPD,
        'remaining_today': remaining_today,
        'can_finish_today': can_finish_today,
        'days_needed': days_needed
    }


def score_round(glyphs: List[str], round_num: int, prompt1: str, prompt2: str, resume: bool = True, quota: Optional[QuotaTracker] = None) -> str:
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
    
    # Initialize quota tracker
    if quota is None:
        quota = QuotaTracker.load()
    
    # Chunk glyphs
    chunks = [glyphs[i:i+CHUNK_SIZE] for i in range(0, len(glyphs), CHUNK_SIZE)]
    total_chunks = len(chunks)
    
    # Cost/time estimation
    estimate = estimate_round_cost(len(glyphs), quota=quota)
    
    print(f"\n{'='*60}")
    print(f"ROUND {round_num}")
    print(f"{'='*60}")
    print(f"Glyphs: {len(glyphs):,}")
    print(f"Chunks: {estimate['chunks']:,} (size={CHUNK_SIZE})")
    print(f"API requests: {estimate['requests']:,} (2 turns per chunk)")
    
    if USE_PAID_TIER:
        print(f"\n💳 PAID TIER MODE")
        print(f"Estimated time: ~{estimate['estimated_minutes']:.1f} minutes ({estimate['estimated_hours']:.2f} hours)")
        print(f"Estimated cost: ${estimate['estimated_cost_usd']:.2f}")
    else:
        print(f"\n🆓 FREE TIER MODE")
        print(f"Daily limit: {FREE_TIER_RPD} requests/day")
        print(f"Used today: {quota.requests_used}")
        print(f"Remaining today: {estimate['remaining_today']}")
        print(f"Estimated days needed: {estimate['days_needed']}")
        print(f"Estimated time: ~{estimate['estimated_minutes']:.1f} minutes per batch")
        
        if not estimate['can_finish_today']:
            requests_today = min(estimate['requests'], estimate['remaining_today'])
            print(f"\n⚠️  Will process {requests_today} requests today, resume tomorrow for remaining")
            response = input(f"\nContinue with multi-day batching? [Y/n]: ").strip().lower()
            if response == 'n':
                print("\n💡 Tip: Set GEMINI_PAID_TIER=true to process all at once")
                print("Aborted.")
                exit(0)
    
    # Determine how many chunks we can process today
    if USE_PAID_TIER:
        chunks_to_process = chunks
        start_chunk_idx = 0
    else:
        max_requests_today = quota.remaining_today()
        max_chunks_today = max_requests_today // 2  # 2 turns per chunk
        
        # Check for existing progress
        existing_chunks = 0
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_chunks = sum(1 for _ in f)
        
        start_chunk_idx = existing_chunks
        end_chunk_idx = min(start_chunk_idx + max_chunks_today, total_chunks)
        chunks_to_process = chunks[start_chunk_idx:end_chunk_idx]
        
        if start_chunk_idx > 0:
            print(f"\n🔄 Resuming from chunk {start_chunk_idx} of {total_chunks}")
        
        if end_chunk_idx < total_chunks:
            print(f"\n📊 Processing chunks {start_chunk_idx} to {end_chunk_idx-1} (of {total_chunks})")
            print(f"   Remaining for tomorrow: {total_chunks - end_chunk_idx} chunks")
    
    if not chunks_to_process:
        print(f"\n✓ Round {round_num} already complete or no quota remaining today")
        return output_file
    
    # Process chunks in parallel
    max_workers = min(10, max(1, len(chunks_to_process) // 10)) if USE_PAID_TIER else 5
    
    results = []
    requests_made = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(score_chunk_with_conversation, chunk, start_chunk_idx + idx, round_num, prompt1, prompt2): idx
            for idx, chunk in enumerate(chunks_to_process)
        }
        
        with tqdm(total=len(chunks_to_process), desc=f"Round {round_num}", unit="chunk") as pbar:
            for future in as_completed(futures):
                chunk_id = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    requests_made += 2  # 2 turns per chunk
                    pbar.set_postfix({"scores": len(result.scores), "chunk": start_chunk_idx + chunk_id})
                    pbar.update(1)
                except Exception as e:
                    pbar.write(f"❌ Chunk {start_chunk_idx + chunk_id} failed: {e}")
                    pbar.update(1)
    
    # Update quota tracker
    quota.add_requests(requests_made)
    
    # Append results to JSONL (for multi-day resume)
    mode = 'a' if start_chunk_idx > 0 else 'w'
    with open(output_file, mode, encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(asdict(result), ensure_ascii=False) + '\n')
    
    # Check if round is complete
    with open(output_file, 'r', encoding='utf-8') as f:
        completed_chunks = sum(1 for _ in f)
    
    if completed_chunks < total_chunks:
        print(f"\n⏸️  Round {round_num} partially complete: {completed_chunks}/{total_chunks} chunks")
        print(f"   Results saved to {output_file}")
        print(f"   Run again tomorrow to continue (daily quota will reset)")
        print(f"\n💡 Tip: Set GEMINI_PAID_TIER=true to finish in one run")
        exit(0)
    else:
        print(f"\n✓ Round {round_num} complete! Results saved to {output_file}")
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

def validate_configuration(strategy: str):
    """Validate that all required configuration is present."""
    errors = []
    
    # Check strategy
    if strategy not in AVAILABLE_STRATEGIES:
        errors.append(
            f"Invalid strategy '{strategy}'\n"
            f"   Available: {', '.join(AVAILABLE_STRATEGIES)}"
        )
    
    # Check prompt files
    strategy_dir = PROMPT_DIR / strategy
    if not PROMPT_DIR.exists():
        errors.append(f"Prompts directory not found: {PROMPT_DIR}")
    if not strategy_dir.exists():
        errors.append(f"Strategy directory not found: {strategy_dir}")
    if not (strategy_dir / "turn1.txt").exists():
        errors.append(f"Prompt file not found: {strategy_dir / 'turn1.txt'}")
    if not (strategy_dir / "turn2.txt").exists():
        errors.append(f"Prompt file not found: {strategy_dir / 'turn2.txt'}")
    
    # Check ranges file
    if not RANGES_FILE.exists():
        errors.append(f"Unicode ranges file not found: {RANGES_FILE}")
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   • {error}")
        print("\n📖 Available strategies:")
        for strat in AVAILABLE_STRATEGIES:
            print(f"   • {strat}")
        print("\n📖 Setup instructions:")
        print("   1. Copy .env.example to .env and add your GOOGLE_API_KEY")
        print("   2. Prompts exist at prompts/<strategy>/turn1.txt and turn2.txt")
        print("   3. Unicode ranges pre-configured in prompts/unicode_ranges.json")
        print(f"   4. Run with: python glyph_scorer.py [strategy]")
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
    # Parse command line arguments
    strategy = DEFAULT_STRATEGY
    if len(sys.argv) > 1:
        strategy = sys.argv[1].lower()
    
    print("🎨 Glyph Scorer - Multi-round selection system")
    print(f"Strategy: {strategy}")
    print(f"Model: {MODEL_NAME}")
    print(f"Tier: {'PAID 💳' if USE_PAID_TIER else 'FREE 🆓'}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print(f"Score threshold: {SCORE_THRESHOLD}")
    print(f"Target final count: {FINAL_COUNT}")
    
    # Validate configuration
    print("\n📋 Validating configuration...")
    validate_configuration(strategy)
    print("✓ Configuration valid")
    
    # Load prompts and ranges
    print(f"\n📝 Loading prompts (strategy: {strategy})...")
    prompt1, prompt2 = load_prompts(strategy)
    print(f"✓ Loaded prompts from {PROMPT_DIR / strategy}")
    
    print("\n🔢 Loading Unicode ranges...")
    unicode_ranges = load_unicode_ranges()
    print(f"✓ Loaded {len(unicode_ranges)} range(s)")
    
    # Load quota tracker
    quota = QuotaTracker.load()
    print(f"\n📊 Quota status: {quota.requests_used}/{quota.requests_limit} requests used today")
    
    # Generate initial glyph set
    print("\n🔤 Generating glyphs from Unicode ranges...")
    glyphs = generate_all_glyphs(unicode_ranges)
    print(f"✓ Generated {len(glyphs):,} glyphs")
    
    # Upfront cost estimation for full run
    total_estimate = estimate_round_cost(len(glyphs), quota=quota)
    print(f"\n💰 Full R1 Estimate:")
    print(f"   Chunks: {total_estimate['chunks']:,}")
    print(f"   Requests: {total_estimate['requests']:,}")
    if USE_PAID_TIER:
        print(f"   Cost: ${total_estimate['estimated_cost_usd']:.2f}")
        print(f"   Time: ~{total_estimate['estimated_hours']:.1f} hours")
    else:
        print(f"   Days needed: {total_estimate['days_needed']}")
        print(f"   Time per day: ~{total_estimate['estimated_minutes']:.0f} minutes")
    
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
        score_round(glyphs, round_num, prompt1, prompt2, quota=quota)
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
