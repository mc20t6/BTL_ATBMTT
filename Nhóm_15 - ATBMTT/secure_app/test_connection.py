# test_connection.py

from db import get_connection

conn = get_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT GETDATE()")  # Lấy thời gian hiện tại từ SQL Server
    row = cursor.fetchone()
    print("🕒 Giờ máy chủ:", row[0])
    conn.close()
