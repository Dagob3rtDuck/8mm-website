#!/usr/bin/env python3
"""Bouwt de 8MM-site.

  python3 build.py           -> dist/     (de echte site voor GitHub Pages)
  python3 build.py preview   -> preview/  (voorbeeld met oranje balk, formulier verstuurt niets)

Alle teksten die vaak veranderen (video's, contactgegevens) staan in site.json.

Recensies en FAQ staan nu niet op de site. De code is er nog: zet in site.json een lijst terug
en de sectie verschijnt vanzelf (zonder lijst blijft hij weg).
  "recensies": [{"citaat": "...", "naam": "...", "functie": "...", "bedrijf": "..."}]
  "faq": [{"vraag": "...", "antwoord": "..."}]
"""
import html, json, shutil, sys, re, datetime
from pathlib import Path

ROOT = Path(__file__).parent
PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
OUT = ROOT / ("preview" if PREVIEW else "dist")
S = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
CSS = (ROOT / "src/style.css").read_text(encoding="utf-8")
JS = (ROOT / "src/main.js").read_text(encoding="utf-8")
e = html.escape

IMG = "img/" if PREVIEW else "/img/"   # live staan pagina's in mappen, dus beeldpaden beginnen met /

def link(naam):
    """Live: nette adressen (/videos/, map met index.html). Voorbeeld: bestandsnamen (videos.html), zodat je ze ook zonder server kunt openen."""
    if PREVIEW:
        return "./" if naam == "" else f"{naam}.html"
    return "/" if naam == "" else f"/{naam}/"

FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..700"
         "&family=IBM+Plex+Mono:wght@500&display=swap")

PIJL = '<span class="pijl" aria-hidden="true">&rarr;</span>'

def link_live(naam):
    return "/" if naam == "" else f"/{naam}/"

def pagina(naam, titel, beschrijving, inhoud, actief=None, lang="nl", extra_ld=""):
    canon = S["domein"] + link_live(naam)
    huidig = ' aria-current="page"'
    nav = "".join(
        f'<li><a href="{link(n)}"{huidig if actief == n else ""}>{t}</a></li>'
        for n, t in (("", "Home"), ("videos", "Video's"), ("contact", "Contact")))
    balk = ('<div class="preview-balk">Voorbeeld, nog niet live. Lege videovakken en gestippelde kaders wachten op content.</div>'
            if PREVIEW else "")
    ld = ""
    if naam == "":
        ld = '<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "ProfessionalService", "name": S["bedrijf"],
            "areaServed": {"@type": "Country", "name": "Nederland"},
            "url": S["domein"], "email": S["email"], "image": S["domein"] + "/img/og.jpg",
            "address": {"@type": "PostalAddress", "streetAddress": S["adres"], "postalCode": S["postcode_plaats"][:7],
                        "addressLocality": "Harderwijk", "addressCountry": "NL"},
            "sameAs": [f"https://www.instagram.com/{S['instagram']}/"] + ([S["youtube_kanaal"]] if S.get("youtube_kanaal") else [])}, ensure_ascii=False) + "</script>"
    ld += extra_ld
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titel)}</title>
<meta name="description" content="{e(beschrijving)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(titel)}">
<meta property="og:description" content="{e(beschrijving)}">
<meta property="og:image" content="{S['domein']}/img/og.jpg">
<meta property="og:url" content="{canon}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0a0a0a">
<link rel="icon" type="image/png" href="{IMG}favicon.png">
<link rel="apple-touch-icon" href="{IMG}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>{CSS}</style>
{ld}
</head>
<body>
{balk}
<header class="kop">
  <div class="wrap">
    <a class="merk" href="{link('')}"><img src="{IMG}logo-wit.png" alt="{e(S['bedrijf'])}" width="64" height="42"></a>
    <nav aria-label="Hoofdmenu"><ul>{nav}</ul></nav>
  </div>
</header>
<main>
{inhoud}
</main>
{footer()}
<script>{JS}</script>
</body>
</html>
"""

def footer():
    return f"""<footer>
  <div class="wrap">
    <div class="voet">
      <div>
        <img src="{IMG}logo-wit.png" alt="{e(S['bedrijf'])}" width="64" height="42" loading="lazy">
        <p>{e(S['slogan'])}</p>
      </div>
      <div>
        <h3>Contact</h3>
        <ul>
          <li><a href="mailto:{S['email']}">{S['email']}</a></li>
          <li>{e(S['adres'])}<br>{e(S['postcode_plaats'])}</li>
          <li><a href="https://www.instagram.com/{S['instagram']}/" rel="noopener" target="_blank">Instagram</a></li>
        </ul>
      </div>
      <div>
        <h3>Info</h3>
        <ul>
          <li><a href="{link('privacy')}">Privacy</a></li>
          <li><a href="{link('terms')}">Terms</a></li>
          <li><a href="{link('agent')}">Mark Agent</a></li>
        </ul>
      </div>
    </div>
    <div class="copy"><span>&copy; 2017&ndash;2026 8MM Film Productions</span><span>KVK {S['kvk']}</span></div>
  </div>
