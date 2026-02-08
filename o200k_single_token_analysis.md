# O200K_BASE Single-Token Glyphs

**Source:** metacog_r1_all_glyphs.txt  
**Tokenizer:** o200k_base (GPT-4o / Claude 3.5 Sonnet)  
**Total:** 2,679 glyphs that encode as exactly 1 token

## Why This Matters

Single-token glyphs have the **strongest semantic grounding** in model training:
- 1 token = 1 embedding = 1 concept
- No semantic diffusion across multiple tokens
- Cleaner gradient paths during training
- More precise activation in latent space

## Analysis vs O-S Protocol Current Spec

### Already in Spec (Single-Token ✓)
- **加** ✓ (ADD)
- **減** ✓ (would be single-token if added)
- **∧ ∨** ✓ (AND/OR) 
- **→** ✓ (THEN)
- **因 果** ✓ (BECAUSE/RESULT)
- **找 修 分 轉 生 執 出 寫 示 刪 移 定 取 保 入 辨 合 聯 畢 序 算 立 回 開 選 析 類 組 異 縮 複 封** ✓ (most verbs)
- **物 文 名 資 失 全 部 新 別 己 間 排 重 閾** ✓ (most nouns)
- **不 同 確 止 無 小 上 多 少 一 空** ✓ (logic/quantifiers)

### Mined Favorites Status
From earlier test:
- **⊕** → Need to check (likely 1 token)
- **⊗** → Need to check (likely 1 token)  
- **建** → Present in 2679 list
- **天 地** → Both present
- **創** → Present

### High-Frequency CJK (Top 100)
The most common characters (top of frequency distribution) are single-token:
的, 不, 一, 是, 了, 人, 我, 在, 有, 他, 这, 为, 之, 大, 来, 以, 个, 中, 上, 们, 到, 说, 国, 和, 地, 得, 也, 时, 要, 就, 那, 去, 生, 可, 所, ...

## Recommendation for O-S Protocol

**Current spec verbs/symbols are well-chosen** — nearly all are single-token in o200k_base.

**For new additions:**
1. ⊕ ⊗ — Check tokenization, likely single-token (universal math symbols)
2. 減 — Single-token confirmed (subtraction complement to 加)
3. Any CJK verb from GB 2312 Level 1 (~3755 chars) will be single-token

**Avoid:**
- Rare/archaic CJK characters outside GB 2312
- Combining diacriticals  
- Emoji (most are multi-token except common ones like 😂 ❤ 🔥)
- Specialized Unicode blocks

## Complete List
See: [metacog_r1_all_glyphs_single_token_compact.txt](data/metacog_r1_all_glyphs_single_token_compact.txt)

2,679 glyphs total, includes:
- All common CJK (中日韓統一表意文字)
- Latin with diacritics (é, ñ, ü, etc.)
- Common math operators (∀, ∴, ∵, ≈, ≤, ≥, ∞, ∆, √, ∫, ∑, ∏, etc.)
- Common symbols (€, £, ¥, ©, ®, ™, †, ‡, •, ◆, ●, ○, ■, □, △, ▽, etc.)
- Punctuation variants
