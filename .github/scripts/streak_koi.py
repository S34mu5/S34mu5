# Draws the streak card with the koi swimming freely around the README box:
# a random path (new every day), bending into its turns, surfacing now and
# then with ripples, and passing behind a frosted-glass card.
# Usage: python3 streak_koi.py streak.svg koi.gif out.svg
import base64, datetime, io, math, random, re, sys, warnings
import numpy as np
from PIL import Image, ImageSequence
warnings.simplefilter("ignore")

streak_path, gif_path, out_path = sys.argv[1:4]
W, H = 846, 195            # README content area width, card height
FW, FH = 120, 60           # koi size on screen
LOOP_S = 120               # seconds before the swim repeats
FPS = 25                   # path samples per second
SURFACES = 4               # times per loop the koi comes up for air
GLASS = 0.55               # card background opacity (frosted glass)
BLUR = 4                   # blur of the koi seen through the card
BUTTON = '#9198a1'         # colour of the 鯉 button (same as GitHub's pencil)
# outline of 鯉 (Noto Sans CJK JP, 1000-unit box) so it needs no font
KANJI = 'M370 726C392 765 416 818 424 853L474 833C463 799 440 747 416 708ZM280 734C301 788 319 860 323 907L374 895C369 848 350 777 328 723ZM193 735C204 794 209 869 205 919L259 910C261 862 255 786 243 728ZM107 726C99 805 79 885 34 931L84 961C134 910 151 824 161 739ZM308 190C294 226 276 264 258 293H153C171 259 187 225 200 190ZM178 40C156 134 110 256 36 349C52 357 76 377 89 392L99 379V680H444V293H326C352 251 377 201 396 155L353 126L340 130H223C232 103 240 76 247 50ZM492 94V539H673V653H495V720H673V870H441V938H962V870H746V720H930V653H746V539H929V94ZM159 515H241V618H159ZM295 515H381V618H295ZM159 355H241V456H159ZM295 355H381V456H295ZM558 346H677V473H558ZM742 346H861V473H742ZM558 159H677V285H558ZM742 159H861V285H742Z'
rng = random.Random(datetime.date.today().isoformat())

# ---------------------------------------------------------------- sprites
gif = Image.open(gif_path)
frames = [f.convert("RGBA") for f in ImageSequence.Iterator(gif)]
frame_ms = gif.info.get("duration", 70)
n = len(frames)
cs = []
for f in frames:
    ys, xs = np.nonzero(np.array(f)[:, :, 3] > 0)
    cs.append((xs.mean(), ys.mean()))
sw, sh = FW * 5 // 4, FH * 5 // 4
rot = []
for i, f in enumerate(frames):
    (x0, y0), (x1, y1) = cs[(i - 3) % n], cs[(i + 3) % n]
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    cx, cy = cs[i]
    r = f.rotate(ang, resample=Image.NEAREST, center=(cx, cy))
    rot.append(np.array(r.crop((int(cx) - 150, int(cy) - 75, int(cx) + 150, int(cy) + 75))))
# The source koi always swims in a clockwise circle, so its body is bent.
# Measure the average bend and shift columns to straighten it.
ys_idx = np.arange(150)[:, None]
lines = []
for a in rot:
    al = (a[:, :, 3] > 0).astype(float); w = al.sum(0)
    lines.append(np.where(w > 2, (al * ys_idx).sum(0) / np.maximum(w, 1), np.nan))
mean = np.nanmedian(np.array(lines), 0)
cols = np.arange(300); ok = ~np.isnan(mean)
bend = np.polyval(np.polyfit(cols[ok], mean[ok], 3), cols)
bend -= bend[ok].mean()
straight = []
for a in rot:
    b = np.zeros_like(a)
    for x in range(300):
        b[:, x] = np.roll(a[:, x], int(round(-bend[x])), axis=0)
    straight.append(b)

def sheet_b64(arrays):
    sheet = Image.new("RGBA", (sw * n, sh))
    for i, arr in enumerate(arrays):
        sheet.paste(Image.fromarray(arr).resize((sw, sh), Image.BOX), (sw * i, 0))
    buf = io.BytesIO()
    sheet.quantize(64, method=Image.Quantize.FASTOCTREE).save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

SPRITES = {"S": sheet_b64(straight),      # straight
           "R": sheet_b64(rot)}           # bending into a clockwise turn
# an anticlockwise turn is the clockwise one mirrored across the body axis
xs_vals = ";".join(str(-sw * i) for i in range(n))