</footer>"""

def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")

def video(titel):
    return next((v for v in S["videos"] if v["titel"] == titel), None)

def categorie(key):
    return next((c for c in S.get("categorieen", []) if c["key"] == key), None)

def label(key, klikbaar=True):
    c = categorie(key)
    if not c:
        return ""
    stijl = f'style="--kleur:{c["kleur"]}"'
    if klikbaar:
        return f'<a class="cat" {stijl} href="{link("videos")}#{c["key"]}">{e(c["naam"])}</a>'
    return f'<span class="cat" {stijl}>{e(c["naam"])}</span>'

def aanvullen(t):
    return f'<span class="aanvullen">AANVULLEN: {e(t)}</span>'

# ---------- onderdelen ----------

def tegel(v, met_tekst):
    titel = e(v["titel"])
    if v.get("youtube") and PREVIEW:
        yid = e(v["youtube"])
        beeld = (f'<a class="leeg yt-link" href="https://www.youtube.com/watch?v={yid}" target="_blank" rel="noopener">'
                 f'<span class="speel"></span><span>Bekijk op YouTube</span></a>')
    elif v.get("youtube"):
        yid = e(v["youtube"])
        beeld = (f'<img src="https://i.ytimg.com/vi/{yid}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">'
                 f'<button type="button" data-yt="{yid}" aria-label="Speel video af: {titel}"><span class="speel"></span></button>')
    else:
        beeld = '<div class="leeg"><span>Video volgt</span></div>'
    if not met_tekst:
        tekst = ""
    elif v.get("tekst"):
        tekst = f'<p>{e(v["tekst"])}</p>'
    else:
        tekst = f'<p>{aanvullen("korte omschrijving van deze video")}</p>' if PREVIEW else ""
    ondertitel = v.get("sub") or (v["klant"] if v.get("klant") != v["titel"] else "")
    sub = f'<span class="klant">{e(ondertitel)}</span>' if ondertitel else ""
    tc = f'<span class="tijdcode">{e(v["duur"])}</span>' if v.get("duur") else ""
    return f"""<article class="tegel" id="{slug(v['titel'])}" data-cat="{e(v.get('categorie', ''))}">
  <div class="beeld">{beeld}{tc}</div>
  <div class="tegel-info">{label(v.get('categorie'))}<h3>{titel}</h3>{sub}{tekst}</div>
</article>"""

def videogrid(met_tekst):
    if met_tekst:
        return '<div class="grid ruim">' + "".join(tegel(v, True) for v in S["videos"]) + "</div>"
    # home: video's die al als uitgelicht project staan, laten we hier weg. Max. 5 video's + een doorlinktegel = 3x2.
    in_cases = {c.get("video") for c in S.get("cases", [])}
    lijst = [v for v in S["videos"] if v["titel"] not in in_cases][:5]
    return '<div class="grid drie">' + "".join(tegel(v, False) for v in lijst) + alle_tegel() + "</div>"

def alle_tegel():
    n = len(S["videos"])
    return f"""<a class="tegel tegel-alle" href="{link('videos')}">
  <div class="beeld"><div class="alle-inhoud"><span class="alle-getal">{n}</span><span class="label">video&rsquo;s</span></div></div>
  <div class="tegel-info"><h3>Alle projecten</h3><span class="klant">Bekijk alle {n} video&rsquo;s {PIJL}</span></div>
</a>"""

def werkmethode():
    fotos = ["stap-kennismaking", "stap-productie", "stap-montage", "stap-oplevering"]
    stappen = "".join(
        f'<li style="--i:{i}">'
        f'<div class="clip" style="--foto:url({IMG}{fotos[i % 4]}.webp)"><span>V1 &middot; {e(s["titel"])}</span></div>'
        f'<div class="audio" aria-hidden="true"></div>'
        f'<h3>{e(s["titel"])}</h3><p>{e(s["tekst"])}</p>'
        f'<span class="levert">{e(s.get("levert", ""))}</span></li>'
        for i, s in enumerate(S["werkmethode"]))
    return f"""<section class="methode" id="werkmethode">
  <div class="wrap">
    <div class="over">
      <div class="over-tekst">
        <span class="label">Over 8MM</span>
        <h2>Onze werk&shy;methode</h2>
        <p>8MM Film Productions werd in 2017 opgericht door Mark Jansen. Vanuit Harderwijk maken we bedrijfsfilms, vacaturevideo's, aftermovies, projectvastleggingen en livestreams voor bedrijven, organisaties en evenementen.</p>
        <p>We denken mee vanaf het eerste idee en bewaken de kwaliteit tot de laatste export. Jij vertelt wat je wilt laten zien, wij zorgen dat het verhaal staat.</p>
      </div>
      <img src="{IMG}mark.webp" alt="Mark Jansen aan het filmen met een camera op gimbal" loading="lazy" width="1000" height="771">
    </div>
    <div class="tijdlijn">
      <div class="liniaal" aria-hidden="true"><span>00:00</span><span>00:10</span><span>00:20</span><span>00:30</span></div>
      <ol class="stappen">{stappen}</ol>
      <div class="afspeelkop" aria-hidden="true"></div>
    </div>
  </div>
