"""Check token ID for 間."""
import tiktoken

enc = tiktoken.get_encoding("o200k_base")

glyph = "間"
tokens = enc.encode(glyph)

print(f"{glyph}")
print(f"Token count: {len(tokens)}")
print(f"Token ID: {tokens[0] if len(tokens) == 1 else tokens}")
