"""下書きを1本取り出して公開する。

    python _local/publish_next.py            # 中身を確かめるだけ（何も書かない）
    python _local/publish_next.py --write    # 公開してコミットまで
    python _local/publish_next.py --write --push

_local/drafts/ にある `NN-slug.html` を番号順に1本取り、記事ページを組み立てて
blog/ に置き、POSTS・更新履歴・OGP・sitemap に登録し、生成スクリプトを順に回す。
最後に組み上がりを検証してから、コミットする。

下書きの書きかたは _local/drafts/README.md を参照。
"""
import glob
import html
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DRAFTS = os.path.join(ROOT, '_local', 'drafts')
D = 'https://mdf.works'

FIELDS = ('slug cat eyebrow title crumb h1a h1b lead pagelead desc ogdesc '
          'jsonlddesc tags icon ogl1 ogl2 ogsub').split()


# ------------------------------------------------------------------ 下書き
def parse_draft(path):
    src = open(path, encoding='utf-8').read()
    m = re.match(r'\s*<!--(.*?)-->\s*(.*)', src, re.S)
    if not m:
        sys.exit('%s: 先頭の <!-- ... --> が見つかりません' % path)
    meta, body = {}, m.group(2).strip()
    for line in m.group(1).strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            sys.exit('%s: "キー: 値" になっていない行があります -> %s' % (path, line))
        k, v = line.split(':', 1)
        meta[k.strip()] = v.strip()
    missing = [f for f in FIELDS if f not in meta]
    if missing:
        sys.exit('%s: 項目が足りません -> %s' % (path, ', '.join(missing)))
    meta['tags'] = [t.strip() for t in meta['tags'].split(',') if t.strip()]
    meta['body'] = body
    return meta


def next_draft():
    files = sorted(glob.glob(os.path.join(DRAFTS, '[0-9]*.html')))
    return files[0] if files else None


# ------------------------------------------------------------------ 記事ページ
PAGE = '''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_tag}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{D}/blog/{slug}.html">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="theme-color" content="#131720">
<meta name="author" content="マカロン大福">
<meta property="og:type" content="article">
<meta property="og:site_name" content="mdf.works">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{title_tag}">
<meta property="og:description" content="{ogdesc}">
<meta property="og:url" content="{D}/blog/{slug}.html">
<meta property="og:image" content="{D}/assets/og/{slug}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_tag}">
<meta name="twitter:description" content="{ogdesc}">
<meta name="twitter:image" content="{D}/assets/og/{slug}.png">
<meta name="twitter:creator" content="@sugerslp">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23131720'/><circle cx='11' cy='12' r='5.5' fill='%23FF8244'/><rect x='4' y='21' width='24' height='5' rx='2.5' fill='%23E7E9EE'/></svg>">
<script type="application/ld+json">
{ld}
</script>
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip" href="#main">本文へスキップ</a>

<header class="site-head">
  <div class="wrap">
    <a class="brand" href="/">
      <span class="mark">mdf<b>.works</b></span>
      <span class="sub">個人開発のウェブツール</span>
    </a>
    <nav class="site-nav" aria-label="メインナビゲーション">
      <a href="/blog/">記事一覧</a>
      <a href="/kuroko/">Kuroko</a>
      <a href="/koma/">Koma</a>
      <a href="/about">このサイトについて</a>
      <a class="cta" href="/kuroko/tool">ツールを開く</a>
    </nav>
  </div>
</header>

<main id="main">
  <div class="wrap prose">

    <p class="crumb"><a href="/">mdf.works</a><span aria-hidden="true">›</span><a href="/blog/">ブログ</a><span aria-hidden="true">›</span>{crumb}</p>

    <div class="page-head">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{h1a}<br>{h1b}</h1>
      <p class="lead">
        {pagelead}
      </p>
    </div>

{body}

  </div>
</main>

<footer class="site-foot">
  <div class="wrap">
    <div class="cols">
      <div>
        <h4>mdf.works</h4>
        <p class="about">ブラウザの中だけで完結する、無料のウェブツールを公開しています。インストールも登録も不要です。</p>
      </div>
      <div>
        <h4>コンテンツ</h4>
        <ul>
          <li><a href="/kuroko/">Kuroko — 概要</a></li>
          <li><a href="/kuroko/tool">匿名化ツールを開く</a></li>
          <li><a href="/kuroko/guide">使い方ガイド</a></li>
          <li><a href="/koma/">Koma — 連番PNG変換</a></li>
          <li><a href="/blog/">ブログ（記事一覧）</a></li>
        </ul>
      </div>
      <div>
        <h4>サイト情報</h4>
        <ul>
          <li><a href="/about">このサイトについて</a></li>
          <li><a href="/changelog">更新履歴</a></li>
          <li><a href="/privacy">プライバシーポリシー</a></li>
          <li><a href="/terms">利用規約・免責事項</a></li>
          <li><a href="/contact">お問い合わせ</a></li>
        </ul>
      </div>
    </div>
    <p class="copy">© 2026 mdf.works</p>
  </div>
</footer>
</body>
</html>
'''


