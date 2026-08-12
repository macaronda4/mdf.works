# mdf.works — サイト一式

ブラウザの中だけで完結するウェブツールを公開する個人サイトです。
サーバー側の処理は一切ないので、静的ホスティングにそのまま置けます。

## 構成

```
index.html                  https://mdf.works/                     ポータル（メインページ）
about.html                  https://mdf.works/about.html           このサイトについて・運営者情報
privacy.html                https://mdf.works/privacy.html         プライバシーポリシー
terms.html                  https://mdf.works/terms.html           利用規約・免責事項
contact.html                https://mdf.works/contact.html         お問い合わせ
404.html                                                           404 ページ

kuroko/index.html           https://mdf.works/kuroko/              Kuroko 概要
kuroko/tool.html            https://mdf.works/kuroko/tool.html     匿名化ツール本体
kuroko/guide.html           https://mdf.works/kuroko/guide.html    使い方ガイド
kuroko/checklist.html       https://mdf.works/kuroko/checklist.html 公開前チェックリスト

assets/site.css             コンテンツページ共通のスタイル
robots.txt / sitemap.xml / ads.txt
dist/preview-site.html      確認用に全ページを1ファイルへまとめたもの（公開不要）
```

`kuroko/tool.html` はツール本体で、CSS も JavaScript も内包した1ファイルです。
外部ライブラリや CDN への依存はありません。

`input.png` / `result.png` / `except.png` は検出精度の検証に使ったテスト画像です。
**公開時はアップロードしないでください。**

---

## 公開前に必ず記入する箇所

ドメインはすべて `https://mdf.works` で設定済みです。残っているのは次の2つだけです。

| 項目 | 場所 | 件数 |
|---|---|---|
| 運営者名（ハンドルネーム可） | `about.html`、`privacy.html` | 2 |
| 連絡先メールアドレス | `contact.html`、`privacy.html` | 2 |

該当箇所はページ上で `要記入：…` とオレンジ色の枠で表示されます。残っていないかの確認:

```powershell
Select-String -Path *.html,kuroko\*.html -Pattern '要記入'
```

---

## ローカルで確認する

ディレクトリ形式のリンク（`kuroko/`）を使っているため、ファイルを直接開くとリンクが切れます。
簡易サーバーを立ててください。

```powershell
cd C:\claude-project\hide-info
python -m http.server 8000
```

ブラウザで <http://localhost:8000/> を開きます。

---

## 公開のしかた

サーバーサイド処理が無いので、静的ホスティングならどれでも動きます。

- **Cloudflare Pages** — フォルダをドラッグ＆ドロップ。独自ドメイン（mdf.works）と HTTPS を無料で設定できます
- **Netlify** — 同上
- **GitHub Pages** — リポジトリに push して Pages を有効化
- **レンタルサーバー** — FTP でフォルダごとアップロード

`mdf.works/kuroko` を機能させるには、ディレクトリの URL でその中の `index.html` を返す設定が必要です。
上記のサービスはいずれも既定でそう動作します。

HTTPS は必須です（AdSense の要件であり、クリップボード API の動作条件でもあります）。

---

## AdSense 申請の前に

1. **mdf.works で公開**し、全ページが表示されることを確認する
2. **`要記入` を4か所すべて差し替える**（残っていると印象が悪くなります）
3. **Google Search Console** に mdf.works を登録し、`sitemap.xml` を送信する
4. Google Analytics を**導入しない**場合は、`privacy.html` の第6項を削除する（記載と実態を一致させる）
5. インデックスされるまで数日待ってから申請する

プライバシーポリシー・利用規約・お問い合わせ・運営者情報へは、全ページのフッターから到達できます。
ツールページからもレール下部のリンクで到達できます。

審査通過後:

- AdSense 管理画面に表示される1行を `ads.txt` に貼り付ける
- 広告コードは `</head>` の直前、または広告を出したい位置に貼る
- ツール本体（`kuroko/tool.html`）は全画面レイアウトなので、広告はコンテンツページ側を推奨します

---

## 注意している点

- **利用者のファイルは送信していません。** ツールは `<canvas>` のみで処理しており、外部に送るコードを持ちません。この点はプライバシーポリシーにも明記しているので、**広告や解析タグを追加する際も、ファイルの内容を送る実装は入れないでください。** 記載と実装が食い違うと、AdSense のポリシー上も問題になります。
- **自動検出は完全ではありません。** 免責事項に明記したうえで、UI 上でも「公開前に確認してください」と案内しています。この案内は消さないでください。
