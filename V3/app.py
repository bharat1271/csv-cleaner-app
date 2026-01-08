import streamlit as st
import pandas as pd
from io import StringIO
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
    extract_affili_ids_strict,
    extract_group_ids,
    ids_to_lines,
    ids_to_csv,
    detect_and_clean_junk_characters,
    reconcile_orgid_counts,
    # extract_variant_name_city,
    # extract_variant_names,
    run_ocr_on_image,
    get_tesseract_languages,
)
from PIL import Image

import os

if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

st.set_page_config(page_title="CSV Cleaner & Text Utilities", layout="wide")
st.title("🧹 CSV & Text Utilities Platform")

TAB1, TAB2, TAB3, TAB4 = st.tabs([
    "📂 CSV Cleaning",
    "📝 Text Utilities",
    "📌 Project Specific Implementations",
    "🖼️ Image to Text (OCR)"
])

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
    # ✍ TEXT CLEANUP
    with st.expander("✍ Text Cleanup"):

        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            if st.button("🧠 Convert to Smart Title", help="Input: Sentence with inconsistent Capitalization || Output: Text will be in Title format"):
                result = smart_title_text(text_input)
                st.code(result)
                
        with col2:
            if st.button("🧹 Detect & Clean Junk Characters"):
                highlighted, cleaned = detect_and_clean_junk_characters(text_input)
                st.subheader("🔍 Highlighted Junk Characters")
                st.code(highlighted, language="text")
                st.subheader("✨ Cleaned Text")
                st.code(cleaned, language="text")


    with st.expander("🆔 Extraction Tools", expanded=True):

        col3, col4, col5, col6 = st.columns(4)
    
    
        with col3:
            if st.button("🔢 Extract 8-digit IDs", help="Input: 8 digit Id's OR numbers || Output: first 8 digit of numeric text || Tip: useful in extracting OrgId's"):
                ids = extract_ids(text_input)
                st.code(ids)
                
        with col4:
            if st.button("🧾 Extract IDs and Names", help="Input: exact copy of Id's and names text from Orgtool || Output: combination of OrgId and Names in a clean excel friendly format || Tip: useful in quickly recording and sharing OrgID and Names"):
                extracted = extract_ids_and_names(text_input)
                st.code(extracted)
                
        with col5:
            if st.button("📥 Extract AfiliD only", help="Input: Raw text from processed review page of a collection || Output: Affiliation Id's in comma saparated format || Tip: useful in quickly extracting and sharing AffilID's"):
                afili_result = extract_affili_ids_strict(text_input)
                st.text_area("AfiliD values:", afili_result, height=100, key="afili_output")
    
        with col6:
            if st.button("📥 Extract Group ID only", help="Input: Raw text from processed review page of a collection || Output: Group Id's in comma saparated format || Tip: useful in quickly extracting and sharing GroupId's"):
                group_result = extract_group_ids(text_input)
                st.text_area("Group ID values:", group_result, height=100, key="group_output")
            
    with st.expander("📊 ID Utilities"):
    
        col7, col8, col9, col10 = st.columns(4)
                
    
        with col7:
            if st.button("🔍 Count IDs", help="Input: 8 digit Id's OR numbers || Output: count of first 8 digit of numeric text || Tip: useful in counting OrgId's in a input text"):
                count_df = count_ids(text_input)
                st.dataframe(count_df)
    
        with col8:
            if st.button("🧬 Find Duplicates & Unique Values", help="Input: 8 digit Id's OR numbers || Output: saparate duplicate and unique first 8 digit number/OrgId || Tip: useful in find duplicate OrgId's in a input text"):
                dupes, uniques = find_duplicates_and_uniques(text_input)
                st.write(f"**Duplicates:** {dupes}")
                st.write(f"**Unique Values:** {uniques}")
                
    
        with col9:
            if st.button("➡️ Comma → Lines", help="Input: 8 Digit OrgId's/Numbers in a comma separated format || Output: 8 digit Id's/numbers in separate lines || Tip: useful in quickly converting the format"):
                result = ids_to_lines(text_input)
                st.text_area("Converted to Line Format:", result, height=150, key="to_lines")
    
        with col10:
            if st.button("➡️ Lines → Comma", help="Input: 8 Digit OrgId's/Numbers in a new-line separated format || Output: 8 digit Id's/numbers in a comma separated format || Tip: useful in quickly converting the format"):
                result = ids_to_csv(text_input)
                st.text_area("Converted to CSV Format:", result, height=150, key="to_csv")

    # with st.expander("### 🧩 Variant Extraction"):

    #     col11, col12, col13, col14 = st.columns(4)

    #     with col11:
    #         if st.button(
    #             "🏷️ Extract Variant Names",
    #             help="Input: Raw OrgTool Variants page text, Output: [\"Variant1\",\"Variant2\"]"
    #         ):
    #             variant_only = extract_variant_names(text_input)
    #             st.text_area(
    #                 "Variant Names",
    #                 variant_only,
    #                 height=150,
    #                 key="variant_only_output"
    #             )

    #     with col12:
    #         if st.button(
    #             "🏙️ Variant + City",
    #             help="Input: Raw OrgTool Variants page text, Output: [\"Variant City\",\"Variant City\"]"
    #         ):
    #             variant_city = extract_variant_name_city(text_input)
    #             st.text_area(
    #                 "Variant + City",
    #                 variant_city,
    #                 height=150,
    #                 key="variant_city_output"
    #         )

