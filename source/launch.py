"""Launch build for the St Matthews Healthcare website.

Writes a complete static website to ../launch/site: one page per address, self hosted
fonts, external stylesheet and script, page titles and descriptions, social share images,
structured data, favicons, sitemap, robots, a 404 page, optimised photographs with their
camera metadata removed, and redirect and header files for the common hosts.

Run:  python3 launch.py      (needs Python 3 and Pillow: pip install pillow)
"""
import os, re, json, shutil, datetime, hashlib
from PIL import Image, ImageOps

import build as B
from data import *

HERE = os.path.dirname(os.path.abspath(__file__))
# In the handover package the photographs and brochures sit in source/media and the
# website is written to ../site. In the working folder they come from ../site.
# In the IT package, the photographs and brochures are read from the site folder itself
# (copied aside first) and the site folder is rebuilt in place.
PACKAGE_SITE = os.path.normpath(os.path.join(HERE, "..", "site"))
IN_PACKAGE = os.path.exists(os.path.join(PACKAGE_SITE, "sitemap.xml"))
if os.path.isdir(os.path.join(HERE, "media")):
    SRC = os.path.join(HERE, "media"); OUT = PACKAGE_SITE
elif IN_PACKAGE:
    SRC = None; OUT = PACKAGE_SITE
else:
    SRC = os.path.normpath(os.path.join(HERE, "..", "site")); OUT = os.path.normpath(os.path.join(HERE, "..", "launch", "site"))
FONTS_DIR = os.path.join(HERE, "fonts")
SITE_URL = "https://smhc.uk.com"          # the current address; no www, as the current site uses
TODAY = datetime.date.today().isoformat()
BRAND = "St Matthews Healthcare"

# ------------------------------------------------------------------ pages
def town(s):
    p = s["place"]
    for t in ("Coventry", "Northampton", "St Leonards-on-Sea"):
        if t in p: return t
    return p.split(",")[0]

def trim(text, n=158):
    if len(text) <= n: return text
    cut = text[:n]
    stop = max(cut.rfind(". "), cut.rfind("? "))
    if stop > 80: return cut[:stop + 1]
    return cut[:cut.rfind(" ")].rstrip(",;:") + "..."

PAGES = [  # view, path, title, description, share image
    ("home", "", f"{BRAND} | Specialist mental health hospitals and nursing homes",
     f"Two specialist mental health hospitals and eight nursing homes across Northamptonshire, Coventry and East Sussex. One referral line for every service: {REF_PHONE}.", "brand"),
    ("services", "services/", f"Our services | {BRAND}",
     "Find the right St Matthews service by need, area or route into care. Two hospitals and eight specialist nursing homes, with a brochure for every service.", "brand"),
    ("refer", "professionals/", f"For professionals and commissioners | {BRAND}",
     f"Make a referral to St Matthews Healthcare. Routes into care, funding and how a placement works, with one referral line for every service: {REF_PHONE}.", "brand"),
    ("families", "families/", f"For families and friends | {BRAND}",
     "What to expect when someone you love moves into a St Matthews service, from daily life to arranging a visit to see it for yourself.", "fam-bedroom-yellow.jpg"),
    ("about", "about/", f"About us | {BRAND}",
     "Our mission, our six values and the senior leadership team behind St Matthews Healthcare.", "brand"),
    ("news", "news/", f"News | {BRAND}",
     "News from across St Matthews Healthcare, from our services and our people.", "brand"),
    ("careers", "careers/", f"Careers | {BRAND}",
     "Work with St Matthews Healthcare across two hospitals and eight nursing homes in Northamptonshire, Coventry and East Sussex. Send an enquiry to our recruitment team.", "careers-team.jpg"),
    ("contact", "contact/", f"Contact | {BRAND}",
     f"Referrals, enquiries and visits all start in the same place: {REF_PHONE} or {REF_EMAIL}.", "brand"),
    ("privacy", "privacy/", f"Privacy and cookies | {BRAND}",
     "How the St Matthews Healthcare website handles your information, including our referral and careers enquiry forms. This website does not use cookies.", "brand"),
]
for s in SERVICES:
    h = s["hero"]
    share = h.get("img") or s["card"]
    PAGES.append((s["id"], f"services/{s['id']}/", f"{s['name']}, {town(s)} | {BRAND}", trim(s["stand"]), share))
