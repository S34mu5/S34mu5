# Draws the streak card with the koi swimming laps around the README box,
# passing behind the card. Usage: python3 streak_koi.py streak.svg koi.gif out.svg
import base64, io, math, re, sys
import numpy as np
from PIL import Image, ImageSequence

streak_path, gif_path, out_path = sys.argv[1:4]
W, H = 718, 195            # README content area width, card height
FW, FH = 120, 60           # koi size on screen
TILT = -12                 # straighten the koi's body axis
LOOP_S = 22                # seconds per lap
GLASS = 0.55               # card background opacity (frosted glass)
BLUR = 4                   # blur of the koi seen through the card

# 1) Koi frames, rotated so the koi always faces right.
gif = Image.open(gif_path)
frames = [f.convert("RGBA") for f in ImageSequence.Iterator(gif)]
frame_ms = gif.info.get("duration", 70)
n = len(frames)
cs = []
for f in frames:
    ys, xs = np.nonzero(np.array(f)[:, :, 3] > 0)
    cs.append((xs.mean(), ys.mean()))
sw, sh = FW * 5 // 4, FH * 5 // 4          # stored a bit larger than shown
sheet = Image.new("RGBA", (sw * n, sh))
for i, f in enumerate(frames):
    (x0, y0), (x1, y1) = cs[(i - 3) % n], cs[(i + 3) % n]
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) + TILT
    cx, cy = cs[i]
    r = f.rotate(ang, resample=Image.NEAREST, center=(cx, cy))
    r = r.crop((int(cx) - 150, int(cy) - 75, int(cx) + 150, int(cy) + 75))
    sheet.paste(r.resize((sw, sh), Image.BOX), (sw * i, 0))
buf = io.BytesIO(); sheet.quantize(64, method=Image.Quantize.FASTOCTREE).save(buf, "PNG", optimize=True)
sheet64 = base64.b64encode(buf.getvalue()).decode()
xs_vals = ";".join(str(-sw * i) for i in range(n))

# 2) Streak card, centred.
card = open(streak_path, encoding="utf-8").read()
card = re.sub(r"<\?xml[^>]*\?>", "", card).strip()
m = re.search(r"viewBox='0 0 ([\d.]+) ([\d.]+)'", card)
cw, ch = float(m.group(1)), float(m.group(2))
cx0 = (W - cw) / 2
card = card.replace("<svg ", f"<svg x='{cx0}' y='0' ", 1)
rx = re.search(r"<rect width='[\d.]+' height='[\d.]+' rx='([\d.]+)'", card)
rx = rx.group(1) if rx else "5"
# Frosted glass: make the card background see-through (same colour).
start = card.index("<g clip-path='url(#outer_rectangle)'>")
bg = card.index("<rect ", start)
card = card[:bg] + f"<rect fill-opacity='{GLASS}' " + card[bg + len("<rect "):]

# 3) Lap around the README box (clockwise), passing behind the card.
top, bot = 55, H - 55
rad = (bot - top) / 2
xl, xr = 12 + FW / 2 + rad - 30, W - 12 - FW / 2 - rad + 30
path = (f"M{xl},{top} L{xr},{top} A{rad},{rad} 0 0 1 {xr},{bot} "
        f"L{xl},{bot} A{rad},{rad} 0 0 1 {xl},{top} Z")

svg = f"""<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>
<defs>
<filter id='koi_blur' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='{BLUR}'/></filter>
<clipPath id='koi_glass'><rect x='{cx0}' y='0' width='{cw}' height='{ch}' rx='{rx}'/></clipPath>
<mask id='koi_outside'><rect width='{W}' height='{H}' fill='white'/><rect x='{cx0}' y='0' width='{cw}' height='{ch}' rx='{rx}' fill='black'/></mask>
</defs>
<g mask='url(#koi_outside)'><use href='#koi'/></g>
<g clip-path='url(#koi_glass)'><use href='#koi' filter='url(#koi_blur)'/></g>
<defs><g id='koi'>
<animateMotion dur='{LOOP_S}s' repeatCount='indefinite' rotate='auto' path='{path}'/>
<svg x='{-FW / 2}' y='{-FH / 2}' width='{FW}' height='{FH}' viewBox='0 0 {sw} {sh}'>
<image href='data:image/png;base64,{sheet64}' x='0' y='0' width='{sw * n}' height='{sh}'>
<animate attributeName='x' values='{xs_vals}' dur='{n * frame_ms / 1000}s' calcMode='discrete' repeatCount='indefinite'/>
</image>
</svg>
</g></defs>
{card}
</svg>"""
open(out_path, "w", encoding="utf-8").write(svg)
print(f"wrote {out_path} ({len(svg) // 1024} KB)")
