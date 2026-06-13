---
name: icon-generator
description: >-
  Generate visually BOLD, instantly-legible project icons, app icons, logo
  marks, and favicons — vector-first (hand-authored SVG), escalating to the
  Higgsfield CLI with Nano Banana Pro (`nano_banana_2`) for dimensional or
  rendered looks. Use whenever the user wants an icon, app icon, favicon, brand
  glyph, or logo mark for a project, site, app, or repo — e.g. "make an icon for
  my project", "generate a favicon", "design an app icon", "I need a logo mark",
  "create a brand symbol" — and ESPECIALLY when an existing icon looks weak,
  thin, washed-out, or generic and needs to read stronger at small sizes.
  Produces several on-brand concepts on a full-bleed rounded-square tile, then
  slices the chosen one into a complete favicon.svg + favicon.ico + apple-touch
  + PWA icon set. NOT for photographs, marketing ads, videos, character work, or
  full illustrations — use higgsfield-generate for those.
argument-hint: "[what the project is] [--dark|--light] [--svg|--render]"
allowed-tools: Bash
---

# Icon Generator

Make project icons that punch. The job isn't "draw the thing" — it's to produce
a mark that is **instantly legible and visually confident at 16px**, the size a
favicon actually renders at. Most AI-generated icons fail because they default
to a thin line drawing floating on white: fine at 1024px, gone at 16px. This
skill exists to avoid exactly that.

**Default to SVG; escalate to the model only when you need a rendered look.**
Most project marks are simple — a glyph, a letterform, a geometric symbol — and
for those a hand-authored SVG is *better* than a generated raster: bold by
construction (solid fills, thick shapes), razor-sharp at every size, a few
hundred bytes, free, instant, and editable. SVG is also the modern primary
favicon format. Reserve **Nano Banana Pro** for the jobs vector can't fake —
dimensional/material/illustrative looks (glossy 3D tiles, soft lighting,
textured or painterly marks) — or when the SVG just isn't landing.

## Step 0 — Bootstrap (only when escalating)

The SVG path needs **no CLI, no API, no auth** — skip straight to Step 1. Only
when you escalate to the generative model (Step 5):

1. If `higgsfield` is not on `$PATH`:
   `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`
2. If `higgsfield account status` fails with `Session expired` /
   `Not authenticated`, ask the user to run `higgsfield auth login` and wait.

## Step 1 — Get the brief (fast)

Pull what you can from context; ask at most **one** short question if a key piece
is missing. Don't interrogate.

- **What the project is / does** — the source of the motif.
- **Mood** — playful, serious, technical, premium, friendly.
- **Light or dark tile** — default to a **deep dark** tile; it reads boldest.
- **Color** — one brand color if they have it; otherwise propose one.
- **Render style** — flat/geometric/letterform → **SVG** (default). Dimensional,
  glossy, textured, illustrative, or "make it look rendered" → plan to escalate.

If the brief is self-explanatory, pick sane defaults and start — showing options
beats asking questions.

## Step 2 — Art direction: what makes an icon BOLD

These are format-agnostic — they hold for SVG and for generated rasters alike.

1. **One shape, one idea.** A single, instantly-readable motif. No scenes, no
   multiple objects. If you can't name the silhouette in two words, simplify.
2. **Fill over line.** Solid filled forms and *thick* strokes. Thin hairlines are
   the #1 cause of weak icons — they disintegrate when downscaled.
