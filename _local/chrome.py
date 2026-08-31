"""全ページ共通の仕上げ:
  - テーマ切替ボタンと、描画前にテーマを適用する head スクリプト
  - インライン SVG に width/height を付与（CSS 読込前でも暴れないように）
  - サイト CSS をページに直接埋め込む（描画をブロックする往復を1つ減らす）
  - 解析タグは本体の読み込みを後回しにし、広告の接続だけ先に張る
"""
import glob, os, re

GA_ID = 'G-5GDKSW8H7X'
ADS_CLIENT = 'ca-pub-8613999974980382'

PRECONNECT = (
    '<link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin>\n'
    '<link rel="preconnect" href="https://www.googletagmanager.com">\n'
    '<link rel="dns-prefetch" href="https://googleads.g.doubleclick.net">'
)

THEME_HEAD = ('<script>(function(){try{var t=localStorage.getItem("theme");'
              'if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t);}'
              'catch(e){}})();</script>')

# 計測値は即座に dataLayer へ積み、165KB のライブラリ本体は主スレッドが空いてから取りに行く。
GA_SNIPPET = '''<!-- Google tag (gtag.js) -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '%s');
  (function () {
    var loaded = false;
    function load() {
      if (loaded) return;
      loaded = true;
      var s = document.createElement('script');
      s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=%s';
      document.head.appendChild(s);
    }
    if (window.requestIdleCallback) requestIdleCallback(load, { timeout: 2500 });
    else setTimeout(load, 1500);
  })();
</script>''' % (GA_ID, GA_ID)

# 広告タグは各ファイルの手書きに任せていたため、あとから足したページで抜けていた。
# ここで一括して配り、抜けが起きないようにする。帯域の優先度は下げておく。
ADS_SNIPPET = ('<!-- Google AdSense -->\n'
               '<script async fetchpriority="low" '
               'src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
               '?client=%s"\n     crossorigin="anonymous"></script>' % ADS_CLIENT)

THEME_BTN = '''    <button class="themebtn" type="button" id="themebtn" aria-label="表示テーマを切り替える" title="表示テーマを切り替える">
      <svg class="i-sun" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>
      <svg class="i-moon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M20 14.4A8.6 8.6 0 1 1 9.6 4a6.9 6.9 0 0 0 10.4 10.4z"/></svg>
    </button>
'''

THEME_JS = '''<script>
(function () {
  var b = document.getElementById('themebtn');
  if (!b) return;
  var meta = document.querySelector('meta[name="theme-color"]');
  function paint(t) {
    if (meta) meta.setAttribute('content', t === 'dark' ? '#131720' : '#EEEFF2');
  }
  var set = document.documentElement.getAttribute('data-theme');
  paint(set || (window.matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light'));
  b.addEventListener('click', function () {
    var cur = document.documentElement.getAttribute('data-theme');
    if (!cur) cur = window.matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light';
    var next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    paint(next);
    try { localStorage.setItem('theme', next); } catch (e) {}
  });
})();
</script>'''


def minify_css(css):
    """コメントと無駄な空白だけ落とす。元ファイルは読みやすいまま残す。"""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out = []
    for line in css.split('\n'):
        line = line.strip()
        if line:
            out.append(line)
    return '\n'.join(out)


def pages():
    return sorted(glob.glob('*.html') + glob.glob('kuroko/*.html')
                  + glob.glob('koma/*.html') + glob.glob('blog/*.html'))


def keep_ads_priority(s):
    """AdSense は残すが、帯域の優先度だけ下げる（実行順は変えない）。"""
    if 'adsbygoogle.js' in s and 'fetchpriority' not in s:
        s = s.replace('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js',
                      '<script async fetchpriority="low" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js')
    return s


def strip_old(s):
    s = s.replace(THEME_HEAD + '\n', '')
    s = re.sub(r'    <button class="themebtn".*?</button>\n', '', s, flags=re.S)
    s = re.sub(r'<script>\n\(function \(\) \{\n  var b = document\.getElementById\(.themebtn.\).*?</script>\n',
               '', s, flags=re.S)
    s = re.sub(r'<link rel="preconnect"[^>]*>\n', '', s)
    s = re.sub(r'<link rel="dns-prefetch"[^>]*>\n', '', s)
    s = re.sub(r'<!-- Google tag \(gtag\.js\) -->\n(<script[^>]*>.*?</script>\n)+', '', s, flags=re.S)
    s = re.sub(r'<!-- Google AdSense -->\n<script [^>]*adsbygoogle\.js.*?</script>\n', '', s, flags=re.S)
    s = re.sub(r'<!-- site css -->\n<style>.*?</style>\n', '', s, flags=re.S)
    s = re.sub(r'<link rel="stylesheet" href="/assets/site\.css[^"]*">\n?', '', s)
    return s


def size_svgs(s):
    def sub(m):
        tag = m.group(0)
        if ' width=' in tag or ' height=' in tag:
            return tag
        return tag.replace('<svg ', '<svg width="24" height="24" ', 1)
    return re.sub(r'<svg [^>]*viewBox="0 0 24 24"[^>]*>', sub, s)


if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    css = minify_css(open('assets/site.css', encoding='utf-8').read())
    style = '<!-- site css -->\n<style>' + css + '</style>'
    print('CSS 埋め込み: %d → %d bytes（コメント除去後）' % (
        os.path.getsize('assets/site.css'), len(css.encode('utf-8'))))

    n = 0
    n_ads = 0
    for p in pages():
        s = open(p, encoding='utf-8').read()
        # ツール本体は全画面レイアウトで、CSS もテーマ切替も自前で持っている
        tool = p.replace('\\', '/').endswith('/tool.html')
        # 広告は読み物のページにだけ置く。全画面のツールと 404 には出さない。
        ads = not tool and p.replace('\\', '/') != '404.html'
        s = strip_old(s)

        m = re.search(r'<meta name="viewport"[^>]*>', s)
        assert m, p
        vp = m.group(0)
        if tool and 'viewport-fit' not in vp:
            # ツールは全画面レイアウトなので、ノッチのある端末に合わせる
            vp = '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        head = vp + '\n' + PRECONNECT + '\n' + GA_SNIPPET
        if not tool:
            head += '\n' + THEME_HEAD
        if ads:
            head += '\n' + ADS_SNIPPET
            n_ads += 1
        s = s[:m.start()] + head + s[m.end():]

        if not tool:
            s = s.replace('    </nav>\n  </div>\n</header>',
                          '    </nav>\n' + THEME_BTN + '  </div>\n</header>', 1)
            s = s.replace('</footer>\n</body>', '</footer>\n' + THEME_JS + '\n</body>', 1)
            s = s.replace('</head>', style + '\n</head>', 1)
            n += 1
        s = size_svgs(s)
        s = keep_ads_priority(s)
        open(p, 'w', encoding='utf-8', newline='').write(s)

    print('テーマ切替と CSS 埋め込み:', n, 'ページ（ツールは自前のCSS/テーマを保持）')
    print('広告タグを配置:', n_ads, 'ページ（ツール本体と 404 は対象外）')
