import re
import pandas as pd
import unicodedata
from collections import Counter
import string
from collections import defaultdict

#OCR Module#
import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
if os.name == "nt":  # Windows only
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#=== Translation Utilities (Local / Offline) ===
#from argostranslate import translate
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
    """
    Detects duplicate and unique values (IDs or text) from mixed input.
    - Supports numeric IDs of 6–15 digits (OrgID, AffilID, GroupID)
    - Supports text-based values (names, institutions, etc.)
    - Case-insensitive and punctuation-tolerant
    """
    if not text:
        return "No input provided", ""

    # Try extracting numeric IDs (6–15 digits)
    ids = re.findall(r'\b\d{6,15}\b', text)

    if ids:
        # Numeric mode
        count = Counter(ids)
    else:
        # Text mode: split on commas, newlines, or tabs
        parts = re.split(r'[\n,\t]+', text)
        # Clean text entries
        clean_parts = [
            p.strip().lower().translate(str.maketrans('', '', string.punctuation))
            for p in parts if p.strip()
        ]
        count = Counter(clean_parts)

    # Separate duplicates and uniques
    duplicates = [k for k, v in count.items() if v > 1]
    uniques = [k for k, v in count.items() if v == 1]

    duplicates_text = ', '.join(duplicates) if duplicates else "No duplicates found"
    uniques_text = ', '.join(uniques) if uniques else "No unique values found"

    return duplicates_text, uniques_text

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
    '\u0455': 's',  # (sometimes used) Cyrillic 'ѕ' -> 's'
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
                # We already handled many common cases; highlight and skip (remove) if not mappable
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
    
    
def count_orgid_occurrences_in_collection_text(collection_text, orgid):
    """Count exact occurrences of an OrgID in the collection text."""
    if not collection_text or not orgid:
        return 0
    pattern = re.compile(rf"\b{re.escape(str(orgid))}\b")
    return len(pattern.findall(collection_text))


def reconcile_orgid_counts(df, collection_text, orgid_col="OrgID", count_col="Count"):
    """
    df must contain:
      - OrgID
      - Count (expected number of occurrences)
    """
    results = []

    for _, row in df.iterrows():
        orgid = str(row[orgid_col]).strip()
        expected = int(row[count_col])

        found = count_orgid_occurrences_in_collection_text(collection_text, orgid)

        status = "PASS" if found == expected else f"FAIL (expected {expected}, found {found})"

        results.append({
            "OrgID": orgid,
            "Expected Count": expected,
            "Found Count": found,
            "Status": status
        })

    return pd.DataFrame(results)

def run_ocr_on_image(
    pil_image,
    lang="eng",
    ocr_mode="auto"
):

    # Convert PIL → OpenCV
    img = np.array(pil_image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Decide preprocessing
    if ocr_mode == "raw":
        processed = gray

    elif ocr_mode == "cjk":
        processed = gray

    else:
        # Latin / default
        processed = cv2.threshold(
            gray, 150, 255, cv2.THRESH_BINARY
        )[1]

    # OCR config
    config = "--psm 6"

    try:
        text = pytesseract.image_to_string(
            processed,
            lang=lang,
            config=config
        )
    except pytesseract.TesseractError as e:
        return f"OCR failed: {e}"

    return text.strip()


# def translate_text_local(text, from_lang="auto", to_lang="en"):
#     """
#     Offline translation using Argos Translate.
#     Assumes required language models are already installed.
#     """

#     installed_languages = translate.get_installed_languages()

#     if not installed_languages:
#         return "⚠️ No translation models installed."

#     # Resolve source language
#     if from_lang == "auto":
#         from_language = None
#         for lang in installed_languages:
#             if lang.code != to_lang:
#                 from_language = lang
#                 break
#     else:
#         from_language = next(
#             (l for l in installed_languages if l.code == from_lang),
#             None
#         )

#     to_language = next(
#         (l for l in installed_languages if l.code == to_lang),
#         None
#     )

#     if not from_language or not to_language:
#         return "⚠️ Translation model not installed for selected language pair."

#     translation = from_language.get_translation(to_language)
#     return translation.translate(text)
    
    
#     #translate_text_local
# def get_installed_translation_languages():
#     languages = translate.get_installed_languages()
#     lang_map = {}
#     for lang in languages:
#         label = f"{lang.name} ({lang.code})"
#         lang_map[label] = lang.code
#     return lang_map
    
    
    #for run_ocr_on_image
def get_tesseract_languages():
    try:
        langs = pytesseract.get_languages(config="")
    except Exception:
        return {}

    language_map = {}
    for code in langs:
        language_map[f"{code}"] = code

    return language_map 
    
    
# def install_translation_models_once():
#     installed = translate.get_installed_languages()
#     if installed:
#         return "Translation models already installed."

#     package.update_package_index()
#     available_packages = package.get_available_packages()

#     required_pairs = [
#         ("zh", "en"),
#         ("de", "en"),
#         ("fr", "en"),
#         ("it", "en"),
#         ("ja", "en"),
#         ("pt", "en"),
#     ]

#     installed_any = False

#     for from_code, to_code in required_pairs:
#         for pkg in available_packages:
#             if pkg.from_code == from_code and pkg.to_code == to_code:
#                 package.install_from_path(pkg.download())
#                 installed_any = True

#     if installed_any:
#         return "Translation models installed successfully."
#     else:
#         return "No matching translation models found."




