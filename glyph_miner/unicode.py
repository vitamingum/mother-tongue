"""Unicode scalar value filtering - no names, no blocks, no metadata."""
import unicodedata

def get_filtered_unicode():
    """Return all valid Unicode scalar values with exclusions.
    
    Excludes:
    - Surrogates (U+D800-U+DFFF)
    - Cc (Control characters)
    - Cf (Format characters)
    - Mn (Nonspacing marks)
    - Mc (Spacing marks)
    - Me (Enclosing marks)
    - Zs (Space separators)
    - PUA (Private Use Area: U+E000-U+F8FF, U+F0000-U+FFFFD, U+100000-U+10FFFD)
    - VS (Variation Selectors: U+FE00-U+FE0F, U+E0100-U+E01EF)
    - Unassigned characters
    """
    filtered = []
    
    # Private Use Areas
    pua_ranges = [
        (0xE000, 0xF8FF),
        (0xF0000, 0xFFFFD),
        (0x100000, 0x10FFFD)
    ]
    
    # Variation Selectors
    vs_ranges = [
        (0xFE00, 0xFE0F),
        (0xE0100, 0xE01EF)
    ]
    
    def in_pua(cp):
        return any(start <= cp <= end for start, end in pua_ranges)
    
    def in_vs(cp):
        return any(start <= cp <= end for start, end in vs_ranges)
    
    # Iterate all valid Unicode scalar values
    for cp in range(0x110000):
        # Skip surrogates
        if 0xD800 <= cp <= 0xDFFF:
            continue
        
        # Skip PUA
        if in_pua(cp):
            continue
        
        # Skip VS
        if in_vs(cp):
            continue
        
        try:
            char = chr(cp)
            category = unicodedata.category(char)
            
            # Skip excluded categories
            if category in ('Cc', 'Cf', 'Mn', 'Mc', 'Me', 'Zs', 'Cn'):
                continue
            
            filtered.append(cp)
            
        except ValueError:
            continue
    
    return filtered


def enum_unicode():
    """Enumerate filtered Unicode as list of integers."""
    return get_filtered_unicode()


if __name__ == "__main__":
    u = enum_unicode()
    print(f"Filtered Unicode size: {len(u)}")
    print(f"First 10: {u[:10]}")
    print(f"Last 10: {u[-10:]}")
