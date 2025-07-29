import streamlit as st
import pandas as pd
from cleaner_utils import *

st.set_page_config(page_title="CSV Cleaner App", layout="wide")
st.title("🧹 CSV Data Cleaner & Text Tools")

tab = st.tabs(["CSV Cleaning", "Text Operations"])[0] if False else st.tabs(["CSV Cleaning","Text Operations"])
csv_tab, text_tab = tab

# ─── CSV Cleaning Tab ─────────────────────────────────────────────────────────
with csv_tab:
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"Loaded file: {df.shape[0]} rows × {df.shape[1]} cols")
        st.dataframe(df.head())

        st.header("🔧 Cleaning Operations")
        with st.expander("Basic Cleaning"):
            dedupe     = st.checkbox("Remove Duplicates")
            trim       = st.checkbox("Trim Whitespace")
            drop_blank = st.checkbox("Drop Blank Rows")
        with st.expander("Text Formatting"):
            capitalize = st.checkbox("Capitalize Names")
            fix_case   = st.checkbox("Fix Text Case")
            case_mode  = st.selectbox("Case Mode", ["lower","upper","title"])
            replace    = st.checkbox("Find & Replace")
            find_val   = st.text_input("Find", value="null")
            replace_val= st.text_input("Replace with", value="NA")
        with st.expander("Value Handling"):
            fillna   = st.checkbox("Fill Missing Values")
            fill_val = st.text_input("Fill with", value="Missing")
            convert  = st.checkbox("Convert to Numeric")
        with st.expander("Column Ops"):
            split     = st.checkbox("Split Column")
            split_col = st.text_input("Column to split", value="Full Name")
            delim     = st.text_input("Delimiter", value=" ")

        if st.button("🚀 Clean Data"):
            cleaned = df.copy(); logs=[]
            if dedupe:     cleaned, m=remove_duplicates(cleaned); logs.append(m)
            if trim:       cleaned, m=trim_whitespace(cleaned); logs.append(m)
            if capitalize: cleaned, m=capitalize_names(cleaned); logs.append(m)
            if drop_blank: cleaned, m=drop_blank_rows(cleaned); logs.append(m)
            if fillna:     cleaned, m=fill_missing_values(cleaned, fill_val); logs.append(m)
            if fix_case:   cleaned, m=fix_text_case(cleaned, mode=case_mode); logs.append(m)
            if replace:    cleaned, m=find_and_replace(cleaned, find_val, replace_val); logs.append(m)
            if convert:    cleaned, m=convert_numbers(cleaned); logs.append(m)
            if split:      cleaned, m=split_column(cleaned, split_col, delim); logs.append(m)

            st.success("Cleaning Complete")
            st.markdown("**Log:**")
            for l in logs: st.markdown(f"- {l}")
            st.dataframe(cleaned.head())
            csv_bytes = cleaned.to_csv(index=False).encode()
            st.download_button("📥 Download CSV", csv_bytes, "cleaned.csv", "text/csv")

# ─── Text Operations Tab ──────────────────────────────────────────────────────
with text_tab:
    st.header("📝 Free Text Tools")
    text_input = st.text_area("Enter your text here", height=150)

    if st.button("🔤 Proper-Case Sentence"):
        result = smart_sentence_format(text_input)
        st.write("**Formatted:**", result)

    st.write("---")
    st.subheader("Extract 8-Digit IDs")
    id_text = st.text_area("Enter text or paste column values, each on new line", height=100, key="ids")
    if st.button("🔍 Extract IDs"):
        ids = extract_8digit_ids_from_text(id_text)
        st.write(ids or "No 8-digit IDs found.")

    if st.button("📊 Count ID Frequencies"):
        series = pd.Series(id_text.splitlines())
        freq_df = extract_8digit_ids_from_series(series)
        st.dataframe(freq_df if not freq_df.empty else "No IDs to count.")

    st.write("---")
    st.subheader("Find Duplicates Between Two Texts")
    text_a = st.text_area("Text A", height=80, key="a")
    text_b = st.text_area("Text B", height=80, key="b")
    if st.button("🔁 Show Duplicates"):
        dup = extract_duplicates_between(text_a, text_b)
        st.write(dup or "No duplicates found.")
