"""ブログの一覧ページを生成し、各記事に共通パーツ（メタ・目次・シェア・前後・関連）を差し込む。

記事を追加するときは POSTS に1件足して、このスクリプトを実行するだけ。
    python _local/build_blog.py
"""
import json, os, re, html

D = 'https://mdf.works'

POSTS = [
    dict(slug='theme', cat='開発', date='2026-08-30',
         title='ダークモードは色を反転するのではない — 実装して分かったこと',
         name='ダークモードは色を反転するのではない — 実装して分かったこと',
         lead='このサイトにテーマ切替を付けたときの記録です。OS の設定に従うだけでは足りず、'
              '利用者の上書きを受け付けると CSS が三段構えになります。描画前の一瞬のちらつき、'
              'localStorage が例外を投げる場面、そして「黒地に白」にしてはいけない理由。',
         tags=['CSS', 'ダークモード', 'アクセシビリティ', '配色', '個人開発'],
         icon='<circle cx="12" cy="12" r="4.4"/>'
              '<path d="M12 2.6v2.3M12 19.1v2.3M2.6 12h2.3M19.1 12h2.3M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M18.7 5.3l-1.6 1.6M6.9 17.1l-1.6 1.6"/>'),
    dict(slug='wifi', cat='セキュリティ', date='2026-08-30',
         title='公衆Wi-Fiは危険か — HTTPSが片付けたことと、残っているもの',
         name='公衆Wi-Fiは危険か — HTTPSが片付けたことと、残っているもの',
         lead='10年前の危なさと、いまの危なさは中身が違います。通信を覗かれる問題はほぼ解決し、'
              '代わりに「つなぐ相手を間違えさせる」経路が残りました。'
              '偽アクセスポイント、同意画面、証明書の警告、そして VPN が効く範囲。',
         tags=['Wi-Fi', 'HTTPS', 'VPN', 'セキュリティ', '公衆無線LAN'],
         icon='<path d="M3.2 9.6a13 13 0 0 1 17.6 0"/>'
              '<path d="M6.2 12.9a8.7 8.7 0 0 1 11.6 0"/>'
              '<rect x="8.8" y="16.2" width="6.4" height="5" rx="1.2"/>'
              '<path d="M10.4 16.2v-1.1a1.6 1.6 0 0 1 3.2 0v1.1"/>'),
    dict(slug='cors', cat='ブラウザ', date='2026-08-27',
         title='ブラウザだけでは動画を保存できない — CORS を実測して確かめる',
         name='ブラウザだけでは動画を保存できない — CORS を実測して確かめる',
         lead='要求は送れるのに、返ってきた中身が読めない。その境目を実際に測りました。'
              'no-cors が返す0文字の応答、指定しても必ず書き換えられる4つのヘッダー、'
              'そして「読めないのが既定」であることが何を守っているのか。',
         tags=['CORS', 'fetch', 'JavaScript', 'セキュリティ', 'ブラウザ'],
         icon='<path d="M2.5 12h9.6"/>'
              '<path d="M8.9 8.8L12.1 12l-3.2 3.2"/>'
              '<circle cx="17.6" cy="12" r="3.9"/>'
              '<path d="M14.8 9.2l5.6 5.6"/>'),
    dict(slug='exif', cat='プライバシー', date='2026-08-24',
         title='スマホの写真から何が分かるか — Exif と、消しても残るもの',
         name='スマホの写真から何が分かるか — Exif と、消しても残るもの',
         lead='写真には撮影地の座標と秒単位の日時が埋め込まれています。精度は数メートルで、'
              '自宅で撮った1枚ほど価値の高い座標になります。中身の一覧と SNS ごとの扱い、'
              '消しかた、そして消しても残る反射・影・電柱の話。',
         tags=['Exif', '位置情報', '写真', 'プライバシー', 'SNS'],
         icon='<path d="M12 21.3s6.3-6.1 6.3-10.3a6.3 6.3 0 1 0-12.6 0C5.7 15.2 12 21.3 12 21.3z"/>'
              '<circle cx="12" cy="10.8" r="2.4"/>'),
    dict(slug='qr', cat='セキュリティ', date='2026-08-23',
         title='QRコードは中身が見えない — 貼り替え詐欺と、読み取る前の確認',
         name='QRコードは中身が見えない — 貼り替え詐欺と、読み取る前の確認',
         lead='四角い模様を見て URL を読める人はいません。QR コードには発行元の証明も署名も無く、'
              '上から貼り替えるだけで宛先を差し替えられます。実際に起きている手口と、'
              'タップする前にできる確認、そして写り込んだ QR から漏れるものまで。',
         tags=['QRコード', 'フィッシング', 'キャッシュレス決済', 'Wi-Fi', 'セキュリティ'],
         icon='<rect x="3.4" y="3.4" width="7" height="7" rx="1.3"/>'
              '<rect x="13.6" y="3.4" width="7" height="7" rx="1.3"/>'
              '<rect x="3.4" y="13.6" width="7" height="7" rx="1.3"/>'
              '<path d="M13.6 13.6h3.1v3.1h-3.1zM20.6 13.6v2.2M13.6 20.6h2.2M18.4 18.4h2.2v2.2"/>'),
    dict(slug='circle', cat='開発', date='2026-08-22',
         title='画像から円を検出する — ハフ変換だけでは足りなかった話',
         name='画像から円を検出する — ハフ変換だけでは足りなかった話',
         lead='スクリーンショットの丸いアイコンをブラウザだけで見つける。'
              '候補を出すのは教科書どおりで足りましたが、本物かどうかの判定が難所でした。'
              '合成画像で16分の1、実写で11分の0まで落ちた原因と、そこから直した手当て。',
         tags=['画像処理', 'ハフ変換', 'Canvas', 'JavaScript', 'アルゴリズム'],
         icon='<circle cx="12" cy="12" r="8.2"/>'
              '<circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/>'
              '<path d="M12 3.8v2.4M12 17.8v2.4M3.8 12h2.4M17.8 12h2.4"/>'),
    dict(slug='extension', cat='ブラウザ', date='2026-08-21',
         title='拡張機能の権限の見かた — 「すべてのサイトのデータを読み取る」とは何か',
         name='拡張機能の権限の見かた — 「すべてのサイトのデータを読み取る」とは何か',
         lead='あの確認画面は具体的に何を許しているのか。入力中の文字も表示内容も読めます。'
              'そして本当の危険は入れた瞬間ではなく、通知なく届く自動更新のほうにあります。'
              '権限を絞る設定と、入れる前に見る場所をまとめました。',
         tags=['拡張機能', 'Chrome', '権限', 'プライバシー', 'セキュリティ'],
         icon='<path d="M9.5 3.5h5v3a2 2 0 0 0 2 2h3v5h-3a2 2 0 0 0-2 2v3h-5v-3a2 2 0 0 0-2-2h-3v-5h3a2 2 0 0 0 2-2z"/>'),
    dict(slug='imageformat', cat='基本', date='2026-08-19',
         title='スクリーンショットはPNG、写真はJPEG — 画像形式の選び方',
         name='スクリーンショットはPNG、写真はJPEG — 画像形式の選び方',
         lead='スクリーンショットを JPEG で保存すると文字がにじみます。'
              '原因は 8×8 ブロック単位の処理と、色を間引く仕組みです。'
              'PNG・JPEG・WebP・AVIF が何に強いのかを、劣化の起きかたから説明します。',
         tags=['PNG', 'JPEG', 'WebP', 'AVIF', '画像'],
         icon='<rect x="3" y="4.5" width="18" height="15" rx="2.2"/>'
              '<path d="M3 15l4.5-4.2 3.6 3.3 3.3-3.9L21 15.5"/>'
              '<circle cx="8.6" cy="9" r="1.4"/>'),
    dict(slug='passkey', cat='セキュリティ', date='2026-08-18',
         title='二段階認証はどれを選ぶか — SMS・認証アプリ・パスキーの違い',
         name='二段階認証はどれを選ぶか — SMS・認証アプリ・パスキーの違い',
         lead='二段階認証を有効にしていても乗っ取られることはあります。'
              '方式によって防げる攻撃が違うからです。分かれ目は「人がコードを入力するかどうか」。'
              'パスキーが仕組みとしてフィッシングに強い理由と、設定する順番を整理します。',
         tags=['パスキー', '二段階認証', 'パスワード', 'フィッシング', 'セキュリティ'],
         icon='<rect x="4" y="10.5" width="16" height="10" rx="2.2"/>'
              '<path d="M7.8 10.5V7.2a4.2 4.2 0 0 1 8.4 0v3.3"/>'
              '<circle cx="12" cy="15.5" r="1.5"/>'),
    dict(slug='battery', cat='ガジェット', date='2026-08-17',
         title='モバイルバッテリーは mAh で選ばない — 見るべきは Wh と W',
         name='モバイルバッテリーは mAh で選ばない — 見るべきは Wh と W',
         lead='10000mAh のバッテリーで 5000mAh のスマートフォンは2回充電できません。'
              'mAh を Wh に直す計算、速さを決める W、USB PD と PPS、ケーブルの上限、'
              '飛行機の 100Wh 制限、日本の PSE マークまで。選ぶときに見る数字は4つだけです。',
         tags=['ガジェット', 'モバイルバッテリー', 'USB', '充電', '選び方'],
         icon='<rect x="2.5" y="7.5" width="16" height="9" rx="2.2"/>'
              '<path d="M21.5 11v2"/>'
              '<path d="M5.5 10.5v3M8.5 10.5v3M11.5 10.5v3"/>'),
    dict(slug='ping', cat='ゲーム', date='2026-08-16',
         title='Ping はどこで生まれるのか — 回線を速くしても下がらない理由',
         name='Ping はどこで生まれるのか — 回線を速くしても下がらない理由',
         lead='回線を 1Gbps にしても Ping は下がりません。速度と遅延は別のものだからです。'
              '光の速度が決める下限から順に、遅延が何ミリ秒ずつどこで積まれているのかを分解し、'
              '実際に効く対策と効かない対策を整理します。',
         tags=['ゲーム', 'ネットワーク', '回線', 'Wi-Fi', '遅延'],
         icon='<path d="M12 20.5v-6"/>'
              '<path d="M8.1 16.6a5.5 5.5 0 0 1 7.8 0"/>'
              '<path d="M5.3 13.8a9.5 9.5 0 0 1 13.4 0"/>'
              '<path d="M2.5 11a13.4 13.4 0 0 1 19 0"/>'),
    dict(slug='cache', cat='開発', date='2026-08-16',
         title='HTMLは新しいのにCSSだけ古い — 静的サイトのキャッシュの罠',
         name='HTMLは新しいのにCSSだけ古い — 静的サイトのキャッシュの罠',
         lead='パソコンでは正常なのに、スマートフォンでだけレイアウトが崩れる。'
              '原因は CSS の中身ではなく、HTML と CSS でキャッシュの寿命が違っていたことでした。'
              '切り分けの手順と、3つの対処のどれを選ぶかまで。',
         tags=['キャッシュ', 'Cloudflare', '静的サイト', 'CSS', 'デプロイ'],
         icon='<path d="M3.5 6.5c0-1.7 3.8-3 8.5-3s8.5 1.3 8.5 3-3.8 3-8.5 3-8.5-1.3-8.5-3z"/>'
              '<path d="M3.5 6.5v11c0 1.7 3.8 3 8.5 3s8.5-1.3 8.5-3v-11"/>'
              '<path d="M3.5 12c0 1.7 3.8 3 8.5 3s8.5-1.3 8.5-3"/>'),
    dict(slug='browser', cat='ブラウザ', date='2026-08-16',
         title='ブラウザの選び方 — 結局どれを使えばいいのか',
         name='ブラウザの選び方 — Chrome・Firefox・Edge・Safari・Brave の違い',
         lead='「どれが速いか」で選ぼうとすると決まりません。実際に差が出るのは拡張機能の扱い、'
              'プライバシーの初期設定、同期の紐づけ先の3つです。用途別の選び方と、'
              '分けて使うという答えについて。',
         tags=['Chrome', 'Firefox', 'Safari', 'Brave', '拡張機能'],
         icon='<circle cx="12" cy="12" r="9"/><path d="M3.4 9.2h17.2M3.4 14.8h17.2"/>'
              '<path d="M12 3a15 15 0 0 0 0 18a15 15 0 0 0 0-18"/>'),
    dict(slug='capture', cat='基本', date='2026-08-16',
         title='スクリーンショットは必要な範囲だけを撮る',
         name='スクリーンショットは必要な範囲だけを撮る',
         lead='隠す作業を減らすいちばん確実な方法は、そもそも写さないことです。'
              'Windows・macOS・iPhone・Android それぞれの範囲指定の撮り方と、'
              '撮る前に止めておきたい通知の設定をまとめました。',
         tags=['Windows', 'macOS', 'iPhone', 'Android', 'ショートカット'],
         icon='<rect x="3" y="6" width="18" height="13" rx="2.5"/><path d="M8 6l1.6-2.4h4.8L16 6"/>'
              '<circle cx="12" cy="12.5" r="3.2"/>'),
    dict(slug='mosaic', cat='プライバシー', date='2026-08-14',
         title='モザイク・ぼかし・塗りつぶし — 文字を隠すならどれを選ぶか',
         name='モザイク・ぼかし・塗りつぶし — 文字を隠すならどれを選ぶか',
         lead='同じ設定でも、写真なら十分で、アカウント名なら心もとない。'
              'その差がどこから来るのかと、隠す対象ごとに何を選べばよいかの基準を整理しました。'
              'ぼかしの半径の目安と、文書ファイルの墨消しについても触れています。',
         tags=['モザイク', 'ぼかし', '塗りつぶし', 'PDF'],
         icon='<rect x="3" y="3" width="5.6" height="5.6" fill="currentColor" stroke="none"/>'
              '<rect x="15.4" y="3" width="5.6" height="5.6" fill="currentColor" stroke="none"/>'
              '<rect x="9.2" y="9.2" width="5.6" height="5.6" fill="currentColor" stroke="none"/>'
              '<rect x="3" y="15.4" width="5.6" height="5.6" fill="currentColor" stroke="none"/>'
              '<rect x="15.4" y="15.4" width="5.6" height="5.6" fill="currentColor" stroke="none"/>'),
    dict(slug='checklist', cat='プライバシー', date='2026-08-13',
         title='スクリーンショットを公開する前のチェックリスト12項目',
         name='スクリーンショットを公開する前のチェックリスト12項目',
         lead='アイコンと名前を隠せば安心、とはいきません。'
              '通知バナー、ステータスバー、Exif、ファイル名、背景の映り込み。'
              '見落としやすいものを、実際に問題になりやすい順に並べました。',
         tags=['Exif', '通知', '確認手順', 'PDF'],
         icon='<path d="M5 6.5h14M5 12h14M5 17.5h9"/><path d="M17.5 16.5l1.6 1.6 3-3.2"/>'),
]

