import re
import pandas as pd
import unicodedata
from collections import Counter

# === CSV Cleaning Functions ===

def remove_duplicates(df):
    before = len(df)
    df = df.drop_duplicates()
    return df, f"Removed {before - len(df)} duplicate rows" if before != len(df) else "No duplicates found"

def trim_whitespace(df):
    str_cols = df.select_dtypes(include='object').columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())
    return df, f"Trimmed whitespace in columns: {', '.join(str_cols)}"

def capitalize_names(df):
    name_col = [col for col in df.columns if 'name' in col.lower()]
    if name_col:
        col_name = name_col[0]
        exceptions = ['and', 'of', 'the', 'a', 'an', 'in']
        def smart_title(text):
            words = str(text).lower().split()
            return ' '.join([words[0].capitalize()] + [w if w in exceptions else w.capitalize() for w in words[1:]]) if words else text
        df[col_name] = df[col_name].astype(str).apply(smart_title)
        return df, f"Capitalized names in column: {col_name}"
    return df, "No 'name' column found for capitalization"

def drop_blank_rows(df):
    before = len(df)
    df = df.dropna(how='all')
    return df, f"Removed {before - len(df)} completely blank rows"

def fill_missing_values(df, fill_value="Missing"):
    missing_before = df.isnull().sum().sum()
    df = df.fillna(fill_value)
    missing_after = df.isnull().sum().sum()
    return df, f"Filled {missing_before - missing_after} missing values with '{fill_value}'"

def fix_text_case(df, mode='title'):
    str_cols = df.select_dtypes(include='object').columns
    if mode == 'lower':
        df[str_cols] = df[str_cols].apply(lambda x: x.str.lower())
    elif mode == 'upper':
        df[str_cols] = df[str_cols].apply(lambda x: x.str.upper())
    else:
        df[str_cols] = df[str_cols].apply(lambda x: x.str.title())
    return df, f"Formatted text case as '{mode}' in: {', '.join(str_cols)}"

def find_and_replace(df, find_val, replace_val):
    df = df.replace(find_val, replace_val)
    return df, f"Replaced '{find_val}' with '{replace_val}'"

def convert_numbers(df):
    converted_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col], errors='raise')
                converted_cols.append(col)
            except:
                continue
    return df, f"Converted columns to numeric: {', '.join(converted_cols)}" if converted_cols else "No numeric conversions applied"

def split_column(df, col, delimiter=' ', into_two=True):
    if col not in df.columns:
        return df, f"Column '{col}' not found for splitting"
    if into_two:
        try:
            new_cols = df[col].str.split(pat=delimiter, n=1, expand=True)
            df[f"{col}_1"], df[f"{col}_2"] = new_cols[0], new_cols[1]
            return df, f"Split '{col}' into '{col}_1' and '{col}_2'"
        except Exception as e:
            return df, f"Error splitting column: {e}"
    return df, "Split skipped"


# === Text Utility Functions ===

def smart_title_text(text):
    exceptions = ['and', 'of', 'the', 'a', 'an', 'in', 'is']
    words = str(text).lower().split()
    return ' '.join(
        [words[0].capitalize()] + [w if w in exceptions else w.capitalize() for w in words[1:]]
    ) if words else text

def extract_ids(text):
    ids = re.findall(r'\d{8}', text)
    return ','.join(ids)

def find_duplicates_and_uniques(text):
    elements = re.findall(r'\d{8}', text)
    count = Counter(elements)
    duplicates = [k for k, v in count.items() if v > 1]
    uniques = [k for k, v in count.items() if v == 1]
    return ', '.join(duplicates), ', '.join(uniques)

def count_ids(text):
    ids = re.findall(r'\d{8}', text)
    id_count = Counter(ids)
    return pd.DataFrame(id_count.items(), columns=['ID', 'Count'])

def extract_ids_and_names(text):
    lines = text.strip().split("\n")
    results = []
    skip_keywords = ["PART_OF", "RENAMED_AS", "MERGED_WITH", "AFFILIATED_WITH"]

    for i, line in enumerate(lines):
        # Case 1: ID and Name on the same line (even if followed by extra columns)
        match = re.match(r'^\s*(\d{8})\s+([A-Za-z][^\t]+)', line)
        if match:
            id_val, name_val = match.groups()
            results.append(f"{id_val}\t{name_val.strip()}")
            continue

        # Case 2: ID on one line, Name on the next line
        if re.match(r'^\s*\d{8}\s*$', line) and i + 1 < len(lines):
            id_val = line.strip()
            name_val = lines[i + 1].strip()

            if not any(keyword in name_val for keyword in skip_keywords):
                results.append(f"{id_val}\t{name_val}")

    return "\n".join(results)
    
def extract_affili_ids_strict(text):
    """
    Extracts only AffilIDs:
    - Always capture the number that comes right after 'Processed', 'Failed', or 'Undefined'.
    - Works for both 8-digit and longer AffilIDs.
    - Skips OrgIDs that appear elsewhere.
    """
    pattern = r'(?:Processed|Failed|Undefined)\s+(\d+)'
    matches = re.findall(pattern, text)
    return ",".join(matches)


def extract_group_ids(text):
    # Look for: Processed/Failed/Undefined → AffilID (any digit length) → GroupID
    pattern = r'(?:Processed|Failed|Undefined)\s*\n?\d+\s*\n?(\d{5,15})'
    group_ids = re.findall(pattern, text)
    return ','.join(group_ids)

