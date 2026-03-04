# 🌉 DBridger

**The Secure Legacy AI Gateway.** DBridger bridges the gap between old-world databases and modern AI Agents (Claude, ChatGPT, etc.) using the Model Context Protocol (MCP).

## 🚀 Features

* **Generic Data Mapping**: Works with any SQLite table without hard-coding column names.
* **Automated PII Masking**: Built-in regex engine that redacts emails and sensitive info before the AI sees it.
* **Schema Introspection**: Allows AI agents to view available tables and columns safely.
* **Dual-Layer Validation**: Every table and column name is verified against the database metadata to prevent **SQL Injection**.
* **Environment Aware**: Configurable via `.env` files for easy deployment across different client environments.

---

## 📂 Project Structure

* `src/server.py`: The MCP server core.
* `src/security.py`: The PII redaction logic ("The Moat").
* `data/example.db`: Your local demo database.
* `.env`: Local configuration (ignored by Git).

---

## 🛠️ Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup the Node inspector
npm install

```

### 2. Configuration

Create a `.env` file in the root:

```text
DB_PATH=data/example.db

```

### 3. Run the Demo

```bash
# Start the MCP Inspector to see the UI
npm run inspect

```

---

## 🛡️ How DBridger protects your data

Unlike standard SQL wrappers, DBridger keeps your data safe by treating external AIs as untrusted entities.

1. The AI asks for data.
2. DBridger **validates** the table/column exists.
3. DBridger **fetches** the data.
4. DBridger **scrubs** the data for PII.
5. The AI receives only what it needs to see.
