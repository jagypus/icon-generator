#!/usr/bin/env python3
"""
make_contact_sheet.py — build a self-contained HTML contact sheet of icon
concepts and open it in the user's browser.

Why this exists: generated icons must be SHOWN to the user so they can choose
one. Inline image rendering is unreliable across clients (a `Read` of a PNG may
display nothing), so the dependable way to present concepts is to write an HTML
sheet that references the images by absolute `file://` URL and `open` it in the
default browser, where it always renders.

Each concept is shown large (on a checkerboard so transparency is visible) plus
a downscaled strip (64/48/32/16px) so the user can judge small-size legibility —
the whole point of a bold icon.

Usage:
    python3 make_contact_sheet.py concept-1.png concept-2.png concept-3.png \
        --title "MyProject icons" \
        --label "Emerald gradient" --label "Neon on charcoal" --label "Origami"

    # labels are optional and match image order; missing ones fall back to the
    # filename. Pass --no-open to write the HTML without launching a browser.
"""
import argparse
import os
import subprocess
import sys
import urllib.parse


def file_url(path):
    return "file://" + urllib.parse.quote(os.path.abspath(path))


CARD = """  <div class="card">
    <img class="big" src="{url}" alt="{label}">
    <div class="label">{n} · {label}</div>
    <div class="strip">
      <figure><img class="s64" src="{url}"><figcaption>64</figcaption></figure>
      <figure><img class="s48" src="{url}"><figcaption>48</figcaption></figure>
      <figure><img class="s32" src="{url}"><figcaption>32</figcaption></figure>
      <figure><img class="s16" src="{url}"><figcaption>16</figcaption></figure>
    </div>
  </div>"""

PAGE = """<!doctype html>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ margin:0; background:#0e0f13; color:#e7e9ee; font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; padding:40px; }}
  h1 {{ font-size:20px; font-weight:650; margin:0 0 4px; }}
  .sub {{ color:#9aa0ab; margin:0 0 32px; }}
  .row {{ display:flex; gap:32px; flex-wrap:wrap; }}
  .card {{ background:#161821; border:1px solid #222634; border-radius:16px; padding:20px; width:300px; }}
  .ck {{ background-image:linear-gradient(45deg,#2a2d39 25%,transparent 25%),linear-gradient(-45deg,#2a2d39 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#2a2d39 75%),linear-gradient(-45deg,transparent 75%,#2a2d39 75%); background-size:20px 20px; background-position:0 0,0 10px,10px -10px,-10px 0; }}
  .big {{ width:260px; height:260px; border-radius:22px; display:block; object-fit:cover; }}
  .label {{ font-weight:600; margin:16px 0 12px; }}
  .strip {{ display:flex; align-items:flex-end; gap:14px; padding:14px; background:#0e0f13; border-radius:10px; }}
  .strip figure {{ margin:0; text-align:center; }}
  .strip img {{ border-radius:5px; display:block; }}
  .strip figcaption {{ font-size:10px; color:#6b7280; margin-top:6px; }}
  .s64{{width:64px;height:64px}}.s48{{width:48px;height:48px}}.s32{{width:32px;height:32px}}.s16{{width:16px;height:16px}}
</style>
<h1>{title}</h1>
<p class="sub">Each card shows the full icon plus the same mark downscaled — boldness is a small-size property, so check the 16/32px strip before choosing.</p>
<div class="row">
{cards}
</div>
"""


def main():
    ap = argparse.ArgumentParser(description="Build + open an HTML contact sheet of icon concepts.")
    ap.add_argument("images", nargs="+", help="concept image paths, in display order")
    ap.add_argument("--title", default="Icon concepts", help="heading for the sheet")
    ap.add_argument("--label", action="append", default=[], help="label per image (repeatable, matches order)")
    ap.add_argument("--out", default=None, help="output HTML path (default: contact-sheet.html next to first image)")
    ap.add_argument("--no-open", action="store_true", help="write the HTML but don't launch a browser")
    args = ap.parse_args()

    missing = [p for p in args.images if not os.path.isfile(p)]
    if missing:
        print(f"error: image(s) not found: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    cards = []
    for i, img in enumerate(args.images):
        label = args.label[i] if i < len(args.label) else os.path.splitext(os.path.basename(img))[0]
        cards.append(CARD.format(url=file_url(img), label=label, n=i + 1))

    html = PAGE.format(title=args.title, cards="\n".join(cards))

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.images[0])) or ".", "contact-sheet.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"wrote contact sheet: {out}")

    if not args.no_open:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        try:
            subprocess.run([opener, out], check=False)
            print(f"opened in browser via `{opener}`")
        except FileNotFoundError:
            print(f"(couldn't auto-open; open {out} manually)")


if __name__ == "__main__":
    main()
