from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ski123'  # 세션 보안 키 (아무 문자열 가능)

# DB 초기화
def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS repair_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                gear_type TEXT NOT NULL,
                repair_detail TEXT NOT NULL,
                price INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()

# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    branches = {
        'gangnam': '1111',
        'hongdae': '2222',
        'daejeon': '3333'
    }

    if request.method == 'POST':
        branch = request.form['branch']
        password = request.form['password']

        if branch in branches and branches[branch] == password:
            session['branch'] = branch
            return redirect('/')
        else:
            return render_template('login.html', error='지점명 또는 비밀번호가 틀렸습니다.')

    return render_template('login.html')

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# 메인 페이지 (수리 내역 보기 + 등록 폼)
@app.route('/')
def index():
    if 'branch' not in session:
        return redirect('/login')

    branch = session['branch']

    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM repair_logs WHERE branch=? ORDER BY date DESC", (branch,))
        logs = c.fetchall()

    return render_template('index.html', logs=logs, branch=branch)

# 등록 처리
@app.route('/register', methods=['POST'])
def register():
    if 'branch' not in session:
        return redirect('/login')

    branch = session['branch']
    customer_name = request.form['customer_name']
    gear_type = request.form['gear_type']
    repair_detail = request.form['repair_detail']
    price = int(request.form['price'])
    date = datetime.now().strftime('%Y-%m-%d')

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO repair_logs (branch, customer_name, gear_type, repair_detail, price, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (branch, customer_name, gear_type, repair_detail, price, date))
        conn.commit()

    return redirect('/')

# 앱 실행
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)  # 외부 접속 가능하도록 수정

