import sqlite3
from db import get_conn
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Policy Report Search", layout="wide")
st.title("Policy Report Search & Dashboard")
st.caption("Put PDFs in the 'data' folder, run 'python ingest.py', then search.")

query = st.text_input("Search reports", placeholder="e.g., charter schools, algorithmic transparency")
conn = get_conn()

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
        pdf_path = Path(r["source_path"])
        if pdf_path.exists():
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", data=f.read(), file_name=pdf_path.name)
        st.divider()
else:
    st.write("Waiting for a query…")