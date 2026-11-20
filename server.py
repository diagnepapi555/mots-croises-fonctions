"""Serveur du Défi des fonctions. Python 3.10+, sans dépendances."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime, timezone
import sqlite3, os, json, secrets, hmac, threading

ROOT = Path(__file__).resolve().parent
DB = Path(os.getenv('DB_PATH', str(ROOT/'progressions.sqlite3')))
DB.parent.mkdir(parents=True, exist_ok=True)
TEACHER_CODE = os.getenv('TEACHER_CODE', 'PROF2026')
PORT = int(os.getenv('PORT', '8000'))
TOKENS = set()
LOCK = threading.Lock()
with sqlite3.connect(DB) as db:
    db.execute('''CREATE TABLE IF NOT EXISTS games (id TEXT PRIMARY KEY, updated_at TEXT NOT NULL,
      status TEXT, mode TEXT, niveau INTEGER, j1 TEXT, j2 TEXT, p1 INTEGER, p2 INTEGER,
      mots INTEGER, valides INTEGER, essais INTEGER, indices INTEGER, duree INTEGER)''')

class Handler(BaseHTTPRequestHandler):
    def send(self, status, data, content_type='application/json'):
        raw = data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type',content_type+'; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers();self.wfile.write(raw)
    def body(self):
        n=int(self.headers.get('Content-Length','0'))
        if n>4096: raise ValueError('Requête trop longue')
        return json.loads(self.rfile.read(n))
    def authorized(self):
        token=self.headers.get('Authorization','').removeprefix('Bearer ')
        with LOCK:return token in TOKENS and bool(token)
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ('/','/index.html'):
            self.send(200,(ROOT/'index.html').read_bytes(),'text/html');return
        if path=='/api/health':self.send(200,{'ok':True});return
        if path=='/api/teacher/games':
            if not self.authorized():self.send(401,{'error':'Non autorisé'});return
            with sqlite3.connect(DB) as db:
                db.row_factory=sqlite3.Row
                rows=[dict(x) for x in db.execute('SELECT * FROM games ORDER BY updated_at DESC LIMIT 500')]
            self.send(200,rows);return
        self.send(404,{'error':'Introuvable'})
    def do_POST(self):
        path=urlparse(self.path).path
        try:d=self.body()
        except (ValueError,json.JSONDecodeError):self.send(400,{'error':'Requête invalide'});return
        if path=='/api/teacher/login':
            if not hmac.compare_digest(str(d.get('code','')),TEACHER_CODE):
                self.send(401,{'error':'Code incorrect'});return
            token=secrets.token_urlsafe(32)
            with LOCK:TOKENS.add(token)
            self.send(200,{'token':token});return
        if path=='/api/progress':
            try:
                ident=str(d['id'])[:90]
                if not ident or len(ident)<8:raise ValueError()
                vals=[ident,datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),str(d.get('status',''))[:20],str(d.get('mode',''))[:10],int(d.get('niveau',1)),str(d.get('j1',''))[:25],str(d.get('j2',''))[:25],int(d.get('p1',0)),None if d.get('p2') is None else int(d['p2']),int(d.get('mots',0)),int(d.get('valides',0)),int(d.get('essais',0)),int(d.get('indices',0)),int(d.get('duree',0))]
                if any(abs(x)>10000000 for x in vals if isinstance(x,int)):raise ValueError()
            except (ValueError,KeyError,TypeError):self.send(400,{'error':'Données invalides'});return
            with LOCK,sqlite3.connect(DB) as db:
                db.execute('''INSERT INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                 ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at,status=excluded.status,
                 mode=excluded.mode,niveau=excluded.niveau,j1=excluded.j1,j2=excluded.j2,
                 p1=excluded.p1,p2=excluded.p2,mots=excluded.mots,valides=excluded.valides,
                 essais=excluded.essais,indices=excluded.indices,duree=excluded.duree''',vals)
            self.send(200,{'ok':True});return
        self.send(404,{'error':'Introuvable'})

if __name__=='__main__':
    print(f'Serveur prêt : http://localhost:{PORT}')
    ThreadingHTTPServer(('0.0.0.0',PORT),Handler).serve_forever()
