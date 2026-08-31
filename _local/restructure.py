"""記事を /blog/ に分けた新しい構成に合わせて、ナビ・フッター・リンク・メタを揃える。"""
import re, os, json, glob

D = 'https://mdf.works'

ARTICLES = {
    'blog/checklist.html': dict(
        slug='checklist', title='スクショ公開前のチェックリスト12項目｜消し忘れを防ぐ',
        crumb='公開前チェックリスト', card='スクリーンショット公開前のチェックリスト12項目',
        lead='通知バナー、Exif、ファイル名、背景の映り込みなど、アイコンと名前を隠しただけでは残ってしまうものを12項目に整理しました。',
        date='2026-08-13', og='checklist.png', kicker='Checklist'),
    'blog/capture.html': dict(
        slug='capture', title='必要な範囲だけを撮る方法｜Windows・Mac・iPhone・Android',
        crumb='必要な範囲だけを撮る', card='スクリーンショットは必要な範囲だけを撮る',
        lead='撮る範囲を絞るだけで、あとから隠す手間も消し忘れも減ります。OSごとの範囲指定の撮り方と、通知を止める設定をまとめました。',
        date='2026-08-16', og='capture.png', kicker='Basics'),
    'blog/mosaic.html': dict(
        slug='mosaic', title='モザイクとぼかしと塗りつぶし｜文字を隠すならどれを選ぶか',
        crumb='隠しかたの選びかた', card='モザイク・ぼかし・塗りつぶし — 文字を隠すならどれを選ぶか',
        lead='写真と文字で効き方が変わる理由と、隠す対象ごとに何を選べばよいかの基準。ぼかしの半径の目安、PDFの墨消しまで。',
        date='2026-08-14', og='mosaic.png', kicker='Column'),
}
ORDER = ['blog/capture.html', 'blog/mosaic.html', 'blog/checklist.html']   # 新しい順


def nav(kind, current=''):
    """kind: root / blog / kuroko"""
    if kind == 'root':
        p, items = '', [('index.html', 'ホーム'), ('blog/index.html', 'ブログ'),
                        ('about.html', 'このサイトについて'), ('contact.html', 'お問い合わせ')]
        cta = ('kuroko/index.html', 'Kuroko')
    elif kind == 'blog':
        p, items = '../', [('index.html', '記事一覧'), ('../kuroko/index.html', 'Kuroko'),
                           ('../about.html', 'このサイトについて')]
        cta = ('../kuroko/tool.html', 'ツールを開く')
    else:
        p, items = '../', [('index.html', 'Kuroko 概要'), ('guide.html', '使い方'),
                           ('../blog/index.html', 'ブログ')]
        cta = ('tool.html', 'ツールを開く')
    links = ''.join('\n      <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == current else '', t)
                    for h, t in items)
    return ('<header class="site-head">\n  <div class="wrap">\n'
            '    <a class="brand" href="%sindex.html">\n'
            '      <span class="mark">mdf<b>.works</b></span>\n'
            '      <span class="sub">個人開発のウェブツール</span>\n'
            '    </a>\n'
            '    <nav class="site-nav" aria-label="メインナビゲーション">%s\n'
            '      <a class="cta" href="%s">%s</a>\n'
            '    </nav>\n  </div>\n</header>') % (p, links, cta[0], cta[1])