</section>"""

def diensten():
    rijen = ""
    for d in S.get("diensten", []):
        aantal = sum(1 for v in S["videos"] if v.get("categorie") == d.get("categorie"))
        if aantal:
            doel = f'{link("videos")}#{d["categorie"]}'
            actie = f'Bekijk {aantal} video{"" if aantal == 1 else "&rsquo;s"} {PIJL}'
        else:
            doel, actie = link("contact"), f"Vraag ernaar {PIJL}"
        rijen += (f'<li><a class="dienst" href="{doel}" style="--kleur:{(categorie(d.get("categorie")) or {}).get("kleur", "#888")}">'
                  f'<h3><span class="stip" aria-hidden="true"></span>{e(d["titel"])}</h3><p>{e(d["tekst"])}</p>'
                  f'<span class="tekstlink">{actie}</span></a></li>')
    return f"""<section class="diensten-sectie" id="diensten">
  <div class="wrap">
    <div class="sectie-kop"><div><span class="label">Wat we maken</span><h2>Van bedrijfsfilm tot meercamera</h2></div></div>
    <ul class="diensten">{rijen}</ul>
  </div>
</section>"""

def case_beeld(v, foto, titel):
    """Grote video in een uitgelicht project. Zelfde klik-om-te-laden als de videotegels."""
    yid = e(v.get("youtube", ""))
    tc = f'<span class="tijdcode">{e(v["duur"])}</span>' if v.get("duur") else ""
    if not yid:
        return '<div class="beeld case-video"><div class="leeg"><span>Video volgt</span></div></div>'
    if PREVIEW:
        return (f'<div class="beeld case-video"><a class="leeg yt-link" href="https://www.youtube.com/watch?v={yid}" target="_blank" rel="noopener">'
                f'<span class="speel"></span><span>Bekijk op YouTube</span></a></div>')
    if foto:
        plaatje = f'<img src="{IMG}{e(foto)}" alt="" loading="lazy" width="1280" height="720">'
    else:  # YouTube-still; main.js valt terug op hqdefault als er geen maxresdefault is
        plaatje = (f'<img src="https://i.ytimg.com/vi/{yid}/maxresdefault.jpg" data-fallback="https://i.ytimg.com/vi/{yid}/hqdefault.jpg" '
                   f'alt="" loading="lazy" width="1280" height="720">')
    return (f'<div class="beeld case-video">{plaatje}'
            f'<button type="button" data-yt="{yid}" aria-label="Speel video af: {e(titel)}"><span class="speel"></span></button>{tc}</div>')

def cases():
    items = [c for c in S.get("cases", []) if video(c.get("video", ""))]
    if not items:
        return ""
    tabs = panelen = ""
    for i, c in enumerate(items):
        v = video(c["video"])
        sl = slug(c["video"])
        cat = categorie(v.get("categorie"))
        kleur = f' style="--kleur:{cat["kleur"]}"' if cat else ""
        tabs += (f'<button type="button" role="tab" class="case-tab" id="tab-{sl}" aria-controls="case-{sl}" '
                 f'aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}"{kleur}>'
                 f'<span class="tab-naam">{e(c.get("tab") or v["titel"])}</span>{label(v.get("categorie"), False)}</button>')
        stappen = "".join(
            f'<li><b>{e(s["titel"])}</b><span>{e(s.get("tekst", ""))}</span></li>'
            for s in c.get("stappen", []) if s.get("titel"))
        chips = "".join(f"<li>{e(x)}</li>" for x in c.get("ingezet", []) if x)
        titel = c.get("titel") or v["titel"]
        panelen += f"""<div class="case-paneel" id="case-{sl}" aria-labelledby="tab-{sl}">
  {case_beeld(v, c.get("foto"), titel)}
  <div class="case-tekst">
    <h3 class="case-titel">{e(titel)}</h3>
    {f'<p class="case-intro">{e(c["intro"])}</p>' if c.get("intro") else ""}
    {f'<div class="case-blok"><span class="label">Zo pakten we het aan</span><ol class="case-stappen">{stappen}</ol></div>' if stappen else ""}
    {f'<div class="case-blok"><span class="label">Ingezet</span><ul class="case-ingezet">{chips}</ul></div>' if chips else ""}
  </div>
</div>
"""
    return f"""<section class="cases-sectie" id="cases">
  <div class="wrap">
    <div class="sectie-kop"><div><span class="label">Uitgelicht</span><h2>Zo pakken we het aan</h2></div></div>
    <div class="cases">
      <div class="case-tabs" role="tablist" aria-label="Uitgelichte projecten" hidden>{tabs}</div>
      {panelen}
    </div>
  </div>
