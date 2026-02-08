"""Reporting and stability analysis."""
import json
from pathlib import Path


def jaccard_similarity(set1, set2):
    """Calculate Jaccard similarity between two sets.
    
    Args:
        set1, set2: sets or lists
    
    Returns:
        float - Jaccard index (intersection / union)
    """
    s1 = set(set1)
    s2 = set(set2)
    
    if not s1 and not s2:
        return 1.0
    
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    
    return intersection / union if union > 0 else 0.0


def check_stability(top_n_history, threshold=0.98, consecutive_required=2):
    """Check if top-N selections have stabilized.
    
    Args:
        top_n_history: list of lists - top N from each pass
        threshold: float - Jaccard threshold for stability
        consecutive_required: int - consecutive passes needed
    
    Returns:
        tuple - (is_stable: bool, similarities: list)
    """
    if len(top_n_history) < 2:
        return False, []
    
    similarities = []
    for i in range(1, len(top_n_history)):
        sim = jaccard_similarity(top_n_history[i-1], top_n_history[i])
        similarities.append(sim)
    
    # Check for consecutive passes above threshold
    consecutive_count = 0
    for sim in reversed(similarities):
        if sim >= threshold:
            consecutive_count += 1
            if consecutive_count >= consecutive_required:
                return True, similarities
        else:
            consecutive_count = 0
    
    return False, similarities


def write_final_output(state, output_dir="output"):
    """Write all final outputs.
    
    Args:
        state: State object with final results
        output_dir: str - output directory path
    
    Returns:
        dict - paths to created files
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    final_glyphs = state.top_n(512)
    
    # Assertion: must be exactly 512
    if len(final_glyphs) != 512:
        raise AssertionError(f"Final output has {len(final_glyphs)} glyphs, expected 512")
    
    # Assertion: must be unique
    if len(set(final_glyphs)) != len(final_glyphs):
        raise AssertionError("Final output contains duplicates")
    
    paths = {}
    
    # final_512.txt - one glyph per line
    txt_path = output_path / "final_512.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        for cp in final_glyphs:
            f.write(f"{chr(cp)}\n")
    paths['txt'] = txt_path
    
    # final_512.json - structured data
    json_data = {
        'count': len(final_glyphs),
        'glyphs': [
            {
                'codepoint': cp,
                'char': chr(cp),
                'score': state.score.get(cp, 0.0),
                'seen': state.seen.get(cp, 0),
                'picked': state.picked.get(cp, 0),
                'byte_len': len(chr(cp).encode('utf-8'))
            }
            for cp in final_glyphs
        ]
    }
    json_path = output_path / "final_512.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    paths['json'] = json_path
    
    # edges.csv - all co-occurrence pairs
    edges_path = output_path / "edges.csv"
    with open(edges_path, 'w', encoding='utf-8') as f:
        f.write("glyph1,glyph2,cp1,cp2\n")
        for cp1, cp2 in state.edges:
            f.write(f"{chr(cp1)},{chr(cp2)},{cp1},{cp2}\n")
    paths['edges'] = edges_path
    
    return paths


def write_stability_report(stability_data, output_dir="output"):
    """Write stability analysis to JSON.
    
    Args:
        stability_data: dict - stability metrics
        output_dir: str - output directory path
    
    Returns:
        Path - path to stability file
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    stability_path = output_path / "stability.json"
    with open(stability_path, 'w') as f:
        json.dump(stability_data, f, indent=2)
    
    return stability_path


def append_log_entry(entry, output_dir="output"):
    """Append entry to JSONL log.
    
    Args:
        entry: dict - log entry
        output_dir: str - output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    log_path = output_path / "log.jsonl"
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + '\n')


if __name__ == "__main__":
    # Test stability
    pass1 = list(range(100, 150))
    pass2 = list(range(100, 148)) + [200, 201]  # 96% overlap
    pass3 = list(range(100, 147)) + [200, 201, 202]  # 94% overlap
    
    history = [pass1, pass2, pass3]
    is_stable, sims = check_stability(history, threshold=0.95, consecutive_required=2)
    
    print(f"Similarities: {sims}")
    print(f"Stable: {is_stable}")
    
    # Test with high stability
    pass4 = list(range(100, 148)) + [200, 201]  # Same as pass2
    history.append(pass4)
    is_stable, sims = check_stability(history, threshold=0.98, consecutive_required=2)
    
    print(f"\nWith pass 4:")
    print(f"Similarities: {sims}")
    print(f"Stable (≥0.98 ×2): {is_stable}")
