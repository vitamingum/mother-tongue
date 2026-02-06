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
   
   # Or create .env file (copy from .env.example)
   ```

3. **Configure Unicode ranges** in `glyph_scorer.py`:
   ```python
   UNICODE_RANGES = [
       (0x0000, 0x6400),  # Replace with actual ranges
   ]
   ```

4. **Configure prompts** in `glyph_scorer.py`:
   - `PROMPT1`: First turn prompt (include `{glyphs}` placeholder)
   - `PROMPT2`: Second turn prompt requesting scores in format: `<glyph> <score>`

## Usage

```bash
python glyph_scorer.py
```

## Configuration Options

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
