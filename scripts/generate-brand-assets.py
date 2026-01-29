#!/usr/bin/env python
from __future__ import annotations

import argparse
import re
import sys
from io import BytesIO
from pathlib import Path
import shutil


DEFAULT_SPECS = [
    ("android-icon", [36, 48, 72, 96, 144, 192]),
    ("apple-icon", [57, 60, 72, 76, 114, 120, 144, 152, 180]),
    ("favicon", [16, 32, 96]),
    ("ms-icon", [70, 144, 150]),
]

FAVICON_ICO_SIZES = [16, 32, 48]
FAVICON_SVG_SIZE = 48


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate brand icon assets from SVG sources.",
    )
    parser.add_argument(
        "--avatar-svg",
        default=None,
        help="Path to the contracted (avatar) SVG. Defaults to ./logo_thumbnail.svg or brand-assets/logo_thumbnail.svg.",
    )
    parser.add_argument(
        "--extended-light",
        default=None,
        help="Path to the extended light SVG. Defaults to ./logo.svg or brand-assets/logo.svg.",
    )
    parser.add_argument(
        "--extended-dark",
        default=None,
        help="Path to the extended dark SVG. Defaults to ./logo_dark.svg or brand-assets/logo_dark.svg.",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory for generated files.",
    )
    parser.add_argument(
        "--skip-favicon-svg",
        action="store_true",
        help="Do not write favicon.svg (copy of avatar SVG).",
    )
    return parser.parse_args()


def require_packages() -> tuple[object, object]:
    try:
        import cairosvg  # type: ignore
    except Exception:  # pragma: no cover - import error path
        print("Missing dependency: cairosvg", file=sys.stderr)
        print("Install with: python -m pip install cairosvg", file=sys.stderr)
        sys.exit(1)

    try:
        from PIL import Image  # type: ignore
    except Exception:  # pragma: no cover - import error path
        print("Missing dependency: pillow", file=sys.stderr)
        print("Install with: python -m pip install pillow", file=sys.stderr)
        sys.exit(1)

    return cairosvg, Image


def render_png(cairosvg: object, svg_path: Path, out_path: Path, size: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(out_path),
        output_width=size,
        output_height=size,
    )


def render_ico(cairosvg: object, Image: object, svg_path: Path, out_path: Path) -> None:
    images = []
    for size in FAVICON_ICO_SIZES:
        png_bytes = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size,
        )
        image = Image.open(BytesIO(png_bytes))
        images.append(image)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        str(out_path),
        format="ICO",
        sizes=[(size, size) for size in FAVICON_ICO_SIZES],
        append_images=images[1:],
    )


def write_favicon_svg(svg_path: Path, out_path: Path, size: int) -> None:
    content = svg_path.read_text(encoding="utf-8")
    match = re.search(r"<svg\\b[^>]*>", content, flags=re.IGNORECASE)
    if not match:
        shutil.copyfile(svg_path, out_path)
        return

    tag = match.group(0)
    updated = tag

    if re.search(r'\\bwidth="[^"]*"', updated):
        updated = re.sub(r'\\bwidth="[^"]*"', f'width="{size}"', updated)
    else:
        if updated.endswith("/>"):
            updated = updated[:-2] + f' width="{size}"/>'
        else:
            updated = updated[:-1] + f' width="{size}">'

    if re.search(r'\\bheight="[^"]*"', updated):
        updated = re.sub(r'\\bheight="[^"]*"', f'height="{size}"', updated)
    else:
        if updated.endswith("/>"):
            updated = updated[:-2] + f' height="{size}"/>'
        else:
            updated = updated[:-1] + f' height="{size}">'

    content = content[: match.start()] + updated + content[match.end() :]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent

    def resolve_svg(arg_value: str | None, script_name: str, fallback: str) -> Path:
        if arg_value:
            return Path(arg_value)
        local_path = script_dir / script_name
        if local_path.exists():
            return local_path
        return Path(fallback)

    avatar_svg = resolve_svg(args.avatar_svg, "logo_thumbnail.svg", "brand-assets/logo_thumbnail.svg")
    extended_light = resolve_svg(args.extended_light, "logo.svg", "brand-assets/logo.svg")
    extended_dark = resolve_svg(args.extended_dark, "logo_dark.svg", "brand-assets/logo_dark.svg")
    out_dir = Path(args.out_dir)

    if not avatar_svg.exists():
        print("Missing avatar SVG:", file=sys.stderr)
        print(f" - {avatar_svg}", file=sys.stderr)
        return 1

    missing_extended = [path for path in (extended_light, extended_dark) if not path.exists()]
    if missing_extended:
        print("Warning: extended SVGs not found (will not block icon generation):", file=sys.stderr)
        for path in missing_extended:
            print(f" - {path}", file=sys.stderr)

    cairosvg, Image = require_packages()

    generated = []

    for prefix, sizes in DEFAULT_SPECS:
        for size in sizes:
            filename = f"{prefix}-{size}x{size}.png"
            render_png(cairosvg, avatar_svg, out_dir / filename, size)
            generated.append(out_dir / filename)

    render_ico(cairosvg, Image, avatar_svg, out_dir / "favicon.ico")
    generated.append(out_dir / "favicon.ico")

    if not args.skip_favicon_svg:
        write_favicon_svg(avatar_svg, out_dir / "favicon.svg", FAVICON_SVG_SIZE)
        generated.append(out_dir / "favicon.svg")

    print(f"Generated {len(generated)} files in {out_dir.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
