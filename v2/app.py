import streamlit as st
import pandas as pd
from cleaner_utils import (
    smart_title_text,
    extract_ids,
    find_duplicates_and_uniques,
    count_ids,
    extract_ids_and_names,
    remove_duplicates,
    trim_whitespace,
    capitalize_names,
    drop_blank_rows,
    fill_missing_values,
    fix_text_case,
    find_and_replace,
    convert_numbers,
    split_column,
    extract_afili_ids,
    extract_group_ids,
    split_id_name,
)

st.set_page_config(page_title="CSV Cleaner & Text Utilities", layout="wide")
st.title("🧹 CSV & Text Utilities")

TAB1, TAB2 = st.tabs(["📂 CSV Cleaning", "📝 Text Utilities"])

with TAB1:
    st.header("CSV Cleaning Operations")

    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    if "csv_df" not in st.session_state:
        st.session_state.csv_df = None
    if "csv_logs" not in st.session_state:
        st.session_state.csv_logs = []


    if uploaded_file:
        st.session_state.csv_df = pd.read_csv(uploaded_file)
        st.success("File uploaded and loaded successfully!")
        st.write(st.session_state.csv_df.head())

    if st.session_state.csv_df is not None:
        with st.expander("Select and Apply Operations Step-by-Step"):
            if st.checkbox("Remove Duplicates"):
                st.session_state.csv_df, msg = remove_duplicates(st.session_state.csv_df)
                st.session_state.csv_logs.append(msg)
                st.success(msg)

            if st.checkbox("Trim Whitespace"):
                st.session_state.csv_df, msg = trim_whitespace(st.session_state.csv_df)
                st.session_state.csv_logs.append(msg)
                st.success(msg)

            if st.checkbox("Capitalize Names"):
                st.session_state.csv_df, msg = capitalize_names(st.session_state.csv_df)
                st.session_state.csv_logs.append(msg)
                st.success(msg)

            if st.checkbox("Drop Blank Rows"):
                st.session_state.csv_df, msg = drop_blank_rows(st.session_state.csv_df)
                st.session_state.csv_logs.append(msg)
                st.success(msg)

            if st.checkbox("Fill Missing Values"):
                fill_val = st.text_input("Fill Value", "Missing")
                st.session_state.csv_df, msg = fill_missing_values(st.session_state.csv_df, fill_val)
                st.session_state.csv_logs.append(msg)
                st.success(msg)

            if st.checkbox("Fix Text Case"):
                case_mode = st.selectbox("Case Mode", ["lower", "upper", "title"])
                st.session_state.csv_df, msg = fix_text_case(st.session_state.csv_df, mode=case_mode)
                st.session_state.csv_logs.append(msg)
                st.success(msg)

            if st.checkbox("Find and Replace"):
                find_val = st.text_input("Find", "null")
                replace_val = st.text_input("Replace with", "NA")
                st.session_state.csv_df, msg = find_and_replace(st.session_state.csv_df, find_val, replace_val)
                st.session_state.csv_logs.append(msg)
                st.success(msg)

            if st.checkbox("Convert Numbers"):
                st.session_state.csv_df, msg = convert_numbers(st.session_state.csv_df)
                st.session_state.csv_logs.append(msg)
                st.success(msg)

            if st.checkbox("Split Column"):
                split_col = st.text_input("Column to Split", "Full Name")
                delim = st.text_input("Delimiter", " ")
                st.session_state.csv_df, msg = split_column(st.session_state.csv_df, split_col, delimiter=delim)
                st.session_state.csv_logs.append(msg)
                st.success(msg)

        st.subheader("Cleaned Data Preview")
        st.dataframe(st.session_state.csv_df.head())

        st.download_button(
            label="📥 Download Cleaned CSV",
            data=st.session_state.csv_df.to_csv(index=False).encode('utf-8'),
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

        with st.expander("🔍 Cleaning Log"):
            for log in st.session_state.csv_logs:
                st.write("- " + log)

with TAB2:
    st.subheader("🆎 Text Processing Tools")

    text_input = st.text_area("Enter text (IDs, Names, or mixed)", height=150, key="main_text_input")

    # First row: 4 buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🧠 Convert to Smart Title"):
            result = smart_title_text(text_input)
            st.code(result)

    with col2:
        if st.button("🔢 Extract 8-digit IDs"):
            ids = extract_ids(text_input)
            st.code(ids)

    with col3:
        if st.button("🔍 Count IDs"):
            count_df = count_ids(text_input)
            st.dataframe(count_df)

    with col4:
        if st.button("🧬 Find Duplicates & Unique IDs"):
            dupes, uniques = find_duplicates_and_uniques(text_input)
            st.write(f"**Duplicates:** {dupes}")
            st.write(f"**Unique Values:** {uniques}")

    # Second row: 3 buttons, can adjust layout as needed
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        if st.button("🧾 Extract IDs and Names"):
            extracted = extract_ids_and_names(text_input)
            st.code(extracted)

    with col6:
        if st.button("📥 Extract AfiliD only"):
            afili_result = extract_afili_ids(text_input)
            st.text_area("AfiliD values:", afili_result, height=100, key="afili_output")

    with col7:
        if st.button("📥 Extract Group ID only"):
            group_result = extract_group_ids(text_input)
            st.text_area("Group ID values:", group_result, height=100, key="group_output")
    
    # col8 is intentionally left blank to maintain layout alignment
    with col8:
        if st.button("🔎 Split ID and Name"):
            result = split_id_name(text_input)
            st.dataframe(pd.DataFrame(result, columns=["ID", "Name"]))