def render_page(m, date):
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article",
             "headline": m['title'],
             "description": m['jsonlddesc'],
             "image": "%s/assets/og/%s.png" % (D, m['slug']),
             "datePublished": date,
             "dateModified": date,
             "inLanguage": "ja",
             "articleSection": m['cat'],
             "author": {"@id": D + "/#person"},
             "publisher": {"@id": D + "/#person"},
             "mainEntityOfPage": "%s/blog/%s.html" % (D, m['slug'])},
            {"@type": "Person", "@id": D + "/#person", "name": "マカロン大福",
             "url": D + "/about.html", "sameAs": ["https://x.com/sugerslp"]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "ホーム", "item": D + "/"},
                {"@type": "ListItem", "position": 2, "name": "ブログ", "item": D + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": m['crumb'],
                 "item": "%s/blog/%s.html" % (D, m['slug'])}]},
        ]
    }
    fields = dict(m)
    # <title> は既存記事に合わせて「主題｜副題」の形にする
    fields['title_tag'] = m['title'].replace(' — ', '｜', 1)
    fields['body'] = '\n'.join('    ' + ln if ln.strip() else ''
                               for ln in m['body'].split('\n'))
    return PAGE.format(D=D, ld=json.dumps(ld, ensure_ascii=False, indent=2),
                       **fields)


# ------------------------------------------------------------------ 登録
def q(s):
    """Python の文字列リテラルとして安全に書き出す。"""
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def wrap_lead(lead, indent=14):
    """長い lead を、既存の書き方に合わせて複数行の文字列リテラルにする。"""
    out, cur = [], ''
    for ch in lead:
        cur += ch
        if len(cur) >= 34 and ch in '。、':
            out.append(cur)
            cur = ''
    if cur:
        out.append(cur)
    pad = ' ' * indent
    return ('\n' + pad).join(q(x) for x in out)


