"""全ページの <head> を検索意図に合わせて作り直し、JSON-LD を注入する。"""
import json, re, os

D = 'https://mdf.works'

PERSON = {"@type": "Person", "@id": D + "/#person", "name": "マカロン大福",
          "url": D + "/about.html", "sameAs": ["https://x.com/sugerslp"]}
SITE = {"@type": "WebSite", "@id": D + "/#website", "url": D + "/", "name": "mdf.works",
        "description": "ファイルをサーバーに送らずに使える無料のウェブツールを公開している個人サイト。",
        "inLanguage": "ja", "publisher": {"@id": D + "/#person"}}

def crumbs(*pairs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": D + u}
        for i, (n, u) in enumerate(pairs)]}

FAQ = [
    ("スクリーンショットの名前やアイコンを隠すのに、画像はアップロードされますか？",
     "されません。Kuroko は読み込み・解析・マスク処理・書き出しのすべてをブラウザの中で行います。画像を送信するコードが存在しないため、ページを読み込んだあとにオフラインにしても最後まで動作します。"),
    ("モザイクをかければ完全に安全ですか？",
     "いいえ。モザイクは粗さが足りないと、文字の形状から内容を推測されることがあります。文字に対してはモザイクよりも塗りつぶしのほうが確実です。重要な情報は塗りつぶしを選び、書き出した画像を拡大して確認してください。"),
    ("Discord 以外のスクリーンショットでも使えますか？",
     "自動検出は円形のアイコンを手がかりにしているため、Discord のように丸いアイコンを使うサービスに向いています。Slack や LINE のような角丸四角のアイコンは自動検出の対象外ですが、手動のマスクツールは画像の種類を問わず使えます。"),
    ("返信の引用に出てくる小さなアイコンと名前も隠せますか？",
     "隠せます。返信プレビューを構造から判定し、その小さなアイコンと名前も検出します。同じ人物には本文と同じ仮名が割り当てられます。"),
    ("料金はかかりますか。登録は必要ですか。",
     "どちらも不要です。無料で利用できます。運営費用は広告によってまかなっています。"),
    ("加工した画像の内容に責任は持ってもらえますか？",
     "いいえ。自動検出は万能ではなく、隠し漏れが起こりえます。公開前にご自身で必ず確認してください。"),
]

HOWTO = {
    "@type": "HowTo", "name": "スクリーンショットの名前とアイコンを隠す手順",
    "description": "Kuroko で画像を読み込み、自動検出でアイコンと名前にマスクをかけ、書き出して保存するまでの手順。",
    "totalTime": "PT2M",
    "tool": [{"@type": "HowToTool", "name": "ウェブブラウザ"}],
    "step": [
        {"@type": "HowToStep", "name": "スクリーンショットを読み込む",
         "text": "ドラッグ＆ドロップ、Ctrl+V での貼り付け、ファイル選択のいずれかで画像を読み込みます。複数枚まとめて扱えます。",
         "url": D + "/kuroko/guide.html#load"},
        {"@type": "HowToStep", "name": "自動検出を実行する",
         "text": "「この画像を自動検出」を押すと、アイコンと名前の行にマスクが並びます。取りこぼすときは検出の積極性を上げます。",
         "url": D + "/kuroko/guide.html#detect"},
        {"@type": "HowToStep", "name": "手作業で直す",
         "text": "足りない場所はドラッグでマスクを追加し、余分なマスクは一覧から削除します。位置と大きさは数値でも指定できます。",
         "url": D + "/kuroko/guide.html#manual"},
        {"@type": "HowToStep", "name": "書き出して保存する",
         "text": "PNG で書き出すと仕上がった画像が表示されます。共有・ダウンロード・コピー、または画像を長押し（右クリック）で保存します。",
         "url": D + "/kuroko/guide.html#save"},
    ],
}

APP = {
    "@type": "SoftwareApplication", "@id": D + "/kuroko/#app",
    "name": "Kuroko", "alternateName": "スクリーンショット匿名化ツール",
    "url": D + "/kuroko/", "applicationCategory": "MultimediaApplication",
    "applicationSubCategory": "画像編集",
    "operatingSystem": "Web ブラウザ（Windows / macOS / iOS / Android）",
    "browserRequirements": "JavaScript と HTML5 Canvas に対応したブラウザ",
    "inLanguage": "ja",
    "description": "Discord などのスクリーンショットから、アイコン・表示名・ユーザーIDを自動で検出してマスクする無料ツール。画像はサーバーに送信されず、ブラウザの中だけで処理されます。",
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
    "featureList": [
        "円形アイコンの自動検出", "表示名・タグ・時刻の行の自動検出",
        "同一人物のアイコンをまとめて同じ仮名に置き換え", "返信プレビューのアイコンと名前に対応",
        "モザイク・ぼかし・塗りつぶし・ダミー名", "手動マスクの追加と数値指定",
        "画像を送信しないブラウザ内処理", "書き出し時に Exif が残らない",
    ],
    "author": {"@id": D + "/#person"}, "publisher": {"@id": D + "/#person"},
    "isAccessibleForFree": True,
}

