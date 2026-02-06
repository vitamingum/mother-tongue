"""Test decimal parsing fix"""
import re

def parse_scores_old(response: str, expected_glyphs: list) -> dict:
    """Old parser - integers only"""
    scores = {}
    pattern = r'^(.)\s+(\d+)$'
    for line in response.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        match = re.match(pattern, line)
        if match:
            glyph = match.group(1)
            score = int(match.group(2))
            if 0 <= score <= 10:
                scores[glyph] = score
    return scores

def parse_scores_new(response: str, expected_glyphs: list) -> dict:
    """New parser - accepts decimals"""
    scores = {}
    pattern = r'^(.)\s+(\d+(?:\.\d+)?)$'
    for line in response.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        match = re.match(pattern, line)
        if match:
            glyph = match.group(1)
            score = round(float(match.group(2)))
            if 0 <= score <= 10:
                scores[glyph] = score
        else:
            # Fallback parsing
            parts = line.split()
            if len(parts) >= 2:
                try:
                    glyph = parts[0]
                    score = round(float(parts[-1]))
                    if 0 <= score <= 10 and glyph in expected_glyphs:
                        scores[glyph] = score
                except (ValueError, IndexError):
                    pass
    return scores

# Test samples
test_response = """嫑 7.2
嫒 7.2
嫓 7.1
嫩 8.2
嫊 9.4
嬍 9.1"""

expected = ['嫑', '嫒', '嫓', '嫩', '嫊', '嬍']

old_scores = parse_scores_old(test_response, expected)
new_scores = parse_scores_new(test_response, expected)

print("Test Results:")
print("="*60)
print(f"Old parser (integers only): {len(old_scores)} scores")
print(f"New parser (decimals OK):   {len(new_scores)} scores")
print()
print("New parser results:")
for g, s in new_scores.items():
    print(f"  {g} → {s}")
print()
print(f"✅ Fix working: {len(new_scores) == 6}")
