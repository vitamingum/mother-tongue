"""Check tokenization of specific glyphs."""
import sys

try:
    import tiktoken
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tiktoken"])
    import tiktoken

def check_glyphs(glyphs_str):
    """Check tokenization of specific glyphs."""
    enc = tiktoken.get_encoding("o200k_base")
    
    print("Glyph Tokenization Check (o200k_base)")
    print("=" * 50)
    
    for glyph in glyphs_str:
        tokens = enc.encode(glyph)
        status = "✓ SINGLE" if len(tokens) == 1 else f"✗ {len(tokens)} tokens"
        token_ids = ", ".join(str(t) for t in tokens)
        print(f"{glyph}  {status}  [{token_ids}]")

if __name__ == "__main__":
    # Check the mined favorites and proposed additions
    test_glyphs = "⊕⊗減加建天地創因果∧∨→●○■【】⟦⟧『』⟨⟩"
    
    check_glyphs(test_glyphs)