URL = {v: p for v, p, *_ in PAGES}

# ------------------------------------------------------------------ helpers
def prefix_for(path, absolute=False):
    return "/" if absolute else "../" * path.count("/")

def link(pre, target):
    out = pre + target
    return out if out else "./"

def view_parts():
    out = {}
    for v in B.all_views():
        m = re.match(r'\s*<section class="view" data-view="([^"]+)"', v)
        out[m.group(1)] = v
    return out

def ids_by_view(parts):
    m = {}
    for name, html in parts.items():
        for i in re.findall(r'\sid="([^"]+)"', html):
            m.setdefault(i, name)
    return m

def rewrite(html, page_view, pre, idmap):
    def fix_anchor(m):
        tag = m.group(0)
        hm = re.search(r'href="#([^"]*)"', tag)
        if not hm: return tag
        tok = hm.group(1)
        svc = re.search(r'data-svc="([^"]+)"', tag)
        if tok in ("", "main"):
            return tag
        if tok in URL:
            new = link(pre, URL[tok])
        elif tok in idmap:
            v = idmap[tok]
            if v == page_view and not svc:
                new = "#" + tok
            else:
                new = link(pre, URL[v]) + (f"?service={svc.group(1)}" if svc else "") + "#" + tok
        else:
            raise SystemExit(f"unresolved link #{tok} on {page_view}")
        return tag.replace(hm.group(0), f'href="{new}"')
    html = re.sub(r'<a\s[^>]*>', fix_anchor, html)
    html = re.sub(r'(\s(?:src|href|data-view-img|data-view-pdf))="(img|brochures)/', lambda m: f'{m.group(1)}="{pre}{m.group(2)}/', html)
    return html

