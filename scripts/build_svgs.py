"""Generate the profile SVGs (header, project cards, footer).

Everything is drawn with a small built-in stroke alphabet, so the images
need no web fonts and render the same on every GitHub client.

    python scripts/build_svgs.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

BLUE = "#1E3BFF"
BLUE_DEEP = "#1428C8"
INK = "#F4EEDC"  # cream
INK_DIM = "#AFC0FF"
OUT = Path(__file__).resolve().parent.parent / "assets"


# --------------------------------------------------------------------------
# Stroke alphabet: glyphs are polylines with optional corner radii.
# (points, radii, closed). Coordinates use w (width), h (height).
# --------------------------------------------------------------------------
def _g(w: float, h: float, ch: str):
    R = w / 2
    m = h / 2
    L = []

    def P(pts, radii=None, closed=False):
        L.append((pts, radii or [0] * len(pts), closed))

    def dot(x, y, s):
        L.append(("dot", x, y, s))

    if ch in "OÖ0":
        P([(0, 0), (w, 0), (w, h), (0, h)], [R] * 4, True)
        if ch == "0":
            P([(w * 0.8, h * 0.2), (w * 0.2, h * 0.8)])
    elif ch == "Q":
        P([(0, 0), (w, 0), (w, h), (0, h)], [R] * 4, True)
        P([(w * 0.55, h * 0.78), (w * 1.05, h * 1.05)])
    elif ch in "CÇ":
        P([(w, 0), (0, 0), (0, h), (w, h)], [0, R, R, 0])
        if ch == "Ç":
            P([(w * 0.5, h), (w * 0.5, h * 1.12), (w * 0.3, h * 1.2)])
    elif ch == "G":
        P([(w, 0), (0, 0), (0, h), (w, h), (w, m * 1.1), (w * 0.45, m * 1.1)], [0, R, R, 0, 0, 0])
    elif ch == "D":
        P([(0, 0), (w, 0), (w, h), (0, h)], [0, R, R, 0], True)
    elif ch == "B":
        P([(0, 0), (w * 0.88, 0), (w * 0.88, m), (0, m)], [0, R * 0.88, R * 0.88, 0], True)
        P([(0, m), (w, m), (w, h), (0, h)], [0, R, R, 0], True)
    elif ch == "E":
        P([(w, 0), (0, 0), (0, h), (w, h)])
        P([(0, m), (w * 0.8, m)])
    elif ch == "F":
        P([(w, 0), (0, 0), (0, h)])
        P([(0, m), (w * 0.8, m)])
    elif ch == "H":
        P([(0, 0), (0, h)]); P([(w, 0), (w, h)]); P([(0, m), (w, m)])
    elif ch in "Iİ":
        P([(0, 0), (0, h)])
        if ch == "İ":
            dot(0, -h * 0.16, h * 0.06)
    elif ch == "J":
        P([(w, 0), (w, h), (0, h), (0, h * 0.68)], [0, R, R, 0])
    elif ch == "K":
        P([(0, 0), (0, h)]); P([(w, 0), (0, h * 0.62)]); P([(w * 0.32, h * 0.42), (w, h)])
    elif ch == "L":
        P([(0, 0), (0, h), (w, h)])
    elif ch == "M":
        P([(0, h), (0, 0), (w / 2, h * 0.62), (w, 0), (w, h)])
    elif ch == "N":
        P([(0, h), (0, 0), (w, h), (w, 0)])
    elif ch == "P":
        P([(0, h), (0, 0), (w, 0), (w, m), (0, m)], [0, 0, R, R, 0])
    elif ch == "R":
        P([(0, h), (0, 0), (w, 0), (w, m), (0, m)], [0, 0, R, R, 0])
        P([(w * 0.45, m), (w, h)])
    elif ch in "SŞ":
        P([(w, 0), (0, 0), (0, m), (w, m), (w, h), (0, h)], [0, R, R, R, R, 0])
        if ch == "Ş":
            P([(w * 0.5, h), (w * 0.5, h * 1.12), (w * 0.3, h * 1.2)])
    elif ch == "T":
        P([(0, 0), (w, 0)]); P([(w / 2, 0), (w / 2, h)])
    elif ch in "UÜ":
        P([(0, 0), (0, h), (w, h), (w, 0)], [0, R, R, 0])
    elif ch == "V":
        P([(0, 0), (w / 2, h), (w, 0)])
    elif ch == "W":
        P([(0, 0), (w * 0.25, h), (w / 2, h * 0.35), (w * 0.75, h), (w, 0)])
    elif ch == "X":
        P([(0, 0), (w, h)]); P([(w, 0), (0, h)])
    elif ch == "Y":
        P([(0, 0), (w / 2, m), (w, 0)]); P([(w / 2, m), (w / 2, h)])
    elif ch == "Z":
        P([(0, 0), (w, 0), (0, h), (w, h)])
    elif ch == "A":
        P([(0, h), (w * 0.38, 0), (w * 0.62, 0), (w, h)])
        P([(w * 0.17, h * 0.62), (w * 0.83, h * 0.62)])
    elif ch == "1":
        P([(0, h * 0.18), (w * 0.6, 0), (w * 0.6, h)])
    elif ch == "2":
        P([(0, 0), (w, 0), (w, h * 0.42), (0, h), (w, h)], [0, R, 0, 0, 0])
    elif ch == "3":
        P([(0, 0), (w, 0), (w, h), (0, h)], [0, R, R, 0]); P([(w * 0.3, m), (w, m)])
    elif ch == "4":
        P([(w * 0.75, h), (w * 0.75, 0), (0, h * 0.68), (w, h * 0.68)])
    elif ch == "5":
        P([(w, 0), (0, 0), (0, m * 0.95), (w, m * 0.95), (w, h), (0, h)], [0, 0, 0, R, R, 0])
    elif ch == "6":
        P([(w, 0), (0, 0), (0, h), (w, h), (w, m), (0, m)], [0, R, R, R, R, 0])
    elif ch == "7":
        P([(0, 0), (w, 0), (w * 0.3, h)])
    elif ch == "8":
        P([(w * 0.06, 0), (w * 0.94, 0), (w * 0.94, m), (w * 0.06, m)], [R * 0.88] * 4, True)
        P([(0, m), (w, m), (w, h), (0, h)], [R] * 4, True)
    elif ch == "9":
        P([(0, h), (w, h), (w, 0), (0, 0), (0, m), (w, m)], [0, R, R, R, R, 0])
    elif ch == "-":
        P([(0, m), (w, m)])
    elif ch == "—":
        P([(0, m), (w, m)])
    elif ch == "/":
        P([(w, 0), (0, h)])
    elif ch == "+":
        P([(0, m), (w, m)]); P([(w / 2, m - w / 2), (w / 2, m + w / 2)])
    elif ch == "→":
        P([(0, m), (w, m)]); P([(w * 0.6, m - w * 0.35), (w, m), (w * 0.6, m + w * 0.35)])
    elif ch == "(":
        P([(w, 0), (0, 0), (0, h), (w, h)], [0, w, w, 0])
    elif ch == ")":
        P([(0, 0), (w, 0), (w, h), (0, h)], [0, w, w, 0])
    elif ch == "#":
        P([(w * 0.3, 0), (w * 0.3, h)]); P([(w * 0.7, 0), (w * 0.7, h)])
        P([(0, h * 0.35), (w, h * 0.35)]); P([(0, h * 0.65), (w, h * 0.65)])
    elif ch == "%":
        P([(w, 0), (0, h)]); dot(w * 0.1, h * 0.12, h * 0.07); dot(w * 0.9, h * 0.88, h * 0.07)
    elif ch == ".":
        dot(0, h * 0.94, h * 0.06)
    elif ch == ",":
        P([(0, h * 0.9), (0, h * 1.1)])
    elif ch == ":":
        dot(0, h * 0.3, h * 0.06); dot(0, h * 0.9, h * 0.06)
    elif ch == "·":
        dot(0, m, h * 0.07)
    elif ch == "×":
        P([(0, m - w / 2), (w, m + w / 2)]); P([(w, m - w / 2), (0, m + w / 2)])
    elif ch == "'":
        P([(0, 0), (0, h * 0.25)])
    if ch in "ÖÜ":
        dot(w * 0.25, -h * 0.16, h * 0.06)
        dot(w * 0.75, -h * 0.16, h * 0.06)
    return L


WIDTH = {"I": 0, "İ": 0, "M": 1.35, "W": 1.45, ".": 0, ":": 0, "·": 0, ",": 0,
         "'": 0, " ": 0.75, "1": 0.7, "-": 0.6, "/": 0.6, "(": 0.3, ")": 0.3,
         "+": 0.8, "×": 0.7, "—": 1.4, "→": 1.2, "#": 0.9}


def text(s: str, x: float, y: float, h: float, w: float, track: float,
         sw: float, color: str = INK, anchor: str = "start") -> tuple[str, float]:
    """Return (svg, advance). y is the top of the caps."""
    adv = text_width(s, w, track, sw)
    if anchor == "end":
        x -= adv
    elif anchor == "middle":
        x -= adv / 2
    paths, dots = [], []
    cx = x
    for ch in s.upper():
        gw = w * WIDTH.get(ch, 1.0)
        if ch != " ":
            for item in _g(gw, h, ch):
                if item[0] == "dot":
                    _, dx, dy, ds = item
                    s2 = max(ds, sw * 1.15)
                    dots.append(f'<rect x="{cx+dx-s2/2:.2f}" y="{y+dy-s2/2:.2f}" width="{s2:.2f}" height="{s2:.2f}"/>')
                else:
                    pts, radii, closed = item
                    paths.append(_path([(cx + px, y + py) for px, py in pts], radii, closed))
        cx += gw + track
    body = ""
    if paths:
        body += (f'<path d="{" ".join(paths)}" fill="none" stroke="{color}" stroke-width="{sw}" '
                 f'stroke-linecap="square" stroke-linejoin="miter"/>')
    if dots:
        body += f'<g fill="{color}">{"".join(dots)}</g>'
    return body, adv


def text_width(s: str, w: float, track: float, sw: float = 0) -> float:
    return sum(w * WIDTH.get(c, 1.0) + track for c in s.upper()) - track


def _path(pts, radii, closed) -> str:
    n = len(pts)

    def fil(i):
        p = pts[i]
        r = radii[i]
        if r <= 0 or (not closed and (i == 0 or i == n - 1)):
            return None
        a, b = pts[i - 1], pts[(i + 1) % n]
        ua = (a[0] - p[0], a[1] - p[1]); la = math.hypot(*ua)
        ub = (b[0] - p[0], b[1] - p[1]); lb = math.hypot(*ub)
        t = min(r, la / 2 if closed or i - 1 > 0 else la, lb / 2 if closed or i + 1 < n - 1 else lb)
        t = min(r, la, lb) if t <= 0 else t
        p1 = (p[0] + ua[0] / la * t, p[1] + ua[1] / la * t)
        p2 = (p[0] + ub[0] / lb * t, p[1] + ub[1] / lb * t)
        # cubic approximating a quarter circle
        k = 0.5523
        c1 = (p1[0] + (p[0] - p1[0]) * k, p1[1] + (p[1] - p1[1]) * k)
        c2 = (p2[0] + (p[0] - p2[0]) * k, p2[1] + (p[1] - p2[1]) * k)
        return p1, c1, c2, p2

    out = []
    for i in range(n):
        f = fil(i)
        if f is None:
            cmd = "M" if i == 0 else "L"
            out.append(f"{cmd}{pts[i][0]:.2f} {pts[i][1]:.2f}")
        else:
            p1, c1, c2, p2 = f
            cmd = "M" if i == 0 else "L"
            out.append(f"{cmd}{p1[0]:.2f} {p1[1]:.2f} C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}")
    if closed:
        out.append("Z")
    return " ".join(out)


# --------------------------------------------------------------------------
# Engraving helpers
# --------------------------------------------------------------------------
def engraved_sphere(cx, cy, r, spacing=4.2, light=(-0.55, -0.6, 0.58), seed=3) -> str:
    """Horizontal hatch lines whose weight follows Lambert shading."""
    lx, ly, lz = light
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / ln, ly / ln, lz / ln
    rnd = random.Random(seed)
    segs = []
    y = cy - r + spacing / 2
    while y < cy + r:
        dy = (y - cy) / r
        half = math.sqrt(max(0.0, 1 - dy * dy)) * r
        steps = max(4, int(half * 2 / 7))
        x0 = cx - half
        for k in range(steps):
            xa = x0 + (2 * half) * k / steps
            xb = x0 + (2 * half) * (k + 1) / steps
            xm = (xa + xb) / 2
            nx = (xm - cx) / r
            nz = math.sqrt(max(0.0, 1 - nx * nx - dy * dy))
            lam = max(0.0, nx * lx + dy * ly + nz * lz)
            wgt = 0.25 + (1 - lam) ** 1.6 * 2.4
            if lam > 0.93:
                continue  # specular gap
            jitter = rnd.uniform(-0.15, 0.15)
            segs.append((wgt, f"M{xa:.1f} {y + jitter:.1f}H{xb + 0.6:.1f}"))
        y += spacing
    # bucket by weight to keep the file small
    buckets: dict[float, list[str]] = {}
    for wgt, d in segs:
        buckets.setdefault(round(wgt * 4) / 4, []).append(d)
    return "".join(
        f'<path d="{"".join(ds)}" stroke="{INK}" stroke-width="{w}" fill="none"/>'
        for w, ds in sorted(buckets.items()) if w > 0)


def rays(cx, cy, r0, r1, n, sw=1, color=INK, opacity=1.0, skip=None, dash=None) -> str:
    d = []
    for i in range(n):
        a = 2 * math.pi * i / n
        if skip and skip(a):
            continue
        d.append(f"M{cx + math.cos(a) * r0:.1f} {cy + math.sin(a) * r0:.1f}L{cx + math.cos(a) * r1:.1f} {cy + math.sin(a) * r1:.1f}")
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{"".join(d)}" stroke="{color}" stroke-width="{sw}" opacity="{opacity}"{da} fill="none"/>'


def grain(id_: str, opacity=0.11) -> tuple[str, str]:
    defs = (f'<filter id="{id_}" x="0" y="0" width="100%" height="100%">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="7" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.4 -0.55"/>'
            '</filter>')
    use = f'<rect width="100%" height="100%" filter="url(#{id_})" opacity="{opacity}"/>'
    return defs, use


def svg(w, h, title, desc, body, defs="") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="t d"><title id="t">{title}</title><desc id="d">{desc}</desc>'
            f'<defs>{defs}</defs>{body}</svg>\n')


def frame(w, h, inset=14, sw=1.2) -> str:
    """Thin cream frame with corner ticks."""
    t = 10
    b = f'<rect x="{inset}" y="{inset}" width="{w - 2 * inset}" height="{h - 2 * inset}" fill="none" stroke="{INK}" stroke-width="{sw}" opacity="0.55"/>'
    for x, y, sx, sy in [(inset, inset, 1, 1), (w - inset, inset, -1, 1), (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)]:
        b += f'<path d="M{x} {y + sy * t * 2}V{y}H{x + sx * t * 2}" stroke="{INK}" stroke-width="{sw * 2.2}" fill="none"/>'
    return b


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
ANIM_CSS = (
    "<style>"
    ".w{stroke-dasharray:1 1;stroke-dashoffset:1;animation:draw 2.4s cubic-bezier(.65,0,.25,1) forwards}"
    ".w2{animation-delay:.7s}.w3{animation-delay:1.4s}"
    "@keyframes draw{to{stroke-dashoffset:0}}"
    ".fade{opacity:0;animation:fade .8s 3.6s forwards}"
    "@keyframes fade{to{opacity:1}}"
    ".caret{animation:blink 1.1s steps(1) infinite}"
    "@keyframes blink{50%{opacity:0}}"
    ".pulse{animation:pulse 2.4s ease-in-out infinite}"
    "@keyframes pulse{50%{opacity:.25}}"
    ".grow{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);animation:grow 1.4s cubic-bezier(.2,.8,.2,1) forwards}"
    "@keyframes grow{to{transform:scaleY(1)}}"
    "@media (prefers-reduced-motion:reduce){.w{stroke-dashoffset:0;animation:none}.fade{opacity:1;animation:none}"
    ".caret,.pulse{animation:none}.grow{transform:none;animation:none}}"
    "</style>"
)


def _ellipse_pts(cx, cy, rx, ry, rot_deg, n=72):
    a = math.radians(rot_deg)
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a), t))
    return pts


def header() -> str:
    W, H = 1280, 460
    gdefs, guse = grain("gr")
    gdefs = ANIM_CSS + gdefs
    b = [f'<rect width="{W}" height="{H}" fill="{BLUE}"/>']
    cx, cy, r = 1000, 236, 128
    px = round(W * 0.56)
    gdefs += f'<clipPath id="panel"><rect x="{px}" y="67" width="{W - 44 - px}" height="{H - 64 - 67}"/></clipPath>'
    gdefs += f'<clipPath id="ball"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
    # slowly turning light behind the sphere
    b.append('<g clip-path="url(#panel)"><g>')
    b.append(rays(cx, cy, r + 14, 900, 120, 0.7, INK, 0.22))
    b.append(rays(cx, cy, r + 14, r + 46, 240, 0.9, INK, 0.7))
    b.append(f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="240s" repeatCount="indefinite"/></g>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 6}" fill="{BLUE}"/>')
    orbit = _ellipse_pts(cx, cy, r + 92, (r + 92) * 0.3, -18)
    od = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y, _ in orbit) + "Z"
    b.append(f'<path d="{od}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.85"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 64}" fill="none" stroke="{INK}" stroke-width="0.8" stroke-dasharray="2 5" opacity="0.8">'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="-360 {cx} {cy}" dur="90s" repeatCount="indefinite"/></circle>')
    b.append('</g>')
    b.append(f'<path d="M{px} 66V{H - 64}" stroke="{INK}" stroke-width="1" opacity="0.55"/>')
    b.append(engraved_sphere(cx, cy, r))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    # spinning meridians: rx = r*|sin(theta + phase)|
    n = 24
    for k in range(4):
        ph = math.pi * k / 4
        vals = ";".join(f"{r * abs(math.sin(math.pi * i / n + ph)):.1f}" for i in range(n + 1))
        b.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r * abs(math.sin(ph)):.1f}" ry="{r}" fill="none" stroke="{INK}" stroke-width="0.7" opacity="0.6">'
                 f'<animate attributeName="rx" values="{vals}" dur="18s" repeatCount="indefinite"/></ellipse>')
    # light sweep across the sphere
    b.append(f'<g clip-path="url(#ball)"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="1.4" fill="{INK}" opacity="0.7">'
             f'<animate attributeName="y" values="{cy - r};{cy + r}" dur="6s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;0.8;0.8;0" keyTimes="0;0.1;0.9;1" dur="6s" repeatCount="indefinite"/></rect></g>')
    # orbiting token (hidden while behind the sphere)
    ops = []
    for x, y, t in orbit:
        behind = math.sin(t) < 0 and math.hypot(x - cx, y - cy) < r + 4
        ops.append("0" if behind else "1")
    lbl, _ = text("TOKEN", 12, 10, 6, 3.8, 2, 1)
    b.append(f'<g><circle r="7" fill="{BLUE}" stroke="{INK}" stroke-width="1.6"/><circle r="2.2" fill="{INK}"/>'
             f'<path d="M6 6L11 10" stroke="{INK}" stroke-width="0.8"/>{lbl}'
             f'<animateMotion dur="16s" repeatCount="indefinite" path="{od}"/>'
             f'<animate attributeName="opacity" values="{";".join(ops)}" dur="16s" repeatCount="indefinite"/></g>')
    cap, _ = text("FIG. 01 — LOCAL FIRST", cx, cy + r + 104, 8, 5, 2.6, 1.1, INK, "middle")
    b.append(cap)

    b.append(frame(W, H))
    s, _ = text("CEMIL CAN ÖZ", 44, 42, 10, 6.4, 3.4, 1.4); b.append(s)
    s, _ = text("COMPUTER ENGINEERING · TR / EN", 44 + 160, 42, 10, 6.4, 3.4, 1.1, INK_DIM); b.append(s)
    lw = text_width("LIVE / 2026.11", 6.4, 3.4)
    b.append(f'<rect class="pulse" x="{W - 44 - lw - 18:.1f}" y="43" width="8" height="8" fill="{INK}"/>')
    s, _ = text("LIVE / 2026.11", W - 44, 42, 10, 6.4, 3.4, 1.1, INK, "end"); b.append(s)
    b.append(f'<path d="M44 66H{W - 44}" stroke="{INK}" stroke-width="1" opacity="0.55"/>')

    # headline that writes itself
    y0, hh, gw, tr, sw = 88, 84, 47, 14, 2.6
    end_x = 0
    for i, line in enumerate(["BUILD", "USEFUL", "THINGS."]):
        s, adv = text(line, 50, y0 + i * (hh + 20), hh, gw, tr, sw)
        s = s.replace('<path d=', f'<path class="w w{i + 1}" pathLength="1" d=', 1).replace('<g fill=', '<g class="fade" fill=')
        b.append(s)
        end_x = 50 + adv
    b.append(f'<rect class="caret" x="{end_x + 16:.1f}" y="{y0 + 2 * (hh + 20) + hh - 6}" width="22" height="6" fill="{INK}"/>')
    for i, nn in enumerate(["01", "02", "03"]):
        s, _ = text(nn, 30, y0 + i * (hh + 20) + 2, 8, 5, 2, 1, INK_DIM, "middle")
        b.append(s)
    b.append(f'<path d="M44 {H - 64}H{W - 44}" stroke="{INK}" stroke-width="1" opacity="0.55"/>')
    s, _ = text("C# · .NET · WPF · SQLITE · PYTHON · JAVASCRIPT · KOTLIN", 44, H - 48, 10, 6.4, 3.4, 1.2); b.append(s)
    s, _ = text("LOCAL TOOLS FOR AI-ASSISTED WORK →", W - 44, H - 48, 10, 6.4, 3.4, 1.2, INK, "end"); b.append(s)
    b.append(guse)
    return svg(W, H, "Cemil Can Öz — Build useful things.",
               "Animated electric blue poster: the tall thin headline 'Build useful things.' writes itself beside an engraved sphere that spins, with turning rays and an orbiting token.",
               "".join(b), gdefs)


# --------------------------------------------------------------------------
# Live data card (refreshed daily by GitHub Actions)
# --------------------------------------------------------------------------
def live_card(d: dict) -> str:
    W, H = 1280, 330
    gdefs, guse = grain("gl", 0.1)
    gdefs = ANIM_CSS + gdefs
    b = [f'<rect width="{W}" height="{H}" fill="{BLUE}"/>', frame(W, H, 12, 1)]
    b.append(f'<rect class="pulse" x="36" y="35" width="8" height="8" fill="{INK}"/>')
    s, _ = text(f"LIVE · UPDATED {d['updated']} · GITHUB ACTIONS", 54, 34, 9, 5.8, 3, 1.3); b.append(s)
    s, _ = text("FIG. 02 — WHAT I SHIPPED LATELY", W - 36, 34, 9, 5.8, 3, 1.1, INK, "end"); b.append(s)
    b.append(f'<path d="M34 58H{W - 34}" stroke="{INK}" stroke-width="0.9" opacity="0.55"/>')
    rel = str(d.get("release") or "-").upper()
    metrics = [
        (f"{d['open_prs']:02d}", "PRS IN REVIEW", "UPSTREAM"),
        (f"{d['merged_prs']:02d}", "PRS MERGED", "ALL REPOS"),
        (f"{d['public_repos']:02d}", "PUBLIC REPOS", "GITHUB"),
        (rel, "CODEX HISTORY", "LATEST RELEASE"),
    ]
    colw = 170
    for i, (val, l1, l2) in enumerate(metrics):
        x = 40 + i * colw
        if i:
            b.append(f'<path d="M{x - 18} 86V{H - 64}" stroke="{INK}" stroke-width="0.8" opacity="0.4"/>')
        s, _ = text(val, x, 100, 70, 26, 9, 2.2)
        b.append(s.replace('<path d=', '<path class="w" pathLength="1" d=', 1).replace('<g fill=', '<g class="fade" fill='))
        s, _ = text(l1, x, 196, 8.5, 5.4, 2.8, 1.2); b.append(s)
        s, _ = text(l2, x, 214, 8, 5, 2.8, 1, INK_DIM); b.append(s)
    weeks = d.get("weeks") or []
    bx0, bx1, base, top = 740, W - 40, H - 80, 100
    if weeks:
        mx = max(weeks) or 1
        bw = (bx1 - bx0) / len(weeks)
        for i, v in enumerate(weeks):
            h = max(2.0, (base - top) * v / mx)
            x = bx0 + i * bw
            hatch = "".join(f"M{x + k:.1f} {base - h:.1f}V{base}" for k in (1.5, 4, 6.5, 9, 11.5) if k < bw - 3)
            b.append(f'<path class="grow" style="animation-delay:{0.4 + i * 0.03:.2f}s" d="{hatch}" stroke="{INK}" stroke-width="1.3"/>')
        b.append(f'<path d="M{bx0} {base + 0.5}H{bx1}" stroke="{INK}" stroke-width="1.2"/>')
        s, _ = text(f"CONTRIBUTIONS · LAST {len(weeks)} WEEKS", bx0, 80, 8.5, 5.4, 2.8, 1.2); b.append(s)
        s, _ = text(f"{d.get('total', sum(weeks))} IN THE LAST YEAR", bx1, 80, 8.5, 5.4, 2.8, 1.2, INK, "end"); b.append(s)
        s, _ = text(f"{len(weeks)} WEEKS AGO", bx0, base + 10, 7.5, 4.8, 2.6, 1, INK_DIM); b.append(s)
        s, _ = text("NOW", bx1, base + 10, 7.5, 4.8, 2.6, 1, INK_DIM, "end"); b.append(s)
    b.append(f'<path d="M34 {H - 50}H{W - 34}" stroke="{INK}" stroke-width="0.9" opacity="0.55"/>')
    s, _ = text(f"LAST PUSH · {d.get('last_push', '-')}", 36, H - 35, 8.5, 5.4, 2.8, 1.2); b.append(s)
    s, _ = text("REFRESHED DAILY · SCRIPTS/LIVE_DATA.PY", W - 36, H - 35, 8.5, 5.4, 2.8, 1.1, INK_DIM, "end"); b.append(s)
    b.append(guse)
    return svg(W, H, "Live GitHub stats",
               f"Live stats updated {d['updated']}: {d['open_prs']} pull requests in review, {d['merged_prs']} merged, "
               f"{d['public_repos']} public repositories, latest Codex History release {d.get('release') or 'none'}, and weekly contributions as engraved bars.",
               "".join(b), gdefs)


# --------------------------------------------------------------------------
# Project cards
# --------------------------------------------------------------------------
def card(num, name_lines, kicker, lines, tags, motif, title, desc) -> str:
    W, H = 620, 340
    gdefs, guse = grain("g" + num, 0.1)
    b = [f'<rect width="{W}" height="{H}" fill="{BLUE}"/>', motif, frame(W, H, 12, 1)]
    s, _ = text(num, 34, 34, 9, 5.8, 3, 1.3); b.append(s)
    s, _ = text(kicker, W - 34, 34, 9, 5.8, 3, 1.1, INK, "end"); b.append(s)
    b.append(f'<path d="M34 56H{W - 34}" stroke="{INK}" stroke-width="0.9" opacity="0.55"/>')
    y = 80
    for ln in name_lines:
        s, _ = text(ln, 36, y, 62, 25, 9, 2.2); b.append(s)
        y += 80
    y += 4
    for ln in lines:
        s, _ = text(ln, 36, y, 8.5, 5.4, 2.9, 1.15); b.append(s)
        y += 19
    b.append(f'<path d="M34 {H - 58}H{W - 34}" stroke="{INK}" stroke-width="0.9" opacity="0.55"/>')
    x = 34
    for tg in tags:
        s, adv = text(tg, x + 9, H - 43, 8, 5, 2.8, 1.1)
        b.append(f'<rect x="{x}" y="{H - 50}" width="{adv + 18:.1f}" height="22" fill="none" stroke="{INK}" stroke-width="0.9"/>')
        b.append(s)
        x += adv + 26
    s, _ = text("OPEN →", W - 34, H - 43, 8, 5, 2.8, 1.3, INK, "end"); b.append(s)
    b.append(guse)
    return svg(W, H, title, desc, "".join(b), gdefs)


def motif_history(W=620, H=340) -> str:
    """A stack of session bars receding into a hatched dial — a log timeline."""
    cx, cy, r = 505, 150, 64
    b = [rays(cx, cy, r + 8, r + 30, 96, 0.8, INK, 0.75)]
    b.append(engraved_sphere(cx, cy, r, 3.6, seed=11))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    # clock hands = time
    b.append(f'<path d="M{cx} {cy}L{cx} {cy - r * 0.72}M{cx} {cy}L{cx + r * 0.5} {cy + r * 0.22}" stroke="{BLUE}" stroke-width="5"/>')
    b.append(f'<path d="M{cx} {cy}L{cx} {cy - r * 0.72}M{cx} {cy}L{cx + r * 0.5} {cy + r * 0.22}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{INK}"/>')
    return "".join(b)


def motif_tokenbar(W=620, H=340) -> str:
    """A semicircular gauge drawn as engraving ticks."""
    cx, cy, r = 505, 190, 78
    d_major, d_minor = [], []
    for i in range(0, 61):
        a = math.pi + math.pi * i / 60
        r0 = r - (16 if i % 10 == 0 else 8)
        seg = f"M{cx + math.cos(a) * r0:.1f} {cy + math.sin(a) * r0:.1f}L{cx + math.cos(a) * r:.1f} {cy + math.sin(a) * r:.1f}"
        (d_major if i % 10 == 0 else d_minor).append(seg)
    b = [rays(cx, cy, r + 8, r + 34, 120, 0.7, INK, 0.65, skip=lambda a: a < math.pi and a > 0)]
    b.append(f'<path d="{"".join(d_minor)}" stroke="{INK}" stroke-width="1"/>')
    b.append(f'<path d="{"".join(d_major)}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<path d="M{cx - r} {cy}A{r} {r} 0 0 1 {cx + r} {cy}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    # hatched fill for "used" sector
    hatch = []
    for k in range(0, 40):
        a = math.pi + math.pi * 0.68 * k / 39
        hatch.append(f"M{cx + math.cos(a) * 22:.1f} {cy + math.sin(a) * 22:.1f}L{cx + math.cos(a) * (r - 22):.1f} {cy + math.sin(a) * (r - 22):.1f}")
    b.append(f'<path d="{"".join(hatch)}" stroke="{INK}" stroke-width="0.7" opacity="0.8"/>')
    a = math.pi + math.pi * 0.68
    b.append(f'<path d="M{cx} {cy}L{cx + math.cos(a) * (r - 4):.1f} {cy + math.sin(a) * (r - 4):.1f}" stroke="{INK}" stroke-width="2.2"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{BLUE}" stroke="{INK}" stroke-width="1.6"/>')
    s, _ = text("68%", cx, cy + 16, 10, 6, 3, 1.3, INK, "middle"); b.append(s)
    return "".join(b)


def footer() -> str:
    W, H = 1280, 120
    gdefs, guse = grain("gf", 0.1)
    b = [f'<rect width="{W}" height="{H}" fill="{BLUE}"/>', frame(W, H, 10, 1)]
    b.append(rays(W / 2, H + 40, 70, 1400, 90, 0.6, INK, 0.25))
    b.append(f'<rect x="{W / 2 - 330}" y="38" width="660" height="44" fill="{BLUE}"/>')
    s, _ = text("THANKS FOR READING · TEŞEKKÜRLER", W / 2, 50, 18, 10.5, 5.5, 1.6, INK, "middle"); b.append(s)
    b.append(guse)
    return svg(W, H, "Thanks for reading", "Electric blue footer strip with radiating lines.", "".join(b), gdefs)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / "header.svg").write_text(header(), encoding="utf-8")
    (OUT / "card-codex-history.svg").write_text(card(
        "01", ["CODEX", "HISTORY"], "WINDOWS · RELEASED",
        ["SEARCH YOUR CODEX SESSIONS, TOKENS AND", "ESTIMATED API COSTS — ON YOUR MACHINE."],
        ["C#", ".NET", "WPF", "SQLITE"], motif_history(),
        "Codex History", "Project card: Codex History, a Windows app to explore Codex sessions, tokens and estimated API costs locally."),
        encoding="utf-8")
    (OUT / "card-tokenbar.svg").write_text(card(
        "02", ["TOKEN", "BAR"], "WINDOWS · TRAY APP",
        ["A FLOATING BADGE FOR CODEX + CLAUDE CODE", "TOKEN USAGE. READS LOCAL LOGS, NO NETWORK."],
        ["C#", ".NET", "TRAY", "OFFLINE"], motif_tokenbar(),
        "TokenBar", "Project card: TokenBar, a Windows tray app that shows local AI coding agents' token usage."),
        encoding="utf-8")
    (OUT / "footer.svg").write_text(footer(), encoding="utf-8")
    live = OUT.parent / "data" / "live.json"
    if live.exists():
        import json
        (OUT / "live.svg").write_text(live_card(json.loads(live.read_text(encoding="utf-8"))), encoding="utf-8")
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.name:28} {p.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
