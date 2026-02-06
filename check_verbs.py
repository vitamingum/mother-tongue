#!/usr/bin/env python3
"""Check scores for specific target glyphs."""

import json
from pathlib import Path

# Load all scores from round_1.jsonl
scores = {}
data_file = Path("data/round_1.jsonl")
if data_file.exists():
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            chunk = json.loads(line)
            scores.update(chunk['scores'])

# Target glyphs
targets = {
    '化': chr(0x5316),  # Transform
    '生': chr(0x751F),  # Generate/Life
    '用': chr(0x7528),  # Use/Utility
    '間': chr(0x9593),  # Between/Space
}

print("TARGET VERB SCORES:")
print("=" * 60)
for name, char in targets.items():
    score = scores.get(char, "NOT SCORED YET")
    print(f"{name:4s} ({char}, U+{ord(char):04X}): {score}")

print("\n" + "=" * 60)
print(f"Total glyphs scored: {len(scores):,}")
print(f"CJK range 19968-40959 status: scanning...")
