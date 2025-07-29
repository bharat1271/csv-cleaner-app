import pandas as pd
import re
from collections import Counter

# Title case with exceptions (smart title)
def smart_title(text):
    exceptions = ['and', 'of', 'the', 'a', 'an', 'in']
    words = str(text).lower().split()
    return ' '.join([
        words[0].capitalize()] + 
        [w if w in exceptions else w.capitalize() for w in words[1:]]
    ) if words else text

def format_text_title_case(text):
    if not text.strip():
        return "Please enter valid text."
    lines = text.strip().split('\n')
    formatted_lines = [smart_title(line) for line in lines]
    return '\n'.join(formatted_lines)

def extract_8_digit_ids(text):
    ids = re.findall(r'\b\d{8}\b', text)
    if not ids:
        return "No valid 8-digit IDs found."
    return ",".join(ids)

def count_8_digit_ids(text):
    ids = re.findall(r'\b\d{8}\b', text)
    if not ids:
        return "No valid 8-digit IDs found."
    counts = Counter(ids)
    return "\n".join([f"{k}: {v}" for k, v in counts.items()])

def find_duplicates_and_uniques(text):
    # Clean and split by commas or newline
    items = re.findall(r'\b\d{8}\b', text)
    if not items:
        return "No valid 8-digit IDs found."
    counter = Counter(items)
    duplicates = [k for k, v in counter.items() if v > 1]
    uniques = [k for k, v in counter.items() if v == 1]
    return f"Duplicates: {', '.join(duplicates)}\nUniques: {', '.join(uniques)}"

def extract_ids_and_names(raw_text):
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    extracted = []
    i = 0
    while i < len(lines) - 1:
        if re.match(r'^\d{8}$', lines[i]):
            id_val = lines[i]
            name = lines[i+1]
            extracted.append(f"{id_val}  {name}")
            i += 2
        else:
            i += 1
    if not extracted:
        return "No ID and Name pairs found."
    return '\n'.join(extracted)
