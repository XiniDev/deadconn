import streamlit as st
import os
from src.server import search_records, list_tables, list_columns

st.set_page_config(page_title="DBridger AI", page_icon="🌉")

st.title("🌉 DBridger: Legacy AI Gateway")
st.sidebar.header("Connection Settings")

db_path = st.sidebar.text_input("Database Path", value=os.getenv("DB_PATH", "data/example.db"))

if st.button("Connect to Database"):
    tables = list_tables()
    st.success(f"Connected! {tables}")

query = st.text_input("Ask your database a question:")
if query:
    st.info(f"AI is analyzing tables to solve: {query}")
    st.write("Results will appear here with PII masking applied.")