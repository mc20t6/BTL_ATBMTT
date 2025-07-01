from flask import Flask, render_template, request, redirect, url_for, session
from db import get_db_connection
from encryption_utils import hash_password, verify_password
from Crypto.Cipher import DES3, AES
from Crypto.Util.Padding import unpad
import base64

app = Flask(__name__)
app.secret_key = '123456781234567812345678'  # Đặt secret key mạnh

# Đặt hash mật khẩu admin
admin_password_hash = hash_password("admin123")

# Định nghĩa các key cho mã hóa
key1 = b'123456781234567812345678'  # 24 bytes cho Triple DES
key2 = b'1234567890123456'  # 16 bytes cho AES

def ensure_admin_exists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (name, cmnd, baohiem, stk, diachi, username, password_hash, is_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ('Administrator', b'', b'', b'', b'', 'admin', admin_password_hash, 1))
        conn.commit()
    cursor.close()
    conn.close()

ensure_admin_exists()

def TripleDES_Decrypt(encrypted_data):
    encrypted_data = base64.b64decode(encrypted_data)
    cipher = DES3.new(key1, DES3.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), DES3.block_size)
    return decrypted_data.decode('utf-8')

def AES_Decrypt(encrypted_data):
    encrypted_data = base64.b64decode(encrypted_data)
    cipher = AES.new(key2, AES.MODE_CBC)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted_data.decode('utf-8')

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    users = []
    show_sensitive = False  # Biến để kiểm soát hiển thị thông tin nhạy cảm

    if 'user_id' in session and session.get('is_admin'):
        if request.method == 'POST':
            password_input = request.form['password']
            if verify_password(password_input, admin_password_hash):  # Kiểm tra mật khẩu
                show_sensitive = True  # Hiện thông tin nhạy cảm
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT name, cmnd, baohiem, stk, diachi FROM users")
                rows = cursor.fetchall()
                cursor.close()
                conn.close()

                for row in rows:
                    user_info = {
                        'name': row[0],
                        'cmnd': row[1],
                        'baohiem': row[2],
                        'stk': row[3],
                        'diachi': row[4]
                    }
                    users.append(user_info)

                return render_template('admin.html', users=users, show_sensitive=show_sensitive)

            else:
                return "Mật khẩu không đúng.", 403

        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM users")  # Chỉ lấy tên người dùng
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            for row in rows:
                user_info = {
                    'name': row[0],
                    'cmnd': "****",  # Che thông tin
                    'baohiem': "****",
                    'stk': "****",
                    'diachi': "****",
                }
                users.append(user_info)

            return render_template('admin.html', users=users, show_sensitive=show_sensitive)

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        cmnd = request.form.get('cmnd')
        baohiem = request.form.get('baohiem')
        stk = request.form.get('stk')
        diachi = request.form.get('diachi')
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([name, cmnd, baohiem, stk, diachi, username, password]):
            return "Vui lòng điền đầy đủ thông tin.", 400

        password_hash = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """INSERT INTO users (name, cmnd, baohiem, stk, diachi, username, password_hash, is_admin)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

        try:
            cursor.execute(sql, (name, cmnd, baohiem, stk, diachi, username, password_hash, 0))
            conn.commit()
            return render_template('register_success.html')  # Chuyển đến trang thành công
        except Exception as e:
            return f"Đăng ký thất bại: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash, is_admin FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row and verify_password(password_input, row[1]):
            session['user_id'] = row[0]
            session['username'] = username
            session['is_admin'] = row[2]
            
            if row[2]:  # Nếu là admin
                return redirect(url_for('admin_dashboard'))
            else:  # Nếu là người dùng thông thường
                return redirect(url_for('dashboard'))

        else:
            return "Đăng nhập thất bại. Sai tên đăng nhập hoặc mật khẩu."

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    show_sensitive = False

    if request.method == 'POST':
        password_input = request.form['password']
        
        # Lấy mật khẩu hash từ cơ sở dữ liệu
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row and verify_password(password_input, row[0]):
            show_sensitive = True  # Hiện thông tin nhạy cảm
        else:
            return "Mật khẩu không đúng.", 403

    # Lấy thông tin người dùng
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, cmnd, baohiem, stk, diachi FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return "Không tìm thấy người dùng", 404

    user_info = {
        'name': row[0],
        'cmnd': row[1],
        'baohiem': row[2],
        'stk': row[3],
        'diachi': row[4]
    }

    return render_template('dashboard.html', user=user_info, show_sensitive=show_sensitive)
    # Lấy thông tin người dùng
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, cmnd, baohiem, stk, diachi FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return "Không tìm thấy người dùng", 404

    user_info = {
        'name': row[0],
        'cmnd': row[1],
        'baohiem': row[2],
        'stk': row[3],
        'diachi': row[4]
    }

    return render_template('dashboard.html', user=user_info, show_sensitive=show_sensitive)



if __name__ == '__main__':
    app.run(debug=True)