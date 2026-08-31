"""更新履歴を1か所で管理し、全件ページとトップページの抜粋を生成する。

ENTRIES に1件足して実行するだけ。トップは最新 SHOWN 件だけを出し、
残りは /changelog へ送る。両方を同じ元データから作るので、
一方だけ古いという状態にならない。

    python _local/build_log.py
"""
import os, re

SHOWN = 5            # トップページに出す件数
LOG_PATH = 'changelog.html'

# 新しい順。kind は「サイト」「ブログ」「Kuroko」「Koma」のいずれか。
ENTRIES = [
    ('2026-08-30', 'ブログ', '記事「ダークモードは色を反転するのではない — 実装して分かったこと」を公開しました。'),
    ('2026-08-30', 'ブログ', '記事「公衆Wi-Fiは危険か — HTTPSが片付けたことと、残っているもの」を公開しました。'),
    ('2026-08-27', 'ブログ', '記事「ブラウザだけでは動画を保存できない — CORS を実測して確かめる」を公開しました。'),
    ('2026-08-25', 'Koma', '新しいツール Koma を公開しました。連番のPNGを背景透過して、APNG またはアニメーションWebP として書き出せます。'),
    ('2026-08-24', 'ブログ', '記事「スマホの写真から何が分かるか — Exif と、消しても残るもの」を公開しました。'),
    ('2026-08-23', 'ブログ', '記事「QRコードは中身が見えない — 貼り替え詐欺と、読み取る前の確認」を公開しました。'),
    ('2026-08-22', 'ブログ', '記事「画像から円を検出する — ハフ変換だけでは足りなかった話」を公開しました。Kuroko の検出処理の解説です。'),
    ('2026-08-21', 'ブログ', '記事「拡張機能の権限の見かた — 「すべてのサイトのデータを読み取る」とは何か」を公開しました。'),
    ('2026-08-19', 'ブログ', '記事「スクリーンショットはPNG、写真はJPEG — 画像形式の選び方」を公開しました。'),
    ('2026-08-19', 'サイト', '更新履歴の全件ページを追加し、トップページには最新5件を表示するようにしました。'),
    ('2026-08-18', 'ブログ', '記事「二段階認証はどれを選ぶか」を公開し、カテゴリ「セキュリティ」を追加しました。'),
    ('2026-08-18', 'サイト', '連絡先のメールアドレスを contact@mdf.works に統一しました。'),
    ('2026-08-18', 'サイト', '記事の公開日が実際より先の日付になっていたのを修正しました。'),
    ('2026-08-17', 'ブログ', '記事「モバイルバッテリーは mAh で選ばない」を公開しました。'),
    ('2026-08-16', 'ブログ', '記事「Pingはどこで生まれるのか」「HTMLは新しいのにCSSだけ古い」を公開しました。'),
    ('2026-08-16', 'サイト', '表示速度を改善しました。CSS をページに直接埋め込み、アクセス解析の読み込みを後回しにしています。'),
    ('2026-08-16', 'サイト', '配色を見直し、文字と背景のすべての組み合わせで WCAG AA のコントラスト比を満たすようにしました。'),
    ('2026-08-16', 'サイト', 'スマートフォンでの表示崩れを修正し、ライトテーマとダークテーマの切替ボタンを追加しました。'),
    ('2026-08-16', 'ブログ', '記事一覧に検索・カテゴリ絞り込み・タグ絞り込み・並び替えを、記事ページに目次と前後リンクを追加しました。'),
    ('2026-08-16', 'ブログ', 'ブログを /blog/ に開設し、記事「ブラウザの選び方」「必要な範囲だけを撮る」を公開しました。'),
    ('2026-08-16', 'サイト', 'AdSense の審査で受けた指摘をもとに、ページ構成と記事の内容を見直しました。'),
    ('2026-08-15', 'サイト', 'アクセス解析（Google アナリティクス）を導入しました。'),
    ('2026-08-14', 'ブログ', '解説記事「モザイク・ぼかし・塗りつぶし — 文字を隠すならどれを選ぶか」を公開しました。'),
    ('2026-08-14', 'サイト', '検索エンジン向けの情報（構造化データと OGP 画像）を整備しました。'),
    ('2026-08-13', 'サイト', 'mdf.works を公開しました。'),
    ('2026-08-13', 'Kuroko', '返信プレビューのアイコンと名前の検出に対応しました。'),
    ('2026-08-10', 'Kuroko', '装飾フレーム付きのアイコンと、背景とのコントラストが低いアイコンの検出精度を改善しました。'),
    ('2026-08-09', 'Kuroko', 'スマートフォン向けの操作画面と、ピンチ操作に対応しました。'),
]

ADS = ('<!-- Google AdSense -->\n'
       '<script async fetchpriority="low" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
       '?client=ca-pub-8613999974980382"\n     crossorigin="anonymous"></script>')

ICON = ("<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' "
        "viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23131720'/>"
        "<circle cx='11' cy='12' r='5.5' fill='%23FF8244'/>"
        "<rect x='4' y='21' width='24' height='5' rx='2.5' fill='%23E7E9EE'/></svg>\">")


