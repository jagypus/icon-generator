#!/usr/bin/env python3
"""
contrast_check.py — measure figure/ground contrast for an icon mark vs its tile.

A bold icon needs LUMINANCE contrast, not just a different hue. A mid-tone mark
on a near-black tile (mid green on charcoal) differs in colour but not in
brightness, so it goes muddy at favicon/toolbar sizes. This computes the WCAG
relative-luminance contrast ratio between two colours so you can verify a mark
pops *before* committing to it — no eyeballing.

Usage:
    python3 contrast_check.py "#aef716" "#1b1d21"        # mark, tile
    python3 contrast_check.py white "#0a9bb0"

Thresholds — an icon mark must POP, so the bar is higher than the WCAG 4.5
text-legibility minimum. A mark can pass for text and still read muddy small:
    >= 10    excellent — pops at any size
    >=  7    strong — good icon floor
    >= 4.5   weak for an icon (passes WCAG text, but muddy in a toolbar) — push it
    <  4.5   fail
"""
import sys

NAMED = {"white": "#ffffff", "black": "#000000"}


def parse_hex(c):
    c = NAMED.get(c.lower().strip(), c).lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        sys.exit(f"error: can't parse colour '{c}' — use #RRGGBB or #RGB")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def rel_luminance(rgb):
    def lin(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(c1, c2):
    l1, l2 = rel_luminance(parse_hex(c1)), rel_luminance(parse_hex(c2))
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: contrast_check.py <mark-color> <tile-color>")
    mark, tile = sys.argv[1], sys.argv[2]
    ratio = contrast_ratio(mark, tile)
    if ratio >= 10:
        verdict = "EXCELLENT — pops at any size"
    elif ratio >= 7:
        verdict = "STRONG — good icon floor"
    elif ratio >= 4.5:
        verdict = "WEAK for an icon — brighten/lighten the mark, or lighten the tile"
    else:
        verdict = "FAIL — far too low"
    print(f"{mark} on {tile}:  {ratio:.1f}:1  — {verdict}")
    sys.exit(0 if ratio >= 7 else 1)


if __name__ == "__main__":
    main()
