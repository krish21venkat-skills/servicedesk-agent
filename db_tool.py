import pyodbc

# Update these to match your SQL Server Express instance
SERVER = "localhost\\SQLEXPRESS"
DATABASE = "service_desk"

def get_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"  # uses Windows auth; swap for UID/PWD if using SQL auth
    )
    return pyodbc.connect(conn_str)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            email NVARCHAR(255),
            department NVARCHAR(255),
            access_level NVARCHAR(50)
        )
    """)
    conn.commit()
    conn.close()

def lookup_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row

"""if __name__ == "__main__":
    init_db()
    print(lookup_user("robert.thomas@company.com"))"""