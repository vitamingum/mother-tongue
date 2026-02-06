import json

# User's picks
user_ratings = {
    '間': 10,
    '⧖': 9,
    '∰': 8,
    '◈': 8,
    '⊗': 8,
    '⧮': 8,
    '儾': 8,
    '劚': 8,
    '勷': 8,
    '叇': 8,
    '囁': 8,
}

# Load AI scores
data = []
with open('data/round_1.jsonl', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

# Find matches
print("=" * 70)
print("YOUR PICKS vs AI SCORES")
print("=" * 70)

for glyph, user_score in sorted(user_ratings.items(), key=lambda x: -x[1]):
    ai_score = None
    for chunk in data:
        if glyph in chunk.get('scores', {}):
            ai_score = chunk['scores'][glyph]
            break
    
    if ai_score is not None:
        diff = user_score - int(ai_score)
        diff_str = f"({diff:+d})" if diff != 0 else "(match)"
        print(f"{glyph}  You: {user_score}  AI: {ai_score}  {diff_str}")
    else:
        print(f"{glyph}  You: {user_score}  AI: NOT SCORED YET")

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)
print(f"Total glyphs you picked: {len(user_ratings)}")
print(f"Your favorite (10): 間")
print(f"Your high picks (9): ⧖")
print(f"Your solid picks (8): {len([g for g, s in user_ratings.items() if s == 8])} glyphs")
