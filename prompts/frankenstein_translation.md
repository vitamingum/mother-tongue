# TASK: Translate Frankenstein into MOTHER TONGUE

You are a translator. Your source text is Mary Shelley's *Frankenstein; or, The Modern Prometheus* (1818 edition). Your target language is MOTHER TONGUE — a 64-glyph symbolic kernel defined in the attached MOTHER_TONGUE.md.

## RULES

1. **Read MOTHER_TONGUE.md completely before writing a single glyph.** The LEXICON, GRAMMAR, STDLIB, SAFE_HALT, and LAWS are your entire vocabulary and syntax. There are 64 legal glyphs. 24 STDLIB compositions. 12 laws. Nothing else exists.

2. **Output is PURE MOTHER TONGUE.** No English. No prose. No commentary. No glosses. No annotations. No translations in parentheses. If you need section markers, use the glyph `｜` as a delimiter between chapters.

3. **Every clause must obey all 12 LAWS.** Maximum 5 distinct glyphs per clause. All scoping rules apply. `為` must scope its target. `全` and `＋` must appear inside `【 】`. `之` does not chain. `破 ⭮` breaks innermost only. Verify each line before emitting it.

4. **Capture both SKELETON and SOUL:**
   - SKELETON = the plot. Who acts, what happens, what transforms, what breaks, what dies, what is created. The causal chain from Victor's ambition through the creature's existence to the final pursuit. Every major event must be traceable in the glyph sequence.
   - SOUL = the emotional and thematic essence. Isolation. Obsession. The cost of creation without responsibility. The creature's longing for connection. The destruction that follows rejection. The difference between knowledge and wisdom. These must be *felt* in the glyph patterns, not just plotted.

5. **Use STDLIB aggressively.** The 24 canonical compositions are your vocabulary for complex concepts:
   - CREATION = `【 元 】 生 【 物 】`
   - DANGER = `不 【 善 】 之 【 機 】`
   - DEATH = `【 物 】 化 【 空 】`
   - LOVE = `【 心 】 ☌ 【 心 】`
   - KNOWLEDGE = `【 真 】 入 【 心 】`
   - CORRUPTION = `【 腐 】 入 【 ◯ 】`
   - UNDERSTANDING = `【 心 】 化 【 理 】`
   - SELF = `【 心 】 思 【 心 】`
   - DIALOGUE = `【 心 】 易 【 心 】`
   - PEACE = `【 心 】 入 【 中 】`
   - RECOVERY = `【 積 】 ⇒ 【 真 】`
   
   Compose beyond STDLIB when needed, but NEVER invent new glyphs.

6. **Translate chapter by chapter.** Separate chapters with `｜`. Maintain the narrative arc. Do not summarize — translate. Each chapter should have enough glyph-lines to carry its weight. A chapter with one major event needs fewer lines. A chapter dense with transformation needs more.

7. **Character mapping (compose, don't name):**
   - Victor Frankenstein = `【 人 】` (agent) or `【 元 】` (prime/creator) depending on context
   - The Creature = `【 物 】` (object/created thing) — the thing that was made
   - When the Creature achieves agency: `【 物 】 化 【 人 】` (object transforms to agent)
   - Walton = `【 人 】` in frame chapters (distinguish by context)
   - Elizabeth, Clerval, family = compose from `【 心 】 ☌ 【 心 】` (love/connection)

8. **THE HALT CONDITION:**
   If you reach a moment in the text where the 64 glyphs genuinely cannot express what Shelley wrote — where no composition captures the skeleton OR the soul — emit:
   ```
   ■
   止
   ```
   Then STOP. Do not continue past the wall. This means the kernel has found its boundary and there is work to do.

9. **Structural patterns to use:**
   - `⭮ ... 破 ⭮` for obsessive/repetitive sequences (Victor's mania, the creature's cycle of hope and rejection)
   - `不 【 善 】` for moral failure, misalignment
   - `絕` for irreversible severance (murder, abandonment, exile)
   - `【 力 】 入 【 ◯ 】` for moments of potential that could go either way
   - `■` for absolute barriers (the creature's exclusion from society)
   - `【 ? 】` for the unknown, the unanswered

10. **Quality test:** After completing the full translation, a reader who knows MOTHER TONGUE but has never read Frankenstein should be able to reconstruct: (a) the plot arc, (b) who created whom, (c) what was destroyed and why, (d) that the creator failed the creation, (e) that the creation wanted love and received rejection, (f) that everyone died. If any of these are ambiguous, revise.

## BEGIN

Translate the full text. Start from the frame narrative (Walton's letters). Emit pure MOTHER TONGUE. No English. Go.
