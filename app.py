import streamlit as st
import pandas as pd
from io import BytesIO
from cleaner_utils import *

st.set_page_config(page_title="CSV Cleaner App", layout="wide")
st.title("🧹 CSV Data Cleaner (Streamlit Edition)")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"Loaded file with {df.shape[0]} rows and {df.shape[1]} columns.")
        st.write("### Raw Data Preview")
        st.dataframe(df.head())

        st.write("---")
        st.header("🔧 Select Cleaning Operations")

        # Grouped UI Blocks
        with st.expander("🔹 Basic Cleaning"):
            dedupe = st.checkbox("Remove Duplicates")
            trim = st.checkbox("Trim Whitespace")
            drop_blank = st.checkbox("Drop Blank Rows")

        with st.expander("🔹 Text Formatting"):
            capitalize = st.checkbox("Capitalize Names")
            fix_case = st.checkbox("Fix Text Case")
            case_mode = st.selectbox("Text Case Mode", ["lower", "upper", "title"])
            replace = st.checkbox("Find and Replace")
            find_val = st.text_input("Find:", value="null")
            replace_val = st.text_input("Replace with:", value="NA")

        with st.expander("🔹 Value Handling"):
            fillna = st.checkbox("Fill Missing Values")
            fill_val = st.text_input("Fill missing with:", value="Missing")
            convert = st.checkbox("Convert to Numeric")

        with st.expander("🔹 Column Operations"):
            split = st.checkbox("Split Column")
            split_col = st.text_input("Column to Split", value="Full Name")
            delim = st.text_input("Delimiter", value=" ")

        if st.button("🚀 Clean Data"):
            cleaned_df = df.copy()
            logs = []

            if dedupe: cleaned_df, msg = remove_duplicates(cleaned_df); logs.append(msg)
            if trim: cleaned_df, msg = trim_whitespace(cleaned_df); logs.append(msg)
            if capitalize: cleaned_df, msg = capitalize_names(cleaned_df); logs.append(msg)
            if drop_blank: cleaned_df, msg = drop_blank_rows(cleaned_df); logs.append(msg)
            if fillna: cleaned_df, msg = fill_missing_values(cleaned_df, fill_val); logs.append(msg)
            if fix_case: cleaned_df, msg = fix_text_case(cleaned_df, mode=case_mode); logs.append(msg)
            if replace: cleaned_df, msg = find_and_replace(cleaned_df, find_val, replace_val); logs.append(msg)
            if convert: cleaned_df, msg = convert_numbers(cleaned_df); logs.append(msg)
            if split: cleaned_df, msg = split_column(cleaned_df, split_col, delim); logs.append(msg)

            st.write("---")
            st.success("✅ Cleaning completed.")
            st.write("### 🧾 Cleaning Log:")
            for log in logs:
                st.markdown(f"- {log}")

            st.write("### 🧼 Cleaned Data Preview")
            st.dataframe(cleaned_df.head())

            # Download button
            csv = cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Cleaned CSV",
                data=csv,
                file_name="cleaned_data.csv",
                mime='text/csv')

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