def page_head(path, title, desc, share, pre, ver, ld, noindex=False):
    canon = SITE_URL + "/" + path
    img = f"{SITE_URL}/img/share/{share_name(share)}"
    meta = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
        f"<title>{B.H(title)}</title>",
        f'<meta name="description" content="{B.H(desc)}">',
    ]
    if noindex:
        meta.append('<meta name="robots" content="noindex">')
    else:
        meta += [f'<link rel="canonical" href="{canon}">',
                 '<meta property="og:type" content="website">', f'<meta property="og:site_name" content="{BRAND}">',
                 f'<meta property="og:title" content="{B.H(title.split(" | ")[0])}">', f'<meta property="og:description" content="{B.H(desc)}">',
                 f'<meta property="og:url" content="{canon}">', f'<meta property="og:image" content="{img}">',
                 '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
                 '<meta property="og:locale" content="en_GB">', '<meta name="twitter:card" content="summary_large_image">']
    meta += ['<meta name="theme-color" content="#16324F">', '<meta name="format-detection" content="telephone=no">',
             f'<link rel="icon" href="{pre}favicon.ico" sizes="32x32">',
             f'<link rel="icon" type="image/png" sizes="192x192" href="{pre}img/icons/icon-192.png">',
             f'<link rel="apple-touch-icon" href="{pre}img/icons/apple-touch-icon.png">',
             f'<link rel="preload" href="{pre}assets/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>',
             f'<link rel="preload" href="{pre}assets/fonts/cormorant-garamond-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>',
             f'<link rel="stylesheet" href="{pre}assets/site.css?v={ver}">']
    for block in ld:
        meta.append('<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False, separators=(",", ":")) + "</script>")
    return "".join(meta)

def share_name(share):
    return "brand.jpg" if share == "brand" else share.rsplit(".", 1)[0] + ".jpg"

ORG = {"@type": "Organization", "@id": SITE_URL + "/#organisation", "name": BRAND, "legalName": "St Matthews Ltd",
       "url": SITE_URL + "/", "logo": SITE_URL + "/img/icons/logo.png", "telephone": "+44 1604 844192", "email": REF_EMAIL,
       "address": {"@type": "PostalAddress", "streetAddress": "29-31 St Matthews Parade", "addressLocality": "Northampton",
                   "postalCode": "NN2 7HF", "addressCountry": "GB"}}

def service_ld(s, path):
    addr = s["address"]
    pc = re.search(r"([A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2})$", addr)
    street = addr[:pc.start()].strip().rstrip(",") if pc else addr
    bits = [b.strip() for b in street.split(",")]
    region = bits.pop() if bits[-1] in ("Northamptonshire", "East Sussex") else ""
    loc = bits[-1] if len(bits) > 1 else town(s)
    return [{"@context": "https://schema.org", "@type": "MedicalOrganization", "name": s["name"], "url": SITE_URL + "/" + path,
             "description": trim(s["stand"]), "telephone": "+44" + re.sub(r"\D", "", s["phone"])[1:], "email": REF_EMAIL,
             "address": {"@type": "PostalAddress", "streetAddress": ", ".join(bits[:-1]) if len(bits) > 1 else street,
                         "addressLocality": loc, **({"addressRegion": region} if region else {}), "postalCode": pc.group(1) if pc else "", "addressCountry": "GB"},
             "parentOrganization": {"@id": SITE_URL + "/#organisation"}},
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
                {"@type": "ListItem", "position": 2, "name": "Our services", "item": SITE_URL + "/services/"},
                {"@type": "ListItem", "position": 3, "name": s["name"], "item": SITE_URL + "/" + path}]}]

def config_json():
    cfg = {"ids": [s["id"] for s in SERVICES], "names": {s["id"]: s["name"] for s in SERVICES},
           "endpoint": FORM_ENDPOINT, "refEmail": REF_EMAIL, "recEmail": REC_EMAIL, "refPhone": REF_PHONE}
    return '<script type="application/json" id="smhc-config">' + json.dumps(cfg, separators=(",", ":")) + "</script>"

NOT_FOUND = f'''<section class="view" data-view="notfound" aria-label="Page not found">
<div class="phero navy"><div class="wrap on-navy"><span class="eyebrow">Page not found</span><h1 class="h1">We could not find that page.<span class="ser">Our website is new.</span></h1>
<p class="lede">The page you were looking for is not here, but everything you need is a click away.</p>
<div class="btns"><a class="btn btn-light" href="#services">Our services {B.ar()}</a><a class="btn btn-line" href="#refer-form">Make a referral</a></div></div></div>
<section class="sec"><div class="wrap"><div class="routes">
<div class="route">{B.ico("building-2")}<span class="t">Our services</span><span class="d">Two hospitals and eight specialist nursing homes, each with its own page and brochure.</span><a class="textlink" href="#services">See every service {B.ar()}</a></div>
<div class="route">{B.ico("phone-call")}<span class="t">Make a referral</span><span class="d">One referral line for every service: {REF_PHONE}.</span><a class="textlink" href="#refer-form">Start a referral {B.ar()}</a></div>
<div class="route">{B.ico("mail")}<span class="t">Contact us</span><span class="d">Referrals, enquiries and visits all start in the same place.</span><a class="textlink" href="#contact">Contact {B.ar()}</a></div>
</div></div></section></section>'''

# ------------------------------------------------------------------ assets
def optimise_jpeg(src, dst, max_edge=1800, target=350_000):
    im = Image.open(src)
    had_exif = "exif" in im.info
    im = ImageOps.exif_transpose(im)
    if max(im.size) > max_edge:
        im.thumbnail((max_edge, max_edge), Image.LANCZOS)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    tmp = dst + ".tmp"
    for q in (84, 80, 76):
        im.save(tmp, "JPEG", quality=q, optimize=True, progressive=True)
        if os.path.getsize(tmp) <= target: break
    if had_exif or os.path.getsize(tmp) < os.path.getsize(src) * 0.9:
        os.replace(tmp, dst)
    else:
        os.remove(tmp); shutil.copy2(src, dst)

