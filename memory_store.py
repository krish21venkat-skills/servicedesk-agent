import pyodbc, json, datetime

SERVER = "localhost\\SQLEXPRESS"
DATABASE = "service_desk"

def get_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

def init_memory():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='memory' AND xtype='U')
        CREATE TABLE memory (
            thread_id NVARCHAR(255) PRIMARY KEY,
            history NVARCHAR(MAX),
            updated_at DATETIME2
        )
    """)
    conn.commit()
    conn.close()

def get_history(thread_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT history FROM memory WHERE thread_id = ?", (thread_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

def append_turn(thread_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.utcnow()

    history = get_history(thread_id)
    history.append({"role": role, "content": content})
    history_json = json.dumps(history)

    cursor.execute("SELECT thread_id FROM memory WHERE thread_id = ?", (thread_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE memory SET history = ?, updated_at = ? WHERE thread_id = ?",
            (history_json, now, thread_id)
        )
    else:
        cursor.execute(
            "INSERT INTO memory (thread_id, history, updated_at) VALUES (?, ?, ?)",
            (thread_id, history_json, now)
        )
    print("Storing in conversational memory..")
    conn.commit()
    conn.close()

"""
if __name__ == "__main__":
    init_memory()
    append_turn("thread-001", "user", "My VPN password isn't working")
    append_turn("thread-001", "assistant", "I've reset it, please try again")
    print(get_history("thread-001"))"""