</section>"""

def faq():
    items = [f for f in S.get("faq", []) if f.get("antwoord") or PREVIEW]
    if not items:
        return ""
    lijst = "".join(
        f'<details><summary>{e(f["vraag"])}</summary><div class="antwoord">'
        + (f'<p>{e(f["antwoord"])}</p>' if f.get("antwoord") else f'<p>{aanvullen("jouw antwoord")}</p>')
        + '</div></details>' for f in items)
    return f"""<section class="faq-sectie" id="vragen">
  <div class="wrap faq-grid">
    <div class="sectie-kop"><div><span class="label">Vragen</span><h2>Veelgestelde vragen</h2>
      <p class="lead">Staat je vraag er niet bij? <a class="tekstlink" href="{link('contact')}">Stel hem gerust</a>.</p></div></div>
    <div class="faq">{lijst}</div>
  </div>
</section>"""

def recensies():
    items = S.get("recensies") or []
    if items:
        kaarten = "".join(
            f'<figure class="recensie"><blockquote>&ldquo;{e(r["citaat"])}&rdquo;</blockquote>'
            f'<figcaption><b>{e(r["naam"])}</b>{e(r.get("functie", ""))}{", " if r.get("functie") else ""}{e(r["bedrijf"])}</figcaption></figure>'
            for r in items)
    else:
        kaarten = ""
    logos = "".join(
        f'<div><img src="{IMG}klanten/{k["bestand"]}" alt="{e(k["naam"])}" loading="lazy"></div>' for k in S["klanten"])
    blok_rec = f'<div class="recensies">{kaarten}</div>' if kaarten else ""
    kop = "Wat klanten zeggen" if kaarten else "Zij gingen je voor"
    return f"""<section class="klanten-sectie" id="klanten">
  <div class="wrap">
    <div class="sectie-kop"><div><span class="label">Klanten</span><h2>{kop}</h2></div></div>
    {blok_rec}
    <div class="logos">{logos}</div>
  </div>
</section>"""

def contactblok(kop="h2"):
    preview_attr = " data-preview" if PREVIEW else ""
    action = "" if PREVIEW else ' action="https://api.web3forms.com/submit" method="POST"'
    key = S.get("web3forms_key") or "WEB3FORMS_KEY_ONTBREEKT"
    return f"""<div class="contact-grid">
  <div class="contact-links">
    <div class="kop-blok">
      <span class="label">Contact</span>
      <{kop}>Vertel wat je wilt maken.</{kop}>
      <p class="lead">Een bedrijfsfilm, vacaturevideo, aftermovie of livestream? Vertel kort wat je in gedachten hebt, dan nemen we snel contact met je op.</p>
    </div>
    <dl class="gegevens">
      <div><dt class="label">Mail</dt><dd><a href="mailto:{S['email']}" data-mail-tekst>{S['email']}</a><button type="button" class="kopieer" data-kopieer="{S['email']}">Kopieer</button></dd></div>
      <div><dt class="label">Instagram</dt><dd><a href="https://www.instagram.com/{S['instagram']}/" rel="noopener" target="_blank">@{S['instagram']}</a></dd></div>
      <div><dt class="label">Adres</dt><dd>{e(S['adres'])}<br>{e(S['postcode_plaats'])}</dd></div>
      <div><dt class="label">KVK</dt><dd>{S['kvk']}</dd></div>
    </dl>
  </div>
  <form id="contactformulier"{action}{preview_attr}>
    <input type="hidden" name="access_key" value="{key}">
    <input type="checkbox" name="botcheck" class="honing" tabindex="-1" autocomplete="off" aria-hidden="true">
    <div class="rij">
      <div class="veld"><label for="naam">Naam</label><input id="naam" name="naam" autocomplete="name" required></div>
      <div class="veld"><label for="email">E-mail</label><input id="email" name="email" type="email" autocomplete="email" required></div>
    </div>
    <div class="rij">
      <div class="veld"><label for="telefoon">Telefoon (optioneel)</label><input id="telefoon" name="telefoon" type="tel" autocomplete="tel"></div>
      <div class="veld"><label for="soort">Soort video</label>
        <select id="soort" name="soort">
          <option>Bedrijfsfilm</option><option>Vacaturevideo</option><option>Aftermovie of evenement</option>
          <option>Livestream</option><option>Iets anders</option>
        </select></div>
    </div>
    <div class="veld"><label for="bericht">Waar gaat je video over?</label><textarea id="bericht" name="bericht" required></textarea></div>
    <p class="akkoord">We gebruiken je gegevens alleen om op je aanvraag te reageren. Zie de <a href="{link('privacy')}">privacyverklaring</a>.</p>
    <div class="form-voet">
      <button class="knop" type="submit">Verstuur aanvraag {PIJL}</button>
      <span class="vangnet">Of mail direct naar <a href="mailto:{S['email']}?subject=Aanvraag%20video">{S['email']}</a></span>
    </div>
    <p id="formstatus" class="status" role="status" hidden></p>
  </form>
