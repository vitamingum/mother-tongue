"""Explore very rare glyphs (120k+) for operational potential."""
import tiktoken

# CJK verbs and nouns in the rare range worth exploring
candidates = {
    # verbs
    '燃': 'burn/ignite',
    '識': 'recognize/know',
    '築': 'build/construct',  
    '減': 'subtract/decrease',
    '鍵': 'key/crucial',
    '競': 'compete',
    '績': 'achievement/result',
    '殺': 'kill/terminate',
    '織': 'weave/organize',
    '獲': 'obtain/acquire',
    '継': 'continue/inherit',
    '層': 'lay/stratum',
    '臓': 'organ/viscera',
    '蔵': 'store/hide',
    '鏈': 'chain/link',
    
    # potential operators
    '∞': 'infinity',
    '⊂': 'subset',
    '⊃': 'superset',
    '∴': 'therefore',
    '∵': 'because',
    '⊥': 'perpendicular/bottom',
    '∥': 'parallel',
}

enc = tiktoken.get_encoding("o200k_base")

results = []
for g, meaning in candidates.items():
    tokens = enc.encode(g)
    if len(tokens) == 1:
        results.append((g, tokens[0], meaning))

# Sort by token ID
results.sort(key=lambda x: x[1])

print("VERY RARE GLYPHS (Token ID > 120k)\n")
print("=" * 70)

rare_ops = [(g, t, m) for g, t, m in results if t >= 120000]
print(f"\nOperational Candidates ({len(rare_ops)} found):\n")

for g, tid, meaning in rare_ops:
    print(f"{g}  {tid:>6}  {meaning:<30}")

print("\n" + "=" * 70)
print("\nUnambiguity Analysis:\n")

# Check specific高-gravity candidates
focus = {
    '鍵': ('key/crucial', 'LOCK/UNLOCK operation, critical path'),
    '競': ('compete', 'RACE condition, concurrent execution'),
    '燃': ('burn/ignite', 'TRIGGER, initiate combustion'),
    '殺': ('kill/terminate', 'TERMINATE process/thread'),
    '築': ('build/construct', 'BUILD incrementally (vs 生 CREATE)'),
    '減': ('subtract/decrease', 'SUBTRACT (complement to 加 ADD)'),
    '識': ('recognize/know', 'IDENTIFY/RECOGNIZE pattern'),
    '鏈': ('chain/link', 'CHAIN operations together'),
}

for g in focus:
    tokens = enc.encode(g)
    if len(tokens) == 1:
        tid = tokens[0]
        meaning, operational = focus[g]
        print(f"\n{g} ({tid})")
        print(f"  Natural: {meaning}")
        print(f"  Operational: {operational}")
