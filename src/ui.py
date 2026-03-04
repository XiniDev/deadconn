import streamlit as st
import os
import shutil
from src.server import search_records, list_tables, list_columns

st.set_page_config(page_title="DBridger", page_icon="🌉", layout="wide")
st.title("🌉 DBridger: Secure Legacy AI Gateway")

if not os.path.exists("data"):
    os.makedirs("data")

if "uploader_id" not in st.session_state:
    st.session_state.uploader_id = 0
if "selectbox_id" not in st.session_state:
    st.session_state.selectbox_id = 0

def on_upload_change():
    """Triggered immediately when a file is uploaded."""
    current_key = f"uploader_{st.session_state.uploader_id}"
    uploaded_file = st.session_state[current_key]
    
    if uploaded_file is not None:
        save_path = os.path.join("data", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.active_db_selection = uploaded_file.name
        st.session_state.uploader_id += 1
        st.session_state.selectbox_id += 1
        st.toast(f"Success: {uploaded_file.name} is now available.", icon="✅")

def delete_active_db(filename):
    """Deletes the physical file and resets UI state."""
    file_path = os.path.join("data", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        if 'active_db_selection' in st.session_state:
            del st.session_state['active_db_selection']
        st.session_state.selectbox_id += 1
        st.toast(f"Removed {filename} from storage.", icon="🗑️")
        st.rerun()


with st.sidebar:
    st.header("🔌 Connection Hub")

    st.file_uploader(
        "Add new database (.db)", 
        type=["db", "sqlite", "sqlite3"],
        key=f"uploader_{st.session_state.uploader_id}",
        on_change=on_upload_change
    )

    existing_files = [f for f in os.listdir("data") if f.endswith(('.db', '.sqlite', '.sqlite3'))]

    if existing_files:
        try:
            current_index = existing_files.index(st.session_state.get('active_db_selection'))
        except (ValueError, KeyError):
            current_index = 0

        selected_file = st.selectbox(
            "Select Database to Bridge", 
            options=existing_files, 
            index=current_index,
            key=f"selectbox_{st.session_state.selectbox_id}"
        )

        if selected_file:
            st.session_state.active_db_selection = selected_file
            active_path = os.path.join("data", selected_file)
            os.environ["DB_PATH"] = active_path

            if st.button(f"🗑️ Delete {selected_file}", use_container_width=True):
                delete_active_db(selected_file)
    else:
        st.session_state.pop('active_db_selection', None)
        st.warning("⚠️ No databases found. Please upload a .db file to begin.")

    st.divider()
    if st.button("🔄 Force Refresh Schema", use_container_width=True):
        tables = list_tables()
        st.session_state['tables_list'] = tables

    st.divider()
    st.header("📋 Schema Explorer")
    if st.button("🔍 Inspect All Tables", use_container_width=True):
        tables_str = list_tables()
        tables = tables_str.replace("Available Tables: ", "").split(", ")
        for table in tables:
            with st.expander(f"Table: {table}"):
                cols = list_columns(table)
                st.write(f"**Columns:** {cols}")


if 'active_db_selection' in st.session_state and st.session_state.active_db_selection in existing_files:
    st.info(f"Connected to: **{st.session_state.active_db_selection}**")
else:
    st.error("Please select or upload a database in the sidebar to start searching.")
    st.stop()

tabs = st.tabs(["🔍 Manual Search", "🧠 AI Agent"])

with tabs[0]:
    st.markdown("### Search Vault")
    col1, col2, col3 = st.columns(3)
    with col1:
        target_table = st.text_input("Table Name", placeholder="Input table name...")
    with col2:
        target_col = st.text_input("Column Name", placeholder="Input column name...")
    with col3:
        target_val = st.text_input("Search Value", placeholder="Input keyword to find...")

    if st.button("Execute Secure Search", type="primary"):
        if not target_table or not target_col or not target_val:
            st.warning("All fields are required for a manual search.")
        else:
            results = search_records(target_table, target_col, target_val)
            if "Error" in results:
                st.error(results)
            else:
                st.success("Results Retrieved (PII Masking Applied)")
                st.code(results, language="text")

with tabs[1]:
    st.write("The AI Agent will automatically navigate your tables to solve business queries.")
    st.text_input("Ask a question about this database:", placeholder="e.g., Which orders are currently flagged as high risk?")