def footer(kind):
    p = '' if kind == 'root' else '../'
    k = 'kuroko/' if kind == 'root' else ('' if kind == 'kuroko' else '../kuroko/')
    b = 'blog/' if kind == 'root' else ('' if kind == 'blog' else '../blog/')
    return ('<footer class="site-foot">\n  <div class="wrap">\n    <div class="cols">\n'
            '      <div>\n        <h4>mdf.works</h4>\n'
            '        <p class="about">ブラウザの中だけで完結する、無料のウェブツールを公開しています。'
            'インストールも登録も不要です。</p>\n      </div>\n'
            '      <div>\n        <h4>コンテンツ</h4>\n        <ul>\n'
            '          <li><a href="%sindex.html">Kuroko — 概要</a></li>\n'
            '          <li><a href="%stool.html">匿名化ツールを開く</a></li>\n'
            '          <li><a href="%sguide.html">使い方ガイド</a></li>\n'
            '          <li><a href="%sindex.html">ブログ（記事一覧）</a></li>\n'
            '        </ul>\n      </div>\n'
            '      <div>\n        <h4>サイト情報</h4>\n        <ul>\n'
            '          <li><a href="%sabout.html">このサイトについて</a></li>\n'
            '          <li><a href="%sprivacy.html">プライバシーポリシー</a></li>\n'
            '          <li><a href="%sterms.html">利用規約・免責事項</a></li>\n'
            '          <li><a href="%scontact.html">お問い合わせ</a></li>\n'
            '        </ul>\n      </div>\n    </div>\n'
            '    <p class="copy">© 2026 mdf.works</p>\n  </div>\n</footer>') % (k, k, k, b, p, p, p, p)


def kind_of(path):
    d = os.path.dirname(path)
    return 'root' if d == '' else d


def swap(path, current=''):
    s = open(path, encoding='utf-8').read()
    k = kind_of(path)
    s = re.sub(r'<header class="site-head">.*?</header>', lambda m: nav(k, current), s, flags=re.S)
    s = re.sub(r'<footer class="site-foot">.*?</footer>', lambda m: footer(k), s, flags=re.S)
    open(path, 'w', encoding='utf-8', newline='').write(s)


if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

    # ---- 1) 記事: kuroko 配下へのリンクを直し、メタとパンくずを付け替える
    for path, cfg in ARTICLES.items():
        s = open(path, encoding='utf-8').read()
        for a, b in [('href="index.html"', 'href="../kuroko/index.html"'),
                     ('href="tool.html"', 'href="../kuroko/tool.html"'),
                     ('href="guide.html"', 'href="../kuroko/guide.html"')]:
            s = s.replace(a, b)
        url = '%s/blog/%s.html' % (D, cfg['slug'])
        s = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', r'\g<1>' + url + r'\g<2>', s)
        s = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', r'\g<1>' + url + r'\g<2>', s)
        s = s.replace('"mainEntityOfPage": "%s/kuroko/%s.html"' % (D, cfg['slug']),
                      '"mainEntityOfPage": "%s"' % url)
        # パンくず（表示）
        s = re.sub(r'<p class="crumb">.*?</p>',
                   '<p class="crumb"><a href="../index.html">mdf.works</a>'
                   '<span aria-hidden="true">›</span><a href="index.html">ブログ</a>'
                   '<span aria-hidden="true">›</span>%s</p>' % cfg['crumb'], s, flags=re.S, count=1)
        # パンくず（JSON-LD）
        s = re.sub(r'\{\s*"@type": "BreadcrumbList".*?\n    \}',
                   json.dumps({"@type": "BreadcrumbList", "itemListElement": [
                       {"@type": "ListItem", "position": 1, "name": "ホーム", "item": D + "/"},
                       {"@type": "ListItem", "position": 2, "name": "ブログ", "item": D + "/blog/"},
                       {"@type": "ListItem", "position": 3, "name": cfg['crumb'], "item": url}]},
                       ensure_ascii=False, indent=6).replace('\n', '\n    ').rstrip() ,
                   s, flags=re.S, count=1)
        open(path, 'w', encoding='utf-8', newline='').write(s)
        swap(path)
        print('article updated:', path)

    # ---- 2) それ以外のページのナビ・フッターを差し替え
    for p in ['index.html', 'about.html', 'privacy.html', 'terms.html', 'contact.html', '404.html']:
        cur = {'index.html': 'index.html', 'about.html': 'about.html',
               'contact.html': 'contact.html'}.get(p, '')
        swap(p, cur)
        print('root page updated:', p)
    for p in ['kuroko/index.html', 'kuroko/guide.html']:
        swap(p, 'index.html' if p.endswith('kuroko/index.html') else 'guide.html')
        print('kuroko page updated:', p)
