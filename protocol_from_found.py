"""
Build the Opus→Sonnet protocol from found_glyphs.txt
Step 1: Which of these are 1-token? Which are 2? Which are 3?
Step 2: Map the protocol opcodes to the best available glyph.
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# All glyphs from found_glyphs.txt (deduplicated)
raw = """● ■ █ ☉ ⊗ ◉ ◆ ◈ ≡ ⇒ ⇔ ∴ ∞ ∫ ∮ ∑ ∏ ∧ ∨ ∈ ≠ ∀ ∃ 變 體
關 龍 鳳 鳴 類 題 饕 鮮 鲲 鶼 鹿 間 開 論 語 誠 韋 靈 非 腦 脑 聖 義 美 絲
網 積 窮 簡 確 眞 破 示 立 絕 機 變 轉 選 連 遠 返 近 複 装 規 視 讀 負 走
⭮ ♾ ⟲ ⟺ ↺ ↻ ⇻ ⇼ ⇜ ⇝ ⇐ ← → ↔ ↕ ↑ ↓ ↭ ↮ ↛ ↴ ↵ 【 】 《
》 「 」 『 』 〈 〉 〔 〕 ⟦ ⟧ ⟨ ⟩ ☌ ⊕ ⊞ ⊂ ⊃ ∩ ∪ ⊗ 物 心 坤 天
人 道 理 化 動 生 來 入 用 思 為 漢 汉 神 明 応 羊 米 王 爲 無 炁 濟 激 澄
潛 清 法 橆 樂 検 椉 更 普 時 无 數 敗 憲 慧 意 想 德 律 帝 問 哲 变 創 制
交 ╬ ╦ ╩ ╣ ╠ ╳ ┼ ╝ ╚ ╗ ╔ ║ ═ 女 元 中 全 多 大 小 真 善 不 火
力 利 腐 止 空 一 易 點 高 面 集 降 量 閉 身 足 終 算 移 看 目 監 減 正 析
書 暗 方 斷 文 拒 手 成 得 後 形 度 左 少 寫 実 定 字 始 增 地 四 器 向 合
右 口 去 升 勸 勵 勝 动 前 削 出 光 做 保 作 低 位 他 五 両 为 二 三 上 下
嬍 嫩 嫓 嫒 嫑 嫊 壹 土 囁 噵 叇 勷 劚 儾 太 新 言 失 同 加 修 水 找 分 因
回 行 取 重 部 送 囃 囂 囀 嚿 嚾 嚽 嚼 嚻 嚹 嚸 嚷 嚶 嚵 嚴 嚳 嚱 嚰 嚮 嚫
嚩 嚨 叢 叆 厵 厴 卛 匷 匶 勳 勴 劙 劘 劗 劖 劐 劎 劀 凟 冁 冀 兿 兾 兣 儽
儼 儻 儇 亹 乽 䨻 䜌 䄄 㫈 㚑 㓁 ◯ ○ ◐ ◎ ◌ ◦ ☆ ★ ⚛ ⚖ ⚗ ⚠ ⚡ ▲
△ ▼ ▽ ▶ ▷ ► ◀ ◁ ◄ ◇ ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ▏ ≥ ≤ ≒ ≈
≋ ∼ ≟ √ ∰ ⋯ ⏸ ⏹ ⏳ ⏿ ⏽ ⏤ ⏣ ⌲ ⌇ ⌖ ⍨ ⍰ ⍴ ⍷ ⍺ ⎃ ⎄ ⎋ ⎌
⫷ ⫸ ⮆ ⮌ ⮻ ⭐ ⩎ ⨾ ⨝ ⧵ ⧮ ⧗ ⧖ ⦀ ⦚ ⦸ ⥂ ⥎ ⥐ ⥮ ⥺ ⤴ ⤵ λ ι
！ ？ の · • ※ ‣ † ‡ ‽ § ¶ © ® ™ ° ± × ÷ ¬ — ש ␛ ␄ ␖
㄀ 。 ⁁ ⁐ ∉ ∎ ☯ ♠ ♣ ♥ ♦ ⛔ ⛬ 现 現 痛 癌 盡 相 积 統 線 置 耳 聲
能 舊 色 英 虛 蛋 观 间 飯 之 ? !"""

# Parse unique glyphs
glyphs = set()
for ch in raw:
    if ch.strip() and ch not in ' \n\t':
        glyphs.add(ch)

# Classify by token cost
by_cost = {1: [], 2: [], 3: [], 4: []}
for g in sorted(glyphs):
    t = len(enc.encode(g))
    bucket = min(t, 4)
    by_cost[bucket].append(g)

print("FOUND_GLYPHS.TXT TOKEN COST INVENTORY")
print("=" * 70)
for cost in [1, 2, 3, 4]:
    chars = by_cost[cost]
    print(f"\n{cost}-TOKEN ({len(chars)} glyphs):")
    # Group meaningfully
    for i in range(0, len(chars), 30):
        print("  " + " ".join(chars[i:i+30]))

# Now map the protocol opcodes
print("\n\n" + "=" * 70)
print("PROTOCOL OPCODE MAPPING (from found_glyphs.txt, 1-token preferred)")
print("=" * 70)

# The opcodes we need for Opus→Sonnet protocol
opcodes = [
    # VERBS (actions Sonnet should take)
    ("FIND/SEARCH", "找", "find"),
    ("FIX/REPAIR", "修", "repair"),
    ("READ/ANALYZE", "分", "analyze/divide"),
    ("TRANSFORM", "化", "transform"),
    ("CREATE/GEN", "生", "give birth"),
    ("RUN/EXECUTE", "動", "move/act"),
    ("SEND/OUTPUT", "出", "exit/output"),
    ("SHOW/DISPLAY", "示", "show"),
    ("ADD/INSERT", "加", "add"),
    ("DELETE/REMOVE", "削", "cut away"),
    ("MOVE", "移", "move"),
    ("SET/ASSIGN", "定", "fix/settle"),
    ("TEST/CHECK", "検", "examine"),
    ("OPEN/START", "開", "open"),
    ("CLOSE/END", "閉", "close"),
    ("SAVE/KEEP", "保", "protect/keep"),
    ("GET/FETCH", "取", "take/get"),
    ("SELECT/CHOOSE", "選", "choose"),
    ("WRITE", "書", "write"),
    ("COPY", "做", "make/do"),
    ("COMPARE", "合", "combine/match"),
    ("SORT/ORDER", "正", "correct/order"),
    ("COUNT", "算", "calculate"),
    ("WAIT/PAUSE", "止", "stop"),
    ("RETRY", "回", "return"),
    
    # NOUNS (targets)
    ("FILE/OBJECT", "物", "thing"),
    ("CODE/TEXT", "文", "text/writing"),
    ("FUNCTION", "λ", "lambda"),
    ("NAME/WORD", "字", "character"),
    ("DATA/INFO", "方", "direction/method"),
    ("ERROR/FAULT", "失", "lose/fail"),
    ("RESULT/OUTPUT", "得", "obtain"),
    ("ALL/SCOPE", "全", "all/complete"),
    ("PART/PIECE", "部", "part/section"),
    ("NEW", "新", "new"),
    ("OLD", "舊", "old"),
    ("SELF/THIS", "心", "heart/mind"),
    ("OTHER", "他", "other"),
    
    # CONNECTIVES (logic/flow)
    ("THEN/SEQUENCE", "→", "arrow"),
    ("AND", "∧", "logical and"),
    ("OR", "∨", "logical or"),
    ("NOT/NEGATE", "不", "not"),
    ("IF/CONDITION", "?", "question"),
    ("IN/SCOPE", "∈", "element of"),
    ("EQUALS", "同", "same"),
    ("BECAUSE/CAUSE", "因", "cause"),
    ("THEREFORE", "∴", "therefore"),
    
    # QUANTIFIERS
    ("MANY/MULTI", "多", "many"),
    ("FEW/SOME", "少", "few"),
    ("ONE/SINGLE", "一", "one"),
    ("EACH/EVERY", "∀", "for all"),
    ("EXISTS/ANY", "∃", "exists"),
    ("NONE/ZERO", "空", "empty"),
    ("BIG/MORE", "大", "big"),
    ("SMALL/LESS", "小", "small"),
    ("GOOD/BEST", "上", "above/top"),
    ("BAD/WORST", "下", "below/bottom"),
    
    # STRUCTURE
    ("GROUP_OPEN", "【", "bracket"),
    ("GROUP_CLOSE", "】", "bracket"),
    ("SCOPE_OPEN", "⟦", "double bracket"),
    ("SCOPE_CLOSE", "⟧", "double bracket"),
    ("IMPORTANT", "!", "bang"),
    ("QUERY", "?", "question"),
]

# Check token costs
print(f"\n{'Opcode':<18} {'Glyph':>5} {'Tok':>4}  {'CJK meaning':<20}")
print("-" * 55)
one_tok = two_tok = three_tok = 0
for name, glyph, meaning in opcodes:
    t = len(enc.encode(glyph))
    marker = "" if t == 1 else f" ← {t}-tok!"
    if t == 1: one_tok += 1
    elif t == 2: two_tok += 1
    else: three_tok += 1
    print(f"  {name:<18} {glyph:>3} {t:>3}   {meaning:<20}{marker}")

total = one_tok + two_tok + three_tok
print(f"\n  SUMMARY: {one_tok}/{total} are 1-token ({one_tok/total*100:.0f}%)")
print(f"           {two_tok}/{total} are 2-token")
print(f"           {three_tok}/{total} are 3-token")

# Demo: rewrite the 5 test cases with ONLY found_glyphs.txt characters
print("\n\n" + "=" * 70)
print("PROTOCOL DEMO (only using found_glyphs.txt characters)")
print("=" * 70)

demos = [
    ("Refactor auth module",
     "Read auth.py, identify public functions. Extract token validation to validate_token(). Extract rate limiting from login/refresh to decorator. Standardize errors to AuthError(code). Add type hints. Don't change signatures. Run tests.",
     "分【auth.py】→ 找 全 public λ\n取【token検】→ 新λ\n取【rate制】∈ login,refresh → 新λ\n定 全 error → 一 形\n加 type → 全 public λ\n不化 signatures\n動 tests"),
    
    ("Debug webhook test",
     "Fix test_payment_webhook. Cause: HMAC(json.dumps) != HMAC(raw body) due to key reordering. Fix: compute body first, derive sig from it, send body not dict. Run test. Find same bug elsewhere.",
     "修 test_payment_webhook\n因: HMAC(json.dumps) ≠ HMAC(raw body)\n定 body=json.dumps(payload)\n定 sig=HMAC(body)\n出 body 不 dict\n動 test\n找 同 ∈ 他 tests → 修"),
    
    ("Add pagination",
     "Add pagination to /api/users. Add page/per_page params. Use LIMIT/OFFSET. Add response metadata. Add Link headers. Update OpenAPI. Add tests. Update frontend fetchAll to fetchPage.",
     "加 pagination →【/api/users】\n加 params: page, per_page\nDB: 加 LIMIT+OFFSET\n加 meta → 得\n加 Link headers\n修 OpenAPI\n加 tests: 全 cases\n修 frontend: fetchAll → fetchPage"),
    
    ("CSV pipeline",  
     "Parse CSV (fail = error + line). Validate rows: email, age 0-150, name non-empty. Collect all errors. If >10% bad, reject all. Normalize valid rows. Dedup by email. Batch insert 500. Return summary.",
     "分 CSV → ? 失 → 出 error+line\n検 行: email ∧ age ∧ 字 不空\n集 全 失 (不止)\n? 失 > 10% → 出 全 失\n正 valid: lower,trim\n去 重 ∈ email\n入 DB ×500\n出 {入,去,失}"),

    ("Redis→PG migration",
     "Migrate sessions from Redis to PostgreSQL. Create table, add indexes, implement SessionStore, migration script, feature flag, monitor 48h, flip default, add cleanup cron.",
     "Redis → PG sessions\n生 table: id,user_id,data,times\n加 index: expires,user_id\n生 SessionStore λ: CRUD+cleanup\n生 migration: Redis → PG\n定 flag SESSION_STORE=pg\n検 48h: 不失\n定 default=pg\n加 cron cleanup 15min"),
]

for name, english, glyph in demos:
    e = len(enc.encode(english))
    g = len(enc.encode(glyph))
    pct = (1 - g/e) * 100
    print(f"\n  [{name}]  EN={e} → GL={g}  ({pct:.0f}% savings)")
    print(f"  {'─' * 55}")
    for line in glyph.split('\n'):
        print(f"  {line}")

# Final totals
en_total = sum(len(enc.encode(e)) for _, e, _ in demos)
gl_total = sum(len(enc.encode(g)) for _, _, g in demos)
print(f"\n\n  TOTAL: EN={en_total} → GL={gl_total}  ({(1-gl_total/en_total)*100:.0f}% savings)")
print(f"  Average savings per handoff: {(en_total-gl_total)//len(demos)} tokens")

# At scale
print(f"\n  AT SCALE (1000 handoffs/day):")
daily_saved = 1000 * (en_total - gl_total) // len(demos)
print(f"  Tokens saved/day: {daily_saved:,}")
print(f"  At Sonnet $3/1M input: ${daily_saved * 3 / 1_000_000:.2f}/day")
print(f"  At Sonnet $3/1M input: ${daily_saved * 3 / 1_000_000 * 30:.2f}/month")
