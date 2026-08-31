"""内部リンク・canonical・構造化データ・サイトマップを、実際に配信される URL に揃える。

Cloudflare Pages は /about.html を /about へ 307 で転送する。リンクや canonical が
.html を指したままだと、すべての参照が転送を1回はさむ形になるので、配信されている
形（拡張子なし・ディレクトリは末尾スラッシュ）に統一する。
"""
import os, re, glob, posixpath

D = 'https://mdf.works'


def clean(path):
    """リポジトリ内のパス -> 実際に配信される絶対パス"""
    p = path.replace('\\', '/')
    if p == 'index.html':
        return '/'
    if p.endswith('/index.html'):
        return '/' + p[:-len('index.html')]
    if p.endswith('.html'):
        return '/' + p[:-len('.html')]
    return '/' + p


def rewrite(path):
    s = open(path, encoding='utf-8').read()
    base = os.path.dirname(path).replace('\\', '/')
    changed = []

    def sub(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith(('http://', 'https://', 'data:', 'mailto:', '#', '/')):
            return m.group(0)
        frag = ''
        if '#' in url:
            url, frag = url.split('#', 1)
            frag = '#' + frag
        if not url:
            return m.group(0)
        target = posixpath.normpath(posixpath.join(base, url))
        if not os.path.exists(target):
            return m.group(0)
        new = clean(target) + frag
        changed.append((m.group(2), new))
        return '%s="%s"' % (attr, new)

    s = re.sub(r'\b(href|src)="([^"]+)"', sub, s)

    # canonical / og:url / JSON-LD の中の絶対 URL も揃える
    def abs_fix(t):
        t = re.sub(r'(https://mdf\.works)/([a-z0-9/_-]*?)index\.html', r'\1/\2', t)
        t = re.sub(r'(https://mdf\.works/[a-z0-9/_-]+?)\.html', r'\1', t)
        return t
    s = abs_fix(s)

    open(path, 'w', encoding='utf-8', newline='').write(s)
    return changed


if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    pages = sorted(glob.glob('*.html') + glob.glob('kuroko/*.html')
                   + glob.glob('koma/*.html') + glob.glob('blog/*.html'))
    total = 0
    for p in pages:
        c = rewrite(p)
        total += len(c)
        print('%-26s %d links' % (p, len(c)))
    print('リンクを書き換え:', total)

    # sitemap も配信 URL に
    sm = open('sitemap.xml', encoding='utf-8').read()
    sm = re.sub(r'(https://mdf\.works)/([a-z0-9/_-]*?)index\.html', r'\1/\2', sm)
    sm = re.sub(r'(https://mdf\.works/[a-z0-9/_-]+?)\.html', r'\1', sm)
    open('sitemap.xml', 'w', encoding='utf-8', newline='').write(sm)
    print('sitemap を更新')
