"""ローカル確認用の簡易サーバー。Cloudflare Pages と同じくクリーン URL を解決する。

    python _local/serve.py      ->  http://localhost:8000/
"""
import http.server, os, socketserver, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def translate_path(self, path):
        p = super().translate_path(path)
        if os.path.isdir(p) or os.path.exists(p):
            return p
        if os.path.exists(p + '.html'):     # /about -> about.html
            return p + '.html'
        return p

    def send_error(self, code, message=None, explain=None):
        if code == 404 and os.path.exists(os.path.join(ROOT, '404.html')):
            self.error_message_format = open(
                os.path.join(ROOT, '404.html'), encoding='utf-8').read().replace('%', '%%')
        super().send_error(code, message, explain)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write('  %s\n' % (fmt % args))


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('', port), Handler) as httpd:
    print('http://localhost:%d/  (Ctrl+C で終了)' % port)
    httpd.serve_forever()
