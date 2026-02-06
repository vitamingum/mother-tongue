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
   $env:GEMINI_API_KEY="your_api_key_here"
   ```

3. **Configure Unicode ranges**:
   - Edit `prompts/unicode_ranges.json` - Format: `[[start, end], ...]`
   - Example: `[[0, 25600], [0x4E00, 0x9FFF]]`

4. **Choose a scoring strategy** (or create your own):
   - `complexity` - Scores based on visual complexity and stroke count
   - `aesthetic` - Scores based on visual beauty and elegance
   - `uniqueness` - Scores based on distinctiveness and rarity

## Usage

```bash
# Run with a specific strategy
python glyph_scorer.py complexity
python glyph_scorer.py aesthetic
python glyph_scorer.py uniqueness

# Or use default (complexity)
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

- **Multiple scoring strategies**: Choose between complexity, aesthetic, or uniqueness scoring
- **Configuration validation**: Checks prompts, ranges, and API key before starting
- **Cost estimation**: Shows estimated API cost and time before each round
- **Checkpoint/resume**: Automatically resumes from existing rounds if interrupted
- **Progress tracking**: Real-time progress bars with tqdm
- **Rate limit handling**: Warns when exceeding free tier limits, exponential backoff on 429 errors
- **Modular prompts**: Easy to create custom strategies by adding new prompt directories

## Scoring Strategies

### Complexity (`prompts/complexity/`)
Scores glyphs 0-10 based on visual complexity, stroke count, and intricacy. Higher scores for characters with many strokes and complex patterns.

### Aesthetic (`prompts/aesthetic/`)
Scores glyphs 0-10 based on visual beauty, balance, and elegance. Higher scores for visually pleasing and well-proportioned characters.

### Uniqueness (`prompts/uniqueness/`)
Scores glyphs 0-10 based on distinctiveness and rarity. Higher scores for unusual, memorable, or uncommon characters.

## Creating Custom Strategies

1. Create a new directory: `prompts/your_strategy/`
2. Add `turn1.txt` with first turn prompt (include `{glyphs}` placeholder)
3. Add `turn2.txt` with second turn prompt (request format: `<glyph> <score>`)
4. Update `AVAILABLE_STRATEGIES` list in `glyph_scorer.py`
5. Run: `python glyph_scorer.py your_strategy`

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
