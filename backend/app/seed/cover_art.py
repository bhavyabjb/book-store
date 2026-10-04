"""Generates simple, distinct placeholder cover art (SVG) for the
hand-authored "override" books, which don't have a real Open Library
cover since they're invented for the capstone wireframes.

Open Library's own covers are used as-is for every other book; this module
only exists so the 9 override titles don't all collide on one borrowed
cover image.
"""

import html
import textwrap
from pathlib import Path

STATIC_COVERS_DIR = Path(__file__).resolve().parent.parent / "static" / "covers"


def _wrap_title(title: str, width: int = 14) -> list[str]:
    return textwrap.wrap(title, width=width) or [title]


def render_cover_svg(title: str, author: str, bg: str, fg: str) -> str:
    lines = _wrap_title(title.upper())
    line_height = 34
    start_y = 200 - (len(lines) - 1) * line_height / 2

    tspans = "".join(
        f'<tspan x="150" dy="{0 if i == 0 else line_height}">{html.escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="450" viewBox="0 0 300 450">
  <rect width="300" height="450" fill="{bg}"/>
  <rect x="10" y="10" width="280" height="430" fill="none" stroke="{fg}" stroke-opacity="0.25" stroke-width="2"/>
  <text x="150" y="{start_y}" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif"
        font-size="26" font-weight="700" fill="{fg}">{tspans}</text>
  <text x="150" y="400" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="16" letter-spacing="1" fill="{fg}" fill-opacity="0.85">{html.escape(author.upper())}</text>
</svg>"""


def write_cover(slug: str, title: str, author: str, bg: str, fg: str) -> str:
    """Writes the SVG to app/static/covers/{slug}.svg and returns its
    web-accessible relative path ("/static/covers/{slug}.svg")."""
    STATIC_COVERS_DIR.mkdir(parents=True, exist_ok=True)
    svg = render_cover_svg(title, author, bg, fg)
    (STATIC_COVERS_DIR / f"{slug}.svg").write_text(svg, encoding="utf-8")
    return f"/static/covers/{slug}.svg"
