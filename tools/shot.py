import sys,os,threading,http.server,socketserver,functools
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
pg=sys.argv[1]; w=int(sys.argv[2]); h=int(sys.argv[3]); y=int(sys.argv[4]) if len(sys.argv)>4 else 0; out=sys.argv[5] if len(sys.argv)>5 else '/tmp/shot.png'; theme=sys.argv[6] if len(sys.argv)>6 else 'light'
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
httpd=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Q,directory=str(ROOT))); port=httpd.server_address[1]
threading.Thread(target=httpd.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pgx=b.new_page(viewport={'width':w,'height':h}); pgx.goto(f'http://127.0.0.1:{port}/{pg}.html'); pgx.wait_for_timeout(600)
    pgx.evaluate(f"document.documentElement.setAttribute('data-theme','{theme}');document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));window.scrollTo(0,{y})"); pgx.wait_for_timeout(400)
    pgx.screenshot(path=out); b.close()
httpd.shutdown()
