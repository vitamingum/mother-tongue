"""Test with more meaningful glyphs - CJK and symbolic."""
import asyncio
import sys
sys.path.insert(0, '.')

from runner_async import AsyncOllamaRunner

async def test_meaningful_slate():
    """Test with glyphs that have strong semantic meaning."""
    print("🔍 Testing meaningful glyphs...\n")
    
    # Test with different categories
    test_cases = [
        # CJK verbs/actions
        {
            'name': 'CJK Actions',
            'slate': '找修分轉生執出寫示加刪移定取保入辨合聯畢序算立回開選析類組異縮複封止破變創統判處造增減測調整建設新舊',
            'set': {ord(c) for c in '找修分轉生執出寫示加刪移定取保入辨合聯畢序算立回開選析類組異縮複封止破變創統判處造增減測調整建設新舊'}
        },
        # Logic & Math symbols
        {
            'name': 'Logic/Math',
            'slate': '∧∨∈∉→←↔⇒⇔≡≠∩∪⊂⊃∀∃¬∞±×÷=≈≤≥∫∑∏∂√∆λμπσφψω',
            'set': {ord(c) for c in '∧∨∈∉→←↔⇒⇔≡≠∩∪⊂⊃∀∃¬∞±×÷=≈≤≥∫∑∏∂√∆λμπσφψω'}
        },
        # Shapes & Symbols
        {
            'name': 'Shapes/Symbols',
            'slate': '●○◯■□▪▫◆◇★☆▲△▼▽◀▶⬆⬇⬅➡↗↘↙↖⊕⊗⊙⊘✓✗✕✖⚡⚠☢☣',
            'set': {ord(c) for c in '●○◯■□▪▫◆◇★☆▲△▼▽◀▶⬆⬇⬅➡↗↘↙↖⊕⊗⊙⊘✓✗✕✖⚡⚠☢☣'}
        },
        # CJK concepts
        {
            'name': 'CJK Concepts',
            'slate': '天地人物心道理氣元空時間因果真實虛無始終全部中內外上下左右東西南北善惡陰陽動靜生死成敗進退得失強弱大小多少',
            'set': {ord(c) for c in '天地人物心道理氣元空時間因果真實虛無始終全部中內外上下左右東西南北善惡陰陽動靜生死成敗進退得失強弱大小多少'}
        },
        # Brackets & Delimiters
        {
            'name': 'Delimiters',
            'slate': '【】『』「」《》〈〉〔〕（）［］｛｝⟨⟩⟦⟧⦃⦄⦗⦘⸢⸣⸤⸥',
            'set': {ord(c) for c in '【】『』「」《》〈〉〔〕（）［］｛｝⟨⟩⟦⟧⦃⦄⦗⦘⸢⸣⸤⸥'}
        },
    ]
    
    async with AsyncOllamaRunner('qwen2.5-coder:14b', max_concurrent=1) as runner:
        for case in test_cases:
            print(f"\n━━ {case['name']} ━━")
            
            # Run 3 times to see variety
            for attempt in range(3):
                output = await runner.infer_one(case['slate'], temperature=0.7)
                result = runner.parse_output(output, case['set'])
                
                if result:
                    g1, g2 = chr(result[0]), chr(result[1])
                    print(f"  {attempt+1}: {g1} {g2}")
                else:
                    print(f"  {attempt+1}: [invalid]")

if __name__ == "__main__":
    asyncio.run(test_meaningful_slate())
