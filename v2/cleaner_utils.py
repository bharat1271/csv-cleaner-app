import pandas as pd
import re

def remove_duplicates(df):
    before = len(df)
    df = df.drop_duplicates()
    return df, f"Removed {before - len(df)} duplicate rows" if before != len(df) else "No duplicates found"

def trim_whitespace(df):
    str_cols = df.select_dtypes(include='object').columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())
    return df, f"Trimmed whitespace in columns: {', '.join(str_cols)}"

def capitalize_names(df):
    name_cols = [c for c in df.columns if 'name' in c.lower()]
    if not name_cols:
        return df, "No 'name' column found for capitalization"
    col = name_cols[0]
    exceptions = {'and','of','the','a','an','in'}
    def smart_title(txt):
        words = str(txt).lower().split()
        if not words: return txt
        out = [words[0].capitalize()] + [w if w in exceptions else w.capitalize() for w in words[1:]]
        return " ".join(out)
    df[col] = df[col].astype(str).apply(smart_title)
    return df, f"Capitalized names in column: {col}"

def drop_blank_rows(df):
    before = len(df)
    df = df.dropna(how='all')
    return df, f"Removed {before - len(df)} completely blank rows"

def fill_missing_values(df, fill_value="Missing"):
    before = df.isnull().sum().sum()
    df = df.fillna(fill_value)
    after = df.isnull().sum().sum()
    return df, f"Filled {before - after} missing values with '{fill_value}'"

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
    converted = []
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col], errors='raise')
                converted.append(col)
            except:
                pass
    if converted:
        return df, f"Converted columns to numeric: {', '.join(converted)}"
    return df, "No numeric conversions applied"

def split_column(df, col, delimiter=' ', into_two=True):
    if col not in df.columns:
        return df, f"Column '{col}' not found for splitting"
    parts = df[col].astype(str).str.split(delimiter, 1, expand=True)
    df[f"{col}_1"], df[f"{col}_2"] = parts[0], parts[1]
    return df, f"Split '{col}' into '{col}_1' and '{col}_2'"

# ─── New Text Operations ───────────────────────────────────────────────────────

def smart_sentence_format(text):
    """
    Proper-case a sentence, skipping small connecting words.
    """
    exceptions = {'a','an','and','in','of','the','to','for'}
    words = text.lower().split()
    if not words:
        return ""
    formatted = [words[0].capitalize()]
    for w in words[1:]:
        formatted.append(w if w in exceptions else w.capitalize())
    return " ".join(formatted)

def extract_8digit_ids_from_series(series):
    """
    Given a pandas Series of strings, extract all 8-digit IDs and count frequencies.
    Returns a DataFrame with columns ['ID', 'Count'].
    """
    ids = series.astype(str).str.extractall(r'(\b\d{8}\b)')[0]
    counts = ids.value_counts().reset_index()
    counts.columns = ['ID', 'Count']
    return counts

def extract_8digit_ids_from_text(text):
    """
    Returns a list of all 8-digit IDs found in the given text.
    """
    return re.findall(r'\b\d{8}\b', text)

def extract_duplicates_between(text1, text2):
    """
    Returns a list of duplicated words/tokens present in both text1 and text2.
    """
    set1 = set(text1.split())
    set2 = set(text2.split())
    return list(set1 & set2)