</div>"""

# ---------- pagina's ----------

def home():
    return pagina("", "Videoproductie Harderwijk | 8MM Film Productions",
        "Videoproductie in Harderwijk sinds 2017: bedrijfsfilms, vacaturevideo's, aftermovies, projectvastleggingen en livestreams voor bedrijven en evenementen.",
        f"""<section class="hero">
  <div class="wrap">
    <div class="doek">
      <img src="{IMG}hero.webp" alt="Filmset op straat: camera op statief, geluidsman met boom en een geïnterviewde" width="2200" height="1467" fetchpriority="high">
      <div class="doek-meta"><span class="rec">Harderwijk</span><span>Sinds 2017</span></div>
    </div>
    <div class="hero-tekst">
      <div class="hero-kop">
        <h1 class="hero-h1">Videoproductie in Harderwijk</h1>
        <p class="slogan">{e(S['slogan'])}</p>
      </div>
      <div class="rechts">
        <p class="lead">{e(S['kop'])} Van concept tot eindmontage nemen we het complete traject uit handen, voor bedrijven, organisaties en evenementen.</p>
        <div class="knoppen">
          <a class="knop" href="{link('contact')}">Vraag een video aan {PIJL}</a>
          <a class="knop licht" href="#projecten">Bekijk ons werk</a>
        </div>
      </div>
    </div>
  </div>
</section>
<section id="projecten">
  <div class="wrap">
    <div class="sectie-kop">
      <div><span class="label">Projecten</span><h2>Ons werk</h2></div>
      <a class="tekstlink" href="{link('videos')}">Alle projecten {PIJL}</a>
    </div>
    {videogrid(False)}
  </div>
</section>
{cases()}
{diensten()}
{werkmethode()}
{recensies()}
{faq()}
<section class="contact-sectie" id="contact"><div class="wrap">{contactblok()}</div></section>""", actief="")

def video_ld():
    items = []
    for v in S["videos"]:
        if not v.get("youtube"):
            continue
        yid = v["youtube"]
        o = {"@context": "https://schema.org", "@type": "VideoObject", "name": v["titel"],
             "description": v.get("tekst") or f'{v["titel"]}, een video van {S["bedrijf"]}.',
             "thumbnailUrl": f"https://i.ytimg.com/vi/{yid}/hqdefault.jpg",
             "embedUrl": f"https://www.youtube-nocookie.com/embed/{yid}",
             "contentUrl": f"https://www.youtube.com/watch?v={yid}"}
        if v.get("datum"):  # uploaddatum, JJJJ-MM-DD. Google vraagt erom; zonder datum laten we het veld weg
            o["uploadDate"] = v["datum"]
        items.append('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>")
    return "".join(items)

def videos():
    knoppen = '<button type="button" class="filter" data-filter="" aria-pressed="true">Alles</button>' + "".join(
        f'<button type="button" class="filter" data-filter="{c["key"]}" aria-pressed="false" style="--kleur:{c["kleur"]}">'
        f'<span class="stip" aria-hidden="true"></span>{e(c["naam"])}</button>'
        for c in S.get("categorieen", []) if any(v.get("categorie") == c["key"] for v in S["videos"]))
    return pagina("videos", "Video's en projecten | 8MM Film Productions",
        "Bekijk onze bedrijfsfilms, vacaturevideo's, aftermovies en meercamera-opnames. Videoproductie uit Harderwijk voor bedrijven en evenementen.",
        f"""<section>
  <div class="wrap">
    <div class="sectie-kop"><div><span class="label">Projecten</span><h1>Video's</h1>
      <p class="lead">Een selectie uit ons werk van de afgelopen jaren. Filter op soort video of klik op een video om hem af te spelen.</p></div></div>
    <div class="filters" role="group" aria-label="Filter op soort video">{knoppen}</div>
    {videogrid(True)}
  </div>
