# db.py
import pyodbc
from config import DB_DRIVER, DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD, USE_WINDOWS_AUTH

def get_db_connection():
    if USE_WINDOWS_AUTH:
        conn_str = f'''
            DRIVER={{{DB_DRIVER}}};
            SERVER={DB_SERVER};
            DATABASE={DB_NAME};
            Trusted_Connection=yes;
        '''
    else:
        conn_str = f'''
            DRIVER={{{DB_DRIVER}}};
            SERVER={DB_SERVER};
            DATABASE={DB_NAME};
            UID={DB_USERNAME};
            PWD={DB_PASSWORD};
        '''
    try:
        conn = pyodbc.connect(conn_str)
        print("✅ Đã kết nối SQL Server")
        return conn
    except Exception as e:
        print("❌ Lỗi kết nối:", e)
        return None
