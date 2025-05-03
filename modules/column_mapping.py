from rapidfuzz import fuzz

def map_columns(input_columns, standard_columns):
    """
    Maps each input column to a standard field using fuzzy matching.
    
    Parameters:
      - input_columns: list of columns from the uploaded file.
      - standard_columns: dict where key is a standard field and value is a list of synonyms.
    
    Returns:
      - mapping: dict mapping original column names to standard field names (or None if unmapped).
      - unmapped: list of columns that did not reach the matching threshold.
    """
    mapping = {}
    unmapped = []
    threshold = 70  # matching threshold percentage

    for col in input_columns:
        best_match = None
        best_score = 0
        for standard, synonyms in standard_columns.items():
            for syn in synonyms:
                score = fuzz.ratio(col.lower(), syn.lower())
                if score > best_score:
                    best_score = score
                    best_match = standard
        if best_score >= threshold:
            mapping[col] = best_match
        else:
            mapping[col] = None
            unmapped.append(col)
    return mapping, unmapped