def register(m, date):
    # POSTS
    p = os.path.join(ROOT, '_local', 'build_blog.py')
    s = open(p, encoding='utf-8').read()
    icon = "\n              ".join(q(x) for x in re.findall(r'<[^>]+/>', m['icon']))
    entry = (
        "    dict(slug=%s, cat=%s, date=%s,\n"
        "         title=%s,\n"
        "         name=%s,\n"
        "         lead=%s,\n"
        "         tags=[%s],\n"
        "         icon=%s),\n"
        % (q(m['slug']), q(m['cat']), q(date), q(m['title']), q(m['title']),
           wrap_lead(m['lead']), ', '.join(q(t) for t in m['tags']), icon)
    )
    anchor = 'POSTS = [\n'
    assert s.count(anchor) == 1
    open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, anchor + entry, 1))

    # 更新履歴
    p = os.path.join(ROOT, '_local', 'build_log.py')
    s = open(p, encoding='utf-8').read()
    line = "    (%s, 'ブログ', %s),\n" % (
        q(date), q('記事「%s」を公開しました。' % m['title']))
    anchor = 'ENTRIES = [\n'
    assert s.count(anchor) == 1
    open(p, 'w', encoding='utf-8', newline='').write(s.replace(anchor, anchor + line, 1))

    # OGP
    p = os.path.join(ROOT, '_local', 'make_og.py')
    s = open(p, encoding='utf-8').read()
    if 'o("%s.png")' % m['slug'] not in s:
        card = ('\ncard(o("%s.png"), "%s",\n     "%s\\n%s",\n     "%s")\n'
                % (m['slug'], m['eyebrow'], m['ogl1'], m['ogl2'], m['ogsub']))
        open(p, 'w', encoding='utf-8', newline='').write(s.rstrip('\n') + '\n' + card)

    # sitemap
    p = os.path.join(ROOT, 'sitemap.xml')
    s = open(p, encoding='utf-8').read()
    row = ('  <url><loc>%s/blog/%s</loc><lastmod>%s</lastmod>'
           '<changefreq>monthly</changefreq><priority>0.7</priority></url>\n'
           % (D, m['slug'], date))
    first = re.search(r'  <url><loc>%s/blog/[a-z0-9-]+</loc>' % re.escape(D), s)
    assert first, 'sitemap に記事の行が見つかりません'
    s = s[:first.start()] + row + s[first.start():]
    for loc in (D + '/', D + '/blog/', D + '/changelog'):
        s = re.sub(r'(<loc>%s</loc><lastmod>)[\d-]+(</lastmod>)' % re.escape(loc),
                   r'\g<1>%s\g<2>' % date, s)
    open(p, 'w', encoding='utf-8', newline='').write(s)


# ------------------------------------------------------------------ 検証
VOID = {'br', 'img', 'meta', 'link', 'input', 'hr', 'source', 'path', 'circle',
        'rect', 'ellipse', 'line', 'polygon', 'polyline', 'use'}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, t, a):
        if t not in VOID:
            self.stack.append(t)

    def handle_endtag(self, t):
        if t in VOID:
            return
        if not self.stack:
            self.errors.append(('余分な閉じタグ', t))
        elif self.stack[-1] != t:
            self.errors.append(('対応しない閉じタグ', t, self.stack[-1]))
        else:
            self.stack.pop()


def verify(slug):
    problems = []
    pages = sorted(glob.glob(os.path.join(ROOT, '*.html'))
                   + glob.glob(os.path.join(ROOT, 'kuroko', '*.html'))
                   + glob.glob(os.path.join(ROOT, 'koma', '*.html'))
                   + glob.glob(os.path.join(ROOT, 'blog', '*.html')))
    for f in pages:
        s = open(f, encoding='utf-8').read()
        b = Balance()
        b.feed(s)
        if b.stack or b.errors:
            problems.append('%s: 閉じ漏れ %s %s' % (os.path.basename(f), b.stack[:2], b.errors[:2]))
        for mm in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(mm.group(1))
            except Exception as e:
                problems.append('%s: JSON-LD が壊れています (%s)' % (os.path.basename(f), e))

    art = os.path.join(ROOT, 'blog', slug + '.html')
    if not os.path.exists(art):
        problems.append('記事ファイルができていません')
    else:
        s = open(art, encoding='utf-8').read()
        for need in ('postnav:start', 'postbody:start', 'class="postmeta"', 'adsbygoogle'):
            if need not in s:
                problems.append('記事に %s が入っていません' % need)
    idx = open(os.path.join(ROOT, 'blog', 'index.html'), encoding='utf-8').read()
    if '/blog/' + slug in idx:
        pass
    else:
        problems.append('記事一覧に載っていません')
    return problems


