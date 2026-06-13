#!/usr/bin/env python3
"""
make_favicons.py — turn one master icon PNG into a complete favicon/app-icon set.

No third-party dependencies. Resizing is done with macOS `sips` (preferred) or
ImageMagick (`magick`/`convert`) if present. The multi-size `.ico` is packed in
pure Python by embedding PNG entries (the modern ICO variant every current
browser supports), so no `icotool`/Pillow is required.

Usage:
    python3 make_favicons.py <master.png | https://...url> [--out-dir DIR]

The master should be a SQUARE PNG, ideally >=1024px. A Higgsfield result URL can
be passed directly and it will be downloaded first.

Outputs (into --out-dir, default ./favicons):
    favicon.ico            multi-res (16/32/48), PNG-encoded entries
    favicon-16.png 32 48 64
    icon-192.png 512       PWA / Android (maskable-safe if the master has padding)
    apple-touch-icon.png   180, for iOS home-screen
    icon-1024.png          master copy (App Store / source of truth)
    site.webmanifest       ready-to-serve manifest
    head.html              <link> tags to paste into <head>
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

# size -> output filename. 1024 is only emitted if the master is large enough.
PNG_TARGETS = {
    16: "favicon-16.png",
    32: "favicon-32.png",
    48: "favicon-48.png",
    64: "favicon-64.png",
    180: "apple-touch-icon.png",
    192: "icon-192.png",
    512: "icon-512.png",
    1024: "icon-1024.png",
}
ICO_SIZES = [16, 32, 48]


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def fetch_if_url(src):
    if src.startswith("http://") or src.startswith("https://"):
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        print(f"downloading {src}")
        try:
            urllib.request.urlretrieve(src, path)
        except Exception as e:
            fail(f"could not download {src}: {e}")
        return path
    if not os.path.isfile(src):
        fail(f"input not found: {src}")
    return src


def resizer():
    if shutil.which("sips"):
        return "sips"
    if shutil.which("magick"):
        return "magick"
    if shutil.which("convert"):
        return "convert"
    fail("need `sips` (macOS) or ImageMagick to resize; none found")


def resize(tool, src, size, dst):
    if tool == "sips":
        # -z height width ; --out target. sips keeps alpha and writes PNG by ext.
        r = subprocess.run(
            ["sips", "-z", str(size), str(size), src, "--out", dst],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            fail(f"sips failed at {size}px: {r.stderr.strip()}")
    else:
        exe = "magick" if tool == "magick" else "convert"
        r = subprocess.run(
            [exe, src, "-resize", f"{size}x{size}", dst],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            fail(f"{exe} failed at {size}px: {r.stderr.strip()}")


def _find_chrome():
    for p in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium"):
        if os.path.isfile(p):
            return p
    return shutil.which("google-chrome") or shutil.which("chromium")


def rasterize_svg(svg_path, out_png, size=1024):
    """Render an SVG to a square PNG. Tries macOS `qlmanage` (built-in, no deps),
    then headless Chrome. SVG is the crisp master; we still need PNG fallbacks for
    favicon.ico / apple-touch / PWA, which can't be vector."""
    if shutil.which("qlmanage"):
        tmpdir = tempfile.mkdtemp()
        subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", tmpdir, svg_path],
                       capture_output=True, text=True)
        produced = os.path.join(tmpdir, os.path.basename(svg_path) + ".png")
        if os.path.isfile(produced):
            shutil.move(produced, out_png)
            shutil.rmtree(tmpdir, ignore_errors=True)
            return out_png
        shutil.rmtree(tmpdir, ignore_errors=True)
    chrome = _find_chrome()
    if chrome:
        fd, wrapper = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        svg_url = "file://" + urllib.parse.quote(os.path.abspath(svg_path))
        with open(wrapper, "w") as f:
            f.write(f'<body style="margin:0"><img src="{svg_url}" '
                    f'style="width:{size}px;height:{size}px;display:block"></body>')
        subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
                        f"--screenshot={out_png}", f"--window-size={size},{size}",
                        "--default-background-color=00000000",
                        "file://" + urllib.parse.quote(os.path.abspath(wrapper))],
                       capture_output=True, text=True)
        os.remove(wrapper)
        if os.path.isfile(out_png):
            return out_png
    fail("could not rasterize SVG — need macOS `qlmanage` or Google Chrome")


