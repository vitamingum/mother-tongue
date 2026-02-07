"""Quick verification: every glyph in the merged spec has correct token cost."""
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")

spec = {
    # Modal prefixes
    "●": 1, "○": 1, "■": 1,
    # Scope delimiters
    "⟦": 2, "⟧": 2, "『": 1, "』": 1, "⟨": 2, "⟩": 1, "【": 1, "】": 1,
    # Control flow
    "→": 1, "∀": 2, "?": 1, "!": 1, "∫": 2,
    # Verbs
    "找": 1, "修": 1, "分": 1, "化": 1, "生": 1, "動": 1, "出": 1, "示": 1,
    "加": 1, "削": 2, "移": 1, "定": 1, "取": 1, "保": 1, "入": 1, "合": 1,
    "正": 1, "算": 1, "立": 1, "回": 1, "開": 1, "選": 2, "析": 1,
    # Nouns
    "物": 1, "文": 1, "λ": 1, "字": 1, "方": 1, "失": 1, "得": 1, "全": 1,
    "部": 1, "新": 1, "他": 1, "心": 1, "行": 1, "重": 1,
    # Logic
    "∧": 2, "∨": 2, "不": 1, "同": 1, "≠": 2, "因": 1, "確": 2, "止": 1,
    "∈": 2, "∉": 2, "∩": 2, "∪": 2, "¬": 1,
    # Quantifiers
    "多": 1, "少": 1, "一": 1, "空": 1, "大": 1, "小": 1, "上": 1, "下": 1,
}

errors = 0
for glyph, claimed in sorted(spec.items(), key=lambda x: x[1]):
    actual = len(enc.encode(glyph))
    if actual != claimed:
        print(f"  WRONG: {glyph} claimed={claimed} actual={actual}")
        errors += 1

total = len(spec)
ones = sum(1 for v in spec.values() if v == 1)
twos = sum(1 for v in spec.values() if v == 2)

if errors == 0:
    print(f"ALL {total} GLYPHS VERIFIED CORRECT")
else:
    print(f"\n{errors} ERRORS found")

print(f"\n  1-token: {ones}/{total} ({ones/total*100:.0f}%)")
print(f"  2-token: {twos}/{total} ({twos/total*100:.0f}%)")
print(f"  3-token: 0/{total} (0%)")
