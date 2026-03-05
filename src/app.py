import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QTabWidget, QLineEdit, 
    QTextEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.server import search_records, list_tables, list_columns

APP_STYLE = """
    QWidget {
        background-color: #1E1E1E;
        color: #D4D4D4;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }
    QPushButton {
        background-color: #0E639C;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 12px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #1177BB; }
    QPushButton:pressed { background-color: #094771; }
    QLineEdit, QTextEdit, QTreeWidget {
        background-color: #252526;
        border: 1px solid #3C3C3C;
        border-radius: 4px;
        padding: 6px;
    }
    QTabWidget::pane { border: 1px solid #3C3C3C; top: -1px; }
    QTabBar::tab {
        background: #2D2D2D;
        border: 1px solid #3C3C3C;
        padding: 8px 16px;
        margin-right: 2px;
    }
    QTabBar::tab:selected { background: #0E639C; color: white; }
    QLabel#header { font-size: 18px; font-weight: bold; color: #FFFFFF; }
    QTreeWidget::item:selected { background-color: #37373D; }
"""

class SidebarWidget(QWidget):
    """Handles Database Connection and Schema Exploration."""
    db_connected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        title_label = QLabel("🌉 DBridger")
        title_label.setObjectName("header")
        
        self.btn_open_db = QPushButton("📂 Open Local Database")
        self.btn_open_db.clicked.connect(self.open_database)
        
        self.lbl_status = QLabel("Status: No database connected")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("color: #888888; font-style: italic;")
        
        schema_label = QLabel("📋 Schema Explorer")
        schema_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        self.tree_schema = QTreeWidget()
        self.tree_schema.setHeaderLabel("Tables & Columns")

        layout.addWidget(title_label)
        layout.addWidget(self.btn_open_db)
        layout.addWidget(self.lbl_status)
        layout.addWidget(schema_label)
        layout.addWidget(self.tree_schema)

    def open_database(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Local Database", "", "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        if file_path:
            os.environ["DB_PATH"] = file_path
            self.lbl_status.setText(f"Connected:\n{os.path.basename(file_path)}")
            self.lbl_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.refresh_schema()

            self.db_connected.emit(file_path) 

    def refresh_schema(self):
        self.tree_schema.clear()
        try:
            tables_str = list_tables()
            tables = tables_str.replace("Available Tables: ", "").split(", ")
            for table in tables:
                if not table.strip(): continue
                table_item = QTreeWidgetItem([table.strip()])
                self.tree_schema.addTopLevelItem(table_item)

                cols_str = list_columns(table.strip())
                cols = cols_str.replace("Columns: ", "").split(", ")
                for col in cols:
                    if col.strip():
                        child_item = QTreeWidgetItem([f"↳ {col.strip()}"])
                        child_item.setForeground(0, Qt.GlobalColor.gray)
                        table_item.addChild(child_item)
        except Exception as e:
            QMessageBox.critical(self, "Schema Error", str(e))


class ManualSearchWidget(QWidget):
    """Handles secure manual searching of the database."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        input_layout = QHBoxLayout()
        self.inp_table = QLineEdit(); self.inp_table.setPlaceholderText("Table Name")
        self.inp_col = QLineEdit(); self.inp_col.setPlaceholderText("Column")
        self.inp_val = QLineEdit(); self.inp_val.setPlaceholderText("Search Keyword")

        input_layout.addWidget(self.inp_table)
        input_layout.addWidget(self.inp_col)
        input_layout.addWidget(self.inp_val)
        
        self.btn_search = QPushButton("🔍 Execute Secure Search")
        self.btn_search.clicked.connect(self.run_manual_search)

        self.txt_results = QTextEdit()
        self.txt_results.setReadOnly(True)
        self.txt_results.setFont(QFont("Consolas", 10))

        layout.addLayout(input_layout)
        layout.addWidget(self.btn_search)
        layout.addWidget(self.txt_results)

    def run_manual_search(self):
        t, c, v = self.inp_table.text().strip(), self.inp_col.text().strip(), self.inp_val.text().strip()
        if not t or not c or not v:
            QMessageBox.warning(self, "Error", "All search fields are required.")
            return

        self.txt_results.append(f"Searching {t} -> {c} for '{v}'...")
        results = search_records(t, c, v)
        self.txt_results.append(f"{results}\n{'-'*40}")


class AIAgentWidget(QWidget):
    """Handles the conversational AI Agent interface."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("The AI Agent will automatically navigate tables to solve queries."))

        self.inp_query = QLineEdit()
        self.inp_query.setPlaceholderText("Ask a question (e.g., Which orders are flagged as high risk?)")
        self.inp_query.returnPressed.connect(self.run_ai_agent)
        
        self.btn_ask = QPushButton("🧠 Ask Agent")
        self.btn_ask.clicked.connect(self.run_ai_agent)

        self.txt_agent_output = QTextEdit()
        self.txt_agent_output.setReadOnly(True)
        self.txt_agent_output.setFont(QFont("Consolas", 10))

        layout.addWidget(self.inp_query)
        layout.addWidget(self.btn_ask)
        layout.addWidget(self.txt_agent_output)

    def run_ai_agent(self):
        query = self.inp_query.text().strip()
        if not query: return

        self.txt_agent_output.append(f"👤 You: {query}")
        self.inp_query.clear()
        self.txt_agent_output.append("🤖 Agent: Thinking... (FUTURE IMPLEMENTATION)\n")

class DBridgerApp(QMainWindow):
    """The main window that coordinates all sub-components."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBridger: Secure Legacy AI Gateway")
        self.resize(1000, 700)
        self.setStyleSheet(APP_STYLE)
        
        self.active_db_path = None
        self.init_ui()

    def init_ui(self):
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)

        self.sidebar = SidebarWidget()
        self.search_tab = ManualSearchWidget()
        self.agent_tab = AIAgentWidget()

        self.sidebar.db_connected.connect(self.on_database_loaded)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.search_tab, "🔍 Manual Search")
        self.tabs.addTab(self.agent_tab, "🧠 AI Agent")

        self.tabs.setEnabled(False) 

        main_splitter.addWidget(self.sidebar)
        main_splitter.addWidget(self.tabs)
        main_splitter.setSizes([250, 750])

    def on_database_loaded(self, file_path):
        """Triggered when the Sidebar successfully loads a database."""
        self.active_db_path = file_path
        self.tabs.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DBridgerApp()
    window.show()
    sys.exit(app.exec())
