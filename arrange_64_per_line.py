import random

# Read shuffled glyphs
with open('data/metacog_r1_all_glyphs_shuffled.txt', 'r', encoding='utf-8') as f:
    glyphs = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(glyphs)} shuffled glyphs")

# Arrange in lines of 64
lines_of_64 = []
for i in range(0, len(glyphs), 64):
    line = glyphs[i:i+64]
    lines_of_64.append(''.join(line))

# Save
with open('data/metacog_r1_all_glyphs_64per_line.txt', 'w', encoding='utf-8') as f:
    for line in lines_of_64:
        f.write(f"{line}\n")

print(f"Created {len(lines_of_64)} lines of 64 glyphs each")
print(f"Saved to: data/metacog_r1_all_glyphs_64per_line.txt")
print(f"\nFirst line (64 glyphs):")
print(lines_of_64[0])
print(f"\nLast line ({len(glyphs) % 64 or 64} glyphs):")
print(lines_of_64[-1])