with TAB3:
    with st.expander("📌 OrgID – Affiliation Count Checker (4GU Emergent)"):

        pasted_table = st.text_area(
            "Paste OrgID + Count here (copied from Excel). Example:\n60018562 5\n60022576 3",
            height=150
        )
    
        df = None
        if pasted_table.strip():
            try:
                df = pd.read_csv(StringIO(pasted_table), 
                                 sep=r"\s+|,|\t",
                                 engine="python",
                                 header=None)
    
                if df.shape[1] == 2:
                    df.columns = ["OrgID", "Count"]
                else:
                    st.error("Input must have exactly TWO columns: OrgID and Count")
    
                st.write("Parsed Input:")
                st.dataframe(df)
    
            except Exception as e:
                st.error(f"Could not parse input table: {e}")
    
        collection_text = st.text_area(
            "Paste raw collection text here (copied from OrgTool page).",
            height=300
        )
    
        if st.button("Run Count Check"):
            if df is None:
                st.error("Please paste a valid OrgID+Count table above.")
            elif not collection_text.strip():
                st.error("Please paste collection text.")
            else:
                output_df = reconcile_orgid_counts(df, collection_text)
                st.success("Reconciliation Complete!")
                st.dataframe(output_df)
    
                st.download_button(
                    "Download Results as CSV",
                    output_df.to_csv(index=False).encode("utf-8"),
                    "orgid_reconciliation.csv",
                    "text/csv"
                )

with TAB4:
    st.header("🖼️ Image to Text (OCR)")
    st.caption(
        "Upload screenshots or image-based content. "
        "Select the correct OCR language for best accuracy."
    )

    uploaded_image = st.file_uploader(
        "Upload image (PNG / JPG / JPEG)",
        type=["png", "jpg", "jpeg"]
    )

    lang_map = get_tesseract_languages()

    if not lang_map:
        st.error("No Tesseract languages found. Check Tesseract installation.")
    else:
        ocr_lang_label = st.selectbox(
            "OCR Language",
            list(lang_map.keys()),
            index=list(lang_map.values()).index("eng") if "eng" in lang_map.values() else 0
        )

        ocr_lang_code = lang_map[ocr_lang_label]

        if ocr_lang_code.startswith(("chi", "jpn", "kor")):
            ocr_mode = "cjk"
        else:
            ocr_mode = st.selectbox(
                "OCR Mode",
                ["auto", "latin", "raw"],
                index=0
            )

        if uploaded_image:
            image = Image.open(uploaded_image)

            col_img, col_txt = st.columns([1, 1])

            with col_img:
                st.subheader("Image Preview")
                st.image(image, use_container_width=True)

            with col_txt:
                st.subheader("Extracted Text")

                with st.spinner("Running OCR..."):
                    extracted_text = run_ocr_on_image(
                        image,
                        lang=ocr_lang_code,
                        ocr_mode=ocr_mode
                    )

                st.session_state.ocr_text = st.text_area(
                    "OCR Output (editable)",
                    extracted_text,
                    height=360
                )

            st.info("Tip: If text looks like gibberish, the OCR language is incorrect. ""Select the correct language and re-run.")














