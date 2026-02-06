"""Test the updated m∴c parser"""
import re

def parse_scores(response: str, expected_glyphs: list) -> dict:
    """Parse scores with m∴c format support"""
    scores = {}
    pattern_mc = r'^(.)\s+(\d+(?:\.\d+)?)\s*∴\s*(\d+(?:\.\d+)?)$'
    pattern_simple = r'^(.)\s+(\d+(?:\.\d+)?)$'
    
    for line in response.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Try m∴c format first
        match = re.match(pattern_mc, line)
        if match:
            glyph = match.group(1)
            magnitude = round(float(match.group(2)))
            confidence = float(match.group(3))
            if 0 <= magnitude <= 10:
                scores[glyph] = magnitude
                print(f"  {glyph} → m={magnitude} (c={confidence:.2f})")
            continue
        
        # Try simple format
        match = re.match(pattern_simple, line)
        if match:
            glyph = match.group(1)
            score = round(float(match.group(2)))
            if 0 <= score <= 10:
                scores[glyph] = score
                print(f"  {glyph} → {score}")
            continue
        
        # Fallback
        parts = line.split()
        if len(parts) >= 2:
            try:
                glyph = parts[0]
                if '∴' in parts[-1]:
                    magnitude_str = parts[-1].split('∴')[0]
                    magnitude = round(float(magnitude_str))
                    if 0 <= magnitude <= 10 and glyph in expected_glyphs:
                        scores[glyph] = magnitude
                        print(f"  {glyph} → m={magnitude} (fallback)")
                else:
                    score = round(float(parts[-1]))
                    if 0 <= score <= 10 and glyph in expected_glyphs:
                        scores[glyph] = score
                        print(f"  {glyph} → {score} (fallback)")
            except (ValueError, IndexError):
                pass
    
    return scores

# Test cases
test_responses = [
    ("m∴c format", """間 10∴0.98
⧖ 9.5∴0.95
∰ 8.2∴0.9"""),
    
    ("Simple format", """間 10
⧖ 9
∰ 8"""),
    
    ("Mixed decimals", """間 10.0∴1.0
⧖ 9.4∴0.95
∰ 7.8∴0.88"""),
    
    ("Edge cases", """間 10∴1
⧖ 0∴0.5
∰ 5.5∴0.99"""),
]

expected = ['間', '⧖', '∰']

for name, response in test_responses:
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print('='*60)
    scores = parse_scores(response, expected)
    print(f"\nParsed {len(scores)}/{len(expected)} scores ✓" if len(scores) == len(expected) else f"ERROR: Only {len(scores)}/{len(expected)}")
