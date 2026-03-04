import streamlit as st
import os
from src.server import search_records, list_tables, list_columns

st.set_page_config(page_title="DBridger", page_icon="🌉")
st.title("🌉 DBridger: Secure Legacy AI Gateway")

with st.sidebar:
    st.header("Connection Settings")
    db_path = st.text_input("Local DB Path", value="data/example.db")
    os.environ["DB_PATH"] = db_path
    
    if st.button("Refresh Schema"):
        tables = list_tables()
        st.session_state['tables'] = tables

st.subheader("Manual Search")
col1, col2, col3 = st.columns(3)

with col1:
    target_table = st.text_input("Table", value="customers")
with col2:
    target_col = st.text_input("Column", value="company_name")
with col3:
    target_val = st.text_input("Search Value", value="Wayne")

if st.button("Search Database"):
    results = search_records(target_table, target_col, target_val)
    
    if "Error" in results:
        st.error(results)
    else:
        st.success("Data Retrieved (PII Masked)")
        st.code(results, language="text")

st.divider()

query = st.text_input("Ask your database a question:")
if query:
    st.info(f"AI is analyzing tables to solve: {query}")
    st.write("Results will appear here with PII masking applied.")