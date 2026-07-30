import pyodbc, datetime

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

def init_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tickets' AND xtype='U')
        CREATE TABLE tickets (
            id INT IDENTITY(1,1) PRIMARY KEY,
            thread_id NVARCHAR(255),
            requester NVARCHAR(255),
            intent NVARCHAR(255),
            status NVARCHAR(50),
            summary NVARCHAR(MAX),
            created_at DATETIME2,
            updated_at DATETIME2
        )
    """)
    conn.commit()
    conn.close()

def create_or_update_ticket(thread_id, requester, intent, summary, status="open"):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.utcnow()

    cursor.execute("SELECT id FROM tickets WHERE thread_id = ?", (thread_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE tickets SET status = ?, summary = ?, updated_at = ? WHERE thread_id = ?",
            (status, summary, now, thread_id)
        )
    else:
        cursor.execute(
            """INSERT INTO tickets (thread_id, requester, intent, status, summary,
               created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (thread_id, requester, intent, status, summary, now, now)
        )
    print("ticket info stored..")
    conn.commit()
    conn.close()

"""if __name__ == "__main__":
    init_tickets()
    create_or_update_ticket(
        thread_id="thread-002",
        requester="john.smith@company.com",
        intent="password_reset",
        summary="User cannot log into VPN",
        status="open"
    )
    print("Ticket created/updated.")"""