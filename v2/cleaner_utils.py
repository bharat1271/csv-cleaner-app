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
    ids = re.findall(r'\b\d{8}\b', text)
    return ','.join(ids)

def find_duplicates_and_uniques(text):
    elements = re.findall(r'\b\d{8}\b', text)
    count = Counter(elements)
    duplicates = [k for k, v in count.items() if v > 1]
    uniques = [k for k, v in count.items() if v == 1]
    return ', '.join(duplicates), ', '.join(uniques)

def count_ids(text):
    ids = re.findall(r'\b\d{8}\b', text)
    id_count = Counter(ids)
    return pd.DataFrame(id_count.items(), columns=['ID', 'Count'])

def extract_ids_and_names(text):
    lines = text.strip().split('\n')
    pairs = []
    i = 0
    while i < len(lines) - 1:
        line = lines[i].strip()
        next_line = lines[i + 1].strip()
        if re.match(r'^\d{8}$', line):
            pairs.append(f"{line}  {next_line}")
            i += 2
        else:
            i += 1
    return '\n'.join(pairs)
