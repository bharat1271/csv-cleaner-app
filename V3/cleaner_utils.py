import re
import pandas as pd
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
    exceptions = ['and', 'of', 'the', 'a', 'an', 'in']
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
    pattern = r'(?:Processed|Failed|Undefined)\s*\n?\d{9,15}\s*\n?(\d{5,15})'
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