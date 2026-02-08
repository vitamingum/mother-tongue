"""Tokenize glyphs with o200k_base and filter to single-token glyphs."""
import sys

# Try to import tiktoken
try:
    import tiktoken
except ImportError:
    print("Installing tiktoken...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tiktoken"])
    import tiktoken

def get_single_token_glyphs(glyphs):
    """Filter glyphs that encode as exactly 1 token in o200k_base.
    
    Args:
        glyphs: list or set of characters
        
    Returns:
        list of single-token glyphs with their token IDs
    """
    enc = tiktoken.get_encoding("o200k_base")
    
    single_token = []
    for glyph in glyphs:
        tokens = enc.encode(glyph)
        if len(tokens) == 1:
            single_token.append((glyph, tokens[0]))
    
    return single_token

def main():
    if len(sys.argv) < 2:
        print("Usage: python tokenize_o200k.py <file_with_glyphs>")
        print("  File should contain glyphs, one per line or all on one line")
        sys.exit(1)
    
    # Read glyphs from file
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract unique glyphs (treat as individual characters)
    glyphs = set(content)
    # Remove whitespace
    glyphs = {g for g in glyphs if not g.isspace()}
    
    print(f"Total unique glyphs: {len(glyphs)}")
    
    single_token = get_single_token_glyphs(glyphs)
    
    print(f"Single-token glyphs in o200k_base: {len(single_token)}")
    print()
    
    # Sort by token ID for consistent output
    single_token.sort(key=lambda x: x[1])
    
    # Output results
    for glyph, token_id in single_token:
        print(f"{glyph}  (token {token_id})")
    
    # Also write to file
    output_file = sys.argv[1].replace('.txt', '_single_token.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        for glyph, token_id in single_token:
            f.write(f"{glyph}\n")
    
    print(f"\nSaved to: {output_file}")
    
    # Also create a compact version
    compact_file = sys.argv[1].replace('.txt', '_single_token_compact.txt')
    with open(compact_file, 'w', encoding='utf-8') as f:
        f.write(''.join(g for g, _ in single_token))
    
    print(f"Compact: {compact_file}")

if __name__ == "__main__":
    main()
