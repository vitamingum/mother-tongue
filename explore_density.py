
import tiktoken

enc = tiktoken.get_encoding('o200k_base')

candidates = {
    # Architecure / Planning
    '謀': 'Scheme / Plan / Plot (heavy cognitive load)',
    '策': 'Strategy / Policy / Plan',
    '構': 'Construct / Compose / Fabricate',
    '築': 'Build / Construct (physical)',
    
    # Refining / Polishing / Improving
    '煉': 'Smelt / Refine (data/code)',
    '磨': 'Grind / Polish / Wear down',
    '精': 'Refined / Essence / Spirit',
    
    # Filtering / Pruning
    '篩': 'Sieve / Filter / Screen',
    '選': 'Select (current spec)',
    '擇': 'Pick / Choose (more decisive)',
    '汰': 'Eliminate / Wash away',
    
    # Understanding / Insight
    '悟': 'Enlighten / Realize / Grok',
    '透': 'Penetrate / Thorough / Transparent',
    '晰': 'Clear / Distinct',
    
    # Validation / Rules
    '律': 'Law / Regulation / Discipline',
    '範': 'Pattern / Model / Example',
    '規': 'Rule / Regulation',
    
    # Execution / Force
    '獵': 'Hunt (aggressive search)',
    '捕': 'Catch / Arrest / Capture',
    '糾': 'Correct / Investigate / Entangle (error correction)',
    
    # Transformation
    '化': 'Transform / Melt / -ize',
    '譯': 'Translate / Interpret',
    '演': 'Perform / Evolve / Deduce',
}

print(f"{'Glyph':<6} {'Token ID':<10} {'Tokens':<10} {'Meaning'}")
print("-" * 60)

for char, meaning in candidates.items():
    tokens = enc.encode(char)
    is_single = len(tokens) == 1
    token_str = str(tokens[0]) if is_single else str(tokens)
    print(f"{char:<6} {token_str:<15} {len(tokens):<10} {meaning}")
