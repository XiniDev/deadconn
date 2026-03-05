from google import genai
from google.genai import types
from src.server import search_records, list_tables, list_columns

class DBridgerAgent:
    def __init__(self, api_key: str):
        """Initializes the Gemini model and gives it access to our secure tools."""
        self.client = genai.Client(api_key=api_key)

        config = types.GenerateContentConfig(
            system_instruction=(
                "You are DBridger, a secure local database assistant. "
                "You have access to tools to read the database schema and search records. "
                "IMPORTANT RULES: "
                "1. If you don't know the table names, ALWAYS call list_tables() first. "
                "2. If you don't know the columns, call list_columns(table_name). "
                "3. Use search_records to find the actual data. "
                "4. Present the final masked data clearly to the user."
            ),
            tools=[search_records, list_tables, list_columns],
            temperature=0.1,
        )

        self.chat = self.client.chats.create(
            model='gemini-3-flash-preview',
            config=config
        )

    def ask_question(self, user_query: str) -> str:
        """Sends the question to Gemini and returns the final response."""
        try:
            response = self.chat.send_message(user_query)
            return response.text
        except Exception as e:
            return f"Agent Error: {str(e)}"