</section>""", actief="videos", extra_ld=video_ld())

def contact():
    return pagina("contact", "Contact en offerte | 8MM Film Productions",
        "Een video laten maken in Harderwijk of omgeving? Vertel wat je wilt maken, dan nemen we snel contact met je op voor een gesprek en offerte.",
        f'<section><div class="wrap">{contactblok("h1")}</div></section>' + faq(), actief="contact")

TAAL = lambda: '<div class="taal"><a href="#nl">Nederlands</a><a href="#en">English</a></div>'
SCOPES_NL = ('<ul><li><b>Gmail (alleen lezen)</b>: e-mails en bijlagen zoeken en lezen. De app kan geen e-mails versturen, concepten maken, labelen, wijzigen of verwijderen.</li>'
             '<li><b>Google Agenda</b>: op Marks uitdrukkelijke verzoek een nieuwe afspraak aanmaken en daarbij eventueel uitnodigingen versturen aan gasten die Mark zelf opgeeft. De app wijzigt of verwijdert geen bestaande afspraken.</li></ul>'
             '<p>De app vraagt alleen toegang tot deze onderdelen. Komt er later iets bij, dan passen we deze pagina eerst aan.</p>')
SCOPES_EN = ('<ul><li><b>Gmail (read-only)</b>: search and read email and attachments. The app cannot send, draft, label, modify or delete email.</li>'
             '<li><b>Google Calendar</b>: at Mark\'s explicit request, create a new event and optionally send invitations to guests Mark specifies himself. The app does not modify or delete existing events.</li></ul>'
             '<p>The app requests access to these services only. If this changes, this page will be updated first.</p>')
BIJGEWERKT = "12 oktober 2026"
UPDATED = "October 12, 2026"

def agent():
    return pagina("agent", "Mark Agent | 8MM Film Productions",
        "Mark Agent is de persoonlijke assistent-app van Mark Jansen (8MM Film Productions), alleen voor eigen gebruik.",
        f"""<div class="wrap doc">
  <span class="label">App</span>
  <h1>Mark Agent</h1>
  {TAAL()}
  <section id="nl">
    <h2>Wat is Mark Agent?</h2>
    <p>Mark Agent is een persoonlijke assistent die Mark Jansen, eigenaar van 8MM Film Productions, voor zichzelf heeft gebouwd. De app draait op Marks eigen computer en helpt hem zijn mail en agenda bij te houden. Mark stuurt de app aan via berichten, bijvoorbeeld om een mail terug te zoeken of een afspraak in te plannen.</p>
    <p>De app wordt niet aangeboden aan anderen. Alleen Mark logt in, met zijn eigen Google-accounts.</p>
    <div class="app-kaart">
      <h3>Wat de app met Google doet</h3>
      <div>{SCOPES_NL}</div>
      <p>Een afspraak wordt pas aangemaakt nadat Mark die heeft bevestigd. Google-gegevens worden niet verkocht, niet gebruikt voor reclame en niet gebruikt om AI-modellen te trainen.</p>
    </div>
    <p>Lees de <a href="{link('privacy')}#mark-agent">privacyverklaring</a> en de <a href="{link('terms')}">gebruiksvoorwaarden</a>. Vragen? Mail <a href="mailto:{S['email']}">{S['email']}</a>.</p>
  </section>
  <hr class="lijn">
  <section id="en" lang="en">
    <h2>What is Mark Agent?</h2>
    <p>Mark Agent is a personal assistant built by Mark Jansen, owner of 8MM Film Productions, for his own use. It runs on Mark's own computer and helps him keep track of his email and calendar. Mark controls the app through messages, for example to find an email or schedule an event.</p>
    <p>The app is not offered to anyone else. Only Mark signs in, with his own Google accounts.</p>
    <div class="app-kaart">
      <h3>What the app does with Google</h3>
      <div>{SCOPES_EN}</div>
      <p>An event is only created after Mark confirms it. Google user data is not sold, not used for advertising and not used to train AI models.</p>
    </div>
    <p>Read the <a href="{link('privacy')}#mark-agent-en">privacy policy</a> and the <a href="{link('terms')}#en">terms of service</a>. Questions? Email <a href="mailto:{S['email']}">{S['email']}</a>.</p>
  </section>
