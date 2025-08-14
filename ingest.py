from pathlib import Path
from pypdf import PdfReader
import sqlite3
from db import get_conn, init_db

DATA_DIR = Path("data")

def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages)

def upsert_doc(conn: sqlite3.Connection, title, source_path, organization, pub_date, content):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO docs(title, source_path, organization, pub_date) VALUES (?,?,?,?)",
        (title, str(source_path), organization, pub_date)
    )
    doc_id = cur.lastrowid
    cur.execute("INSERT INTO docs_fts(rowid, content) VALUES (?,?)", (doc_id, content))
    conn.commit()
    return doc_id

def main():
    init_db()
    conn = get_conn()
    for pdf in sorted(DATA_DIR.glob("*.pdf")):
        content = extract_text(pdf)
        title = pdf.stem.replace("_", " ").title()
        upsert_doc(conn, title=title, source_path=pdf, organization="", pub_date="", content=content)
    conn.close()

if __name__ == "__main__":
    main()