TITLE = 'ブログ｜ブラウザ・ガジェット・プライバシーのはなし - mdf.works'
DESC = ('ブラウザやガジェット、作ったものの話、そしてスクリーンショットと個人情報のこと。'
        '手を動かすときに役立つ形でまとめた記事の一覧です。タグと検索で絞り込めます。')

GA_ADS = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-5GDKSW8H7X"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-5GDKSW8H7X');
</script>
<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8613999974980382"
     crossorigin="anonymous"></script>'''

ICON = ("<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' "
        "viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23131720'/>"
        "<circle cx='11' cy='12' r='5.5' fill='%23FF8244'/>"
        "<rect x='4' y='21' width='24' height='5' rx='2.5' fill='%23E7E9EE'/></svg>\">")


# ---------------------------------------------------------------- helpers
def jp_date(d):
    y, m, dd = d.split('-')
    return '%s年%d月%d日' % (y, int(m), int(dd))


def reading_minutes(path):
    """本文の文字数からおおよその読了時間を出す（日本語 500 字/分）。"""
    s = open(path, encoding='utf-8').read()
    m = re.search(r'<main id="main">(.*?)</main>', s, re.S)
    body = m.group(1) if m else s
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<[^>]+>', '', body)
    body = html.unescape(body)
    n = len(re.sub(r'\s+', '', body))
    return max(1, round(n / 500))


def all_tags():
    seen = []
    for p in POSTS:
        for t in p['tags']:
            if t not in seen:
                seen.append(t)
    return seen


def cat_counts():
    out = {}
    for p in POSTS:
        out[p['cat']] = out.get(p['cat'], 0) + 1
    return out


# ---------------------------------------------------------------- index page
def cards(mins):
    out = []
    for p in POSTS:
        tags = ''.join('<span class="tag">%s</span>' % t for t in p['tags'])
        search = ' '.join([p['title'], p['lead'], p['cat']] + p['tags']).lower()
        out.append(f'''      <a class="proj" href="/blog/{p['slug']}"
         data-cat="{p['cat']}" data-tags="{'|'.join(p['tags'])}"
         data-date="{p['date']}" data-text="{html.escape(search, quote=True)}">
        <div class="top">
          <span class="glyph" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">{p['icon']}</svg>
          </span>
          <div class="meta" style="margin:0">
            <span class="cat">{p['cat']}</span>
            <time datetime="{p['date']}">{jp_date(p['date'])}</time>
          </div>
        </div>
        <h3 class="post">{p['title']}</h3>
        <p>{p['lead']}</p>
        <div class="tags">{tags}</div>
        <span class="go">読む · 約{mins[p['slug']]}分
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12h15M12 5l7 7-7 7"/></svg>
        </span>
      </a>''')
    return '\n\n'.join(out)


def cat_chips():
    c = cat_counts()
    out = ['<button type="button" data-cat="" aria-pressed="true">すべて <b>%d</b></button>' % len(POSTS)]
    for name, n in c.items():
        out.append('<button type="button" data-cat="%s" aria-pressed="false">%s <b>%d</b></button>' % (name, name, n))
    return ''.join(out)


def tag_chips():
    return ''.join('<button type="button" data-tag="%s" aria-pressed="false">%s</button>' % (t, t)
                   for t in all_tags())


FILTER_JS = '''<script>
(function () {
  var wrap  = document.getElementById('posts');
  if (!wrap) return;
  var cards = Array.prototype.slice.call(wrap.querySelectorAll('.proj'));
  var q     = document.getElementById('q');
  var clear = document.getElementById('qclear');
  var sort  = document.getElementById('sort');
  var count = document.getElementById('count');
  var reset = document.getElementById('reset');
  var none  = document.getElementById('noresult');
  var state = { q: '', cat: '', tag: '' };

  function press(group, attr, value) {
    group.querySelectorAll('button').forEach(function (b) {
      b.setAttribute('aria-pressed', (b.dataset[attr] || '') === value ? 'true' : 'false');
    });
  }

  function apply(push) {
    var kw = state.q.trim().toLowerCase();
    var n = 0;
    cards.forEach(function (c) {
      var ok = true;
      if (state.cat && c.dataset.cat !== state.cat) ok = false;
      if (ok && state.tag && c.dataset.tags.split('|').indexOf(state.tag) < 0) ok = false;
      if (ok && kw && c.dataset.text.indexOf(kw) < 0) ok = false;
      c.hidden = !ok;
      if (ok) n++;
    });
    var order = cards.slice().sort(function (a, b) {
      return sort.value === 'old'
        ? a.dataset.date.localeCompare(b.dataset.date)
        : b.dataset.date.localeCompare(a.dataset.date);
    });
    order.forEach(function (c) { wrap.appendChild(c); });

    count.textContent = n === cards.length ? n + '件の記事' : n + '件 / 全' + cards.length + '件';
    none.hidden = n > 0;
    reset.hidden = !(state.q || state.cat || state.tag);
    if (clear) clear.hidden = !state.q;

    if (push) {
      var h = [];
      if (state.cat) h.push('cat=' + encodeURIComponent(state.cat));
      if (state.tag) h.push('tag=' + encodeURIComponent(state.tag));
      if (state.q)   h.push('q='   + encodeURIComponent(state.q));
      history.replaceState(null, '', h.length ? '#' + h.join('&') : location.pathname);
    }
  }

  function readHash() {
    var h = location.hash.replace(/^#/, '');
    if (!h) return;
    h.split('&').forEach(function (kv) {
      var i = kv.indexOf('=');
      if (i < 0) return;
      var k = kv.slice(0, i), v = decodeURIComponent(kv.slice(i + 1));
      if (k === 'cat') state.cat = v;
      if (k === 'tag') state.tag = v;
      if (k === 'q')   state.q = v;
    });
    if (q) q.value = state.q;
    press(document.getElementById('cats'), 'cat', state.cat);
    press(document.getElementById('tags'), 'tag', state.tag);
    if (state.tag) { var d = document.getElementById('tagbox'); if (d) d.open = true; }
  }

  document.getElementById('cats').addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    state.cat = b.dataset.cat || '';
    press(this, 'cat', state.cat);
    apply(true);
  });
  document.getElementById('tags').addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    state.tag = (state.tag === b.dataset.tag) ? '' : b.dataset.tag;
    press(this, 'tag', state.tag);
    apply(true);
  });
  if (q) q.addEventListener('input', function () { state.q = q.value; apply(true); });
  if (clear) clear.addEventListener('click', function () { state.q = ''; q.value = ''; q.focus(); apply(true); });
  sort.addEventListener('change', function () { apply(true); });
  reset.addEventListener('click', function () {
    state = { q: '', cat: '', tag: '' };
    if (q) q.value = '';
    press(document.getElementById('cats'), 'cat', '');
    press(document.getElementById('tags'), 'tag', '');
    apply(true);
  });

  readHash();
  apply(false);
})();
</script>'''


def build_index(mins):
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Blog", "@id": D + "/blog/#blog", "url": D + "/blog/", "name": "mdf.works ブログ",
             "description": "ブラウザやガジェット、作ったものの話、スクリーンショットと個人情報のこと。",
             "inLanguage": "ja", "author": {"@id": D + "/#person"},
             "publisher": {"@id": D + "/#person"}, "isPartOf": {"@id": D + "/#website"}},
            {"@type": "Person", "@id": D + "/#person", "name": "マカロン大福",
             "url": D + "/about.html", "sameAs": ["https://x.com/sugerslp"]},
            {"@type": "ItemList", "itemListOrder": "https://schema.org/ItemListOrderDescending",
             "numberOfItems": len(POSTS),
             "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                  "url": "%s/blog/%s.html" % (D, p['slug']), "name": p['name']}
                                 for i, p in enumerate(POSTS)]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "ホーム", "item": D + "/"},
                {"@type": "ListItem", "position": 2, "name": "ブログ", "item": D + "/blog/"}]},
        ]
    }
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{GA_ADS}
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{D}/blog/">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="theme-color" content="#131720">
<meta name="author" content="マカロン大福">
<meta property="og:type" content="website">
<meta property="og:site_name" content="mdf.works">
<meta property="og:locale" content="ja_JP">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{D}/blog/">
<meta property="og:image" content="{D}/assets/og/blog.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{D}/assets/og/blog.png">
<meta name="twitter:creator" content="@sugerslp">
{ICON}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
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
      <a href="/blog/" aria-current="page">記事一覧</a>
      <a href="/kuroko/">Kuroko</a>
      <a href="/koma/">Koma</a>
      <a href="/about">このサイトについて</a>
      <a class="cta" href="/kuroko/tool">ツールを開く</a>
    </nav>
  </div>
</header>

<main id="main">
  <div class="wrap">

    <p class="crumb"><a href="/">mdf.works</a><span aria-hidden="true">›</span>ブログ</p>

    <div class="page-head prose">
      <p class="eyebrow">Blog</p>
      <h1>調べたこと、作ったこと、<br>気をつけていること</h1>
      <p class="lead">
        ブラウザやガジェットの話、個人開発で分かったこと、
        そしてスクリーンショットと個人情報のこと。
        読んだあとに手を動かせる形で書くようにしています。
      </p>
    </div>

    <h2 id="articles">記事一覧</h2>

    <div class="blogtools">
      <div class="searchbox">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.4 15.4L21 21"/></svg>
        <input type="search" id="q" placeholder="キーワードで探す" aria-label="記事をキーワードで検索" autocomplete="off">
        <button type="button" id="qclear" aria-label="検索語を消す" hidden>×</button>
      </div>
      <label class="visually-hidden" for="sort">並び替え</label>
      <select id="sort">
        <option value="new">新しい順</option>
        <option value="old">古い順</option>
      </select>
    </div>

    <div class="chips" id="cats" role="group" aria-label="カテゴリで絞り込む">{cat_chips()}</div>

    <details class="tagbox" id="tagbox">
      <summary>タグで絞り込む</summary>
      <div class="chips" id="tags" role="group" aria-label="タグで絞り込む">{tag_chips()}</div>
    </details>

    <div class="resultbar">
      <span class="n" id="count">{len(POSTS)}件の記事</span>
      <button type="button" class="reset" id="reset" hidden>絞り込みを解除</button>
    </div>

    <div class="projects" id="posts">

{cards(mins)}

    </div>

    <div class="noresult" id="noresult" hidden>
      <b>該当する記事がありませんでした</b>
      キーワードを短くするか、カテゴリとタグの絞り込みを解除してみてください。
    </div>

    <h2>これから書くこと</h2>
    <div class="prose">
      <p>
        もともとは <a href="/kuroko/">Kuroko</a> というツールを作る過程で気づいたことの記録として始めました。
        アイコンと名前をきれいに隠しても、画面の隅に通知が写っていれば意味がない。
        ツールが引き受けられるのは作業の一部で、判断の部分は人が持っている。
        そういう「ツールの外側」の話が最初の3本です。
      </p>
      <p>
        いまは範囲を広げて、ブラウザやアプリの選び方、使っているガジェット、
        個人開発でつまずいたところ、遊んでいるゲームの話なども書いていく予定です。
        共通しているのは、<strong>確かめられることだけを書く</strong>という点です。
        自分で試した話も、調べて整理した話もありますが、
        どちらも「読んだあとに手を動かせるか」を基準にしています。
      </p>
      <p>
        扱ってほしい話題や、内容についてのご指摘があれば
        <a href="/contact">お問い合わせ</a>からお知らせください。
      </p>
      <div class="btnrow">
        <a class="btn primary" href="/kuroko/tool">Kuroko を使ってみる</a>
        <a class="btn" href="/about">このサイトについて</a>
      </div>
    </div>

  </div>
{FILTER_JS}
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


# ---------------------------------------------------------------- article parts
POST_JS = '''<script>
(function () {
  var prose = document.querySelector('main .prose');
  var toc = document.getElementById('toc');
  if (prose && toc) {
    var ol = toc.querySelector('ol'), n = 0;
    prose.querySelectorAll('h2, h3').forEach(function (h) {
      if (h.closest('.postnav')) return;
      if (!h.id) h.id = 'sec' + (++n);
      var li = document.createElement('li');
      li.className = h.tagName === 'H3' ? 'lv3' : 'lv2';
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent.trim();
      li.appendChild(a);
      ol.appendChild(li);
    });
    if (ol.children.length >= 3) toc.hidden = false;
  }
  var copy = document.getElementById('copylink');
  if (copy) copy.addEventListener('click', function () {
    var done = function (ok) {
      copy.textContent = ok ? 'コピーしました' : 'コピーできませんでした';
      setTimeout(function () { copy.textContent = 'リンクをコピー'; }, 1800);
    };
    if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(function () { done(true); }, function () { done(false); });
    else done(false);
  });
})();
</script>'''


def post_head(p, mins):
    return (f'''      <div class="postmeta">
        <span class="cat">{p['cat']}</span>
        <time datetime="{p['date']}">{jp_date(p['date'])}</time>
        <span class="read">約{mins}分で読めます</span>
      </div>''')


def post_nav(i, p, mins):
    prev = POSTS[i + 1] if i + 1 < len(POSTS) else None      # 一覧は新しい順なので次が古い記事
    nxt = POSTS[i - 1] if i > 0 else None
    share_url = '%s/blog/%s.html' % (D, p['slug'])
    x = ('https://x.com/intent/post?text=' + p['title'].replace('&', '＆').replace('#', '＃')
         + '&url=' + share_url)
    pager = []
    if prev:
        pager.append('<a class="prev" href="/blog/%s"><span class="dir">← 前の記事</span>'
                     '<span class="t">%s</span></a>' % (prev['slug'], prev['title']))
    if nxt:
        pager.append('<a class="next" href="/blog/%s"><span class="dir">次の記事 →</span>'
                     '<span class="t">%s</span></a>' % (nxt['slug'], nxt['title']))

    rel = [q for q in POSTS if q['slug'] != p['slug'] and q['cat'] == p['cat']]
    for q in POSTS:
        if len(rel) >= 2:
            break
        if q['slug'] != p['slug'] and q not in rel:
            rel.append(q)
    rel = rel[:2]
    cards_html = '\n'.join(
        '      <div class="card">\n'
        '        <h3><a href="/blog/%s" style="text-decoration:none">%s</a></h3>\n'
        '        <p>%s</p>\n'
        '      </div>' % (q['slug'], q['title'], q['lead'][:78] + '…') for q in rel)

    return f'''    <!-- postnav:start -->
    <div class="postnav">
      <div class="share">
        <span class="label">この記事を共有</span>
        <a href="{html.escape(x, quote=True)}" target="_blank" rel="noopener noreferrer">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 3h3.2l-7 8 8.3 10h-6.5l-5-6.2-5.8 6.2H1.5l7.5-8.6L1 3h6.7l4.6 5.8L17.5 3zm-1.1 16.2h1.8L7.7 4.7H5.8l10.6 14.5z"/></svg>
          X で共有
        </a>
        <button type="button" id="copylink">リンクをコピー</button>
      </div>

      <nav class="pager" aria-label="記事の移動">
        {''.join(pager)}
      </nav>

      <h2>ほかの記事</h2>
      <div class="grid cols-2">
{cards_html}
      </div>
      <div class="btnrow">
        <a class="btn" href="/blog/">記事一覧に戻る</a>
      </div>
    </div>
    <!-- postnav:end -->