def run(script):
    r = subprocess.run([sys.executable, os.path.join(ROOT, '_local', script)],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        sys.exit('%s が失敗しました' % script)
    return r.stdout.strip().split('\n')[-1]


def git(*args, check=True):
    r = subprocess.run(['git'] + list(args), cwd=ROOT, capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    if check and r.returncode != 0:
        sys.exit('git %s に失敗しました:\n%s%s' % (' '.join(args), r.stdout, r.stderr))
    return r.stdout.strip()


def dgit(*args):
    """下書き置き場は別リポジトリ。失敗しても公開作業は止めない。

    リモートを設定していない段階でも動くようにしてある。
    """
    if not os.path.isdir(os.path.join(DRAFTS, '.git')):
        return None
    r = subprocess.run(['git'] + list(args), cwd=DRAFTS, capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print('  （下書き側の git %s は失敗しました。公開自体には影響しません）'
              % ' '.join(args[:2]))
        return None
    return r.stdout.strip()


# ------------------------------------------------------------------ main
def main():
    write = '--write' in sys.argv
    push = '--push' in sys.argv
    import datetime
    date = datetime.date.today().isoformat()
    for a in sys.argv[1:]:
        if a.startswith('--date='):
            date = a.split('=', 1)[1]

    path = next_draft()
    if not path:
        print('下書きがありません。_local/drafts/ に足してください。')
        return 0

    m = parse_draft(path)
    n_left = len(glob.glob(os.path.join(DRAFTS, '[0-9]*.html'))) - 1
    print('次に公開する下書き : %s' % os.path.basename(path))
    print('  slug   : %s' % m['slug'])
    print('  日付   : %s' % date)
    print('  区分   : %s' % m['cat'])
    print('  題名   : %s' % m['title'])
    print('  タグ   : %s' % ' / '.join(m['tags']))
    print('  本文   : 約%d文字' % len(re.sub(r'\s+|<[^>]+>', '', html.unescape(m['body']))))
    print('  残り   : %d本' % n_left)

    if os.path.exists(os.path.join(ROOT, 'blog', m['slug'] + '.html')):
        sys.exit('blog/%s.html は既にあります' % m['slug'])

    if not write:
        print('\n（確認のみ。実際に公開するには --write を付けてください）')
        return 0

    dirty = git('status', '--porcelain')
    if dirty:
        sys.exit('作業ツリーに未コミットの変更があります。先に片付けてください:\n' + dirty)

    # 組み立てに失敗したときに空ファイルが残らないよう、先に文字列を作る
    page = render_page(m, date)
    open(os.path.join(ROOT, 'blog', m['slug'] + '.html'), 'w',
         encoding='utf-8', newline='').write(page)
    register(m, date)

    print()
    for s in ('make_og.py', 'build_log.py', 'build_blog.py', 'cleanurls.py', 'chrome.py'):
        print('  %-14s %s' % (s, run(s)))

    problems = verify(m['slug'])
    if problems:
        print('\n検証で問題が見つかりました。コミットしません:')
        for x in problems:
            print('  - ' + x)
        return 1
    print('\n検証: 問題なし')

    os.remove(path)
    git('add', '-A')
    msg = ('記事「%s」を公開\n\n下書き %s から自動公開。残り %d 本。\n'
           % (m['title'], os.path.basename(path), n_left))
    git('commit', '-m', msg)
    print('コミットしました:', git('log', '--oneline', '-1'))

    # 下書きは別リポジトリなので、取り出したことをそちらにも記録する
    dgit('add', '-A')
    dgit('commit', '-m', '公開したので下書きを外す: %s（残り %d 本）'
         % (os.path.basename(path), n_left))

    if push:
        git('fetch', 'origin')
        behind = git('rev-list', '--count', 'HEAD..origin/main')
        if behind != '0':
            print('リモートが %s コミット進んでいます。載せ直します。' % behind)
            git('rebase', 'origin/main')
        git('push', 'origin', 'main')
        print('push しました。')
        # 下書き側はリモート未設定でも止まらないようにしてある
        dgit('push', 'origin', 'main')
    return 0


if __name__ == '__main__':
    sys.exit(main())
