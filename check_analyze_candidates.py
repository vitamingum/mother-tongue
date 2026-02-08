
import tiktoken

enc = tiktoken.get_encoding('o200k_base')

candidates = {
    '分': 'Current spec (Analyze / Divide)',
    '察': 'Examine / Observe / Scrutinize',
    '審': 'Judge / investigate / Audit',
    '檢': 'Check / Inspect / Examine',
    '究': 'Study / Investigate / Drill into',
    '鑑': 'Mirror / Reflect / Inspect / Discriminate',
    '研': 'Grind / Study / Research',
    '診': 'Diagnose (examine medical/system)',
    '閱': 'Read / Peruse / Review',
    '看': 'Look / Watch (maybe too common)',
    '解': 'Untie / Solve / Explain / Dissect',
    '剖': 'Dissect / Cut open (Anatomy)',
    '識': 'Know / Recognize / Identify',
    '測': 'Measure / Conjecture / Fathom',
    '繹': 'Unravel / Deduce / Interpret',
}

print(f"{'Glyph':<6} {'Token ID':<10} {'Tokens':<10} {'Meaning'}")
print("-" * 60)

for char, meaning in candidates.items():
    tokens = enc.encode(char)
    is_single = len(tokens) == 1
    token_str = str(tokens[0]) if is_single else str(tokens)
    
    # Check if it's a common CJK char (often shorter token IDs) vs rare
    # In o200k, lower IDs aren't necessarily "more common" in the same way as p50k, 
    # but single token is the requirement.
    
    print(f"{char:<6} {token_str:<10} {len(tokens):<10} {meaning}")
