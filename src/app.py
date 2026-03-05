import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QTabWidget, QLineEdit, 
    QTextEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.server import search_records, list_tables, list_columns

class DBridgerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBridger: Secure Legacy AI Gateway")
        self.resize(1000, 700)
        self.active_db_path = None

        self.setStyleSheet("""
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
        """)

        self.init_ui()

    def init_ui(self):
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)

        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(15)

        title_label = QLabel("🌉 DBridger")
        title_label.setObjectName("header")
        sidebar_layout.addWidget(title_label)

        self.btn_open_db = QPushButton("📂 Open Local Database")
        self.btn_open_db.clicked.connect(self.open_database)
        sidebar_layout.addWidget(self.btn_open_db)

        self.lbl_status = QLabel("Status: No database connected")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("color: #888888; font-style: italic;")
        sidebar_layout.addWidget(self.lbl_status)

        schema_label = QLabel("📋 Schema Explorer")
        schema_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        sidebar_layout.addWidget(schema_label)

        self.tree_schema = QTreeWidget()
        self.tree_schema.setHeaderLabel("Tables & Columns")
        sidebar_layout.addWidget(self.tree_schema)

        main_content_widget = QWidget()
        main_layout = QVBoxLayout(main_content_widget)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.setup_manual_search_tab()
        self.setup_ai_agent_tab()

        main_splitter.addWidget(sidebar_widget)
        main_splitter.addWidget(main_content_widget)
        main_splitter.setSizes([250, 750])

    def setup_manual_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        input_layout = QHBoxLayout()
        self.inp_table = QLineEdit()
        self.inp_table.setPlaceholderText("Table Name (e.g., customers)")
        self.inp_col = QLineEdit()
        self.inp_col.setPlaceholderText("Column (e.g., company_name)")
        self.inp_val = QLineEdit()
        self.inp_val.setPlaceholderText("Search Keyword")

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
        self.tabs.addTab(tab, "🔍 Manual Search")

    def setup_ai_agent_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info_label = QLabel("The AI Agent will automatically navigate tables to solve queries.")
        layout.addWidget(info_label)

        self.inp_query = QLineEdit()
        self.inp_query.setPlaceholderText("Ask a question (e.g., Which orders are flagged as high risk?)")
        self.inp_query.returnPressed.connect(self.run_ai_agent) # Press Enter to send
        
        self.btn_ask = QPushButton("🧠 Ask Agent")
        self.btn_ask.clicked.connect(self.run_ai_agent)

        self.txt_agent_output = QTextEdit()
        self.txt_agent_output.setReadOnly(True)
        self.txt_agent_output.setFont(QFont("Consolas", 10))

        layout.addWidget(self.inp_query)
        layout.addWidget(self.btn_ask)
        layout.addWidget(self.txt_agent_output)
        self.tabs.addTab(tab, "🧠 AI Agent")

    def open_database(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Local Database", "", "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if file_path:
            self.active_db_path = file_path
            os.environ["DB_PATH"] = file_path
            filename = os.path.basename(file_path)
            self.lbl_status.setText(f"Connected:\n{filename}")
            self.lbl_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.refresh_schema()

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

    def run_manual_search(self):
        if not self.active_db_path:
            QMessageBox.warning(self, "Error", "Please open a database first.")
            return

        t = self.inp_table.text().strip()
        c = self.inp_col.text().strip()
        v = self.inp_val.text().strip()

        if not t or not c or not v:
            QMessageBox.warning(self, "Error", "All search fields are required.")
            return

        self.txt_results.append(f"Searching {t} -> {c} for '{v}'...")
        results = search_records(t, c, v)
        self.txt_results.append(f"{results}\n{'-'*40}")

    def run_ai_agent(self):
        if not self.active_db_path:
            QMessageBox.warning(self, "Error", "Please open a database first.")
            return
            
        query = self.inp_query.text().strip()
        if not query: return

        self.txt_agent_output.append(f"👤 You: {query}")
        self.inp_query.clear()

        self.txt_agent_output.append("🤖 Agent: Thinking... (FUTURE IMPLEMENTATION)\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DBridgerApp()
    window.show()
    sys.exit(app.exec())
