import streamlit as st
import pandas as pd
from cleaner_utils import (
    smart_title_text,
    count_ids,
    extract_8_digit_ids,
    find_duplicates_and_uniques,
    extract_ids_and_names_from_tool_output
)

st.set_page_config(page_title="CSV & Text Cleaner App", layout="wide")
st.title("🧹 CSV & Text Cleaner App")

st.sidebar.title("Choose an Operation")
option = st.sidebar.radio("Select a mode:", ["CSV Cleaning", "Text Operations"])

if option == "CSV Cleaning":
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("### Preview of Uploaded Data:", df.head())

        operations = st.multiselect(
            "Select cleaning operations:",
            [
                "Remove Duplicates",
                "Trim Whitespace",
                "Capitalize Names",
                "Drop Blank Rows",
                "Fill Missing Values",
                "Fix Text Case",
                "Find & Replace",
                "Convert Numbers",
                "Split Column"
            ]
        )

        case_mode = st.selectbox("Text case mode:", ["lower", "upper", "title"])
        fill_value = st.text_input("Value to fill missing cells with:", "Missing")
        find_val = st.text_input("Find this value:", "null")
        replace_val = st.text_input("Replace with:", "NA")
        col_to_split = st.text_input("Column to split:", "Full Name")
        delimiter = st.text_input("Delimiter for splitting:", " ")

        if st.button("Apply Cleaning"):
            logs = []
            if "Remove Duplicates" in operations:
                df, msg = df.drop_duplicates(), "Removed duplicate rows"
                logs.append(msg)
            if "Trim Whitespace" in operations:
                str_cols = df.select_dtypes(include='object').columns
                df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())
                logs.append("Trimmed whitespace")
            if "Capitalize Names" in operations:
                name_cols = [col for col in df.columns if 'name' in col.lower()]
                if name_cols:
                    col = name_cols[0]
                    df[col] = df[col].astype(str).apply(smart_title_text)
                    logs.append(f"Capitalized names in column: {col}")
            if "Drop Blank Rows" in operations:
                df = df.dropna(how='all')
                logs.append("Dropped blank rows")
            if "Fill Missing Values" in operations:
                df = df.fillna(fill_value)
                logs.append(f"Filled missing values with '{fill_value}'")
            if "Fix Text Case" in operations:
                str_cols = df.select_dtypes(include='object').columns
                if case_mode == 'lower':
                    df[str_cols] = df[str_cols].apply(lambda x: x.str.lower())
                elif case_mode == 'upper':
                    df[str_cols] = df[str_cols].apply(lambda x: x.str.upper())
                else:
                    df[str_cols] = df[str_cols].apply(lambda x: x.str.title())
                logs.append(f"Formatted text case to '{case_mode}'")
            if "Find & Replace" in operations:
                df = df.replace(find_val, replace_val)
                logs.append(f"Replaced '{find_val}' with '{replace_val}'")
            if "Convert Numbers" in operations:
                for col in df.columns:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='ignore')
                    except:
                        continue
                logs.append("Converted applicable columns to numeric")
            if "Split Column" in operations:
                if col_to_split in df.columns:
                    new_cols = df[col_to_split].str.split(delimiter, 1, expand=True)
                    df[f"{col_to_split}_1"], df[f"{col_to_split}_2"] = new_cols[0], new_cols[1]
                    logs.append(f"Split column '{col_to_split}'")
            st.success("Cleaning complete")
            st.write("\n".join(logs))
            st.download_button("Download Cleaned CSV", df.to_csv(index=False), "cleaned_data.csv")

elif option == "Text Operations":
    st.subheader("Free Text-Based Functions")

    mode = st.radio("Choose text operation:", [
        "🧼 Convert to Proper Title Case",
        "🔢 Count IDs",
        "🧲 Extract 8-digit IDs",
        "🧩 Find Duplicates and Uniques",
        "📋 Extract IDs and Names from Raw Tool Output"
    ])

    input_text = st.text_area("Paste your data here:")

    if st.button("Run Operation") and input_text:
        if mode == "🧼 Convert to Proper Title Case":
            result = smart_title_text(input_text)
            st.text_area("Formatted Output", result, height=150)

        elif mode == "🔢 Count IDs":
            result = count_ids(input_text)
            st.write(result)

        elif mode == "🧲 Extract 8-digit IDs":
            result = extract_8_digit_ids(input_text)
            st.text_area("Extracted IDs", result, height=150)

        elif mode == "🧩 Find Duplicates and Uniques":
            dup_text, uniq_text = find_duplicates_and_uniques(input_text)
            st.text_area("Duplicates", dup_text, height=150)
            st.text_area("Uniques", uniq_text, height=150)

        elif mode == "📋 Extract IDs and Names from Raw Tool Output":
            result = extract_ids_and_names_from_tool_output(input_text)
            st.text_area("Extracted ID & Name Pairs", result, height=300)
