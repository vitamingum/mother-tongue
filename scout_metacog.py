import json
import unicodedata

def get_name(char):
    try:
        return unicodedata.name(char)
    except ValueError:
        return f"U+{ord(char):04X}"

def main():
    scores = {}
    filepath = 'data/metacog_round_1.jsonl'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    chunk_scores = data.get('scores', {})
                    for glyph, score in chunk_scores.items():
                        # Handle different score formats if any
                        if isinstance(score, dict):
                             final_score = score.get('magnitude', 0)
                        else:
                             final_score = score
                        
                        scores[glyph] = float(final_score)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return

    # Filter for high scores (e.g., >= 9.0 for "scouting best candidates")
    high_scores = [(g, s) for g, s in scores.items() if s >= 9.0]
    
    # Sort by score descending
    high_scores.sort(key=lambda x: x[1], reverse=True)

    print(f"Found {len(high_scores)} glyphs with score >= 9.0 from {len(scores)} total scored.")
    print("-" * 60)
    print(f"{'Glyph':<6} {'Score':<6} {'Name'}")
    print("-" * 60)
    
    # Show top 20
    for glyph, score in high_scores[:20]:
        print(f"{glyph:<6} {score:<6.1f} {get_name(glyph)}")

    print("-" * 60)
    print("Scouting complete.")

if __name__ == "__main__":
    main()
