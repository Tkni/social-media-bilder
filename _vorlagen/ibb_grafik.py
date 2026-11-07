"""Grafik-Vorlage im Design von In-Berlin-Brandenburg.com.

Farben und Schriften aus css-neu/main.css der Seite:
  Primär-Rot #C5251B, Spreeblau #315C72, Brandenburg-Grün #2F5D50,
  warmes Beige #F4EFE5, Off-White #FAF7F1, Border #D6CFC0,
  Überschriften Source Serif 4, Fließtext Inter.

Aufruf (Beispiel):
  from ibb_grafik import balken
  balken(pfad, werte, titel=..., unterzeile=..., einheit="°C", quelle=..., modus="divergierend", mitte=10.4)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image

HIER = os.path.dirname(os.path.abspath(__file__))

RED = "#C5251B"
BLUE = "#315C72"
GREEN = "#2F5D50"
BG = "#F4EFE5"
CARD = "#FAF7F1"
BORDER = "#D6CFC0"
INK = "#111111"
INK2 = "#4F4F4F"
MUTED = "#7A7A7A"
NEUTRAL = "#C9C1B1"

MONATE = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


def _fonts():
    for f in os.listdir(os.path.join(HIER, "fonts")):
        if f.endswith((".otf", ".ttf")):
            fm.fontManager.addfont(os.path.join(HIER, "fonts", f))
    for f in ["/usr/share/fonts/opentype/inter/Inter-Regular.otf",
              "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
              "/usr/share/fonts/opentype/inter/Inter-Bold.otf"]:
        if os.path.exists(f):
            fm.fontManager.addfont(f)


def _hex(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255


def _mix(a, b, t):
    a, b = _hex(a), _hex(b)
    return tuple(a * (1 - t) + b * t)


def _fmt(v):
    return f"{v:.1f}".replace(".", ",")


def balken(pfad, werte, titel, unterzeile, quelle, labels=MONATE, format="feed",
           modus="sequentiell", farbe=BLUE, mitte=None, mitte_text=None, einheit=""):
    """modus: 'sequentiell' (eine Farbe, hell->dunkel) oder 'divergierend' (Blau <-> Rot um 'mitte')."""
    _fonts()
    W, H = (1080, 1350) if format == "feed" else (1000, 1500)
    tall = format != "feed"
    dpi = 100
    fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi, facecolor=BG)
    fy = lambda px: 1 - px / H
    fx = lambda px: px / W

    # Karte
    m = 36
    card = fig.add_axes([fx(m), fy(H - m), fx(W - 2 * m), (H - 2 * m) / H])
    card.set_xlim(0, 1); card.set_ylim(0, 1); card.axis("off")
    card.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.015",
                                  facecolor=CARD, edgecolor=BORDER, linewidth=1.5,
                                  transform=card.transAxes, mutation_aspect=(W - 2 * m) / (H - 2 * m)))

    pad = 84
    # Logo
    logo = Image.open(os.path.join(HIER, "logo.png"))
    lw = 470
    lh = lw * logo.height / logo.width
    lax = fig.add_axes([fx(pad), fy(pad + lh), fx(lw), lh / H])
    lax.imshow(logo); lax.axis("off")

    # rote Linie wie "eyebrow" auf der Seite
    y_line = pad + lh + 34
    fig.add_artist(Rectangle((fx(pad), fy(y_line)), fx(64), 5 / H, transform=fig.transFigure,
                             facecolor=RED, edgecolor="none"))

    title_y = y_line + 26
    tsize = 54 if not tall else 52
    t = fig.text(fx(pad), fy(title_y), titel, fontsize=tsize, fontfamily="Source Serif 4",
                 fontweight="bold", color=INK, va="top", linespacing=1.0)
    bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
    sub_y = (H - bb.y0) + 24
    for i, zeile in enumerate(unterzeile.split("\n")):
        fig.text(fx(pad), fy(sub_y + i * 38), zeile, fontsize=23, fontfamily="Inter", color=INK2, va="top")

    top = sub_y + 38 * len(unterzeile.split("\n")) + 70
    bottom = H - (170 if not tall else 185)
    ax = fig.add_axes([fx(pad), fy(bottom), fx(W - 2 * pad), (bottom - top) / H])
    ax.set_facecolor(CARD)
    n = len(werte)
    x = np.arange(n)
    vmax = max(werte)
    ymax = vmax * 1.12

    def col(v):
        if modus == "divergierend":
            span = max(abs(w - mitte) for w in werte)
            d = (v - mitte) / span
            return _mix(NEUTRAL, RED, d) if d >= 0 else _mix(NEUTRAL, BLUE, -d)
        lo, hi = min(werte), max(werte)
        t = (v - lo) / (hi - lo) if hi > lo else 1
        return _mix("#B9CCD6", farbe, 0.25 + 0.75 * t)

    bw = 0.66
    for xi, v in zip(x, werte):
        ax.add_patch(FancyBboxPatch((xi - bw / 2, -ymax * 0.05), bw, v + ymax * 0.05,
                                    boxstyle="round,pad=0,rounding_size=0.08",
                                    mutation_aspect=ymax / n * (bottom - top) / (W - 2 * pad),
                                    facecolor=col(v), edgecolor="none", zorder=3, clip_on=True))
        ax.text(xi, v + ymax * 0.018, _fmt(v), ha="center", va="bottom", fontsize=19 if not tall else 18,
                fontfamily="Inter", fontweight="semibold", color=INK, zorder=4)

    if mitte is not None and mitte_text:
        ax.axhline(mitte, color=INK2, lw=1.8, ls=(0, (4, 4)), zorder=2)
        ax.text(-0.5, mitte - ymax * 0.02, mitte_text, ha="left", va="top", fontsize=18,
                fontfamily="Inter", color=INK2, zorder=4, linespacing=1.15)

    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(0, ymax)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=20, color=INK2, fontfamily="Inter")
    ax.tick_params(axis="x", length=0, pad=12)
    ax.set_yticks([])
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BORDER)
    ax.spines["bottom"].set_linewidth(1.5)

    fig.text(fx(pad), fy(H - pad + 6), quelle, fontsize=16, fontfamily="Inter", color=MUTED, va="bottom")
    fig.text(fx(W - pad), fy(H - pad + 6), "in-berlin-brandenburg.com", fontsize=16, fontfamily="Inter",
             fontweight="semibold", color=RED, va="bottom", ha="right")
    fig.savefig(pfad, dpi=dpi, facecolor=BG)
    plt.close(fig)
