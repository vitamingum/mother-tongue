"""
Tests for the Round 2 assay parser.
"""

from assay import parse_assay_line, parse_assay_response, GlyphAssay


def test_strict_format():
    """Standard pipe-delimited with C:/A:/D:/F: prefixes."""
    result = parse_assay_line("化 | C:PRO | A:2 | D:R | F:STALL")
    assert result is not None
    assert result.glyph == "化"
    assert result.category == "PRO"
    assert result.arity == "2"
    assert result.direction == "R"
    assert result.failure == "STALL"
    print("✓ strict format")


def test_relaxed_format():
    """No C:/A:/D:/F: prefixes."""
    result = parse_assay_line("物 | SUB | 0 | O | SAT")
    assert result is not None
    assert result.glyph == "物"
    assert result.category == "SUB"
    assert result.arity == "0"
    assert result.direction == "O"
    assert result.failure == "SAT"
    print("✓ relaxed format")


def test_all_categories():
    """Each valid category parses."""
    for cat in ["SUB", "PRO", "REL", "MOD", "STR"]:
        line = f"X | C:{cat} | A:0 | D:O | F:SAT"
        result = parse_assay_line(line)
        assert result is not None, f"Failed on category {cat}"
        assert result.category == cat
    print("✓ all categories")


def test_all_arities():
    for a in ["0", "1", "2", "N"]:
        line = f"X | C:SUB | A:{a} | D:O | F:SAT"
        result = parse_assay_line(line)
        assert result is not None, f"Failed on arity {a}"
        assert result.arity == a
    print("✓ all arities")


def test_all_directions():
    for d in ["L", "R", "S", "O"]:
        line = f"X | C:SUB | A:0 | D:{d} | F:SAT"
        result = parse_assay_line(line)
        assert result is not None, f"Failed on direction {d}"
        assert result.direction == d
    print("✓ all directions")


def test_all_failures():
    for f_mode in ["SAT", "STALL", "BOOM", "NULL"]:
        line = f"X | C:SUB | A:0 | D:O | F:{f_mode}"
        result = parse_assay_line(line)
        assert result is not None, f"Failed on failure {f_mode}"
        assert result.failure == f_mode
    print("✓ all failure modes")


def test_invalid_category_rejected():
    result = parse_assay_line("X | C:FOO | A:0 | D:O | F:SAT")
    assert result is None
    print("✓ invalid category rejected")


def test_invalid_arity_rejected():
    result = parse_assay_line("X | C:SUB | A:3 | D:O | F:SAT")
    assert result is None
    print("✓ invalid arity rejected")


def test_invalid_direction_rejected():
    result = parse_assay_line("X | C:SUB | A:0 | D:X | F:SAT")
    assert result is None
    print("✓ invalid direction rejected")


def test_invalid_failure_rejected():
    result = parse_assay_line("X | C:SUB | A:0 | D:O | F:DEAD")
    assert result is None
    print("✓ invalid failure rejected")


def test_empty_line():
    assert parse_assay_line("") is None
    assert parse_assay_line("   ") is None
    print("✓ empty lines")


def test_prose_rejected():
    assert parse_assay_line("Here are the results:") is None
    assert parse_assay_line("# Header") is None
    print("✓ prose rejected")


def test_extra_whitespace():
    result = parse_assay_line("  化  |  C:PRO  |  A:2  |  D:R  |  F:STALL  ")
    assert result is not None
    assert result.glyph == "化"
    assert result.category == "PRO"
    print("✓ extra whitespace handled")


def test_case_insensitive():
    """Parser uppercases values."""
    result = parse_assay_line("物 | sub | 0 | o | sat")
    assert result is not None
    assert result.category == "SUB"
    assert result.direction == "O"
    assert result.failure == "SAT"
    print("✓ case insensitive")


