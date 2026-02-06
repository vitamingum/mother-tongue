# Glyph Scorer

Multi-round Unicode glyph scoring system using Google Gemini API.

**Scale: 105,040 glyphs | 1,641 chunks | 3,282 API calls**

## Architecture

- **Multi-round filtering**: Start with ~105k glyphs, filter down to 64 through successive rounds
- **2-turn conversations**: Each batch of 64 glyphs uses a stateful conversation for context
- **Parallel processing**: ThreadPoolExecutor for efficient API usage
- **Multi-day batching**: Free tier auto-splits work across days with quota tracking
- **Rate limiting**: Automatic quota management with exponential backoff on errors

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key**:
   
   Copy `.env.example` to `.env` and add your Google API key:
   ```bash
   # .env file
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

3. **Tier mode** (PAID TIER is default):
   
   **PAID TIER** (default) - unlimited requests:
   - R1 completes in ~3.3 hours
   - Cost: ~$6.56 for full run
   - Processes everything in one session
   - No configuration needed
   
   **FREE TIER** - 1500 requests/day (opt-in):
   ```bash
   $env:GEMINI_PAID_TIER="false"
   ```
   - R1 will take ~3 days (auto-batches and resumes)
   - No cost
   - Run script once per day

4. **Unicode ranges are pre-configured** with 105k glyphs covering:
   - Mathematical operators & symbols
   - Arrows (all variants)
   - Geometric shapes
   - Box drawing & blocks  
   - CJK ideographs (80k+ characters)
   - Greek, Hebrew, Arabic, Runic
   - Emoji & symbols
   - Egyptian hieroglyphs & Cuneiform

5. **Prompts are organized** in three strategy folders:
   - `prompt1` - First scoring strategy
   - `prompt2` - Second scoring strategy  
   - `prompt3` - Third scoring strategy

## Usage

```bash
# Run with a specific prompt strategy
python glyph_scorer.py prompt1
python glyph_scorer.py prompt2
python glyph_scorer.py prompt3

# Or use default (prompt1)
python glyph_scorer.py
```

The script will:
- Validate configuration (prompts, ranges, API key)
- Estimate cost and time for each round
- Show progress with tqdm progress bars
- Ask before proceeding if rate limits will be exceeded
- Automatically resume from existing rounds if interrupted

## Configuration Options

Edit constants in `glyph_scorer.py`:

- `CHUNK_SIZE = 64` - Glyphs per API conversation
- `SCORE_THRESHOLD = 7` - Minimum score to advance to next round
- `FINAL_COUNT = 64` - Target number of final glyphs
- `FREE_TIER_SLEEP = 4` - Delay between requests (free tier)
- `PAID_TIER_SLEEP = 0.1` - Delay for paid tier

## Output

- `data/round_N.jsonl` - Results from each round (chunk results, scores, API responses)
- `data/quota_tracking.json` - Daily quota usage tracking
- `data/final.txt` - Final 64 glyphs (one per line)

## Features

- **Scale optimized**: Handles 105k glyphs efficiently
- **Multi-day batching**: Free tier auto-splits work across days with perfect resume
- **Quota tracking**: Automatic daily quota management in `data/quota_tracking.json`
- **Paid tier mode**: Fast single-session processing via environment variable
- **Multiple prompts**: Choose between prompt1, prompt2, or prompt3
- **Configuration validation**: Checks prompts, ranges, and API key before starting
- **Cost estimation**: Shows estimated API cost and time before each round
- **Checkpoint/resume**: Automatically resumes from existing rounds if interrupted  
- **Progress tracking**: Real-time progress bars with tqdm
- **Rate limit handling**: Exponential backoff on 429 errors
- **Modular prompts**: Easy to create custom strategies

## Prompt Strategies

### Prompt 1 (`prompts/prompt1/`)
Visual complexity scoring: stroke count, intricacy, and pattern complexity.

### Prompt 2 (`prompts/prompt2/`)
Aesthetic scoring: visual beauty, balance, and elegance.

### Prompt 3 (`prompts/prompt3/`)
Uniqueness scoring: distinctiveness, rarity, and memorability.

## Creating Custom Prompts

1. Create a new directory: `prompts/your_strategy/`
2. Add `turn1.txt` with first turn prompt (include `{glyphs}` placeholder)
3. Add `turn2.txt` with second turn prompt (request format: `<glyph> <score>`)
4. Update `AVAILABLE_STRATEGIES` list in `glyph_scorer.py`
5. Run: `python glyph_scorer.py your_strategy`

## Flow

```
Round 1: 105k glyphs → ~7k (score ≥ 7)
  FREE: 3 days × 1500 requests
  PAID: 3.3 hours × 3282 requests
Round 2: 7k glyphs → ~400
Round 3: 400 glyphs → ~100  
Round 4: 100 glyphs → 64
Final: 64 glyphs saved
```

## Multi-Day Batching (Free Tier)

The free tier automatically batches work across days:

**Day 1:**
```bash
$env:GEMINI_PAID_TIER="false"  # Enable free tier
python glyph_scorer.py prompt1
# Processes 750 chunks (1500 requests)
# Script exits with progress saved
```

**Day 2:**
```bash
python glyph_scorer.py prompt1  
# Auto-resumes from chunk 750
# Processes next 750 chunks
# Script exits with progress saved
```

**Day 3:**
```bash
python glyph_scorer.py prompt1
# Completes remaining ~140 chunks
# Round 1 complete!
```

Quota tracking is automatic via `data/quota_tracking.json`.

## Cost & Time

### Paid Tier (Default)
- **Cost**: ~$6.56 for R1, ~$7 total
- **Time**: ~3.3 hours for R1
- **Effort**: Single continuous run
- **Total**: 4-5 hours for complete 4-round filtering

### Free Tier (opt-in with `GEMINI_PAID_TIER=false`)
- **Cost**: $0
- **Time**: ~3 days for R1 (1500 req/day limit)
- **Effort**: Run script once per day
- **Total**: 3-4 days for complete 4-round filtering

### Cost Breakdown (Paid)
- **Model**: gemini-3-flash-preview
- **Rates**: $0.075/1M input tokens, $0.30/1M output tokens
- **R1**: 105k glyphs = 3282 requests = ~$6.56
- **R2-R4**: ~$0.50 combined

## Rate Limit Management

- **Free tier**: Auto-batches to 1500 requests/day, resumes next day
- **Paid tier**: No practical limits
- **Retry logic**: Exponential backoff on 429 errors
- **Tracking**: Quota usage persisted in `data/quota_tracking.json`

## API Pattern

```python
model = genai.GenerativeModel("gemini-3-flash-preview")
chat = model.start_chat()
response1 = chat.send_message(PROMPT1)  # Turn 1: context
response2 = chat.send_message(PROMPT2)  # Turn 2: scoring
# Parse response2 for: <glyph> <score>
```