</div>""")

def privacy():
    return pagina("privacy", "Privacy | 8MM Film Productions",
        "Privacyverklaring van 8MM Film Productions en de app Mark Agent.",
        f"""<div class="wrap doc">
  <span class="label">Privacy</span>
  <h1>Privacyverklaring</h1>
  <p class="datum">Bijgewerkt op {BIJGEWERKT}</p>
  {TAAL()}
  <section id="nl">
    <h2>Wie zijn we</h2>
    <p>8MM Film Productions (Mark Jansen), {e(S['adres'])}, {e(S['postcode_plaats'])}, KVK {S['kvk']}. Vragen over privacy mail je naar <a href="mailto:{S['email']}">{S['email']}</a>.</p>

    <h2>Website</h2>
    <h3>Contactformulier</h3>
    <p>Vul je het contactformulier in, dan ontvangen we je naam, e-mailadres, eventueel je telefoonnummer, het soort video en je bericht. Het formulier wordt via Web3Forms doorgestuurd naar ons mailadres. We gebruiken deze gegevens alleen om op je aanvraag te reageren en, als we samen een opdracht doen, voor die opdracht.</p>
    <p>We bewaren je bericht zolang dat nodig is voor je aanvraag. Komt er geen opdracht, dan verwijderen we het uiterlijk na twee jaar. Gegevens die we voor de boekhouding moeten bewaren, bewaren we zolang de wet dat vraagt.</p>
    <h3>Video's</h3>
    <p>Onze video's staan op YouTube. Een video wordt pas geladen als je erop klikt. Vanaf dat moment kan YouTube (Google) cookies plaatsen en gegevens verwerken volgens zijn eigen privacybeleid.</p>
    <h3>Cookies en statistieken</h3>
    <p>Deze website plaatst zelf geen cookies en gebruikt geen statistieken- of advertentiediensten. De site wordt gehost via GitHub Pages. GitHub kan technische gegevens zoals je IP-adres tijdelijk vastleggen om de site veilig te laten werken.</p>

    <h2 id="mark-agent">App: Mark Agent</h2>
    <p>Mark Agent is een persoonlijke assistent-app die alleen door Mark Jansen wordt gebruikt, met zijn eigen Google-accounts. Er zijn geen andere gebruikers.</p>
    <h3>Welke Google-gegevens</h3>
    <div>{SCOPES_NL}</div>
    <h3>Waarvoor</h3>
    <p>Alleen om Mark te helpen met zijn mail en agenda, op zijn eigen verzoek. Een afspraak wordt pas aangemaakt nadat Mark die heeft bevestigd. Van gasten die Mark uitnodigt, wordt alleen het e-mailadres gebruikt om de uitnodiging te versturen.</p>
    <h3>Waar de gegevens heen gaan</h3>
    <ul>
      <li>De app draait op Marks eigen computer. De inloggegevens voor Google (tokens) staan alleen daar.</li>
      <li>Om Marks vragen te begrijpen en te beantwoorden, stuurt de app alleen de gegevens die daarvoor nodig zijn naar een AI-dienst (Claude van Anthropic).</li>
      <li>Antwoorden van de app komen bij Mark binnen via zijn eigen berichtenkanaal.</li>
      <li>Niemand anders dan Mark krijgt de gegevens te zien. Ze worden niet verkocht, niet gebruikt voor reclame en niet gedeeld met anderen dan hierboven genoemd.</li>
    </ul>
    <h3>Bewaren en verwijderen</h3>
    <p>Gegevens uit Gmail en Google Agenda worden niet langer bewaard dan nodig om Marks verzoek uit te voeren. Toegang intrekken kan altijd via <a href="https://myaccount.google.com/permissions" rel="noopener" target="_blank">myaccount.google.com/permissions</a>. De tokens werken dan niet meer en worden ook van Marks computer verwijderd.</p>
    <p>Het gebruik en doorgeven van gegevens die Mark Agent van Google API's ontvangt, voldoet aan het <a href="https://developers.google.com/terms/api-services-user-data-policy" rel="noopener" target="_blank">Google API Services User Data Policy</a>, inclusief de Limited Use-eisen. Gegevens van Google worden niet gebruikt om algemene AI- of machine-learningmodellen te ontwikkelen, verbeteren of trainen.</p>

    <h2>Je rechten</h2>
    <p>Je mag ons vragen welke gegevens we van je hebben, ze laten aanpassen of laten verwijderen. Mail daarvoor naar <a href="mailto:{S['email']}">{S['email']}</a>. Ben je het niet eens met hoe we met je gegevens omgaan, dan kun je een klacht indienen bij de Autoriteit Persoonsgegevens.</p>
  </section>
  <hr class="lijn">
  <section id="en" lang="en">
    <h2>Privacy policy (English)</h2>
    <p class="datum">Last updated {UPDATED}</p>
    <p>8MM Film Productions (Mark Jansen), {e(S['adres'])}, {e(S['postcode_plaats'])}, the Netherlands, Chamber of Commerce no. {S['kvk']}. Contact: <a href="mailto:{S['email']}">{S['email']}</a>.</p>
    <h3>Website</h3>
    <p>The contact form sends your name, email address, optional phone number, video type and message to us via Web3Forms. We use it only to reply to your request. The site sets no cookies of its own and uses no analytics. Videos are hosted on YouTube and load only when you click them. The site is hosted on GitHub Pages.</p>
    <h2 id="mark-agent-en">Mark Agent</h2>
    <p>Mark Agent is a personal assistant app used only by its developer, Mark Jansen, with his own Google accounts. It has no other users.</p>
    <h3>Google data accessed</h3>
    <div>{SCOPES_EN}</div>
    <h3>How the data is used</h3>
    <p>Google user data is used only to help Mark with his email and calendar, at his request. An event is only created after Mark confirms it. For guests Mark invites, only their email address is used to send the invitation.</p>
    <h3>Where the data goes</h3>
    <ul>
      <li>The app runs on Mark's own computer. The Google access tokens are stored only there.</li>
      <li>To understand and answer Mark's requests, the app sends only the data needed for that request to an AI service (Claude by Anthropic).</li>
      <li>The app's replies reach Mark through his own messaging channel.</li>
      <li>No one other than Mark sees the data. It is not sold, not used for advertising and not shared with anyone other than described above.</li>
    </ul>
    <h3>Storage and deletion</h3>
    <p>Data from Gmail and Google Calendar is kept no longer than needed to carry out Mark's request. Access can be revoked at any time at <a href="https://myaccount.google.com/permissions" rel="noopener" target="_blank">myaccount.google.com/permissions</a>. The tokens then stop working and are also deleted from Mark's computer.</p>
    <p>Mark Agent's use and transfer of information received from Google APIs to any other app will adhere to the <a href="https://developers.google.com/terms/api-services-user-data-policy" rel="noopener" target="_blank">Google API Services User Data Policy</a>, including the Limited Use requirements. Google user data is not used to develop, improve or train generalized AI or machine learning models.</p>
  </section>
