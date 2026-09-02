"""OGP 画像（1200x630）を生成する。サイトの配色・書体に合わせた自前生成。"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 630
BG      = (19, 23, 32)      # --bg dark
PANEL   = (27, 32, 40)      # --surface dark
INK     = (231, 233, 238)
MUTED   = (132, 140, 156)
ACCENT  = (255, 130, 68)
LINE    = (43, 50, 64)

F_DISPLAY = "C:/Windows/Fonts/bahnschrift.ttf"
F_JP_B    = "C:/Windows/Fonts/YuGothB.ttc"
F_JP_R    = "C:/Windows/Fonts/YuGothR.ttc"

def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()

def wrap(draw, text, fnt, maxw):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if draw.textlength(cur + ch, font=fnt) > maxw and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines

def card(path, eyebrow, title, sub, badge="mdf.works"):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    # subtle grid, echoing the tool's canvas stage
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(24, 29, 39))
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(24, 29, 39))

    # accent rule down the left
    d.rectangle([0, 0, 10, H], fill=ACCENT)

    pad = 86
    f_eye = font(F_DISPLAY, 30)
    f_ttl = font(F_JP_B, 66, 0)
    f_sub = font(F_JP_R, 30, 0)
    f_bdg = font(F_DISPLAY, 34)

    y = 96
    d.text((pad, y), eyebrow.upper(), font=f_eye, fill=ACCENT)
    y += 62

    for ln in wrap(d, title, f_ttl, W - pad * 2 - 40)[:3]:
        d.text((pad, y), ln, font=f_ttl, fill=INK)
        y += 84
    y += 18

    for ln in wrap(d, sub, f_sub, W - pad * 2 - 60)[:2]:
        d.text((pad, y), ln, font=f_sub, fill=MUTED)
        y += 44

    # footer badge: a redaction bar + the site name
    by = H - 96
    d.ellipse([pad, by - 6, pad + 40, by + 34], fill=ACCENT)
    d.rounded_rectangle([pad + 54, by + 2, pad + 250, by + 28], radius=13, fill=(58, 64, 78))
    d.text((pad + 272, by - 2), badge, font=f_bdg, fill=MUTED)

    im.save(path, optimize=True)
    print("wrote", path, os.path.getsize(path), "bytes")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "og")
os.makedirs(out, exist_ok=True)
o = lambda n: os.path.join(out, n)

card(o("home.png"), "web tools",
     "アップロード不要の\nウェブツール",
     "ファイルを預けずに使える無料ツールを公開しています")

card(o("kuroko.png"), "Kuroko",
     "スクショの名前と\nアイコンを隠す",
     "Discord 対応・無料・画像は端末から出ません")

card(o("guide.png"), "Guide",
     "Kuroko の使い方",
     "自動検出の調整から保存まで、画面に沿って解説します")

card(o("checklist.png"), "Checklist",
     "公開前チェックリスト\n12項目",
     "アイコンと名前を隠しただけでは残るもの")

card(o("mosaic.png"), "Column",
     "モザイクは\n復元できるのか",
     "文字に対して弱い理由と、安全な隠しかた")

card(o("about.png"), "About",
     "このサイトについて",
     "運営者情報と、作るときに決めていること")

card(o("capture.png"), "Basics",
     "必要な範囲だけを\n撮る",
     "Windows・Mac・iPhone・Android の範囲指定の撮り方")

card(o("blog.png"), "Blog",
     "スクリーンショットと\n個人情報のはなし",
     "撮る範囲、隠しかた、公開前の確認")

card(o("browser.png"), "Browser",
     "ブラウザの選び方",
     "Chrome・Firefox・Edge・Safari・Brave の違いと使い分け")

card(o("cache.png"), "Development",
     "HTMLは新しいのに\nCSSだけ古い",
     "静的サイトのキャッシュ設定でハマった話")

card(o("ping.png"), "Game",
     "Ping はどこで\n生まれるのか",
     "回線を速くしても下がらない理由と、実際に効く対策")

card(o("battery.png"), "Gadget",
     "mAh ではなく\nWh と W を見る",
     "モバイルバッテリーの選び方と、飛行機・PSE の話")

card(o("passkey.png"), "Security",
     "パスキーはなぜ\nフィッシングに強いのか",
     "SMS・認証アプリとの違いと、設定する順番")

card(o("imageformat.png"), "Basics",
     "スクショはPNG、\n写真はJPEG",
     "文字がにじむ理由と、WebP・AVIF の使い分け")

card(o("extension.png"), "Browser",
     "拡張機能は\n画面を読んでいる",
     "権限の意味と、自動更新という本当の危険")

card(o("circle.png"), "Development",
     "画像から円を\n検出する",
     "ハフ変換だけでは足りなかった、16分の1からの立て直し")

card(o("qr.png"), "Security",
     "QRコードは\n中身が見えない",
     "貼り替えという手口と、タップする前にできる確認")

card(o("exif.png"), "Privacy",
     "写真は撮った場所を\n覚えている",
     "Exif に入るものと、消しても残るもの")

card(o("koma.png"), "Koma",
     "連番PNGを\nアニメーションに",
     "背景を抜いて APNG・WebP へ／画像は端末から出ません")

card(o("cors.png"), "Browser",
     "ブラウザだけでは\n動画を保存できない",
     "要求は送れる。けれど中身が読めない")

card(o("wifi.png"), "Security",
     "公衆Wi-Fiは\n危険か",
     "HTTPSが片付けたことと、残っているもの")

card(o("theme.png"), "Development",
     "ダークモードは\n色を反転しない",
     "三段構えのCSSと、描画前のちらつき")

card(o("framerate.png"), "Game",
     "144Hzで\n何が変わるのか",
     "滑らかさと反応の速さは別物")