'''def split_id_name(text):
    """
    Splits lines like '12345678 ABCDEFGH' or '12345678 - ABCDEFGH'
    into ID and Name cleanly.
    """
    rows = text.strip().splitlines()
    cleaned = []
    for row in rows:
        # Remove extra spaces/dashes between ID and name
        parts = re.split(r'\s*-\s*|\s+', row.strip(), maxsplit=1)
        if len(parts) == 2:
            cleaned.append((parts[0], parts[1]))
    return cleaned

'''
def ids_to_lines(text):
    ids = [x.strip() for x in text.replace("\n", ",").split(",") if x.strip()]
    return "\n".join(ids)

def ids_to_csv(text):
    ids = [x.strip() for x in text.replace(",", "\n").split("\n") if x.strip()]
    return ",".join(ids)

# Common homoglyphs mapping
HOMOGLYPHS_MAP = {
    # common Cyrillic lowercase -> Latin
    '\u0430': 'a',  # Cyrillic 'а' -> Latin 'a'
    '\u0435': 'e',  # Cyrillic 'е' -> Latin 'e'
    '\u043E': 'o',  # Cyrillic 'о' -> Latin 'o'
    '\u0441': 'c',  # Cyrillic 'с' -> Latin 'c'
    '\u0440': 'p',  # Cyrillic 'р' -> Latin 'p'
    '\u0445': 'x',  # Cyrillic 'х' -> Latin 'x'
    '\u043A': 'k',  # Cyrillic 'к' -> Latin 'k'
    '\u0456': 'i',  # Cyrillic 'і' -> Latin 'i'
    '\u0455': 's',  # Cyrillic 'ѕ' -> 's'
    # Cyrillic uppercase
    '\u0410': 'A',
    '\u0415': 'E',
    '\u041E': 'O',
    '\u0421': 'C',
    '\u0420': 'P',
    '\u0425': 'X',
    '\u041A': 'K',
    # Fullwidth Latin
    'Ａ': 'A', 'Ｂ': 'B', 'Ｃ': 'C', 'Ｄ': 'D', 'Ｅ': 'E', 'Ｆ': 'F',
    'Ｇ': 'G', 'Ｈ': 'H', 'Ｉ': 'I', 'Ｊ': 'J', 'Ｋ': 'K', 'Ｌ': 'L',
    'Ｍ': 'M', 'Ｎ': 'N', 'Ｏ': 'O', 'Ｐ': 'P', 'Ｑ': 'Q', 'Ｒ': 'R',
    'Ｓ': 'S', 'Ｔ': 'T', 'Ｕ': 'U', 'Ｖ': 'V', 'Ｗ': 'W', 'Ｘ': 'X',
    'Ｙ': 'Y', 'Ｚ': 'Z',
}

# Zero-width / invisible characters to strip
ZERO_WIDTH = {
    '\u200B',  # zero width space
    '\u200C',  # zero width non-joiner
    '\u200D',  # zero width joiner
    '\uFEFF',  # zero width no-break space (BOM)
}

def detect_and_clean_junk_characters(text):
    """
    Detects non-standard characters and attempts to replace them with ASCII equivalents.
    Returns:
      - highlighted_text: original text but junk chars shown in brackets [⋯]
      - cleaned_text: repaired text (replacing junk look-alikes with Latin equivalents where possible)
    Notes: mapping can be expanded (HOMOGLYPHS_MAP) based on observed inputs.
    """
    if text is None:
        return "", ""

    highlighted_parts = []
    cleaned_parts = []

    for ch in text:
        # quick keep for normal printable ascii & common whitespace/newlines/tabs
        if 32 <= ord(ch) <= 126 or ch in "\n\r\t":
            highlighted_parts.append(ch)
            cleaned_parts.append(ch)
            continue

        # remove zero-width / invisible characters (but highlight in output)
        if ch in ZERO_WIDTH:
            highlighted_parts.append(f"[U+{ord(ch):04X}]")
            # do not add anything to cleaned_parts (effectively removed)
            continue

        # direct homoglyph mapping (Cyrillic -> Latin, fullwidth -> ASCII)
        if ch in HOMOGLYPHS_MAP:
            replacement = HOMOGLYPHS_MAP[ch]
            highlighted_parts.append(f"[{ch}]")
            cleaned_parts.append(replacement)
            continue

        # try unicode normalization to ascii base (e.g., é -> e)
        normalized = unicodedata.normalize('NFKD', ch)
        ascii_equiv = normalized.encode('ascii', 'ignore').decode('ascii', errors='ignore')
        if ascii_equiv:
            # ascii_equiv might be multiple chars; pick it
            highlighted_parts.append(f"[{ch}]")
            cleaned_parts.append(ascii_equiv)
            continue

        try:
            name = unicodedata.name(ch)
            # crude heuristics: if name contains 'CYRILLIC' or 'GREEK' and a latin lookalike exists
            if 'CYRILLIC' in name or 'GREEK' in name or 'FULLWIDTH' in name:
                # highlight and skip (remove) if not mappable
                highlighted_parts.append(f"[{ch}]")
                # don't append to cleaned_parts if no safe mapping
                continue
        except ValueError:
            # some control chars might not have a name
            pass

        # If nothing worked: mark as junk and remove in cleaned output
        highlighted_parts.append(f"[{ch}]")
        # cleaned_parts -> nothing (drop)

    highlighted_text = ''.join(highlighted_parts)
    cleaned_text = ''.join(cleaned_parts)
    return highlighted_text, cleaned_text