def png_dimensions(path):
    """Read width/height from a PNG IHDR without any image library."""
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def pack_ico(png_paths, ico_path):
    """Build a .ico whose entries are raw PNG images (ICO supports this)."""
    entries = []
    for p in png_paths:
        with open(p, "rb") as f:
            data = f.read()
        dims = png_dimensions(p)
        size = dims[0] if dims else 0
        entries.append((size, data))

    n = len(entries)
    header = struct.pack("<HHH", 0, 1, n)  # reserved=0, type=1 (icon), count
    offset = 6 + 16 * n
    dir_blob = b""
    img_blob = b""
    for size, data in entries:
        b = 0 if size >= 256 else size  # 0 means 256 in ICO
        dir_blob += struct.pack(
            "<BBBBHHII",
            b, b,          # width, height
            0,             # palette count
            0,             # reserved
            1,             # color planes
            32,            # bits per pixel
            len(data),     # bytes of image data
            offset,        # offset from start of file
        )
        img_blob += data
        offset += len(data)
    with open(ico_path, "wb") as f:
        f.write(header + dir_blob + img_blob)


WEBMANIFEST = """{
  "name": "%(name)s",
  "short_name": "%(name)s",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#000000",
  "background_color": "#000000",
  "display": "standalone"
}
"""

HEAD_HTML = """<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
"""


def main():
    ap = argparse.ArgumentParser(description="Generate a favicon/app-icon set from one master PNG or SVG.")
    ap.add_argument("master", help="path or https URL to a square master — PNG, or a local SVG")
    ap.add_argument("--out-dir", default="favicons", help="output directory (default: favicons)")
    ap.add_argument("--name", default="App", help="app name for site.webmanifest")
    args = ap.parse_args()

    master = fetch_if_url(args.master)

    # SVG master: ship it as the primary favicon and rasterize a 1024 PNG for the
    # raster fallbacks (.ico / apple-touch / PWA can't be vector).
    svg_source = None
    if master.lower().endswith(".svg"):
        svg_source = master
        fd, raster = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        print(f"rasterizing {os.path.basename(svg_source)} → 1024px master")
        rasterize_svg(svg_source, raster, 1024)
        master = raster

    dims = png_dimensions(master)
    if dims is None:
        fail("master is not a valid PNG")
    w, h = dims
    if w != h:
        print(f"warning: master is {w}x{h}, not square — icons may look off-center", file=sys.stderr)
    if min(w, h) < 512:
        print(f"warning: master is only {w}x{h}; regenerate at 2k for crisp large icons", file=sys.stderr)

    os.makedirs(args.out_dir, exist_ok=True)
    tool = resizer()

    made = []
    for size, fname in sorted(PNG_TARGETS.items()):
        if size > max(w, h) and size != 1024:
            continue  # don't upscale beyond the master (except keep a 1024 master copy)
        dst = os.path.join(args.out_dir, fname)
        if size == 1024 and max(w, h) < 1024:
            # copy the master as-is rather than upscaling
            shutil.copyfile(master, dst)
        else:
            resize(tool, master, size, dst)
        made.append((size, dst))

    # favicon.ico from the small PNGs we just made
    ico_inputs = [os.path.join(args.out_dir, PNG_TARGETS[s]) for s in ICO_SIZES
                  if os.path.isfile(os.path.join(args.out_dir, PNG_TARGETS[s]))]
    if ico_inputs:
        pack_ico(ico_inputs, os.path.join(args.out_dir, "favicon.ico"))
        made.append(("ico", os.path.join(args.out_dir, "favicon.ico")))

    # Ship the original SVG as the primary favicon (browsers prefer it; .ico is the fallback)
    head = HEAD_HTML
    if svg_source:
        svg_dst = os.path.join(args.out_dir, "favicon.svg")
        shutil.copyfile(svg_source, svg_dst)
        made.insert(0, ("svg", svg_dst))
        head = '<link rel="icon" type="image/svg+xml" href="/favicon.svg">\n' + HEAD_HTML

    with open(os.path.join(args.out_dir, "site.webmanifest"), "w") as f:
        f.write(WEBMANIFEST % {"name": args.name})
    with open(os.path.join(args.out_dir, "head.html"), "w") as f:
        f.write(head)

    print(f"\nwrote {len(made)} icon files to {args.out_dir}/")
    labels = {"ico": "favicon.ico", "svg": "favicon.svg"}
    for size, path in made:
        label = labels.get(size, f"{size}px")
        print(f"  {label:>12}  {path}")
    print(f"\n  paste {args.out_dir}/head.html into your <head>; serve files from web root")


if __name__ == "__main__":
    main()
