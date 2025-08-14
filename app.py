import os
from pathlib import Path
import streamlit as st

# Reuse your existing helpers
from db import get_conn, init_db
from ingest import extract_text, upsert_doc

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Policy Report Search", layout="wide")
st.title("Policy Report Search & Dashboard")
st.caption("Upload PDFs below or place them in 'data/' and run 'python ingest.py'. Search is powered by SQLite FTS5.")

# Ensure DB exists
init_db()
conn = get_conn()

# --- Sidebar: admin actions ---
with st.sidebar:
    st.header("Admin")
    if st.button("Clear database (keeps files)", type="secondary"):
        conn.execute("DELETE FROM docs;")
        conn.execute("DELETE FROM docs_fts;")
        conn.commit()
        st.success("Database cleared.")

# --- File uploader ---
st.subheader("Upload PDFs")
uploaded = st.file_uploader(
    "Drop one or more PDF reports here",
    type=["pdf"],
    accept_multiple_files=True
)

def sanitize_filename(name: str) -> str:
    # Simple cross-platform filename sanitizer
    keep = "-_.() "
    return "".join(c for c in name if c.isalnum() or c in keep).strip() or "document.pdf"

if uploaded:
    for file in uploaded:
        raw_name = file.name if file.name.lower().endswith(".pdf") else f"{file.name}.pdf"
        safe_name = sanitize_filename(raw_name)
        save_path = DATA_DIR / safe_name

        # Write bytes so the file is available for download later
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())

        # Extract text and insert into DB
        try:
            content = extract_text(save_path)
            title = Path(safe_name).stem.replace("_", " ").title()
            upsert_doc(conn, title=title, source_path=save_path, organization="", pub_date="", content=content)
            st.success(f"Ingested: {safe_name}")
        except Exception as e:
            st.error(f"Failed to ingest {safe_name}: {e}")

# --- Search UI ---
st.subheader("Search")
query = st.text_input("Search reports", placeholder="e.g., charter schools, algorithmic transparency")

def search(q: str, limit: int = 20):
    if not q.strip():
        return []
    sql = """
    SELECT d.id, d.title, d.organization, d.pub_date, d.source_path,
           snippet(docs_fts, 0, '[', ']', ' … ', 12) AS snippet
    FROM docs_fts JOIN docs d ON docs_fts.rowid = d.id
    WHERE docs_fts MATCH ?
    ORDER BY rank
    LIMIT ?;
    """
    cur = conn.execute(sql, (q, limit))
    cols = ["id","title","organization","pub_date","source_path","snippet"]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

if query:
    results = search(query)
    st.caption(f"{len(results)} result(s)")
    for r in results:
        st.subheader(r["title"])
        meta = " • ".join(x for x in [r["organization"], r["pub_date"]] if x)
        if meta:
            st.markdown(meta)
        st.write(r["snippet"])

        # Offer download when file exists (works locally and on Streamlit Cloud during the session)
        pdf_path = Path(r["source_path"]) if r["source_path"] else None
        if pdf_path and pdf_path.exists():
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", data=f.read(), file_name=pdf_path.name)
        st.divider()
else:
    st.caption("Type a query to search the ingested corpus.")