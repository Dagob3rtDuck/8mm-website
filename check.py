#!/usr/bin/env python3
"""Controleert de gebouwde site in dist/ (draai eerst python3 build.py).

  python3 check.py

Meldt: dubbele of te lange titels, ontbrekende of te lange omschrijvingen, pagina's zonder
precies één H1, afbeeldingen zonder alt-tekst en interne links die nergens naartoe wijzen.
"""
import html, re, sys
from pathlib import Path
from urllib.parse import urlparse

DIST = Path(__file__).parent / "dist"
paginas = sorted(DIST.rglob("*.html"))
if not paginas:
    sys.exit("Geen dist/ gevonden. Draai eerst: python3 build.py")

def url_van(pad):
    r = pad.relative_to(DIST).as_posix()
    if r == "index.html":
        return "/"
    return "/" + (r[:-len("/index.html")] + "/" if r.endswith("/index.html") else r)

def bestaat(pad):
    pad = pad.split("?")[0]
    doel = DIST / pad.lstrip("/")
    return doel.is_file() or (doel / "index.html").is_file()

problemen, titels = [], {}
for f in paginas:
    u = url_van(f)
    h = f.read_text(encoding="utf-8")
    zichtbaar = re.sub(r"<(script|style)\b.*?</\1>", "", h, flags=re.S)
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    titel = html.unescape(m.group(1)).strip() if m else ""
    if not titel:
        problemen.append(f"{u}: geen titel")
    else:
        titels.setdefault(titel, []).append(u)
        if len(titel) > 60:
            problemen.append(f"{u}: titel is {len(titel)} tekens (max. 60): {titel}")
    d = re.search(r'<meta name="description" content="(.*?)"', h, re.S)
    omschr = html.unescape(d.group(1)).strip() if d else ""
    if not omschr:
        problemen.append(f"{u}: geen omschrijving")
    elif len(omschr) > 155:
        problemen.append(f"{u}: omschrijving is {len(omschr)} tekens (max. 155)")
    n1 = len(re.findall(r"<h1\b", zichtbaar))
    if n1 != 1:
        problemen.append(f"{u}: {n1} H1-koppen (moet er precies 1 zijn)")
    for img in re.findall(r"<img\b[^>]*>", zichtbaar):
        if not re.search(r"\balt=", img):
            problemen.append(f"{u}: afbeelding zonder alt-tekst: {img[:90]}")
    verwijzingen = re.findall(r'(?:href|src)="([^"]+)"', zichtbaar) + re.findall(r"url\(([^)\"']+)\)", zichtbaar)
    for l in set(verwijzingen):
        p = urlparse(l)
        if p.scheme or l.startswith(("#", "mailto:", "tel:", "data:")):
            continue
        if not l.startswith("/"):
            problemen.append(f"{u}: relatieve verwijzing {l} (werkt niet in een map)")
        elif ".html" in p.path:
            problemen.append(f"{u}: verwijzing naar .html: {l}")
        elif not bestaat(p.path):
            problemen.append(f"{u}: kapotte link {l}")

for titel, waar in titels.items():
    if len(waar) > 1:
        problemen.append(f"dubbele titel '{titel}' op: {', '.join(waar)}")

print(f"{len(paginas)} pagina's gecontroleerd")
if problemen:
    print("Gevonden:")
    for p in problemen:
        print("  -", p)
    sys.exit(1)
print("Niets gevonden.")