# ---------------------------------------------------------------- card
card = open(streak_path, encoding="utf-8").read()
card = re.sub(r"<\?xml[^>]*\?>", "", card).strip()
m = re.search(r"viewBox='0 0 ([\d.]+) ([\d.]+)'", card)
cw, ch = float(m.group(1)), float(m.group(2))
cx0 = (W - cw) / 2
card = card.replace("<svg ", f"<svg x='{cx0}' y='0' ", 1)
rx = re.search(r"<rect width='[\d.]+' height='[\d.]+' rx='([\d.]+)'", card)
rx = rx.group(1) if rx else "5"
start = card.index("<g clip-path='url(#outer_rectangle)'>")
bg = card.index("<rect ", start)
card = card[:bg] + f"<rect fill-opacity='{GLASS}' " + card[bg + len("<rect "):]

# ---------------------------------------------------------------- swim
N = LOOP_S * FPS
dt = 1 / FPS
margin = 34
surf_at = []
while len(surf_at) < SURFACES:
    c = rng.randrange(int(N * 0.05), int(N * 0.88))
    if all(abs(c - s) > 15 * FPS for s in surf_at):
        surf_at.append(c)
surf_at.sort()
pending, surf_real = list(surf_at), []
pos = np.array([rng.uniform(margin, cx0 - 10), rng.uniform(margin, H - margin)])
head = rng.uniform(-math.pi, math.pi)
speed, target_speed = 45.0, 45.0
goal = None
P, A, SURF = [], [], []
for k in range(N):
    # pick a new place to wander to every few seconds
    if goal is None or np.linalg.norm(goal - pos) < 30 or rng.random() < 0.0016:
        if rng.random() < 0.5:   # half the time, head for one side of the card
            gx = rng.choice([rng.uniform(margin, cx0), rng.uniform(cx0 + cw, W - margin)])
        else:
            gx = rng.uniform(margin, W - margin)
        goal = np.array([gx, rng.uniform(margin, H - margin)])
        target_speed = rng.choice([25, 35, 45, 55, 75])
    # come up for air when there is room ahead (heading roughly sideways)
    if pending and k >= pending[0] and k < N - 12 * FPS and (not surf_real or k - surf_real[-1] > 12 * FPS) and 70 < pos[0] < W - 70 and 60 < pos[1] < H - 60 and abs(math.sin(head)) < 0.5 \
            and (pos[0] < cx0 - 20 or pos[0] > cx0 + cw + 20 or k - pending[0] > 10 * FPS):
        surf_real.append(k); pending.pop(0)
    surfacing = any(0 <= k - s < 3 * FPS for s in surf_real)
    want = math.atan2(goal[1] - pos[1], goal[0] - pos[0])
    # steer away from the edges
    for d, push in ((pos[0] - margin, 0.0), (W - margin - pos[0], math.pi),
                    (pos[1] - margin, math.pi / 2), (H - margin - pos[1], -math.pi / 2)):
        if d < 20:
            want = push
    if surfacing:
        want = head   # hold course while rising
    diff = (want - head + math.pi) % (2 * math.pi) - math.pi
    max_turn = math.radians(110) * dt
    head += max(-max_turn, min(max_turn, diff)) + rng.gauss(0, 0.01)
    ts = 5 if surfacing else target_speed
    speed += (ts - speed) * 0.035
    pos = pos + speed * dt * np.array([math.cos(head), math.sin(head)])
    pos = np.clip(pos, 8, [W - 8, H - 8])
    P.append(pos.copy()); A.append(head); SURF.append(surfacing)
P = np.array(P)
surf_at = surf_real
# close the loop smoothly: Hermite blend of the last seconds back to the start
K = 8 * FPS
p0, p1 = P[N - K], P[0]
v0 = (P[N - K] - P[N - K - 1]) * K
v1 = (P[1] - P[0]) * K
for j in range(K):
    t = j / K
    h00, h10, h01, h11 = 2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2
    P[N - K + j] = h00 * p0 + h10 * v0 + h01 * p1 + h11 * v1
    SURF[N - K + j] = False
# smooth the whole lap (it wraps around) so the motion is fluid
kern = np.exp(-0.5 * (np.arange(-12, 13) / 4.0) ** 2); kern /= kern.sum()
P = np.stack([np.convolve(np.r_[P[-12:, i], P[:, i], P[:12, i]], kern, mode="valid") for i in (0, 1)], 1)
P = np.clip(P, 8, [W - 8, H - 8])
# heading and turn rate from the final path
d = np.diff(np.vstack([P, P[:1]]), axis=0)
ang = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
turn = np.convolve(np.gradient(ang) * FPS, np.ones(9) / 9, mode="same")
state = []
cur = "S"
for tr in turn:
    if cur == "S" and abs(tr) > 0.9:
        cur = "R" if tr > 0 else "L"
    elif cur != "S" and abs(tr) < 0.5:
        cur = "S"
    state.append(cur)

def vis_anim(letter):
    vals, times, last = [], [], None
    for k, s in enumerate(state):
        v = "visible" if s == letter else "hidden"
        if v != last:
            vals.append(v); times.append(k / N); last = v
    return (f"<animate attributeName='visibility' values='{';'.join(vals)}' "
            f"keyTimes='{';'.join(f'{t:.5f}' for t in times)}' dur='{LOOP_S}s' "
            "calcMode='discrete' repeatCount='indefinite'/>")