</div>""")

def terms():
    return pagina("terms", "Terms | 8MM Film Productions",
        "Gebruiksvoorwaarden van de app Mark Agent van 8MM Film Productions.",
        f"""<div class="wrap doc">
  <span class="label">Terms</span>
  <h1>Gebruiks&shy;voorwaarden</h1>
  <p class="datum">Bijgewerkt op {BIJGEWERKT}</p>
  {TAAL()}
  <section id="nl">
    <h2>Mark Agent</h2>
    <p>Deze voorwaarden gelden voor de app Mark Agent, gemaakt door Mark Jansen (8MM Film Productions, KVK {S['kvk']}).</p>
    <ul>
      <li>Mark Agent is een persoonlijke app, alleen voor eigen gebruik door Mark Jansen. De app wordt niet aangeboden aan anderen.</li>
      <li>De app gebruikt Marks eigen Google-accounts: Gmail alleen om te lezen, en Google Agenda om na Marks bevestiging nieuwe afspraken aan te maken.</li>
      <li>Toegang tot Google kan altijd worden ingetrokken via de Google-accountinstellingen.</li>
      <li>De app wordt geleverd zoals hij is, zonder garanties. 8MM Film Productions is niet aansprakelijk voor schade door het gebruik van de app, behalve als de wet dat anders bepaalt.</li>
      <li>Hoe de app met gegevens omgaat, lees je in de <a href="{link('privacy')}#mark-agent">privacyverklaring</a>.</li>
      <li>We kunnen deze voorwaarden aanpassen. De datum bovenaan laat zien wanneer dat het laatst gebeurde.</li>
      <li>Op deze voorwaarden is Nederlands recht van toepassing.</li>
    </ul>
    <p>Vragen? Mail <a href="mailto:{S['email']}">{S['email']}</a>.</p>
  </section>
  <hr class="lijn">
  <section id="en" lang="en">
    <h2>Terms of service (English)</h2>
    <p>These terms apply to the Mark Agent app, made by Mark Jansen (8MM Film Productions, Chamber of Commerce no. {S['kvk']}, the Netherlands).</p>
    <ul>
      <li>Mark Agent is a personal app for use by Mark Jansen only. It is not offered to anyone else.</li>
      <li>The app uses Mark's own Google accounts: Gmail read-only, and Google Calendar to create new events after Mark confirms them.</li>
      <li>Access to Google can be revoked at any time in the Google account settings.</li>
      <li>The app is provided as is, without warranties. 8MM Film Productions is not liable for damage resulting from its use, except where the law requires otherwise.</li>
      <li>How the app handles data is described in the <a href="{link('privacy')}#mark-agent-en">privacy policy</a>.</li>
      <li>These terms may change. The date at the top shows the latest update.</li>
      <li>These terms are governed by Dutch law.</li>
    </ul>
    <p>Questions? Email <a href="mailto:{S['email']}">{S['email']}</a>.</p>
  </section>
</div>""")

def niet_gevonden():
    return pagina("404", "Pagina niet gevonden | 8MM Film Productions", "Deze pagina bestaat niet (meer).",
        f"""<div class="wrap doc"><span class="label">404</span><h1>Scène niet gevonden</h1>
<p>Deze pagina bestaat niet of is verplaatst. Ga terug naar de <a href="{link('')}">homepage</a> of bekijk onze <a href="{link('videos')}">video's</a>.</p></div>""")

# ---------- bouwen ----------

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "src/img", OUT / "img")
    paginas = {"index": home(), "videos": videos(), "contact": contact(),
               "agent": agent(), "privacy": privacy(), "terms": terms(), "404": niet_gevonden()}
    for naam, inhoud in paginas.items():
        if PREVIEW or naam in ("index", "404"):
            doel = OUT / f"{naam}.html"
        else:
            (OUT / naam).mkdir()
            doel = OUT / naam / "index.html"
        doel.write_text(inhoud, encoding="utf-8")
    if not PREVIEW:
        (OUT / "CNAME").write_text("www.8mmfilmproductions.nl\n")
        (OUT / ".nojekyll").write_text("")
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {S['domein']}/sitemap.xml\n")
        vandaag = datetime.date.today().isoformat()
        urls = "".join(f"<url><loc>{S['domein']}{p}</loc><lastmod>{vandaag}</lastmod></url>" for p in [link_live(n) for n in ("", "videos", "contact", "agent", "privacy", "terms")])
        (OUT / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    # controle: open punten
    open_punten = set()
    for naam, inhoud in paginas.items():
        for m in re.findall(r"AANVULLEN: [^<]+", inhoud):
            open_punten.add(f"{naam}: {html.unescape(m)}")
        if "WEB3FORMS_KEY_ONTBREEKT" in inhoud and not PREVIEW:
            open_punten.add(f"{naam}: Web3Forms access key ontbreekt in site.json")
        if 'class="leeg"' in inhoud:
            open_punten.add(f"{naam}: nog video's zonder YouTube-link")
    for c in S.get("cases", []):
        if not video(c.get("video", "")):
            open_punten.add(f"index: case '{c.get('video')}' hoort bij geen video in site.json en wordt niet getoond")
    print(f"Gebouwd in {OUT.name}/ ({len(paginas)} pagina's)")
    if open_punten:
        print("Nog open:")
        for p in sorted(open_punten):
            print("  -", p)

if __name__ == "__main__":
    main()
