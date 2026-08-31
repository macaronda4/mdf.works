# 公開手順（GitHub → Cloudflare Pages → mdf.works）

ローカルのコミットまでは完了しています。残りはアカウント認証が必要なため、
以下をご自身で実行してください。所要 10 分ほどです。

現在の状態:

```
コミット済み  6377c08  Add mdf.works static site with the Kuroko screenshot anonymiser
ブランチ      main
除外設定      _local/（テスト画像）、dist/（プレビュー）、*.png
```

---

## 1. GitHub にリポジトリを作る

<https://github.com/new> を開き、次のとおり作成します。**README や .gitignore は追加しないでください**
（すでにローカルにあるため衝突します）。

| 項目 | 値 |
|---|---|
| Repository name | `mdf.works` |
| Description | ブラウザの中だけで完結するウェブツール |
| 公開設定 | Public / Private どちらでも可（Cloudflare Pages は両方に対応） |
| Add a README file | **チェックしない** |
| Add .gitignore | **None** |
| Choose a license | 任意 |

## 2. プッシュする

Claude Code のプロンプトで、先頭に `!` を付けて実行してください。
`YOUR_NAME` はご自身の GitHub ユーザー名に置き換えます。

```
! cd C:\claude-project\hide-info && git remote add origin https://github.com/YOUR_NAME/mdf.works.git && git push -u origin main
```

初回はブラウザが開いて GitHub のログインを求められます（Git Credential Manager）。
許可すれば以後は自動です。

うまくいかない場合は、リモートを設定し直してから再実行します。

```
! cd C:\claude-project\hide-info && git remote set-url origin https://github.com/YOUR_NAME/mdf.works.git && git push -u origin main
```

---

## 3. Cloudflare Pages につなぐ

1. <https://dash.cloudflare.com/> にログイン
2. 左メニューの **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. GitHub と連携し、`mdf.works` リポジトリを選択
4. ビルド設定は**すべて空のまま**にします（静的サイトなのでビルド不要）

   | 項目 | 値 |
   |---|---|
   | Framework preset | None |
   | Build command | （空欄） |
   | Build output directory | `/` |
   | Root directory | （空欄） |

5. **Save and Deploy**

1〜2 分で `https://<プロジェクト名>.pages.dev` が発行され、そこで全ページが見られます。
以後は `git push` するたびに自動で反映されます。

---

## 4. 独自ドメイン mdf.works をつなぐ

### mdf.works を Cloudflare で管理している場合

1. Pages プロジェクト → **Custom domains** → **Set up a domain**
2. `mdf.works` を入力 → **Continue** → **Activate domain**
3. DNS レコードは自動で作成されます

`www.mdf.works` も使いたい場合は、同じ手順でもう一度追加してください。

### 他社（お名前.com など）で管理している場合

先にドメインを Cloudflare へ移管するか、ネームサーバーを Cloudflare に向けます。

1. Cloudflare ダッシュボード → **Add a site** → `mdf.works`
2. 表示された 2 つのネームサーバーを、ドメイン取得元の管理画面で設定
3. 反映後（数分〜数時間）、上記の Custom domains の手順を実行

HTTPS 証明書は Cloudflare が自動で発行します。

---

## 5. 公開後の確認

```
https://mdf.works/                      ポータル
https://mdf.works/kuroko/               Kuroko 概要
https://mdf.works/kuroko/tool.html      ツール本体
https://mdf.works/kuroko/guide.html     使い方
https://mdf.works/kuroko/checklist.html チェックリスト
https://mdf.works/about.html            このサイトについて
https://mdf.works/privacy.html          プライバシーポリシー
https://mdf.works/terms.html            利用規約
https://mdf.works/contact.html          お問い合わせ
https://mdf.works/sitemap.xml           サイトマップ
```

とくに確認したい点:

- `mdf.works/kuroko` が（末尾スラッシュなしでも）概要ページに繋がるか
- ツールで画像を読み込み、書き出しまでできるか
- `mdf.works/_local/input.png` が **404 になること**（テスト画像が公開されていないこと）

---

## 6. AdSense を申請する

1. Google Search Console に `mdf.works` を登録し、`sitemap.xml` を送信
2. インデックスされるまで数日待つ
3. AdSense に申請
4. 通過後、管理画面に出る 1 行を `ads.txt` に貼り付けて push
5. 広告コードを貼る（コンテンツページ推奨。ツール本体は全画面レイアウトのため）

Google Analytics を導入しない場合は、`privacy.html` の第 6 項を削除してください。

---

## 更新のしかた

ファイルを編集して、以下を実行するだけです。Cloudflare Pages が自動で再デプロイします。

```
! cd C:\claude-project\hide-info && git add -A && git commit -m "変更内容" && git push
```
