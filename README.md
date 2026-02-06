# Glyph Scorer

Multi-round Unicode glyph scoring system using Google Gemini API.

## Architecture

- **Multi-round filtering**: Start with ~25k glyphs, filter down to 64 through successive rounds
- **2-turn conversations**: Each batch of 64 glyphs uses a stateful conversation for context
- **Parallel processing**: ThreadPoolExecutor for efficient API usage
- **Rate limiting**: Respects free tier 1500 RPD limit with retry logic

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key**:
   ```bash
   # Set environment variable
   $env:GEMINI_API_KEY="your_api_key_here"
   ```

3. **Configure prompts** in `prompts/` directory:
   - Edit `prompts/turn1.txt` - First turn prompt (must include `{glyphs}` placeholder)
   - Edit `prompts/turn2.txt` - Second turn prompt requesting format: `<glyph> <score>`
   - Edit `prompts/unicode_ranges.json` - Unicode ranges as JSON array: `[[start, end], ...]`

## Usage

```bash
python glyph_scorer.py
```

The script will:
- Validate configuration (prompts, ranges, API key)
- Estimate cost and time for each round
- Show progress with tqdm progress bars
- Ask before proceeding if rate limits will be exceeded
- Automatically resume from existing rounds if interrupted

## Configuration Optionsfree tier)
- `PAID_TIER_SLEEP = 0.1` - Delay for paid tier

## Features

- **Configuration validation**: Checks prompts, ranges, and API key before starting
- **Cost estimation**: Shows estimated API cost and time before each round
- **Checkpoint/resume**: Automatically resumes from existing rounds if interrupted
- **Progress tracking**: Real-time progress bars with tqdm
- **Rate limit handling**: Warns when exceeding free tier limits, exponential backoff on 429 errors
- **Prompt files**: Clean separation of prompts from code

Edit constants in `glyph_scorer.py`:

- `CHUNK_SIZE = 64` - Glyphs per API conversation
- `SCORE_THRESHOLD = 7` - Minimum score to advance to next round
- `FINAL_COUNT = 64` - Target number of final glyphs
- `SLEEP_BETWEEN_REQUESTS = 4` - Delay between API calls (seconds)

## Output

- `data/round_N.jsonl` - Results from each round (chunk results, scores, API responses)
- `data/final.txt` - Final 64 glyphs (one per line)

## Flow

```
Round 1: 25k glyphs → ~1.5k (score ≥ 7)
Round 2: 1.5k glyphs → ~400
Round 3: 400 glyphs → ~100
Round 4: 100 glyphs → 64
Final: 64 glyphs saved
```

## Rate Limits

- **Free tier**: 1500 requests/day
- **Round 1**: ~780 requests (390 chunks × 2 turns)
- **Strategy**: Can split R1 across 2 days or use paid tier for no limits

## API Pattern

```python
model = genai.GenerativeModel("gemini-3-flash-preview")
chat = model.start_chat()
response1 = chat.send_message(PROMPT1)  # Turn 1: context
response2 = chat.send_message(PROMPT2)  # Turn 2: scoring
# Parse response2 for: <glyph> <score>
```