'''


def strip_generated(s):
    """前回の生成物を取り除く。何度実行しても同じ結果になるように。"""
    s = re.sub(r'    <!-- postnav:start -->.*?    <!-- postnav:end -->\n', '', s, flags=re.S)
    s = re.sub(r'    <nav class="toc" id="toc".*?</nav>\n\n', '', s, flags=re.S)
    s = re.sub(r'<script>\n\(function \(\) \{\n  var prose.*?</script>\n', '', s, flags=re.S)
    s = re.sub(r'    <h2>関連(?:ページ|する記事)</h2>\n    <div class="grid.*?</div>\n\n', '', s, flags=re.S)
    s = re.sub(r'\n *<div class="postmeta">.*?</div>', '', s, flags=re.S)
    s = s.replace('    <!-- postbody:start --><div class="postbody">\n', '')
    s = s.replace('    </div><!-- postbody:end -->\n', '')
    return s


def set_page_head(s, block):
    """page-head の末尾にある日付表示を、生成したメタ表示に差し替える。"""
    m = re.search(r'(    <div class="page-head">.*?)\n(\s*)</div>\n', s, re.S)
    if not m:
        return s
    h = m.group(1)
    h = re.sub(r'\n *<p class="updated">.*?</p>', '', h, flags=re.S)
    h = re.sub(r'\n *<div class="postmeta">.*?\n *</div>', '', h, flags=re.S)
    return s[:m.start()] + h + '\n' + block + '\n' + m.group(2) + '</div>\n' + s[m.end():]


def sync_jsonld_dates(s, date):
    """記事 head の JSON-LD は手書きなので、日付だけ POSTS を正とする。

    本文に表示される日付は POSTS から生成されるため、放っておくと
    構造化データ側だけが古い日付のまま残る。実際にそれで1〜3日のズレが出た。
    """
    n = 0
    for key in ('datePublished', 'dateModified'):
        s, k = re.subn(r'("%s": ")[\d-]+(")' % key, r'\g<1>%s\g<2>' % date, s)
        n += k
    assert n == 2, '%s: JSON-LD の日付が %d 箇所（2 のはず）' % (date, n)
    return s


def inject(i, p):
    path = 'blog/%s.html' % p['slug']
    s = strip_generated(open(path, encoding='utf-8').read())
    mins = reading_minutes(path)

    s = set_page_head(s, post_head(p, mins))
    s = sync_jsonld_dates(s, p['date'])

    toc = ('    <nav class="toc" id="toc" hidden aria-label="目次">\n'
           '      <p class="toctitle">目次</p>\n      <ol></ol>\n    </nav>\n\n')
    s = s.replace('    </div>\n\n', '    </div>\n\n' + toc, 1)
    # 本文をまとめて包む。広い画面で目次を右に置くための足場で、
    # 段落どうしのマージンは中で従来どおり相殺される。
    s = s.replace(toc, toc + '    <!-- postbody:start --><div class="postbody">\n', 1)

    tail = '\n  </div>\n</main>'
    s = s.replace(tail, '\n    </div><!-- postbody:end -->\n' + post_nav(i, p, mins)
                  + '  </div>\n' + POST_JS + '\n</main>', 1)
    open(path, 'w', encoding='utf-8', newline='').write(s)
    return mins


if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    mins = {}
    for i, post in enumerate(POSTS):
        mins[post['slug']] = inject(i, post)
        print('  記事を更新: blog/%s.html（約%d分）' % (post['slug'], mins[post['slug']]))
    page = build_index(mins)
    open('blog/index.html', 'w', encoding='utf-8', newline='').write(page)
    json.loads(re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', page, re.S).group(1))
    print('blog/index.html を生成:', len(page), 'chars,', len(POSTS), '記事,',
          len(all_tags()), 'タグ,', len(cat_counts()), 'カテゴリ')