3. **High figure/ground contrast — measured, not vibed.** It's *luminance* that
   matters, not hue: a mid-tone mark (mid green, mid blue) on a near-black tile
   differs in colour but barely in brightness, so it goes muddy at toolbar /
   favicon sizes. On a dark tile the mark must be near-white or a bright/light
   tint; on a light tile, a deep saturated mark. An icon must *pop*, so aim
   higher than the WCAG text minimum: **contrast ratio ≥7, ideally ≥10**. Verify
   before committing — you know the exact hexes, so check them:
   `python3 scripts/contrast_check.py <mark-hex> <tile-hex>`. (~5:1 passes for
   text but still reads weak as an icon — don't settle for it.)
4. **Full-bleed container.** A **rounded-square ("squircle") tile** whose
   background fills the **entire frame edge-to-edge** — the icon *is* the frame.
   Never a squircle floating on white; that leaves stray white corners that look
   cheap and show as white pixels at favicon sizes.
5. **Big, centered, generous padding.** Motif fills ~62–70% of the tile,
   centered, even margins. Nothing touches the edges.
6. **Confident, limited palette.** One dominant color + one accent, or a two-stop
   gradient. Saturated, not pastel.
7. **Flat or subtly dimensional — never photoreal in SVG.** Flat vector, or a
   slight bevel / two-tone fold. No noise, no fine detail that won't survive
   downscaling.
8. **No text.** Tiny words vanish at favicon sizes. The only exception is a
   *single* bold monogram letter as the whole motif.

## Step 3 — SVG-first: author the mark directly

This is the default. Hand-author the SVG using the principles above expressed as
construction rules:

- **Canvas:** `viewBox="0 0 512 512"`.
- **Full-bleed tile:** `<rect width="512" height="512" rx="115">` (rx≈115 is the
  iOS squircle curve). Wrap *everything* in a `<clipPath>` of that rect so the
  mark and any shadow are clipped to the tile — no overflow, no white corners.
- **Background:** a solid fill or a two-stop `<linearGradient>` (diagonal:
  `x1="0" y1="0" x2="1" y2="1`).
- **Mark:** thick **filled** `<path>`s. Avoid thin strokes; if you must stroke,
  use `stroke-width` ≥ ~24 (at 512) with `stroke-linejoin="round"`. Thin lines
  are the cardinal sin.
- **Depth without thin lines:** split the mark into two facets filled with two
  shades (e.g. `#fff` + `#dfe8ef`) for an origami fold, and/or a low-opacity
  black copy offset behind it for a soft shadow — never hairline detail.
- **Placement:** center the mark and scale it to ~62–70% of the frame via a
  `transform`. Generous, even padding.
- **Color:** two colors + one accent, saturated.
- **No `<text>`** except a single monogram — and draw it as a path (the render
  host may not have your font).

**Worked template** (the paper-plane mark — adapt the gradient and the path):

```svg
<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="paper plane app icon">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1fd18a"/>
      <stop offset="1" stop-color="#0a9bb0"/>
    </linearGradient>
    <clipPath id="tile"><rect width="512" height="512" rx="115"/></clipPath>
  </defs>
  <g clip-path="url(#tile)">
    <rect width="512" height="512" fill="url(#g)"/>
    <g transform="translate(256,260) rotate(-35) scale(13.5) translate(-12,-12)">
      <path d="M2 3 L22 12 L6 12 Z" fill="#000" opacity="0.10" transform="translate(0.7,1.4)"/>
      <path d="M2 21 L22 12 L6 12 Z" fill="#000" opacity="0.10" transform="translate(0.7,1.4)"/>
      <path d="M2 3 L22 12 L6 12 Z" fill="#fff"/>
      <path d="M2 21 L22 12 L6 12 Z" fill="#dfe8ef"/>
    </g>
  </g>
</svg>
```

Author **2–3 directions** that vary along one axis (background treatment, mark
color, or flat-vs-faceted). Save them as `icon-concepts/concept-1.svg` etc.

## Step 4 — Show the concepts — always launch a contact sheet

The user has to *see* the concepts to choose, and **inline image rendering is not
reliable** — a `Read` of an image often displays nothing in the client. So build
an HTML contact sheet and open it in the browser, where it always renders. The
script accepts `.svg` and `.png` alike (SVG renders crisp at every strip size):

```bash
python3 scripts/make_contact_sheet.py \
  icon-concepts/concept-1.svg icon-concepts/concept-2.svg icon-concepts/concept-3.svg \
  --title "ProjectName — icon concepts" \
  --label "Flat emerald" --label "Faceted indigo" --label "Mono on charcoal"
```

It writes a self-contained sheet (each concept large + a 64/48/32/16px strip for
small-size legibility) using absolute `file://` URLs and `open`s it. Always run
this after producing concepts. Then, in chat, give a one-line note on what
differs and ask which to ship — or whether to iterate or escalate.

## Step 5 — Escalate to Nano Banana Pro (only when needed)

Reach for the generative model when:

- the brief wants a **dimensional / material / illustrative** look (glossy 3D
  tile, soft lighting, painterly or textured mark) that's hard to fake in vector;
- the motif is too **organic or complex** to hand-author cleanly;
- after ~2 SVG iterations it's **still not landing**; or
- the user explicitly wants the **rendered / AI** look.

Do Step 0 first, then generate 3 concepts at 1:1, 2k. Use a **full-bleed** prompt
(see the recipe below) so the tile fills the frame edge-to-edge:

```bash
mkdir -p icon-concepts
higgsfield generate create nano_banana_2 \
  --prompt "App icon for <project>: <one-motif>. Bold flat vector mark, <color/2-stop gradient> tile whose colour reaches ALL FOUR CORNERS of the square (full-bleed square, NOT a rounded sticker on a white background — no white corners, no keyline/border, no margin), thick confident shapes, high contrast, centered with generous padding, no text, crisp edges, premium, legible at 16px, sharp 1:1." \
  --aspect_ratio 1:1 --resolution 2k --wait
# then: curl -fsSL "<result-url>" -o icon-concepts/concept-1.png
```

- `nano_banana_2` is **Nano Banana Pro** (best edges). Naming trap: the catalog's
  display name "Nano Banana 2" is actually the weaker `nano_banana_flash` — don't
  use it. `2k` is plenty (it's the favicon master).
- **Hybrid:** to keep an SVG composition but get a rendered finish, rasterize the
  SVG (Step 6's rasterizer) and pass it as a reference: add `--image comp.png` to
  the `generate create` call.
- Present the results with the same contact sheet (Step 4).

## Step 6 — Finalize: slice the icon set

Once a concept is chosen, run the slicer on the chosen master — **a `.svg` or a
`.png`** — and it produces the full set:

```bash
python3 scripts/make_favicons.py icon-concepts/concept-2.svg \
  --out-dir favicons --name "ProjectName"
```

- **SVG chosen** → ships `favicon.svg` as the primary, rasterizes a 1024 master
  (via macOS `qlmanage`, or Chrome — automatic, no deps), and emits the raster
  fallbacks. `head.html` lists the SVG `<link>` first, `.ico` as fallback.
- **Raster chosen** → same set, no `favicon.svg`.
- Either way you get: `favicon.ico` (16/32/48), `favicon-16/32/48/64.png`,
  `apple-touch-icon.png` (180), `icon-192/512.png`, `icon-1024.png`,
  `site.webmanifest`, and `head.html` (the `<link>` tags to paste into `<head>`).

Tell the user the output dir and that `head.html` drops straight into `<head>`,
served from web root.

## Step 7 — Verify it holds up small

Boldness is a small-size property, so check it there. Two checks:

- **Contrast** (do this *before* finalizing, while you still know the hexes):
  `python3 scripts/contrast_check.py <mark-hex> <tile-hex>` — want ≥7, ideally
  ≥10. A mid-tone mark on a dark tile is the classic trap; bump the mark toward
  white/bright or lighten the tile.
- **Silhouette:** glance at `favicons/favicon-32.png` (and the contact sheet's
  16/32px strip) and confirm the shape still reads. If it goes muddy or thin, the
  motif was too detailed — simplify, thicken, redo.

This is the single most useful quality gate.

## Notes & gotchas

- **SVG editing is one-line.** Want a different brand color or gradient? Edit the
  `stop-color`s in the `.svg` and re-slice — no regeneration, no credits.
- **Rasterizer:** `qlmanage` is built into macOS (no install); Google Chrome is
  the fallback. The slicer picks automatically.
- **Maskable PWA icons:** the generous padding (principle 5) means `icon-512.png`
  survives Android's circular/rounded mask without re-cropping.
- **White corners (raster only):** the model often renders a rounded tile on
  white, leaving white square corners that become white favicon pixels. SVG
  avoids this entirely (transparent corners by construction). If a *chosen*
  raster has white corners, regenerate with the all-four-corners wording above,
  or switch that concept to SVG — don't ship white corners.
- **Transparent glyph variant:** if the user needs a transparent-background mark
  (to sit on their own UI), author the SVG without the `<rect>` tile, or prompt
  the model for "flat vector glyph on transparent background, no tile."
- **Cost (generative only):** 3 concepts at 2k is a few credits; check
  `higgsfield account status` if a run fails. Don't pre-quote cost unasked.
- **Safety:** trademarks/real brands can be rejected (`ip_detected`) — describe
  the motif generically.
- For non-icon work (photos, ads, video, characters), use `higgsfield-generate`.