# ---------------------------------------------------------------- per page
PAGES = {
 'index.html': dict(
   url=D + '/', og='home.png', type='website',
   title='mdf.works｜アップロード不要のブラウザ完結ウェブツール',
   desc='ファイルをサーバーに送らずに使える無料のウェブツールを公開しています。インストールも登録も不要。スクリーンショットの名前とアイコンを隠す「Kuroko」を公開中です。',
   ld=[SITE, PERSON,
       {"@type": "CollectionPage", "@id": D + "/#webpage", "url": D + "/", "name": "mdf.works",
        "isPartOf": {"@id": D + "/#website"}, "inLanguage": "ja",
        "about": {"@id": D + "/kuroko/#app"}},
       APP]),

 'kuroko/index.html': dict(
   url=D + '/kuroko/', og='kuroko.png', type='website',
   title='スクショの名前・アイコンを隠す無料ツール｜Kuroko',
   desc='Discord などのスクリーンショットから、アイコン・表示名・ユーザーIDを自動で見つけて隠せる無料ツールです。アップロード不要、ブラウザだけで完結。登録もインストールも要りません。',
   ld=[APP, PERSON,
       {"@type": "FAQPage", "mainEntity": [
           {"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
       crumbs(("ホーム", "/"), ("Kuroko", "/kuroko/"))]),

 'kuroko/tool.html': dict(
   url=D + '/kuroko/tool.html', og='kuroko.png', type='website',
   title='スクショ匿名化ツール（無料・登録不要）｜Kuroko',
   desc='画像を読み込んでボタンを押すだけ。アイコンと名前を自動検出し、モザイク・塗りつぶし・仮名への置き換えができます。画像はどこにも送信されません。',
   ld=[APP, crumbs(("ホーム", "/"), ("Kuroko", "/kuroko/"), ("匿名化ツール", "/kuroko/tool.html"))]),

 'kuroko/guide.html': dict(
   url=D + '/kuroko/guide.html', og='guide.png', type='article',
   title='Kurokoの使い方｜スクショの名前とアイコンを隠す手順',
   desc='画像の読み込みから保存まで画面に沿って解説します。自動検出がうまくいかないときの感度調整、手動マスクの操作、ショートカット、保存できないときの対処まで。',
   ld=[HOWTO, PERSON, crumbs(("ホーム", "/"), ("Kuroko", "/kuroko/"), ("使い方ガイド", "/kuroko/guide.html"))]),

 'kuroko/checklist.html': dict(
   url=D + '/kuroko/checklist.html', og='checklist.png', type='article',
   title='スクショ公開前のチェックリスト12項目｜消し忘れを防ぐ',
   desc='通知バナー、Exif、ファイル名、モザイクの強度不足、PDFの墨消しの落とし穴など、アイコンと名前を隠しただけでは残ってしまうものを12項目に整理しました。',
   ld=[{"@type": "Article", "headline": "スクリーンショットを公開する前のチェックリスト12項目",
        "description": "アイコンと名前を隠しただけでは足りません。見落としやすい12項目を整理しました。",
        "image": D + "/assets/og/checklist.png",
        "datePublished": "2026-08-13", "dateModified": "2026-08-14",
        "inLanguage": "ja", "author": {"@id": D + "/#person"}, "publisher": {"@id": D + "/#person"},
        "mainEntityOfPage": D + "/kuroko/checklist.html"},
       PERSON, crumbs(("ホーム", "/"), ("Kuroko", "/kuroko/"), ("公開前チェックリスト", "/kuroko/checklist.html"))]),

 'kuroko/mosaic.html': dict(
   url=D + '/kuroko/mosaic.html', og='mosaic.png', type='article',
   title='モザイクやぼかしは復元できる？文字を隠すときの注意点',
   desc='モザイクが文字に弱い理由を仕組みから説明します。どのくらい粗くすれば安全か、ぼかしとの違い、塗りつぶしを使うべき場面、PDFの墨消しの落とし穴まで。',
   ld=[{"@type": "Article", "headline": "モザイクやぼかしは復元できるのか",
        "description": "モザイクが文字に対して弱い理由と、安全に隠すための具体的な基準。",
        "image": D + "/assets/og/mosaic.png",
        "datePublished": "2026-08-14", "dateModified": "2026-08-14",
        "inLanguage": "ja", "author": {"@id": D + "/#person"}, "publisher": {"@id": D + "/#person"},
        "mainEntityOfPage": D + "/kuroko/mosaic.html"},
       PERSON, crumbs(("ホーム", "/"), ("Kuroko", "/kuroko/"), ("モザイクは復元できるのか", "/kuroko/mosaic.html"))]),

 'about.html': dict(
   url=D + '/about.html', og='about.png', type='profile',
   title='このサイトについて・運営者情報｜mdf.works',
   desc='mdf.works の方針、公開しているツール、技術的な仕組み、運営者情報を記載しています。運営者はマカロン大福です。',
   ld=[PERSON, {"@type": "AboutPage", "url": D + "/about.html", "name": "このサイトについて",
                "inLanguage": "ja", "isPartOf": {"@id": D + "/#website"}},
       crumbs(("ホーム", "/"), ("このサイトについて", "/about.html"))]),

 'privacy.html': dict(
   url=D + '/privacy.html', og='home.png', type='website',
   title='プライバシーポリシー｜mdf.works',
   desc='mdf.works における情報の取り扱い、Cookie、Google AdSense をはじめとする第三者配信広告、アクセス解析、免責事項について記載しています。',
   ld=[{"@type": "WebPage", "url": D + "/privacy.html", "name": "プライバシーポリシー",
        "inLanguage": "ja", "isPartOf": {"@id": D + "/#website"}},
       crumbs(("ホーム", "/"), ("プライバシーポリシー", "/privacy.html"))]),

 'terms.html': dict(
   url=D + '/terms.html', og='home.png', type='website',
   title='利用規約・免責事項｜mdf.works',
   desc='mdf.works が提供するツールおよびコンテンツの利用条件です。サービスの内容、禁止事項、保証の範囲、責任の制限、知的財産権について定めています。',
   ld=[{"@type": "WebPage", "url": D + "/terms.html", "name": "利用規約・免責事項",
        "inLanguage": "ja", "isPartOf": {"@id": D + "/#website"}},
       crumbs(("ホーム", "/"), ("利用規約・免責事項", "/terms.html"))]),

 'contact.html': dict(
   url=D + '/contact.html', og='home.png', type='website',
   title='お問い合わせ｜mdf.works',
   desc='mdf.works へのご質問、不具合のご報告、ご要望、掲載内容に関するご連絡はこちらから承ります。メール・Discord・X で受け付けています。',
   ld=[{"@type": "ContactPage", "url": D + "/contact.html", "name": "お問い合わせ",
        "inLanguage": "ja", "isPartOf": {"@id": D + "/#website"}},
       crumbs(("ホーム", "/"), ("お問い合わせ", "/contact.html"))]),
}


def build_head(path, cfg):
    depth = path.count('/')
    root = '../' * depth
    ld = json.dumps({"@context": "https://schema.org", "@graph": cfg['ld']},
                    ensure_ascii=False, indent=2)
    img = D + '/assets/og/' + cfg['og']
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cfg['title']}</title>
<meta name="description" content="{cfg['desc']}">
<link rel="canonical" href="{cfg['url']}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="theme-color" content="#131720">
<meta name="author" content="マカロン大福">
<meta property="og:type" content="{cfg['type']}">
<meta property="og:site_name" content="mdf.works">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{cfg['title']}">
<meta property="og:description" content="{cfg['desc']}">
<meta property="og:url" content="{cfg['url']}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{cfg['title']}">
<meta name="twitter:description" content="{cfg['desc']}">
<meta name="twitter:image" content="{img}">
<meta name="twitter:creator" content="@sugerslp">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23131720'/><circle cx='11' cy='12' r='5.5' fill='%23FF8244'/><rect x='4' y='21' width='24' height='5' rx='2.5' fill='%23E7E9EE'/></svg>">
<script type="application/ld+json">
{ld}
</script>'''


if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    for path, cfg in PAGES.items():
        if not os.path.exists(path):
            print('SKIP (not yet created):', path); continue
        s = open(path, encoding='utf-8').read()
        head = build_head(path, cfg)
        # keep whatever style/stylesheet link the page already has
        keep = []
        m = re.search(r'<link rel="stylesheet" href="[^"]+">', s)
        if m: keep.append(m.group(0))
        m = re.search(r'<style>.*?</style>', s, re.S)
        if m: keep.append(m.group(0))
        new_head = head + ('\n' + '\n'.join(keep) if keep else '')
        s = re.sub(r'<head>\n.*?\n</head>', '<head>\n' + new_head + '\n</head>', s, flags=re.S)
        open(path, 'w', encoding='utf-8', newline='').write(s)
        # validate the JSON-LD round-trips
        blob = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', s, re.S).group(1)
        json.loads(blob)
        print(f'{path:24s} ok  title={len(cfg["title"])}字  desc={len(cfg["desc"])}字')
