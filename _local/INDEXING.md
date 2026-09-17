# インデックス未登録の調査（2026-09-17）

「検出 - インデックス未登録」はURLが発見されているものの、まだクロールされていない状態です。
「クロール済み - インデックス未登録」や AdSense の不承認理由とは別です。

## 公開サイトで確認したこと

- sitemap.xml の30 URLをGET確認。すべて200、自己参照canonical、noindexなし。
- robots.txt / sitemap.xml は200、robots.txtはクロールを許可。
- 記事本文と一覧へのリンクは静的HTMLに含まれ、JS実行なしで読める。
- トップから全公開ページへ2リンク以内で到達（404ページは除外）。
- 存在しないURLは404。GooglebotのUser-Agent文字列での代表記事への要求も200。
  ただしGoogleのIPからの実アクセスやWAFの通過を証明するテストではない。
- HTML拡張子付きの旧URLは拡張子なしへ307。正規URLと内部リンクは拡張子なしで統一。
- HTTP版が200でありHTTPSへの転送がない。Cloudflareの設定改善候補。
- wwwホストはDNS解決できない。サイト内ではwww無しを使用している。

ユーザー報告: 8月中旬の開設当初からトップ以外が未登録。例は /about、/blog、/blog/battery。
/blog は /blog/ に転送されるため、URL検査は正規URLの /blog/ でも行う。

## 今回のサイト側の改善

トップページに最新3記事への通常のHTMLリンクと概要を追加。
build_blog.pyで日々の公開時に自動更新し、記事数表示も実数へ同期。
実際に本文を変更したaboutのサイトマップ更新日を修正。
/blog などのディレクトリ入口は _redirects で正規の末尾スラッシュ付きURLへ301転送。
この改善だけでGoogleのクロールやインデックス登録を保証するものではない。

## Search Consoleで確認すること

1. 未登録URLの具体例を選び「URL検査」→「公開URLをテスト」。
2. ページ取得成功、クロール許可、インデックス許可を確認する。
3. sitemap.xml の送信状態が「成功しました」か確認する。
4. 「設定」→「クロールの統計情報」でホストの可用性と403/429/5xx等を確認する。
5. 取得可能な重要ページだけインデックス登録をリクエストする。同じURLの連打はしない。
6. CloudflareのSSL/TLS→エッジ証明書でAlways Use HTTPSを確認。
   セキュリティイベントでGoogleのアクセス拒否がある場合は、検証済みボットへの影響を確認する。
   根拠なしにWAF全体を無効化しない。

リクエスト後のクロールには数日〜数週間かかる場合があり、登録は保証されない。
URL検査結果・クロール統計・Cloudflareログをまだ確認していないため、根本原因は未確定。

参考:
- https://support.google.com/webmasters/answer/7440203?hl=ja
- https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
- https://developers.cloudflare.com/ssl/edge-certificates/additional-options/always-use-https/
