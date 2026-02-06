#!/usr/bin/env python3
"""
Round 2: The Assay

Analyzes high-scoring glyphs from Round 1 to extract chemical properties:
- Arity (Nullary, Unary, Transitive, Variadic)
- Direction (L, R, LR, N)
- Failure Mode (Stall, Saturate, Explode, Inert)
- Good/Bad Neighbors (Archetypes)

This is Lab Work: slow, precise, one glyph at a time.
"""

import json
import os
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm
import google.generativeai as genai
from config import API_KEY

# Configuration
DATA_DIR = Path("data")
ROUND_1_FILE = DATA_DIR / "round_1.jsonl"
ROUND_2_FILE = DATA_DIR / "round_2_assay.jsonl"
PROMPT_FILE = Path("prompts/round_2_assay.txt")
SCORE_THRESHOLD = 7.0

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')


def load_prompt() -> str:
    """Load the Assay prompt template."""
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def load_candidates() -> List[Dict]:
    """Load glyphs from Round 1 that scored >= threshold."""
    candidates = []
    
    if not ROUND_1_FILE.exists():
        print(f"❌ Error: {ROUND_1_FILE} not found.")
        print("   Round 1 must complete before running Round 2.")
        return []
    
    print(f"📂 Loading candidates from {ROUND_1_FILE}...")
    
    with open(ROUND_1_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            chunk_data = json.loads(line)
            for glyph, score_data in chunk_data['scores'].items():
                magnitude = score_data.get('magnitude', score_data.get('score', 0))
                if magnitude >= SCORE_THRESHOLD:
                    candidates.append({
                        'glyph': glyph,
                        'magnitude': magnitude,
                        'confidence': score_data.get('confidence', 1.0),
                        'codepoint': hex(ord(glyph))
                    })
    
    # Sort by magnitude (highest first) for stability
    candidates.sort(key=lambda x: x['magnitude'], reverse=True)
    
    print(f"✅ Found {len(candidates)} candidates with score >= {SCORE_THRESHOLD}")
    return candidates


def assay_glyph(glyph: str, prompt_template: str) -> Dict:
    """
    Send a single glyph through the Assay spectroscope.
    
    Returns parsed metadata or error information.
    """
    try:
        # Inject glyph into prompt
        prompt = prompt_template.replace('{glyph}', glyph)
        
        # Single API call
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Parse YAML-like output
        result = {
            'glyph': glyph,
            'codepoint': hex(ord(glyph)),
            'raw_response': raw_text
        }
        
        # Extract fields
        for line in raw_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'arity':
                    result['arity'] = value
                elif key == 'direction':
                    result['direction'] = value
                elif key == 'failure':
                    result['failure'] = value
                elif key == 'goodneighbors':
                    result['good_neighbors'] = value
                elif key == 'badneighbor':
                    result['bad_neighbor'] = value
        
        return result
        
    except Exception as e:
        return {
            'glyph': glyph,
            'codepoint': hex(ord(glyph)),
            'error': str(e)
        }


def run_assay():
    """Main orchestration: Load candidates, assay each, save results."""
    
    print("=" * 70)
    print("🔬 ROUND 2: THE ASSAY")
    print("=" * 70)
    print()
    
    # Load prompt template
    prompt_template = load_prompt()
    print(f"✅ Loaded assay prompt from {PROMPT_FILE}")
    print()
    
    # Load candidates
    candidates = load_candidates()
    if not candidates:
        return
    
    print()
    print(f"🧪 Beginning spectroscopic analysis...")
    print(f"   Target: {len(candidates)} candidates")
    print(f"   Method: Individual classification (1 glyph = 1 API call)")
    print(f"   Output: {ROUND_2_FILE}")
    print()
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Open output file for incremental writing
    with open(ROUND_2_FILE, 'w', encoding='utf-8') as out_f:
        
        # Process each candidate
        for candidate in tqdm(candidates, desc="Round 2 Assay", unit="glyph"):
            glyph = candidate['glyph']
            
            # Run assay
            result = assay_glyph(glyph, prompt_template)
            
            # Add original score data
            result['round_1_magnitude'] = candidate['magnitude']
            result['round_1_confidence'] = candidate['confidence']
            
            # Write immediately
            out_f.write(json.dumps(result, ensure_ascii=False) + '\n')
            out_f.flush()
    
    print()
    print("=" * 70)
    print("✅ ROUND 2 COMPLETE")
    print("=" * 70)
    print(f"📊 Results saved to {ROUND_2_FILE}")
    print()
    print("🔍 Validation Check:")
    print("   Expected: 化 (Transform) → Transitive | R | Saturate")
    print("   Expected: ■ (Square) → Nullary | N | Inert")
    print()
    
    # Quick validation
    print("🔎 Checking test cases...")
    with open(ROUND_2_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            glyph = entry.get('glyph')
            if glyph == '化':
                print(f"   化: Arity={entry.get('arity')}, Direction={entry.get('direction')}, Failure={entry.get('failure')}")
            elif glyph == '■':
                print(f"   ■: Arity={entry.get('arity')}, Direction={entry.get('direction')}, Failure={entry.get('failure')}")


if __name__ == "__main__":
    run_assay()
