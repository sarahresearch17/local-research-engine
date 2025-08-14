# local-research-engine
# # Policy Report Search & Dashboard
A small search app for policy PDFs. Ingests a corpus of public reports, indexes with SQLite FTS5, and provides keyword search with context snippets and download links.

Tech: Python, SQLite (FTS5), Streamlit.

## Quick start
1) Put PDFs in ./data
2) pip install -r requirements.txt
3) python ingest.py
4) streamlit run app.py

Notes: Initial build Summer 2025. Expanding corpus and metadata over time.
