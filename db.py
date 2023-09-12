import os
import sqlite3
from sqlite3 import Cursor


def get_db_conn():
    return sqlite3.connect(get_db_path())


def get_db_path():
    return os.path.expanduser('~/personal-chatgpt.sqlite')


def create_tables():
    db_path = get_db_path()

    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Check if the conversations table already exists
    c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='conversations'")
    table_exists = c.fetchone()[0]

    # Create the conversations table if it doesn't already exist
    if not table_exists:
        c.execute('''
        CREATE TABLE conversations (
          id INTEGER PRIMARY KEY,
          summary TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        c.execute('''
        CREATE TABLE messages (
          id INTEGER PRIMARY KEY,
          conversation_id INTEGER,
          role TEXT,
          content TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );
        ''')

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()


def fetch_messages(conversation_id: int):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute(
        'SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC',
        conversation_id,
    )
    messages = c.fetchall()
    conn.close()
    return messages


def fetch_all_conversations():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('SELECT id FROM conversations ORDER BY created_at DESC')
    conversation_ids = list(map(lambda convo: convo[0], c.fetchall()))
    conversations = []
    for convo_id in conversation_ids:
        conversations = conversations + [fetch_conversation(conversation_id=convo_id)]
    conn.close()
    return list(conversations)


def fetch_conversation(conversation_id):
    if conversation_id == '' or conversation_id is None:
        return None
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('SELECT id, summary FROM conversations WHERE id = ?', (int(conversation_id),))
    conversation = c.fetchone()
    c.execute('SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at ASC', (int(conversation_id),))
    messages = c.fetchall()
    conn.close()
    return {
        'id': conversation[0],
        'summary': conversation[1],
        'messages': list(map(lambda m: {'role': m[0], 'content': m[1]}, messages)),
    }


def fetch_conversation_next_id():
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('SELECT max(id) FROM conversations')
    result = c.fetchone()[0]
    return 1 if result is None else result + 1

def add_conversation(c: Cursor, summary: str):
    c.execute('INSERT INTO conversations (summary) VALUES (?)', (summary, ))


def add_message(c: Cursor, conversation_id, role: str, content: str):
    c.execute('INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)', (int(conversation_id), role, content))
