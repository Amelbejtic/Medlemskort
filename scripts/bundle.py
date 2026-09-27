"""
bundle.py – laver én selvstændig HTML-fil med data indbygget.
Bruges til deling og til indlejring i WordPress, hvor der ikke er en data/-mappe.

Kør:  python scripts/bundle.py      ->  dist/medlemskort.html
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent if Path(__file__).parent.name == "scripts" else Path(__file__).parent
data = {
    "members": json.loads((ROOT / "data/members.json").read_text("utf-8")),
    "orgs":    json.loads((ROOT / "data/orgs.json").read_text("utf-8")),
    "geo":     json.loads((ROOT / "data/kommuner.geojson").read_text("utf-8")),
}
html = (ROOT / "index.html").read_text("utf-8")
# "</" escapes, så et navn med "</script>" aldrig kan bryde ud af script-tagget
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
marker = '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/'
assert marker in html, "Kunne ikke finde d3-script-tagget i index.html"
html = html.replace(marker, f"<script>window.EMBEDDED_DATA={payload};</script>\n{marker}", 1)

out = ROOT / "dist/medlemskort.html"; out.parent.mkdir(exist_ok=True)
out.write_text(html, "utf-8")
print(f"Skrev {out} ({out.stat().st_size/1024:.0f} KB)")