def sheet(key):
    return (f"<svg id='koi_{key}' x='{-FW / 2}' y='{-FH / 2}' width='{FW}' height='{FH}' viewBox='0 0 {sw} {sh}'>"
            f"<image href='data:image/png;base64,{SPRITES[key]}' x='0' y='0' width='{sw * n}' height='{sh}'>"
            f"<animate attributeName='x' values='{xs_vals}' dur='{n * frame_ms / 1000}s' "
            "calcMode='discrete' repeatCount='indefinite'/></image></svg>")

def sprite(letter):
    key = "S" if letter == "S" else "R"
    flip = " transform='scale(1,-1)'" if letter == "L" else ""
    return f"<g>{vis_anim(letter)}<g{flip}><use href='#koi_{key}'/></g></g>"

motion = ";".join(f"{x:.2f},{y:.2f}" for x, y in np.vstack([P, P[:1]]))
# surfacing: the koi rises (grows a little) and its snout breaks the surface
scale_vals, scale_times = ["1"], ["0"]
ripples = []
for s in surf_at:
    a, b, c, e = s / N, (s + 0.8 * FPS) / N, (s + 2.2 * FPS) / N, (s + 3 * FPS) / N
    scale_vals += ["1", "1.15", "1.15", "1"]; scale_times += [f"{a:.5f}", f"{b:.5f}", f"{c:.5f}", f"{e:.5f}"]
    k = int(s + 1.2 * FPS)
    hx = P[k][0] + math.cos(ang[k]) * FW * 0.45
    hy = P[k][1] + math.sin(ang[k]) * FW * 0.45
    for delay in (0, 0.5, 1.0):
        t0 = (s + (1.2 + delay) * FPS) / N
        t1 = t0 + 1.8 / LOOP_S
        kt = f"0;{t0 - 0.0001:.5f};{t0:.5f};{t1:.5f};1"
        ripples.append(
            f"<ellipse cx='{hx:.1f}' cy='{hy:.1f}' rx='0' ry='0' fill='none' stroke='#e6edf3' stroke-width='2' opacity='0'>"
            f"<animate attributeName='rx' values='0;0;3;42;42' keyTimes='{kt}' dur='{LOOP_S}s' repeatCount='indefinite'/>"
            f"<animate attributeName='ry' values='0;0;2;28;28' keyTimes='{kt}' dur='{LOOP_S}s' repeatCount='indefinite'/>"
            f"<animate attributeName='opacity' values='0;0;0.85;0;0' keyTimes='{kt}' dur='{LOOP_S}s' repeatCount='indefinite'/>"
            "</ellipse>")
scale_vals.append("1"); scale_times.append("1")

svg = f"""<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>
<defs>
{sheet('S')}
{sheet('R')}
<filter id='koi_blur' x='-50%' y='-50%' width='200%' height='200%'><feGaussianBlur stdDeviation='{BLUR}'/></filter>
<clipPath id='koi_glass'><rect x='{cx0}' y='0' width='{cw}' height='{ch}' rx='{rx}'/></clipPath>
<mask id='koi_outside'><rect width='{W}' height='{H}' fill='white'/><rect x='{cx0}' y='0' width='{cw}' height='{ch}' rx='{rx}' fill='black'/></mask>
<g id='koi_scene'>
<g>
<animateMotion dur='{LOOP_S}s' repeatCount='indefinite' rotate='auto' calcMode='linear' values='{motion}'/>
<g><animateTransform attributeName='transform' type='scale' values='{';'.join(scale_vals)}' keyTimes='{';'.join(scale_times)}' dur='{LOOP_S}s' repeatCount='indefinite'/>
{sprite("S")}
{sprite("R")}
{sprite("L")}
</g>
</g>
</g>
<g id='koi_ripples'>{''.join(ripples)}</g>
<filter id='ripple_blur'><feGaussianBlur stdDeviation='1'/></filter>
</defs>
<g mask='url(#koi_outside)'><use href='#koi_scene'/><use href='#koi_ripples'/></g>
<g clip-path='url(#koi_glass)'><use href='#koi_scene' filter='url(#koi_blur)'/><use href='#koi_ripples' filter='url(#ripple_blur)'/></g>
{card}
<g transform='translate({W - 17},{H - 17}) scale(0.016)'><title>鯉 · cómo funciona este koi</title><path fill='{BUTTON}' d='{KANJI}'/></g>
</svg>"""
open(out_path, "w", encoding="utf-8").write(svg)
print(f"wrote {out_path} ({len(svg) // 1024} KB), surfaces at {[round(s / FPS) for s in surf_at]}s")