def test_full_response_parse():
    """Simulate a real Gemini response with headers and mixed content."""
    response = """
物 | C:SUB | A:0 | D:O | F:SAT
空 | C:SUB | A:0 | D:O | F:SAT
化 | C:PRO | A:2 | D:R | F:STALL
生 | C:PRO | A:2 | D:R | F:STALL
⇒ | C:REL | A:2 | D:S | F:BOOM
大 | C:MOD | A:1 | D:R | F:NULL
中 | C:STR | A:2 | D:S | F:SAT
"""
    expected = ["物", "空", "化", "生", "⇒", "大", "中"]
    assays, unparsed = parse_assay_response(response, expected)

    assert len(assays) == 7, f"Expected 7 assays, got {len(assays)}"
    assert len(unparsed) == 0, f"Unexpected unparsed: {unparsed}"

    # Check specific classifications
    by_glyph = {a.glyph: a for a in assays}
    assert by_glyph["化"].category == "PRO"
    assert by_glyph["化"].arity == "2"
    assert by_glyph["化"].failure == "STALL"
    assert by_glyph["物"].category == "SUB"
    assert by_glyph["物"].arity == "0"
    assert by_glyph["⇒"].category == "REL"
    assert by_glyph["大"].category == "MOD"
    assert by_glyph["中"].category == "STR"
    print("✓ full response parse (7 glyphs, all correct)")


def test_dedup():
    """Duplicate glyph in response: keep first only."""
    response = """
化 | C:PRO | A:2 | D:R | F:STALL
化 | C:MOD | A:1 | D:L | F:SAT
"""
    assays, _ = parse_assay_response(response, ["化"])
    assert len(assays) == 1
    assert assays[0].category == "PRO"  # first wins
    print("✓ dedup (first wins)")


def test_missing_glyphs_reported():
    """Parser reports missing glyphs from expected set."""
    response = "化 | C:PRO | A:2 | D:R | F:STALL\n"
    assays, _ = parse_assay_response(response, ["化", "物", "空"])
    assert len(assays) == 1
    print("✓ missing glyphs reported")


def test_mixed_strict_relaxed():
    """Response mixing both formats."""
    response = """
物 | C:SUB | A:0 | D:O | F:SAT
化 | PRO | 2 | R | STALL
"""
    assays, unparsed = parse_assay_response(response, ["物", "化"])
    assert len(assays) == 2
    assert len(unparsed) == 0
    print("✓ mixed strict/relaxed in same response")


def test_example_glyphs():
    """Test all 5 examples from the prompt."""
    lines = [
        ("物 | C:SUB | A:0 | D:O | F:SAT",     "物", "SUB", "0", "O", "SAT"),
        ("化 | C:PRO | A:2 | D:R | F:STALL",    "化", "PRO", "2", "R", "STALL"),
        ("⇒ | C:REL | A:2 | D:S | F:BOOM",      "⇒", "REL", "2", "S", "BOOM"),
        ("大 | C:MOD | A:1 | D:R | F:NULL",      "大", "MOD", "1", "R", "NULL"),
        ("中 | C:STR | A:2 | D:S | F:SAT",       "中", "STR", "2", "S", "SAT"),
    ]
    for line, g, c, a, d, f in lines:
        result = parse_assay_line(line)
        assert result is not None, f"Failed to parse: {line}"
        assert result.glyph == g
        assert result.category == c
        assert result.arity == a
        assert result.direction == d
        assert result.failure == f
    print("✓ all 5 prompt examples")


if __name__ == "__main__":
    test_strict_format()
    test_relaxed_format()
    test_all_categories()
    test_all_arities()
    test_all_directions()
    test_all_failures()
    test_invalid_category_rejected()
    test_invalid_arity_rejected()
    test_invalid_direction_rejected()
    test_invalid_failure_rejected()
    test_empty_line()
    test_prose_rejected()
    test_extra_whitespace()
    test_case_insensitive()
    test_full_response_parse()
    test_dedup()
    test_missing_glyphs_reported()
    test_mixed_strict_relaxed()
    test_example_glyphs()
    print(f"\n✅ All 19 tests passed")
