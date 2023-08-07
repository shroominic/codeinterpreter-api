import sqlite3
from datetime import datetime


class DBManager:
    def __init__(self, db_name='chat.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self):
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT 'New Chat',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        ''')
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                category TEXT,
                content TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY(chat_id) REFERENCES chats(id)
            )
        ''')
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS generated_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_message_id INTEGER,
                name TEXT,
                content BLOB,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY(chat_message_id) REFERENCES chat_messages(id)
            )
        ''')

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_query(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    # Chat Operations
    def save_chat(self, title):
        now = datetime.now()
        self.execute_query('''
            INSERT INTO chats (title, created_at, updated_at)
            VALUES (?, ?, ?)
        ''', (title, now, now))
        return self.cursor.lastrowid

    def update_chat_title(self, chat_id, title):
        now = datetime.now()
        self.execute_query('''
            UPDATE chats
            SET title = ?, updated_at = ?
            WHERE id = ?
        ''', (title, now, chat_id))

    def get_chats(self):
        return self.fetch_query("SELECT * FROM chats ORDER BY updated_at DESC")

    def get_chat(self, chat_id):
        return self.fetch_query("SELECT * FROM chats WHERE id = ?", (chat_id,))[0]

    # Chat Message Operations
    def save_message(self, chat_id, category, content):
        now = datetime.now()
        self.execute_query('''
            INSERT INTO chat_messages (chat_id, category, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (chat_id, category, content, now, now))
        return self.cursor.lastrowid

    def get_chat_messages(self, chat_id):
        return self.fetch_query("SELECT * FROM chat_messages WHERE chat_id = ?", (chat_id,))

    def get_chat_message(self, chat_message_id):
        return self.fetch_query("SELECT * FROM chat_messages WHERE id = ?", (chat_message_id,))[0]

    # File Operations
    def save_file(self, chat_message_id, name, content):
        now = datetime.now()
        self.execute_query('''
            INSERT INTO generated_files (chat_message_id, name, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (chat_message_id, name, content, now, now))

    def get_generated_files(self, chat_message_id):
        return self.fetch_query("SELECT * FROM generated_files WHERE chat_message_id = ?", (chat_message_id,))