def rows(entries):
    out = []
    for date, kind, text in entries:
        out.append('      <li><time datetime="%s">%s</time>'
                   '<span><span class="kind">%s</span>%s</span></li>' % (date, date, kind, text))
    return '\n'.join(out)


def counts():
    c = {}
    for _, kind, _ in ENTRIES:
        c[kind] = c.get(kind, 0) + 1
    return c


def page():
    c = counts()
    breakdown = '／'.join('%s %d件' % (k, n) for k, n in c.items())
    return '''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
%(ads)s
<title>更新履歴 - mdf.works</title>
<meta name="description" content="mdf.works の更新履歴です。ツール Kuroko の改善、記事の公開、サイト全体の変更を新しい順にすべて記録しています。">
<link rel="canonical" href="https://mdf.works/changelog">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#131720">
<meta name="author" content="マカロン大福">
<meta property="og:type" content="website">
<meta property="og:site_name" content="mdf.works">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="更新履歴 - mdf.works">
<meta property="og:description" content="ツールの改善、記事の公開、サイトの変更を新しい順にすべて記録しています。">
<meta property="og:url" content="https://mdf.works/changelog">
<meta property="og:image" content="https://mdf.works/assets/og/home.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="更新履歴 - mdf.works">
<meta name="twitter:description" content="ツールの改善、記事の公開、サイトの変更を新しい順にすべて記録しています。">
<meta name="twitter:image" content="https://mdf.works/assets/og/home.png">
%(icon)s
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebPage",
      "name": "更新履歴",
      "description": "mdf.works の更新履歴。ツールの改善、記事の公開、サイトの変更の記録。",
      "url": "https://mdf.works/changelog",
      "inLanguage": "ja",
      "dateModified": "%(latest)s",
      "isPartOf": { "@type": "WebSite", "name": "mdf.works", "url": "https://mdf.works/" }
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://mdf.works/" },
        { "@type": "ListItem", "position": 2, "name": "更新履歴", "item": "https://mdf.works/changelog" }
      ]
    }
  ]
}
</script>
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

    <p class="crumb"><a href="/">mdf.works</a><span aria-hidden="true">&rsaquo;</span>更新履歴</p>

    <div class="page-head">
      <p class="eyebrow">Changelog</p>
      <h1>更新履歴</h1>
      <p class="lead">
        ツール Kuroko の改善、記事の公開、サイト全体の変更を新しい順に記録しています。
        直したことだけでなく、<strong>自分が出してしまった不具合を直した記録も残しています</strong>。
        そのほうが、何がどう動いているかを判断する材料になると思うからです。
      </p>
      <p class="updated">全%(total)d件（%(breakdown)s）／最終更新：%(latest)s</p>
    </div>

    <ul class="log">
%(rows)s
    </ul>

    <div class="btnrow" style="margin-top:28px">
      <a class="btn" href="/">トップページへ</a>
      <a class="btn" href="/blog/">記事一覧を見る</a>
    </div>

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
    <p class="copy">&copy; 2026 mdf.works</p>
  </div>
</footer>
</body>
</html>
''' % dict(ads=ADS, icon=ICON, rows=rows(ENTRIES), total=len(ENTRIES),
           breakdown=breakdown, latest=ENTRIES[0][0])


def patch_index():
    """トップの更新履歴を最新 SHOWN 件に差し替え、全件ページへの導線を付ける。"""
    s = open('index.html', encoding='utf-8').read()
    block = ('    <ul class="log">\n' + rows(ENTRIES[:SHOWN]) + '\n    </ul>\n'
             '    <p class="more"><a href="/changelog">更新履歴をすべて見る（全%d件）'
             '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'aria-hidden="true"><path d="M4 12h15M12 5l7 7-7 7"/></svg></a></p>\n' % len(ENTRIES))
    old = re.search(r'    <ul class="log">.*?</ul>\n(    <p class="more">.*?</p>\n)?', s, re.S)
    assert old, 'index.html に更新履歴のブロックが見つからない'
    s = s[:old.start()] + block + s[old.end():]
    open('index.html', 'w', encoding='utf-8', newline='').write(s)
    return s


def patch_footers():
    """全ページのフッターに更新履歴へのリンクを足す（無い場合だけ）。"""
    import glob
    n = 0
    target = '          <li><a href="/privacy">プライバシーポリシー</a></li>'
    add = '          <li><a href="/changelog">更新履歴</a></li>\n' + target
    for p in sorted(glob.glob('*.html') + glob.glob('kuroko/*.html')
                    + glob.glob('koma/*.html') + glob.glob('blog/*.html')):
        if p.replace('\\', '/').endswith('/tool.html'):
            continue          # ツールは自己完結ページなので触らない
        s = open(p, encoding='utf-8').read()
        if '/changelog' in s or target not in s:
            continue
        open(p, 'w', encoding='utf-8', newline='').write(s.replace(target, add, 1))
        n += 1
    return n


if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    open(LOG_PATH, 'w', encoding='utf-8', newline='').write(page())
    print('%s を生成: 全%d件（%s）' % (LOG_PATH, len(ENTRIES),
          '／'.join('%s %d' % kv for kv in counts().items())))
    patch_index()
    print('index.html: 最新%d件 + 全件ページへの導線' % SHOWN)
    print('フッターにリンクを追加:', patch_footers(), 'ページ')