def crop_cover(im, w, h, pos=(0.5, 0.5)):
    im = ImageOps.exif_transpose(im).convert("RGB")
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = round((im.width - w) * pos[0]); y = round((im.height - h) * pos[1])
    return im.crop((x, y, x + w, y + h))

def parse_pos(p):
    try:
        a, b = p.replace("%", "").split()
        return float(a) / 100, float(b) / 100
    except Exception:
        return 0.5, 0.5

def share_images(dst):
    os.makedirs(dst, exist_ok=True)
    navy = (22, 50, 79)
    # brand card: the Hawthorne House front on the left, the reversed logo on navy on the right
    photo = crop_cover(Image.open(f"{SRC}/img/home-hh-exterior.jpg"), 720, 630, (0.6, 0.72))
    card = Image.new("RGB", (1200, 630), navy); card.paste(photo, (0, 0))
    logo = Image.open(f"{SRC}/img/logo-reverse.png").convert("RGBA")
    logo.thumbnail((340, 260), Image.LANCZOS)
    card.paste(logo, (720 + (480 - logo.width) // 2, (630 - logo.height) // 2), logo)
    card.save(f"{dst}/brand.jpg", "JPEG", quality=86, optimize=True, progressive=True)
    pos = {s["hero"].get("img"): parse_pos(s["hero"].get("pos", "50% 50%")) for s in SERVICES if s["hero"].get("img")}
    for v, path, title, desc, share in PAGES:
        if share == "brand": continue
        crop_cover(Image.open(f"{SRC}/img/{share}"), 1200, 630, pos.get(share, (0.5, 0.4))).save(
            f"{dst}/{share_name(share)}", "JPEG", quality=84, optimize=True, progressive=True)

def icons(dst_root):
    d = f"{dst_root}/img/icons"; os.makedirs(d, exist_ok=True)
    fleur = Image.open(f"{SRC}/img/fleur-light.png").convert("RGBA")
    ivory = (251, 248, 243, 255)
    def tile(size, frac, bg):
        im = Image.new("RGBA", (size, size), bg)
        f = fleur.copy(); f.thumbnail((round(size * frac), round(size * frac)), Image.LANCZOS)
        im.alpha_composite(f, ((size - f.width) // 2, (size - f.height) // 2))
        return im
    tile(180, .74, ivory).convert("RGB").save(f"{d}/apple-touch-icon.png", optimize=True)
    tile(192, .74, ivory).save(f"{d}/icon-192.png", optimize=True)
    tile(64, .9, (0, 0, 0, 0)).save(f"{dst_root}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    logo = Image.open(f"{SRC}/img/logo-reverse.png").convert("RGBA")
    sq = Image.new("RGBA", (600, 600), (22, 50, 79, 255)); logo.thumbnail((480, 380), Image.LANCZOS)
    sq.alpha_composite(logo, ((600 - logo.width) // 2, (600 - logo.height) // 2))
    sq.convert("RGB").save(f"{d}/logo.png", optimize=True)

FONT_FILES = ([("inter", f"inter-latin-{w}-normal.woff2", "Inter", w, "normal") for w in (400, 500, 600, 700)] +
              [("cormorant-garamond", f"cormorant-garamond-latin-{w}-{st}.woff2", "Cormorant Garamond", w, st)
               for w in (500, 600, 700) for st in ("normal", "italic")])

def fonts_css():
    return "".join(f"@font-face{{font-family:'{fam}';font-style:{st};font-weight:{w};font-display:swap;src:url(fonts/{f}) format('woff2')}}"
                   for pkg, f, fam, w, st in FONT_FILES) + "\n"

# ------------------------------------------------------------------ redirects
REDIRECTS = [  # old path on smhc.uk.com, new path
    ("/home/", "/"),
    ("/about-us/privacy-policy/", "/privacy/"),
    ("/about-us/", "/about/"),
    ("/our-ethos/", "/about/"), ("/research/", "/about/"), ("/why-smhc/", "/about/"), ("/colleagues-feedback/", "/careers/"),
    ("/contact-us/", "/contact/"),
    ("/care-facilities/", "/services/"),
    ("/care-facilities/the-dallingtons-mental-health-hospital/", "/services/the-dallingtons/"),
    ("/care-facilities/st-matthews-hospital/", "/services/st-matthews-hospital/"),
    ("/care-facilities/broomhill-mental-health-hospital-2/", "/services/althorp-grange/"),
    ("/care-facilities/althorp-grange/", "/services/althorp-grange/"),
    ("/care-facilities/st-matthews-unit-care-home/", "/services/st-matthews-unit/"),
    ("/care-facilities/kingsthorpe-grange/", "/services/kingsthorpe-grange/"),
    ("/care-facilities/the-avenue-care-home/", "/services/the-avenue/"),
    ("/care-facilities/willowbrook-house-care-home/", "/services/willowbrook-house/"),
    ("/care-facilities/maple-leaf-house-nursing-care-home-coventry/", "/services/maple-leaf-house/"),
    ("/care-facilities/hawthorne-house-care-home-coventry/", "/services/hawthorne-house/"),
    ("/care-facilities/the-moreton-centre-nursing-care-home/", "/services/the-moreton-centre/"),
    ("/nursing-home-the-avenue/", "/services/the-avenue/"),
    ("/care-types/", "/services/"),
    ("/mental-health-hospitals/", "/services/"), ("/hospital-care/", "/services/"), ("/dementia-care/", "/services/"),
    ("/community-based-mdt-pathways/", "/services/"), ("/mental-health-nursing-care-homes/", "/services/"),
    ("/careers/register-your-interest/", "/careers/"), ("/careers/recruitment-event-for-nurses/", "/careers/"),
]
WILDCARDS = [  # old prefix, new path; none of these prefixes is a live page on the new site
    ("/care-facilities/", "/services/"),
    ("/care-types/", "/services/"),
    ("/about-us/", "/about/"),
    ("/job-openings/", "/careers/"), ("/job-category/", "/careers/"), ("/job-type/", "/careers/"), ("/jobs/", "/careers/"),
] + [(f"/{y}/", "/news/") for y in range(2012, 2027)]

CQC_HOSTS = "https://www.cqc.org.uk https://*.cqc.org.uk"
CSP = (f"default-src 'self'; script-src 'self' {CQC_HOSTS}; style-src 'self' 'unsafe-inline' {CQC_HOSTS}; "
       f"img-src 'self' data: {CQC_HOSTS}; font-src 'self' {CQC_HOSTS}; frame-src {CQC_HOSTS}; connect-src 'self' {CQC_HOSTS}; "
       "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'")

def cqc_widget(html):
    """The official CQC ratings widget on each service page (Regulation 20A), in the CQC panel."""
    def add(m):
        loc = m.group(1)
        tag = (f'<div class="cqcw"><script type="text/javascript" src="https://www.cqc.org.uk/sites/all/modules/custom/cqc_widget/widget.js'
               f'?data-id={loc}&amp;data-host=www.cqc.org.uk&amp;type=location"></script></div>')
        return m.group(0) + tag
    return re.sub(r'<div class="panel" data-cqc-location="([^"]+)">.*?</span>.*?reports\.</span>', add, html, count=1, flags=re.S)
HEADERS = [("X-Content-Type-Options", "nosniff"), ("Referrer-Policy", "strict-origin-when-cross-origin"),
           ("X-Frame-Options", "SAMEORIGIN"), ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
           ("Content-Security-Policy", CSP)]

def write_host_files(root):
    # Apache, including most WordPress hosting
    lines = ["# St Matthews Healthcare website: Apache settings", "# Generated by launch.py", "",
             "DirectoryIndex index.html", "Options -Indexes", "ErrorDocument 404 /404.html", "",
             "# The GitHub read-me files are for IT and Claude, not for visitors", "RedirectMatch 404 ^/(README|CLAUDE)\\.md$", "",
             "<IfModule mod_rewrite.c>", "RewriteEngine On", "",
             "# One address for the site: https and no www", "RewriteCond %{HTTPS} off [OR]", "RewriteCond %{HTTP_HOST} ^www\\. [NC]",
             "RewriteRule ^(.*)$ " + SITE_URL + "/$1 [R=301,L]", "",
             "# Pages from the old website"]
    for old, new in REDIRECTS:
        lines.append(f"RewriteRule ^{re.escape(old.strip('/'))}/?$ {new} [R=301,L,NC]")
    lines.append("RewriteRule ^Careers/?$ /careers/ [R=301,L]")
    lines.append("")
    lines.append("# Anything else under the old sections")
    for old, new in WILDCARDS:
        lines.append(f"RewriteRule ^{re.escape(old.strip('/'))}/ {new} [R=301,L,NC]")
    lines += ["RewriteRule ^wp-(admin|login|content|includes) - [G,L]", "</IfModule>", "",
              "<IfModule mod_headers.c>"] + [f'Header always set {k} "{v}"' for k, v in HEADERS] + [
              '<FilesMatch "\\.(html)$">', 'Header set Cache-Control "no-cache"', "</FilesMatch>",
              '<FilesMatch "\\.(css|js|woff2|jpg|png|ico|pdf)$">', 'Header set Cache-Control "public, max-age=2592000"', "</FilesMatch>",
              "</IfModule>", "",
              "<IfModule mod_deflate.c>", "AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/xml text/plain", "</IfModule>", ""]
    open(f"{root}/.htaccess", "w").write("\n".join(lines))
    # Netlify and Cloudflare Pages
    rl = ["# St Matthews Healthcare: redirects from the old website (Netlify and Cloudflare Pages)"]
    rl += [f"{old}  {new}  301" for old, new in REDIRECTS]
    rl += [f"{old}*  {new}  301" for old, new in WILDCARDS]
    open(f"{root}/_redirects", "w").write("\n".join(rl) + "\n")
    hl = ["/*"] + [f"  {k}: {v}" for k, v in HEADERS] + ["", "/assets/*", "  Cache-Control: public, max-age=2592000", "",
          "/img/*", "  Cache-Control: public, max-age=2592000", ""]
    open(f"{root}/_headers", "w").write("\n".join(hl) + "\n")
    # Azure Static Web Apps
    routes = [{"route": old.rstrip("/"), "redirect": new, "statusCode": 301} for old, new in REDIRECTS if old != "/"]
    routes += [{"route": old + "*", "redirect": new, "statusCode": 301} for old, new in WILDCARDS]
    cfg = {"routes": routes, "responseOverrides": {"404": {"rewrite": "/404.html", "statusCode": 404}},
           "globalHeaders": dict(HEADERS), "trailingSlash": "always"}
    open(f"{root}/staticwebapp.config.json", "w").write(json.dumps(cfg, indent=2))
    # any other host
    with open(f"{root}/../redirects.csv", "w") as f:
        f.write("old address,new address,type\n")
        for old, new in REDIRECTS: f.write(f"{SITE_URL}{old},{SITE_URL}{new},exact\n")
        for old, new in WILDCARDS: f.write(f"{SITE_URL}{old}...,{SITE_URL}{new},everything under\n")

# ------------------------------------------------------------------ build
def main():
    global SRC
    if SRC is None:
        import tempfile
        SRC = tempfile.mkdtemp(prefix="smhc-media-")
        for d in ("img", "brochures"):
            shutil.copytree(os.path.join(OUT, d), os.path.join(SRC, d))
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(f"{OUT}/assets/fonts")
    parts = view_parts()
    parts["notfound"] = NOT_FOUND
    idmap = ids_by_view(parts)
    URL["notfound"] = "404.html"

    css = open(f"{HERE}/site.css").read().replace("url(img/", "url(../img/")
    css = fonts_css() + css
    js = open(f"{HERE}/site.js").read()
    ver = hashlib.md5((css + js).encode()).hexdigest()[:10]
    open(f"{OUT}/assets/site.css", "w").write(css)
    open(f"{OUT}/assets/site.js", "w").write(js)
    for pkg, f, *_ in FONT_FILES:
        shutil.copy2(os.path.join(FONTS_DIR, f), f"{OUT}/assets/fonts/{f}")
    for lic in ("LICENSE-Inter.txt", "LICENSE-Cormorant-Garamond.txt"):
        shutil.copy2(os.path.join(FONTS_DIR, lic), f"{OUT}/assets/fonts/{lic}")

    used = set()
    pages = PAGES + [("notfound", "404.html", f"Page not found | {BRAND}", "This page is not on the new St Matthews Healthcare website.", "brand")]
    for view, path, title, desc, share in pages:
        absolute = view == "notfound"
        pre = prefix_for(path, absolute)
        vhtml = parts[view].replace(" hidden>", ">", 1) if view != "notfound" else parts[view]
        body = B.header() + '<main id="main" tabindex="-1">' + vhtml + "</main>" + B.footer()
        if "data-view-img" in vhtml: body += B.viewer_html()
        if "data-job" in vhtml: body += B.job_html()
        body += B.TOAST
        body = rewrite(B.typo(body), view, pre, idmap)
        if view in BYID_IDS:
            body = cqc_widget(body)
            if 'class="cqcw"' not in body: raise SystemExit("no CQC widget on " + view)
        ld = []
        if view == "home": ld = [dict({"@context": "https://schema.org"}, **ORG)]
        elif view in BYID_IDS: ld = service_ld(B.BYID[view], path)
        head = page_head(path, title, desc, share, pre, ver, ld, noindex=absolute)
        doc = (f'<!doctype html><html lang="en-GB"><head>{head}</head><body>{body}{config_json()}'
               f'<script src="{pre}assets/site.js?v={ver}"></script></body></html>')
        dst = f"{OUT}/{path}" + ("index.html" if path.endswith("/") or path == "" else "")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "w").write(doc)
        used |= set(re.findall(r'(?:src|href|data-view-img|data-view-pdf)="(?:\.\./|/)*((?:img|brochures)/[^"?#]+)"', doc))
    used |= {"img/" + m for m in re.findall(r"url\(\.\./img/([^)]+)\)", css)}

    # photographs and brochures actually used, optimised, metadata removed
    for rel in sorted(used):
        if rel.startswith(("img/icons/", "img/share/")): continue
        src, dst = f"{SRC}/{rel}", f"{OUT}/{rel}"
        if not os.path.exists(src): raise SystemExit("missing " + rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if rel.lower().endswith((".jpg", ".jpeg")) and rel.startswith("img/"):
            optimise_jpeg(src, dst)
        else:
            shutil.copy2(src, dst)
    # brochure cover thumbnails are referenced from the page images too
    share_images(f"{OUT}/img/share")
    icons(OUT)

    # sitemap, robots
    urls = "".join(f"<url><loc>{SITE_URL}/{p}</loc><lastmod>{TODAY}</lastmod></url>" for v, p, *_ in PAGES)
    open(f"{OUT}/sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    write_host_files(OUT)
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    print(f"launch build: {len(pages)} pages, {n} files, {size/1e6:.1f} MB, assets v{ver}")

BYID_IDS = {s["id"] for s in SERVICES}

if __name__ == "__main__":
    main()
