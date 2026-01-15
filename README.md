# 🧹 CSV & Text Utilities App

A **production-style CSV cleaning and text utilities web application** built with **Python** and **Streamlit**, designed to automate repetitive data-cleaning and QA tasks commonly encountered in **research analytics**, **affiliation profiling**, and **data validation workflows**.

This project evolved iteratively from a local script into a fully interactive web app, with each version adding real-world capabilities.

---

## 📂 Versions & Evolution

### ✅ Version 1 – Core CSV Cleaning
- Basic CSV cleaning:
  - Remove duplicates
  - Trim whitespace
  - Drop blank rows
  - Fill missing values
  - Fix text case
- Output as cleaned CSV

📂 [View v1 Code](./v1)

---

### 🚀 Version 2 – CSV + Basic Text Utilities
✅ Includes all features of v1, plus:
- Text Utilities:
  - Smart title-case formatting (skips stop words like and, of, the)
  - Identify duplicate and unique values
- UI improvements for better usability

📂 [View v2 Code](./v2)

---

### 🧠 Version 3 – Advanced QA & Automation (Current)

✅ Includes all v2 features, plus significant functional expansion:
- Advanced CSV Cleaning
- Step-by-step, selectable cleaning operations
- Real-time preview of cleaned data
- Action logs for traceability
- Download-ready output after each operation

Extended Text Utilities

- Detect duplicates and unique values from mixed numeric or text inputs
- Convert comma-separated IDs ↔ line-separated formats
- Detect and clean junk/homoglyph characters (copy-paste errors, Unicode issues)

Image-to-Text (OCR)

- Upload screenshots or scanned images
- Extract structured text using local OCR (Tesseract)
- Optimized for website screenshots and UI text
- Output reusable text for further processing

Offline Translation (Optional, Local)

- Translate extracted text using local Argos Translate models
- No external APIs or data sharing
- Designed for multilingual affiliation and metadata checks

📂 [View v3 Code](./V3)

---

## 🌐 Live Demo (v3)
👉 [Click to open the app](https://bh-datacleaner.streamlit.app/)

---

## 🛠 Tech Stack
- Python
- Streamlit
- Pandas
- Regular Expressions
- Tesseract OCR
- Argos Translate (offline translation)

---

## ✅ How to Run Locally
1. Clone the repo:
 git clone https://github.com/bharat1271/csv-cleaner-app.git
 cd csv-cleaner-app/v2

2. Install dependencies:
 pip install -r requirements.txt

3. Run Streamlit app:
 streamlit run app.py

⚠️ OCR requires a local Tesseract installation.

---

### 🔥 Key Features at a Glance

✔ Upload → Clean → Preview → Download workflow
✔ Modular CSV cleaning with traceable logs
✔ Advanced text utilities
✔ OCR for screenshot-based validation
✔ Local, offline-first design (privacy-safe) 

---

## 👤 Author
**Bharat Kumar**  
Data Research Analyst | Research Intelligence | Data Quality Automation

---

## ⭐ Contribution & Feedback
This project is actively evolving.
Suggestions, improvements, and refactoring ideas are welcome - feel free to fork or raise an issue.
