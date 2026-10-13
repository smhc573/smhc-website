import json, html, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data import *
from icons import ICONS

H = html.escape
BYID = {s["id"]: s for s in SERVICES}
MAP = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "map.json")))
VB = "168 228 330 300"  # England and Wales, cropped round the services

def ico(name, cls=""):
    return f'<span class="ico{(" " + cls) if cls else ""}" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg></span>'

def ic(name):
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'

def bro_attrs(title, f):
    stem = f[:-4]
    return f'href="brochures/view/{stem}.jpg" data-view-img="brochures/view/{stem}.jpg" data-view-pdf="brochures/{f}" data-view-file="{f}" data-view-title="{H(title)}"' + (' data-view-land="1"' if "Pathway" in f else '')

def bro_card(title, f):
    stem = f[:-4]
    land = " land" if "Pathway" in f else ""
    return f'<a class="bcard{land}" {bro_attrs(title, f)}><span class="cv"><img src="brochures/thumb/{stem}.jpg" alt="" loading="lazy"></span><span class="bt">{H(title)}</span><span class="go">{ic("eye")}View brochure</span></a>'

def feats(items, cls=""):
    # items: (icon, eyebrow, title, desc)
    out = "".join(f'<div class="feat"><div class="top">{ico(i)}</div><span class="n">{H(n)}</span><span class="t">{H(t)}</span><span class="d">{H(d)}</span></div>' for i, n, t, d in items)
    return f'<div class="feats{(" " + cls) if cls else ""}">{out}</div>'

VAL_ICONS = ["user-check", "heart", "users-round", "lightbulb", "handshake", "trending-up"]
def vcards():
    return '<div class="vcards">' + "".join(f'<div class="vcard">{ico(VAL_ICONS[i])}<div class="tx"><span class="n">{i+1:02d}</span><span class="t">{H(v)}</span></div></div>' for i, v in enumerate(VALUES)) + '</div>'

MISSION_LEAD = MISSION.split(": ")[0] + "."
MISSION_REST = MISSION.split("Positive Impact. ", 1)[1]

LEADERS = [("Richard Whitby", "Chief Executive Officer", "lt-richard-whitby.jpg", "50% 30%"),
           ("Gayle Palmer", "Director of Operations", "lt-gayle-palmer-2.jpg", "50% 50%"),
           ("Wincent Kordula", "Chief Financial Officer", "lt-wincent-kordula.jpg", "50% 30%"),
           ("Dr Vishelle Kamath", "Medical Director", "lt-vishelle-kamath.jpg", "50% 30%"),
           ("Paul Allam", "Director of Quality and Governance", "lt-paul-allan.jpg", "50% 30%"),
           ("Bianca Socol", "HR Director", "lt-bianca-socol.jpg", "50% 35%"),
           ("Phil Tattersall", "National Business Development Director", "lt-phil-tattersall.jpg", "50% 30%")]
def team():
    return "".join(f'<figure class="mate"><div class="ph"><img src="img/{f}" alt="{H(n)}, {H(t)}" loading="lazy" style="object-position:{pos}"></div><figcaption><b>{H(n)}</b><span>{H(t)}</span></figcaption></figure>' for n, t, f, pos in LEADERS)

def ar():
    return '<span class="ar" aria-hidden="true">&rarr;</span>'

def ref_inline(dark=False):
    return (f'<span class="copyrow"><a href="tel:01604844192">{REF_PHONE}</a>'
            f'<button class="copy-btn" type="button" data-copy="{REF_PHONE}" aria-label="Copy the referral line">Copy</button></span>')

def email_inline():
    return (f'<span class="copyrow"><a href="mailto:{REF_EMAIL}">{REF_EMAIL}</a>'
            f'<button class="copy-btn" type="button" data-copy="{REF_EMAIL}" aria-label="Copy the referral email">Copy</button></span>')

# --------------------------------------------------------------------------- map
CLUSTERS = [
    ("northampton", "Northampton", ["the-dallingtons", "st-matthews-hospital", "st-matthews-unit", "kingsthorpe-grange", "the-avenue", "althorp-grange"], "r"),
    ("corby", "Corby", ["willowbrook-house"], "r"),
    ("coventry", "Coventry", ["maple-leaf-house", "hawthorne-house"], "l"),
    ("stleonards", "St Leonards-on-Sea", ["the-moreton-centre"], "l"),
]

MAPN = 0
def map_svg(highlight=None, interactive=True, label=True, cls=""):
    p = MAP["pts"]
    vb = VB
    global MAPN
    MAPN += 1
    mid = f"mapfade{MAPN}"
    out = [f'<svg viewBox="{vb}" role="img" aria-label="Map of England showing where St Matthews services are" class="{cls}">',
           f'<defs><radialGradient id="{mid}g" cx="62%" cy="62%" r="62%"><stop offset="55%" stop-color="#fff"/><stop offset="100%" stop-color="#000"/></radialGradient>'
           f'<mask id="{mid}"><rect x="168" y="228" width="330" height="300" fill="url(#{mid}g)"/></mask></defs>',
           f'<path class="map-land" mask="url(#{mid})" d="{MAP["uk"]}"/>']
    lx, ly = p["london"]
    out.append(f'<g class="map-ref" aria-hidden="true"><circle cx="{lx}" cy="{ly}" r="2.4"/><text x="{lx+6}" y="{ly+3}">London</text></g>')
    if highlight:
        s = BYID[highlight]; x, y = p[s["pin"]]
        left = x > 400
        out.append(f'<g class="pin on" aria-hidden="true"><circle class="h" cx="{x}" cy="{y}" r="16"/><circle class="o" cx="{x}" cy="{y}" r="7"/>'
                   f'<text class="lab" x="{x-14 if left else x+14}" y="{y-12}" text-anchor="{"end" if left else "start"}">{H(s["place"].split(",")[0])}</text></g>')
    else:
        for key, name, ids, side in CLUSTERS:
            x, y = p[key]; n = len(ids)
            r = 5 + n * 0.75
            tx = x + r + 10 if side == "r" else x - r - 10
            anchor = "start" if side == "r" else "end"
            att = f'tabindex="0" role="button" data-place="{key}" aria-label="{name}, {n} service{"s" if n>1 else ""}"' if interactive else 'aria-hidden="true"'
            out.append(f'<g class="pin" {att}><circle class="h" cx="{x}" cy="{y}" r="{r+3}"/><circle class="o" cx="{x}" cy="{y}" r="{r}"/>'
                       f'<text x="{x}" y="{y+3.2}" text-anchor="middle">{n}</text>'
                       + (f'<text class="lab" x="{tx}" y="{y+3.5}" text-anchor="{anchor}">{H(name)}</text>' if label else '') + '</g>')
    out.append('</svg>')
    return "".join(out)

# --------------------------------------------------------------------------- chrome
NAV = [("services", "Our services"), ("refer", "For professionals"), ("families", "For families"),
       ("about", "About us"), ("news", "News"), ("careers", "Careers"), ("contact", "Contact")]

def header():
    links = "".join(f'<a href="#{k}" data-nav="{k}">{H(v)}</a>' for k, v in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="util"><div class="wrap">
  <div class="ref"><span>Referral line <b><a href="tel:01604844192">{REF_PHONE}</a></b></span><span><a href="mailto:{REF_EMAIL}">{REF_EMAIL}</a></span></div>
  <div class="ts" role="group" aria-label="Text size"><span>Text size</span><button type="button" data-ts="0" aria-pressed="true" aria-label="Standard text">A</button><button type="button" data-ts="1" aria-pressed="false" aria-label="Larger text">A</button><button type="button" data-ts="2" aria-pressed="false" aria-label="Largest text">A</button></div>
</div></div>
<header class="site"><div class="wrap">
  <a class="brand" href="#home" aria-label="St Matthews Healthcare, home"><img class="fl" src="img/fleur-light.png" alt="" width="126" height="160"><img class="wm" src="img/wordmark-light.png" alt="St Matthews Healthcare" width="472" height="120"></a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mainnav">Menu</button>
  <nav class="main" id="mainnav" aria-label="Main">{links}<a class="btn btn-navy" href="#refer-form" data-nav="refer">Make a referral {ar()}</a></nav>
</div></header>'''

def footer():
    svc = "".join(f'<li><a href="#{s["id"]}">{H(s["name"])}</a></li>' for s in SERVICES)
    return f'''<footer class="site"><div class="wrap">
  <div class="top">
    <div class="lock"><img src="img/logo-reverse.png" alt="St Matthews Healthcare" width="470" height="360"><p class="line">Supporting lives, shaping futures.</p>
      <div class="ref"><span class="eyebrow">Referral line</span><b>{REF_PHONE}</b><a href="mailto:{REF_EMAIL}">{REF_EMAIL}</a></div></div>
    <div><h4>Our services</h4><ul>{svc}</ul></div>
    <div><h4>For you</h4><ul><li><a href="#refer">Commissioners and professionals</a></li><li><a href="#refer-form">Make a referral</a></li><li><a href="#families">Families and friends</a></li><li><a href="#careers">Careers</a></li><li><a href="#services-brochures">Service brochures</a></li></ul></div>
    <div><h4>St Matthews</h4><ul><li><a href="#about">About us</a></li><li><a href="#about-values">Our values</a></li><li><a href="#about-leadership">Our leadership</a></li><li><a href="#news">News</a></li><li><a href="#contact">Contact</a></li></ul>
      <h4 style="margin-top:26px">Registered office</h4><p>{H(GROUP["office"])}</p></div>
  </div>
  <div class="base"><span>{H(GROUP["company"])}. Every service is registered with the Care Quality Commission.</span><span class="bl"><a href="#privacy">Privacy and cookies</a><span>&copy; 2026 St Matthews Healthcare</span></span></div>
</div></footer>
<div class="callbar"><a href="tel:01604844192">Call {REF_PHONE}</a><a href="#refer-form">Make a referral</a></div>'''

def tiles():
    return f'''<div class="tiles">
  <a class="tile dark" href="#refer-form">{ico("clipboard-check")}<span class="k">Professionals</span><span class="t">Make a referral</span><span class="d">Tell us who you cannot place. Enquiries and assessments welcome now.</span><span class="go">Start {ar()}</span></a>
  <div class="tile">{ico("phone-call")}<span class="k">Referral line</span><span class="t">{REF_PHONE}</span><span class="d">One line reaches every service in the group.</span><span class="go"><button class="copy-btn" type="button" data-copy="{REF_PHONE}">Copy number</button></span></div>
  <a class="tile" href="#services-brochures">{ico("file-text")}<span class="k">Brochures</span><span class="t">View a brochure</span><span class="d">One page brochures for our services, to view, download or attach to a referral.</span><span class="go">See them all {ar()}</span></a>
  <a class="tile" href="#contact">{ico("calendar-heart")}<span class="k">Families</span><span class="t">Arrange a visit</span><span class="d">See a service for yourself. Tell us which one, and we will set it up.</span><span class="go">How to visit {ar()}</span></a>
</div>'''

def rail(cells, extra=""):
    c = "".join(f'<div class="c"><span class="f">{H(f)}</span><span class="l">{H(l).replace("carehome.co.uk", "carehome.<wbr>co.uk")}</span></div>' for f, l in cells)
    return f'<section class="rail" aria-label="At a glance"{extra}><div class="wrap">{c}</div></section>'

def card(s):
    img = s["card"]
    chips = "".join(f'<span class="chip">{H(c)}</span>' for c in s["chips"][:3])
    tag = "Hospital" if s["type"] == "hospital" else "Nursing home"
    return (f'<a class="scard" href="#{s["id"]}" data-id="{s["id"]}" data-type="{s["type"]}" data-region="{H(s["region"])}" data-tags="{" ".join(s["tags"])}" data-place="{next(k for k,_,ids,_s in CLUSTERS if s["id"] in ids)}">'
            f'<div class="im"><img src="img/{img}" alt="" loading="lazy" style="object-position:{s.get("cardPos","50% 50%")}"><span class="tag">{tag}</span></div>'
            f'<div class="bd"><span class="pl"><span>{H(s["place"].split(",")[0])}</span><span>{s["beds"]} beds</span></span><span class="nm">{H(s["name"])}</span>'
            f'<span class="ln">{H(s["cardLine"])}</span><span class="chips">{chips}</span></div></a>')

def quote(text, cite, light=False):
    cap = f'<figcaption><cite>{H(cite)}</cite></figcaption>' if cite else ''
    return f'<figure class="qbox{" light" if light else ""}"><blockquote>{H(text)}</blockquote>{cap}</figure>'

# --------------------------------------------------------------------------- views
def v_home():
    picons = ["phone-call", "clipboard-check", "puzzle", "door-open", "bed-double", "sun", "target", "house-heart"]
    path = "".join(f'<li><div class="pt">{ico(picons[i])}<span class="n">{i+1:02d}</span></div><span class="t">{H(t)}</span><span class="d">{H(d)}</span></li>' for i, (t, d) in enumerate(PATHWAY))
    regions = []
    for reg in ["Northamptonshire", "Coventry", "East Sussex"]:
        items = [s for s in SERVICES if s["region"] == reg]
        li = "".join(f'<li><a href="#{s["id"]}"><span class="n">{H(s["name"])}</span><span class="m">{H(s["place"].split(",")[0])} &middot; {s["beds"]} beds</span></a></li>' for s in items)
        regions.append(f'<div class="region"><h3><span>{reg}</span><span>{len(items)} service{"s" if len(items)>1 else ""}</span></h3><ul>{li}</ul></div>')
    news = "".join(f'<a class="ncard" href="#news-{n["id"]}"><div class="im"><img src="img/{n["img"]}" alt="{H(n["alt"])}" loading="lazy" style="object-position:{n.get("pos","50% 50%")}"></div><span class="meta">{H(n["tag"])} &middot; {H(n["date"])}</span><span class="t">{H(n["title"])}</span><span class="d">{H(n["lede"])}</span></a>' for n in NEWS[:3])
    ml = BYID["maple-leaf-house"]
    return f'''<section class="view" data-view="home" aria-label="Home">
<div class="hero hero-home navy">
  <div class="copy on-navy">
    <span class="eyebrow kick">Specialist mental health and nursing care</span>
    <h1 class="h1">Tell us who you cannot place.<span class="ser">Supporting lives, shaping futures.</span></h1>
    <p class="lede" style="color:var(--on-navy)">Two mental health hospitals and eight specialist nursing homes across Northamptonshire, Coventry and East Sussex. One referral line reaches every service, and the same provider stays with the person at every stage, so the placement search never has to start over.</p>
    <div class="btns"><a class="btn btn-light" href="#refer-form">Make a referral {ar()}</a><a class="btn btn-line" href="#services">Find a service</a></div>
  </div>
  <div class="mosaic">
    <figure><img src="img/home-hh-exterior.jpg" alt="Hawthorne House from the front, a purpose built nursing home in Tile Hill, Coventry, under a blue sky" fetchpriority="high" style="object-position:60% 72%"></figure>
    <figure><img src="img/home-hh-reception.jpg" alt="The reception lounge at Hawthorne House, with yellow sofas under a timber mezzanine" style="object-position:50% 62%"></figure>
    <figure><img src="img/home-bedroom.jpg" alt="A bright bedroom with an orange throw, an armchair and a view over trees" style="object-position:55% 55%"></figure>
  </div>
</div>
{rail([("10","Services"),(str(GROUP["beds"]),"Beds"),("2","Mental health hospitals"),("8","Specialist nursing homes")])}

<section class="sec"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">How can we help?</span><h2 class="h2">Start where <em>you are.</em></h2></div>
  <div class="doors">
    <a class="door" href="#refer">{ico("clipboard-check")}<span class="who">Commissioners and professionals</span><span class="t">Make a referral, or check a service before you do.</span><span class="d">Routes into care, legal frameworks, and every service side by side, ready for a brokerage or discharge conversation.</span><span class="go">For professionals {ar()}</span></a>
    <a class="door" href="#families">{ico("house-heart")}<span class="who">Families and friends</span><span class="t">Find the right place for someone you love.</span><span class="d">What a placement looks like day to day, how to arrange a visit, and how care is funded.</span><span class="go">For families {ar()}</span></a>
    <a class="door" href="#careers">{ico("users-round")}<span class="who">Careers</span><span class="t">Join the people who make St Matthews what it is.</span><span class="d">Ten services, one set of values, and a culture where speaking up is supported.</span><span class="go">Work with us {ar()}</span></a>
  </div>
</div></section>

<section class="sec cream"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Where we are</span><h2 class="h2">Ten services. <em>Three regions.</em></h2><p class="lede">Local placements, and repatriation from out of area. Choose a service to see who it is for, how people get in, and what the neighbourhood is like.</p></div>
  <div class="where"><div class="mapbox">{map_svg(interactive=False)}<p class="mapnote">Northampton, Spratton, Corby, Coventry and St Leonards-on-Sea.</p></div><div class="regions">{"".join(regions)}<a class="btn btn-navy" href="#services" style="align-self:flex-start">Find the right service {ar()}</a></div></div>
</div></section>

<section class="sec navy"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">The St Matthews pathway</span><h2 class="h2">Eight stages. <em>One provider, the whole way.</em></h2><p class="lede">{H(PATHWAY_INTRO)}</p></div>
  <ol class="path">{path}</ol>
  <div class="path-close"><p>{H(PATHWAY_CLOSE)}</p><a class="btn btn-light" href="#refer">How referrals work {ar()}</a></div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Why commissioners place with us</span><h2 class="h2">The placements <em>others decline.</em></h2></div>
  <div class="why">
    <div>{ico("anchor")}<span class="t">Placements that hold.</span><span class="d">Complex needs taken and kept, so the search does not start again.</span></div>
    <div>{ico("route")}<span class="t">One provider, every stage.</span><span class="d">Continuity of care across every stage, without searching for a new placement as needs change.</span></div>
    <div>{ico("venus-and-mars")}<span class="t">Single sex where it matters.</span><span class="d">Male only and female only wards and units across six of our services, for privacy, dignity, choice and wellbeing.</span></div>
    <div>{ico("map-pin")}<span class="t">Local, or the way home.</span><span class="d">Local placements, and repatriation from out of area.</span></div>
  </div>
</div></section>

<section class="sec cream"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Independent evidence</span><h2 class="h2">Scores you can <em>check for yourself.</em></h2><p class="lede">Review scores from carehome.co.uk, where families and residents review independently, a food hygiene rating and the trade press. Every one of them published by somebody other than us.</p></div>
  <div class="proof">
    {quote(ml["quotes"][0], "A family review of Maple Leaf House, carehome.co.uk")}
    <div class="seals">
      <a class="seal" href="#maple-leaf-house" style="text-decoration:none"><span class="f">9.5<small>out of 10</small></span><span class="w">Maple Leaf House</span><span class="s">carehome.co.uk review score, October 2026, from 9 reviews</span></a>
      <a class="seal alt" href="#willowbrook-house" style="text-decoration:none"><span class="f">9<small>out of 10</small></span><span class="w">Willowbrook House</span><span class="s">carehome.co.uk review score, September 2026, from 11 reviews</span></a>
      <a class="seal alt" href="#news" style="text-decoration:none"><span class="f">5<small>out of 5</small></span><span class="w">Food hygiene, Hawthorne House</span><span class="s">The highest rating there is, after inspection on 2 October 2026</span></a>
      <a class="seal" href="#news" style="text-decoration:none"><span class="f">Cover<small>story</small></span><span class="w">Care Home Professional</span><span class="s">Our digital journey, September 2026 issue</span></a>
    </div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="vision">
    <figure><img src="img/richard-whitby.jpg" alt="Richard Whitby, Chief Executive of St Matthews Healthcare" loading="lazy"><figcaption><b>Richard Whitby</b><span>Chief Executive Officer</span></figcaption></figure>
    <div class="txt"><span class="eyebrow">Our vision</span><h2 class="h2">We care.</h2><p>{H(VISION[0])}</p>{quote(VISION_CLOSE, "Richard Whitby, Chief Executive")}<a class="textlink" href="#about">Our mission and values {ar()}</a></div>
  </div>
</div></section>

<section class="sec cream"><div class="wrap">
  <div class="sec-head" style="flex-direction:row;justify-content:space-between;align-items:end;max-width:none;flex-wrap:wrap;gap:14px"><div style="display:flex;flex-direction:column;gap:14px"><span class="eyebrow">News</span><h2 class="h2">From across <em>St Matthews.</em></h2></div><a class="textlink" href="#news">All news {ar()}</a></div>
  <div class="cards3">{news}</div>
</div></section>

<section class="band navy">
  <div class="im"><img src="img/team-nurses.jpg" alt="Two St Matthews colleagues in uniform, smiling" loading="lazy" style="object-position:50% 12%"></div>
  <div class="tx on-navy"><span class="eyebrow">Careers</span><h2 class="h2">Built by <em>our people.</em></h2><p class="lede">Change at St Matthews is not being done to our people. It is being built by them. Join colleagues across ten services who see the person before the condition.</p><div class="btns"><a class="btn btn-light" href="#careers">Work with us {ar()}</a></div></div>
</section>

<section class="sec"><div class="wrap">{tiles()}</div></section>
</section>'''

def v_services():
    cards = "".join(card(s) for s in SERVICES) + f'<div class="shelp"><span class="eyebrow">Not sure which service fits?</span><span class="t">Tell us who you need to place.</span><span class="d">One referral line reaches every service, and our team will match the person to the right one.</span><span class="ln"><a href="tel:01604844192">{REF_PHONE}</a><a class="textlink" href="#refer-form">Start a referral {ar()}</a></span></div>'
    rows = []
    for sid, where, what, beds, units, ss, who, routes in MATRIX:
        rows.append(f'<tr><td class="sv"><a href="#{sid}">{H(BYID[sid]["name"])}</a></td><td data-l="Where">{H(where)}</td><td data-l="What it is">{H(what)}</td><td class="num" data-l="Beds">{beds}</td><td data-l="Units and wards">{H(units)}</td><td data-l="Single sex">{H(ss)}</td><td data-l="Who it is for">{H(who)}</td><td data-l="Routes in">{H(routes)}</td></tr>')
    bro = brochures_list()
    def fb(group, val, label, pressed=False):
        return f'<button type="button" class="fb" data-f="{group}" data-v="{val}" aria-pressed="{"true" if pressed else "false"}">{H(label)}</button>'
    return f'''<section class="view" data-view="services" aria-label="Our services" hidden>
<div class="phero navy"><div class="wrap on-navy">
  <div class="crumbs"><a href="#home">Home</a><span aria-hidden="true">/</span><span>Our services</span></div>
  <span class="eyebrow">Our services</span>
  <h1 class="h1">Ten services.<span class="ser">One standard.</span></h1>
  <p class="lede">Two independent mental health hospitals and eight specialist nursing homes, with {GROUP["beds"]} beds across Northamptonshire, Coventry and East Sussex. Filter by the kind of service, the region, or the way a person needs to come in.</p>
</div></div>
<section class="sec"><div class="wrap">
  <div class="finder">
    <div class="filters" aria-label="Filter services">
      <fieldset class="fgroup"><legend>Type of service</legend><div class="fbtns">{fb("type","all","All",True)}{fb("type","hospital","Hospitals")}{fb("type","nursing","Nursing homes")}</div></fieldset>
      <fieldset class="fgroup"><legend>Region</legend><div class="fbtns">{fb("region","all","All",True)}{fb("region","Northamptonshire","Northamptonshire")}{fb("region","Coventry","Coventry")}{fb("region","East Sussex","East Sussex")}</div></fieldset>
      <fieldset class="fgroup"><legend>Routes in and provision</legend><div class="fbtns">{fb("tag","stepdown","Step down")}{fb("tag","eol","End of life care")}{fb("tag","singlesex","Single sex provision")}{fb("tag","female","Female only provision")}</div><p class="fnote">Every service offers long term nursing, respite and discharge to assess.</p></fieldset>
      <div class="mapbox" style="padding:12px">{map_svg(interactive=True)}</div>
      <p class="count" aria-live="polite" id="fcount">Showing all 10 services</p>
      <button type="button" class="reset" id="freset">Clear filters</button>
    </div>
    <div><div class="sgrid" id="sgrid">{cards}</div><p class="empty" id="fempty" hidden>No service matches every filter you have chosen. Clear one, or call the referral line on {REF_PHONE} and tell us who you need to place.</p></div>
  </div>
</div></section>
<section class="sec cream" id="services-matrix"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">National referral reference</span><h2 class="h2">Every service, <em>side by side.</em></h2><p class="lede">A brokerage team with somebody to place reads across a row. Long term nursing, respite and discharge to assess are offered at every service. Timescales are agreed per referral, and fees are never published.</p></div>
  <div class="tscroll"><table class="mx"><thead><tr><th scope="col">Service</th><th scope="col">Where</th><th scope="col">What it is</th><th scope="col">Beds</th><th scope="col">Units and wards</th><th scope="col">Single sex</th><th scope="col">Who it is for</th><th scope="col">Routes in</th></tr></thead><tbody>{"".join(rows)}</tbody><tfoot><tr><td class="sv">Ten services</td><td data-l="Regions">Three regions</td><td class="emp"></td><td class="num" data-l="Beds">{GROUP["beds"]}</td><td colspan="4" class="emp"></td></tr></tfoot></table></div>
</div></section>
<section class="sec" id="services-brochures"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Brochures</span><h2 class="h2">Take a service <em>with you.</em></h2><p class="lede">Tap a cover to open the brochure, then download it to attach to a referral or print for a visit.</p></div>
  {bro}
</div></section>
<section class="sec cream"><div class="wrap">{tiles()}</div></section>
</section>'''

def brochures_list():
    items = []
    for sv in SERVICES:
        for label, f in sv["brochures"]:
            nm = sv["name"] if label == sv["name"] else f'{sv["name"]}: {label}'
            items.append(bro_card(nm, f))
    extra = bro_card("The St Matthews pathway", "St-Matthews-Pathway-A4.pdf") + bro_card("Our mission and values", "St-Matthews-Our-Mission-A4.pdf")
    return ('<div class="bgrid">' + "".join(items) + '</div>'
            '<div class="bsub"><span class="eyebrow">About St Matthews</span><h3 class="h3">The pathway, and our mission and values</h3></div>'
            '<div class="bgrid">' + extra + '</div>')

def hero_service(s):
    h = s["hero"]
    crumbs = f'<div class="crumbs"><a href="#home">Home</a><span aria-hidden="true">/</span><a href="#services">Our services</a><span aria-hidden="true">/</span><span>{H(s["name"])}</span></div>'
    facts = f'<div class="facts"><span><b>{H(s["place"])}</b></span><span><b>{s["beds"]}</b> beds</span><span>{H(s["typeLabel"])}</span></div>'
    btns = f'<div class="btns"><a class="btn btn-light" href="#refer-form" data-svc="{s["id"]}">Make a referral {ar()}</a><a class="btn btn-line" href="#contact">Arrange a visit</a></div>'
    copy = (f'<div class="copy">{crumbs}<span class="eyebrow">{H(s["kicker"])}</span>'
            f'<h1 class="h1">{H(s["h1"][0])}<span class="ser">{H(s["h1"][1])}</span></h1>'
            f'<p class="stand">{H(s["stand"])}</p>{facts}{btns}</div>')
    k = h["kind"]
    if k == "bleed":
        return f'<div class="shero bleed"><div class="bg"><img src="img/{h["img"]}" alt="{H(h["alt"])}" style="object-position:{h.get("pos","50% 50%")}"></div><div class="wrap" style="width:100%">{copy}</div></div>'
    if k == "plate":
        return f'<div class="shero split">{copy}<div class="plate"><img src="img/{h["img"]}" alt="{H(h["alt"])}" style="object-position:{h.get("pos","50% 50%")}"></div></div>'
    if k == "pair":
        return f'<div class="shero split mirror"><div class="pair"><div><img src="img/{h["img"]}" alt="{H(h["alt"])}"></div><div><img src="img/{h["img2"]}" alt="{H(h["alt2"])}"></div></div>{copy}</div>'
    if k == "row":
        strip = "".join(f'<img src="img/{i}" alt="{H(a)}">' for i, a in zip(h["imgs"], h["alts"]))
        return f'<div class="shero rowv"><div class="strip">{strip}</div><div class="wrap">{copy}</div></div>'

def offer_strip():
    items = "".join(f'<li>{ic(i)}<span>{H(l)}</span></li>' for t, l, i in EVERY_SERVICE)
    return f'<div class="offer"><span class="k">Available here, as at every St Matthews service</span><ul>{items}</ul></div>'

def v_service(s):
    who = "".join(f'<li>{H(x)}</li>' for x in s["who"])
    routes = "".join(f'<li>{H(x)}</li>' for x in s["routes"])
    legal = ("".join(f'<li>{H(x)}</li>' for x in s["legal"]) if s["legal"] else '<li class="note">Confirmed at referral.</li>')
    units = "".join(f'<div class="unit"><span class="n">{H(n)}</span><span class="g">{H(g)}</span><span class="d">{H(d)}</span></div>' for n, g, d in s["units"])
    why = "".join(f'<div><span class="n">{i+1:02d}</span><span class="t">{H(t)}</span><span class="d">{H(d)}</span></div>' for i, (t, d) in enumerate(s["why"]))
    show_steps = s["id"] != "the-moreton-centre"
    steps = "".join(f'<li><span class="n">{H(a)}</span><span class="t">{H(b)}</span><span class="e">{H(c)}</span><span class="d">{H(d)}</span></li>' for a, b, c, d in s["steps"])
    g = s["gallery"]
    gcls = {1: " n1", 2: " n2", 3: " n3"}.get(len(g), "")
    gallery = "".join(f'<figure><img src="img/{f}" alt="{H(a)}" loading="lazy"></figure>' for f, a in g)
    quotes = ""
    if s["quotes"]:
        who_by = {"What patients say": f"A patient, {s['name']}", "What residents say": f"A resident, {s['name']}",
                  "What families say": f"A family, {s['name']}", "Reviews on carehome.co.uk": f"A review of {s['name']}, carehome.co.uk"}.get(s["quoteLabel"], "")
        q = "".join(quote(t, who_by, light=(i == len(s["quotes"]) - 1)) for i, t in enumerate(s["quotes"]))
        cols = "twocol" if len(s["quotes"]) > 1 else ""
        quotes = f'<div><div class="sub-h"><span class="eyebrow">{H(s["quoteLabel"])}</span></div><div class="{cols}">{q}</div></div>'
    review = ""
    if s["review"]:
        r = s["review"]
        review = f'<div class="panel dark"><span class="k">carehome.co.uk review score</span><span class="score"><b>{r["score"]}</b><span>out of {r["out"]}</span></span><span class="sm">{r["when"]}, from {r["count"]} by residents, families and friends.</span><a class="textlink" href="https://www.carehome.co.uk/submitreview">Leave a review {ar()}</a></div>'
    bro = ""
    if s["brochures"]:
        bl = "".join(f'<a class="bmini" {bro_attrs((s["name"] if l == s["name"] else s["name"] + ": " + l), f)}><img src="brochures/thumb/{f[:-4]}.jpg" alt="" loading="lazy"><span><b>{H(l)}</b><span class="go">{ic("eye")}View brochure</span></span></a>' for l, f in s["brochures"])
        bro = f'<div class="panel" id="{s["id"]}-brochure"><span class="k">Brochure</span>{bl}</div>'
    aside = f'''<aside class="aside" aria-label="Key details">
  <div class="panel dark"><span class="k">Make a referral</span><span class="big">{REF_PHONE}</span>{email_inline()}<span class="sm">One referral line and one inbox reach every service in the group.</span><a class="btn btn-light" href="#refer-form" data-svc="{s["id"]}" style="justify-content:center;margin-top:6px">Start a referral {ar()}</a></div>
  <div class="panel"><span class="k">Address</span><span class="addr">{H(s["address"])}</span><div class="minimap">{map_svg(highlight=s["id"], interactive=False)}</div></div>
  <div class="panel" data-cqc-location="{s["cqc"].rsplit("/",1)[-1]}"><span class="k">Care Quality Commission</span><span class="addr">{H(s["name"])} is registered with the CQC{(" as " + chr(8220) + H(s["cqcName"]) + chr(8221)) if s.get("cqcDiff") else ""}. The CQC publishes its current rating and inspection reports.</span><a class="textlink" href="{s["cqc"]}" target="_blank" rel="noopener">Read the latest CQC report {ar()}</a></div>
  {review}{bro}
</aside>'''
    units_block = f'<div><div class="sub-h"><span class="eyebrow">{H(s["unitsTitle"])}</span><h2 class="h3">How the service is organised</h2></div><div class="units">{units}</div></div>'
    steps_block = (f'<div id="{s["id"]}-steps"><div class="sub-h"><span class="eyebrow">A placement here</span><h2 class="h2" style="font-size:clamp(1.9rem,3.2vw,2.6rem)">{H(s["stepsTitle"][0])} <em>{H(s["stepsTitle"][1])}</em></h2></div><ol class="steps">{steps}</ol></div>') if show_steps else ""
    who_note = f'<p class="note">{H(s["whoNote"])}</p>' if s["whoNote"] else ""
    jl = [(f'#{s["id"]}-glance', "users", "Who it is for")]
    if show_steps: jl.append((f'#{s["id"]}-steps', "footprints", "A placement here"))
    jl.append((f'#{s["id"]}-life', "sun", "Daily life"))
    jl.append((f'#{s["id"]}-photos', "images", "Photos"))
    if s["brochures"]: jl.append((f'#{s["id"]}-brochure', "file-text", "Brochure"))
    jump = '<nav class="jump" aria-label="On this page"><div class="wrap">' + "".join(f'<a href="{h}">{ic(i)}{H(t)}</a>' for h, i, t in jl) + f'<a class="ref" href="#refer-form" data-svc="{s["id"]}">{ic("phone-call")}Make a referral</a></div></nav>'
    idx = [x["id"] for x in SERVICES].index(s["id"])
    pv, nx = SERVICES[idx - 1], SERVICES[(idx + 1) % len(SERVICES)]
    nextprev = (f'<nav class="np" aria-label="More services"><div class="wrap"><a class="pv" href="#{pv["id"]}">{ic("arrow-left")}<span><small>Previous<span class="hm"> service</span></small><b>{H(pv["name"])}</b></span></a>'
                f'<a class="all" href="#services">All ten services</a>'
                f'<a class="nx" href="#{nx["id"]}"><span><small>Next<span class="hm"> service</span></small><b>{H(nx["name"])}</b></span>{ic("arrow-right")}</a></div></nav>')
    return f'''<section class="view" data-view="{s["id"]}" aria-label="{H(s["name"])}" hidden>
{hero_service(s)}
{rail(s["rail"])}
{jump}
<section class="sec svc-body"><div class="wrap"><div class="svc-grid"><div class="svc-main">
  <div id="{s["id"]}-glance"><div class="sub-h"><span class="eyebrow">At a glance</span><h2 class="h3">Who it is for, and how people come in</h2></div>
  <div class="cols3"><div><h3>{ic("users")}Who it is for</h3><ul class="list">{who}</ul>{who_note}</div><div><h3>{ic("door-open")}Routes in</h3><ul class="list">{routes}</ul></div><div><h3>{ic("scale")}Legal frameworks</h3><ul class="list">{legal}</ul></div></div>{offer_strip()}</div>
  {units_block}
  {steps_block}
  <div id="{s["id"]}-life"><div class="sub-h"><span class="eyebrow">Daily life and the neighbourhood</span><h2 class="h3">What a day looks like, and what is nearby</h2></div><div class="twocol life"><div><span class="lk">{ic("sun")}A day here</span><p>{H(s["life"])}</p></div><div><span class="lk">{ic("map-pin")}Nearby</span><p>{H(s["local"])}</p></div></div></div>
  <div class="gallery{gcls}" id="{s["id"]}-photos">{gallery}</div>
  {quotes}
</div>{aside}</div></div></section>
<section class="sec navy"><div class="wrap"><div class="sec-head"><span class="eyebrow">Why commissioners place here</span><h2 class="h2">{H(s["name"])}</h2></div><div class="why">{why}</div></div></section>
{nextprev}
<section class="sec"><div class="wrap">{tiles()}</div></section>
</section>'''

def v_refer():
    # routes, computed from tags
    ricons = {"longterm": "bed-double", "d2a": "hospital", "stepdown": "footprints", "respite": "calendar-heart", "eol": "hand-heart", "singlesex": "venus-and-mars"}
    defs = [
        ("longterm", "Long term nursing", "Nursing for as long as it is needed, at every one of our services."),
        ("d2a", "Discharge to assess", "Assessment and nursing direct from a hospital bed, at every one of our services."),
        ("respite", "Respite and planned stays", "Short stays and planned breaks, at every one of our services."),
        ("stepdown", "Step down", "From a hospital bed, or within our own services as support needs reduce."),
        ("eol", "End of life care", "Nursing care and end of life care accepted, with palliative care here when the time comes."),
        ("singlesex", "Single sex provision", "Male only and female only wards and units, for privacy, dignity, choice and wellbeing. Female only provision at Althorp Grange and The Moreton Centre, with a new ward opening soon at The Dallingtons."),
    ]
    rb = []
    for tag, t, d in defs:
        every = all(tag in s["tags"] for s in SERVICES)
        li = '<li><a href="#services">All ten services</a></li>' if every else "".join(f'<li><a href="#{s["id"]}">{H(s["name"])}</a></li>' for s in SERVICES if tag in s["tags"])
        rb.append(f'<div class="route">{ico(ricons[tag], "")}<span class="t">{H(t)}</span><span class="d">{H(d)}</span><ul>{li}</ul></div>')
    hosp = "".join(f'<li><a href="#{s["id"]}">{H(s["name"])}</a></li>' for s in SERVICES if s["type"] == "hospital")
    rb.insert(0, f'<div class="route">{ico("brain", "")}<span class="t">Mental health rehabilitation</span><span class="d">High dependency rehabilitation in our two independent mental health hospitals.</span><ul>{hosp}</ul></div>')
    legal_s = [s for s in SERVICES if s["legal"]]
    legal = "".join(f'<li><b>{H(s["name"])}</b>: {H("; ".join(s["legal"]))}</li>' for s in legal_s)
    opts = "".join(f'<option value="{s["id"]}">{H(s["name"])}, {H(s["place"].split(",")[0])}</option>' for s in SERVICES)
    steps = [("The enquiry", "One referral line and one inbox reach every service in the group."),
             ("The assessment", "Pre admission assessment by our clinical team, wherever the person is, with a clear view of what we can offer."),
             ("The match", "The service, the unit, single sex where it matters, and the observation level."),
             ("The admission", "Discharge to assess, planned from hospital or home, respite, and Section 117.")]
    sicons = ["phone-call", "clipboard-check", "puzzle", "door-open"]
    st = "".join(f'<li class="feat step"><div class="top">{ico(sicons[i])}<span class="num" aria-hidden="true">{i+1}</span></div><span class="n">Step {i+1}</span><span class="t">{H(t)}</span><span class="d">{H(d)}</span></li>' for i, (t, d) in enumerate(steps))
    return f'''<section class="view" data-view="refer" aria-label="For professionals" hidden>
<div class="phero navy"><div class="wrap on-navy">
  <div class="crumbs"><a href="#home">Home</a><span aria-hidden="true">/</span><span>For professionals</span></div>
  <span class="eyebrow">For commissioners, brokerage, social workers and discharge teams</span>
  <h1 class="h1">One referral line.<span class="ser">Every service.</span></h1>
  <p class="lede">Tell us who you cannot place. Enquiries and assessments are welcome now, and one referral line and one inbox reach every service in the group.</p>
  <div class="btns"><a class="btn btn-light" href="#refer-form">Start a referral {ar()}</a><a class="btn btn-line" href="#services-matrix">Every service side by side</a></div>
</div></div>
<section class="rail" aria-label="Referral contacts"><div class="wrap two"><div class="c"><span class="l">Referral line</span><span class="f">{REF_PHONE}</span></div><div class="c"><span class="l">Referral email</span><span class="f em">{REF_EMAIL}</span></div></div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">How a referral works</span><h2 class="h2">From the first call <em>to the admission.</em></h2><p class="lede">Timescales are agreed per referral. Whatever the route in, the person is assessed by our clinical team before admission.</p></div>
  <ol class="feats steps4">{st}</ol>
  <p style="margin-top:22px"><a class="textlink" href="#home">See all eight stages of the pathway, through to moving on or staying {ar()}</a></p>
</div></section>

<section class="sec cream"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Routes into care</span><h2 class="h2">Find the service <em>by the way in.</em></h2><p class="lede">Alongside planned admissions, these are the routes into care and the provision that are specific to some of our services.</p></div>
  <div class="routes">{"".join(rb)}</div>
</div></section>

<section class="sec"><div class="wrap"><div class="twocol">
  <div><span class="eyebrow">Legal frameworks</span><h2 class="h3" style="margin-top:10px">What each service states</h2><ul class="list" style="margin-top:14px">{legal}</ul><p class="note" style="margin-top:12px">Other services do not state legal frameworks in their published material. Confirm at referral.</p></div>
  <div><span class="eyebrow">Funding</span><h2 class="h3" style="margin-top:10px">Agreed with the commissioner</h2><p style="margin-top:14px">Placements are funded through the NHS and local authorities, including Section 117 aftercare. Observation levels and the cost of a placement are agreed per referral. Fees are a conversation, never a published price.</p><p class="muted" style="margin-top:12px">Service brochures are ready to attach to a placement paper.</p><a class="textlink" href="#services-brochures" style="margin-top:12px">Service brochures {ar()}</a></div>
</div></div></section>

<section class="sec cream" id="refer-form"><div class="wrap">
  <div class="formwrap">
    <div style="display:flex;flex-direction:column;gap:16px"><span class="eyebrow">Start a referral</span><h2 class="h2">Tell us <em>who you need to place.</em></h2><p class="muted">Complete the form and press Send referral. Your email app opens with the referral addressed to our referrals inbox, ready to send. Prefer to talk it through? Call the referral line.</p>
      <ul class="sendlist"><li>{ic("send")}<span><b>Straight to our referrals inbox.</b>The form addresses your referral to {REF_EMAIL}.</span></li><li>{ic("paperclip")}<span><b>Add your documents.</b>Attach any referral paperwork to the email before you send it.</span></li><li>{ic("lock")}<span><b>No identifying details.</b>We ask for the person’s name, date of birth and NHS number securely, once we speak.</span></li></ul>
      <div class="panel dark"><span class="k">Or contact us directly</span><span class="big">{REF_PHONE}</span>{email_inline()}<span class="sm">Send referral documents to {REF_EMAIL}.</span></div></div>
    <div>
    <form class="ref" id="refform" novalidate>
      <p class="warn full">Please do not include the person’s name, date of birth or NHS number in this form. We will ask for those securely.</p>
      <div class="field"><label for="f-role">I am a</label><select id="f-role" required><option value="">Choose one</option><option>ICB or continuing healthcare team</option><option>Local authority commissioner or brokerage</option><option>Social worker</option><option>Hospital discharge team</option><option>NHS clinician</option><option>Family member or friend</option><option>Other</option></select></div>
      <div class="field"><label for="f-org">Organisation</label><input id="f-org" autocomplete="organization"></div>
      <div class="field"><label for="f-name">Your name</label><input id="f-name" autocomplete="name" required></div>
      <div class="field"><label for="f-email">Work email</label><input id="f-email" type="email" autocomplete="email" required></div>
      <div class="field"><label for="f-tel">Telephone</label><input id="f-tel" type="tel" autocomplete="tel"></div>
      <div class="field"><label for="f-svc">Service of interest</label><select id="f-svc"><option value="">Not sure yet</option>{opts}</select></div>
      <div class="field"><label for="f-need">Main need</label><select id="f-need"><option>Not sure yet</option><option>Mental health rehabilitation</option><option>Complex needs nursing</option><option>Long term nursing</option><option>Mental health and nursing, older adults</option><option>Discharge to assess</option><option>Step down from hospital</option><option>Respite</option><option>End of life care</option><option>Female only provision</option></select></div>
      <div class="field"><label for="f-fund">Funding route</label><select id="f-fund"><option>Not yet known</option><option>NHS continuing healthcare</option><option>Section 117 aftercare</option><option>Local authority</option><option>Joint funded</option></select></div>
      <div class="field"><label for="f-when">How soon</label><select id="f-when"><option>As soon as possible</option><option>Within the next few weeks</option><option>Planning ahead</option></select></div>
      <div class="field"><label for="f-area">Area the person is from</label><input id="f-area" placeholder="For example, Coventry"></div>
      <div class="field full"><label for="f-msg">About the need, without identifying details</label><textarea id="f-msg" placeholder="Diagnosis, current setting, risks, observation level, and why the current placement is ending."></textarea></div>
      <p class="err full" id="f-err" role="alert" hidden>Please choose who you are, and add your name and a valid email address.</p>
      <div class="full sendrow"><button class="btn btn-navy" type="submit">{ic("send")}<span>Send referral</span></button><span class="sendnote">Opens your email app with the referral addressed to {REF_EMAIL}, ready to send. <a href="#privacy">How we use your details</a></span></div>
    </form>
    <div class="done-box" id="refdone" hidden tabindex="-1" aria-labelledby="refdone-t">
      <div class="dhead">{ico("circle-check")}<div class="dtt"><span class="eyebrow" id="refdone-k">Nearly there</span><h3 class="h3" id="refdone-t">Your referral is ready to send.</h3></div></div>
      <p id="refdone-p">Your email app should now be open with the referral addressed to <b>{REF_EMAIL}</b>. Attach any documents, then press send.</p>
      <p class="dlong" id="reflong" hidden>Your note was long, so the email holds a shortened version. Copy the summary and paste it into the email in full.</p>
      <div class="btns"><a class="btn btn-light" id="refmail" href="mailto:{REF_EMAIL}">{ic("mail")}<span>Open the email again</span></a><button class="btn btn-line" type="button" id="refcopy">{ic("copy")}<span>Copy summary</span></button><button class="btn btn-line" type="button" id="refedit">{ic("pencil")}<span>Edit</span></button></div>
      <span class="k">Your referral</span><pre id="refsum"></pre>
      <p class="sm" id="refdone-f">Email app not opening? Copy the summary and send it to {REF_EMAIL}, or call {REF_PHONE} and we will take it from there.</p></div>
    </div>
  </div>
</div></section>
</section>'''

def v_families():
    local = "".join(f'<li>{ic("map-pin")}<span><b>{H(s["name"])}</b>{H(s["local"])}</span></li>' for s in SERVICES)
    wb = BYID["willowbrook-house"]; ml = BYID["maple-leaf-house"]
    return f'''<section class="view" data-view="families" aria-label="For families" hidden>
<div class="shero split"><div class="copy"><div class="crumbs"><a href="#home">Home</a><span aria-hidden="true">/</span><span>For families</span></div><span class="eyebrow">For families and friends</span>
  <h1 class="h1">Your family becomes our family.<span class="ser">A room they can truly call home.</span></h1>
  <p class="stand">Choosing specialist care for someone you love is a big decision. Here is what a placement with us looks like, how to arrange a visit, and how care is funded.</p>
  <div class="btns"><a class="btn btn-light" href="#contact">Arrange a visit {ar()}</a><a class="btn btn-line" href="#services">Find a service</a></div></div>
  <div class="plate"><img src="img/fam-bedroom-yellow.jpg" alt="A bright bedroom with yellow bedding, a matching armchair, and a table and chairs by a window over trees" style="object-position:42% 50%"></div></div>

<section class="sec"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">What to expect</span><h2 class="h2">Care built around <em>the person.</em></h2></div>
  {feats([("bed-double", "Settling in", "A room they can truly call home.", "With a personalised care plan reviewed and adapted as often as their needs change."),
          ("sun", "Living well", "A day worth having.", "Therapy, activity and outings. The things that make a day worth having."),
          ("refresh-cw", "As needs change", "Care that adapts.", "Person centred care that adapts as needs change, so support stays appropriate and meaningful."),
          ("house-heart", "Staying", "No search to restart.", "Step down within our own services, or a home here for as long as needed.")])}
  <div class="lifestrip">
    <figure><img src="img/av-baking.jpg" alt="Residents and colleagues baking together around a table at The Avenue" loading="lazy" style="object-position:50% 40%"></figure>
    <figure><img src="img/fam-cinema.jpg" alt="A cinema room with rows of red and cream reclining seats" loading="lazy"></figure>
    <figure><img src="img/wb-dining.jpg" alt="Tea in the dining room at Willowbrook House" loading="lazy"></figure>
  </div>
</div></section>

<section class="sec cream"><div class="wrap">
  <div class="twocol" style="align-items:start">
    <div class="nbsticky" style="display:flex;flex-direction:column;gap:16px"><span class="eyebrow">Know the neighbourhood</span><h2 class="h2">What is <em>round the corner.</em></h2><p class="lede">Every service page names the real places nearby: churches, parks, walks, shops and stations. It is the question families ask first, and the answer helps you picture visiting.</p><figure class="nbimg"><img src="img/smh-front.jpg" alt="St Matthews Hospital, a Victorian house with bay windows behind a hedge on St Matthews Parade, Northampton" loading="lazy"><figcaption>St Matthews Parade, Northampton</figcaption></figure></div>
    <ul class="list pins">{local}</ul>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Funding</span><h2 class="h2">How a placement <em>is paid for.</em></h2><p class="lede">Placements can be funded in different ways. Our team will talk you through how a placement is funded before anything is agreed.</p></div>
  <div class="routes">
    <div class="route">{ico("heart-pulse")}<span class="t">NHS continuing healthcare</span><span class="d">Care arranged and funded by the NHS for adults whose needs are mainly health needs, following an assessment by the local integrated care board.</span></div>
    <div class="route">{ico("scale")}<span class="t">Section 117 aftercare</span><span class="d">Aftercare for people who have been detained under certain sections of the Mental Health Act, arranged by the NHS and the local authority together.</span></div>
    <div class="route">{ico("landmark")}<span class="t">Local authority funding</span><span class="d">Care arranged by the council's adult social care team, following a care needs assessment and a financial assessment.</span></div>
  </div>
</div></section>

<section class="sec cream"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">What families say</span><h2 class="h2">In their <em>own words.</em></h2></div>
  <div class="twocol">{quote(wb["quotes"][0], "A family of a resident at Willowbrook House")}{quote(ml["quotes"][0], "A family review of Maple Leaf House, carehome.co.uk", light=True)}</div>
  <p style="margin-top:26px" class="muted">Families and friends can share their experience independently at carehome.co.uk. <a href="https://www.carehome.co.uk/submitreview">Leave a review</a>.</p>
</div></section>
<section class="sec"><div class="wrap">{tiles()}</div></section>
</section>'''

def v_about():
    vals = "".join(f'<div><span class="n">{i+1:02d}</span><span class="t">{H(v)}</span></div>' for i, v in enumerate(VALUES))
    vis = "".join(f'<p>{H(p)}</p>' for p in VISION)
    return f'''<section class="view" data-view="about" aria-label="About us" hidden>
<div class="phero navy"><div class="wrap on-navy">
  <div class="crumbs"><a href="#home">Home</a><span aria-hidden="true">/</span><span>About us</span></div>
  <span class="eyebrow">Our mission and values</span>
  <h1 class="h1">We care.<span class="ser">Six values, one standard.</span></h1>
  <p class="lede">{H(MISSION_LEAD)}</p>
</div></div>
{rail([("10","Services"),(str(GROUP["beds"]),"Beds"),("2","Hospitals"),("8","Nursing homes")])}
<section class="sec" id="about-values"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Our values</span><h2 class="h2">Six values. <em>One culture.</em></h2><p class="lede">{H(MISSION_REST)}</p></div>
  {vcards()}
</div></section>
<section class="sec cream"><div class="wrap"><div class="vision">
  <figure><img src="img/richard-whitby.jpg" alt="Richard Whitby, Chief Executive of St Matthews Healthcare" loading="lazy"><figcaption><b>Richard Whitby</b><span>Chief Executive Officer</span></figcaption></figure>
  <div class="txt"><span class="eyebrow">Our vision, in the words of our Chief Executive</span>{vis}{quote(VISION_CLOSE, "Richard Whitby, Chief Executive")}</div>
</div></div></section>
<section class="sec" id="about-leadership"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Our leadership</span><h2 class="h2">Meet the senior <em>leadership team.</em></h2></div>
  <div class="team">{team()}</div>
</div></section>
<section class="sec cream"><div class="wrap"><div class="where">
  <div class="mapbox">{map_svg(interactive=False)}</div>
  <div style="display:flex;flex-direction:column;gap:18px"><span class="eyebrow">Where we work</span><h2 class="h2">Northamptonshire, Coventry <em>and East Sussex.</em></h2><p class="lede">Two independent mental health hospitals and eight specialist nursing homes. Mental health is the thread through all of them, from rehabilitation to specialist nursing for older adults.</p><a class="btn btn-navy" href="#services" style="align-self:flex-start">Our services {ar()}</a></div>
</div></div></section>
<section class="band navy"><div class="im"><img src="img/about-phil.jpg" alt="Phil Tattersall, National Business Development Director at St Matthews Healthcare" loading="lazy" style="object-position:50% 24%"></div>
  <div class="tx on-navy"><span class="eyebrow">In the press, September 2026</span><h2 class="h2">Ahead of <em>the curve.</em></h2><p class="lede">Our digital journey made the cover of Care Home Professional, in a six page feature with Nourish Care under the headline “Tech should enhance rather than replace”.</p><a class="textlink" href="#news">Read the story {ar()}</a></div></section>
<section class="sec"><div class="wrap"><div class="twocol">
  <div><span class="eyebrow">The company</span><h2 class="h3" style="margin-top:10px">St Matthews Healthcare</h2><p style="margin-top:12px">{H(GROUP["company"])}. Registered office {H(GROUP["office"])}. The Moreton Centre is operated by St Matthews (Moreton Centre) Limited, part of St Matthews Healthcare.</p></div>
  <div><span class="eyebrow">Regulation</span><h2 class="h3" style="margin-top:10px">Registered with the CQC</h2><p style="margin-top:12px">Every service is registered with the Care Quality Commission, which publishes its current ratings and reports. Each service page links to its own CQC profile.</p></div>
</div></div></section>
</section>'''

def v_news():
    st = []
    for n in NEWS:
        body = "".join(f'<p>{H(p)}</p>' for p in n["body"])
        ext = n["link"] and not n["link"][1].startswith("#")
        link = (f'<a class="textlink" href="{n["link"][1]}"' + (' target="_blank" rel="noopener"' if ext else '') + f'>{H(n["link"][0])} {ar()}</a>') if n["link"] else ""
        tall = " tall" if (n["id"] in ("press", "speakup") or n.get("tall")) else ""
        spos = "" if tall else f' style="object-position:{n.get("pos","50% 50%")}"'
        st.append(f'<article class="story" id="news-{n["id"]}"><div class="im{tall}"><img src="img/{n["img"]}" alt="{H(n["alt"])}" loading="lazy"{spos}></div><div class="tx"><span class="eyebrow">{H(n["tag"])} &middot; {H(n["date"])}</span><h2 class="h2" style="font-size:clamp(2rem,3.6vw,2.8rem)">{H(n["title"])}</h2><p class="lede">{H(n["lede"])}</p>{body}{link}</div></article>')
    return f'''<section class="view" data-view="news" aria-label="News" hidden>
<div class="phero navy"><div class="wrap on-navy"><div class="crumbs"><a href="#home">Home</a><span aria-hidden="true">/</span><span>News</span></div><span class="eyebrow">News</span><h1 class="h1">From across<span class="ser">St Matthews.</span></h1></div></div>
<section class="sec"><div class="wrap">{"".join(st)}</div></section>
<section class="sec cream"><div class="wrap">{tiles()}</div></section>
</section>'''

def v_careers():
    vals = "".join(f'<div><span class="n">{i+1:02d}</span><span class="t">{H(v)}</span></div>' for i, v in enumerate(VALUES))
    roles = [("Nursing", "Registered nurses across mental health hospitals and specialist nursing homes."),
             ("Care and support", "Assistant practitioners and care colleagues, at the heart of every shift."),
             ("Therapies", "Psychology and occupational therapy, within the multidisciplinary team."),
             ("Activities and wellbeing", "Event coordination, activities and the outings that make a day worth having."),
             ("Kitchen and hospitality", "Chefs and kitchen teams cooking fresh, safely and well."),
             ("Support services", "The teams behind every service, from the front door to the back office.")]
    roleicons = ["stethoscope", "hand-heart", "brain", "palette", "chef-hat", "building-2"]
    rl = "".join(f'<div class="route">{ico(roleicons[i], "")}<span class="t">{H(t)}</span><span class="d">{H(d)}</span>'
                 f'<button class="rq" type="button" data-job="{H(t)}" aria-haspopup="dialog">{ic("mail")}<span>Enquire about {H(t.lower())}</span>{ar()}</button></div>' for i, (t, d) in enumerate(roles))
    jobhelp = (f'<div class="jobhelp"><div class="jh-tx"><span class="eyebrow">Our recruitment team</span><span class="t">Not sure where you would fit?</span>'
               f'<span class="d">Tell us a little about yourself and we will talk you through the roles across our services.</span></div>'
               f'<div class="jh-ac"><button class="btn btn-light" type="button" data-job="" aria-haspopup="dialog">{ic("send")}<span>Send a general enquiry</span></button>'
               f'<span class="copyrow"><a href="mailto:{REC_EMAIL}">{REC_EMAIL}</a><button class="copy-btn" type="button" data-copy="{REC_EMAIL}" aria-label="Copy the recruitment email">Copy</button></span></div></div>')
    return f'''<section class="view" data-view="careers" aria-label="Careers" hidden>
<div class="shero split"><div class="copy"><div class="crumbs"><a href="#home">Home</a><span aria-hidden="true">/</span><span>Careers</span></div><span class="eyebrow">Careers at St Matthews</span>
  <h1 class="h1">Built by our people.<span class="ser"><span class="nw">I see you.</span> <span class="nw">I hear you.</span> <span class="nw">You matter.</span></span></h1>
  <p class="stand">Change at St Matthews is not being done to our people. It is being built by them. Transformation happens because people believe in it, feel listened to and feel valued.</p>
  <div class="btns"><a class="btn btn-light" href="#careers-roles">Roles across our services {ar()}</a><button class="btn btn-line" type="button" data-job="" aria-haspopup="dialog">Send an enquiry</button></div></div>
  <div class="plate"><img src="img/careers-team.jpg" alt="A group of St Matthews colleagues on the lawn in front of a Victorian red brick house" style="object-position:50% 78%"></div></div>
<section class="sec"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">What you can expect</span><h2 class="h2">A culture where <em>every voice counts.</em></h2></div>
  {feats([("megaphone", "Speak up", "Listened to, and followed up.", "We promise to listen with respect, take every concern seriously and follow up so you know what is happening."),
          ("life-buoy", "Support", "Here for you.", "Free, confidential support, 24 hours a day, through Your Assistance Programme."),
          ("award", "Recognition", "Great people make a difference.", "From a five star kitchen at Hawthorne House to our Falls Champion, we celebrate the work done when nobody is watching."),
          ("sprout", "Change", "Built together.", "People have stepped up, teams have challenged themselves and ideas have become action.")])}
</div></section>
<section class="sec cream" id="careers-teamday"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">The team day in pictures</span><h2 class="h2">Two hospitals, one field <em>and a lot of team spirit.</em></h2><p class="lede">Teams from both hospitals took on challenge after challenge together. Thank you to everyone who took part and made the day what it was.</p></div>
  <div class="tdgrid">
    <figure class="w2"><img src="img/teamday-hoop.jpg" alt="Colleagues working together on a pipe and ring challenge" loading="lazy" style="object-position:40% 50%"></figure>
    <figure><img src="img/teamday-bibs.jpg" alt="Colleagues in team bibs planning their next move" loading="lazy" style="object-position:50% 30%"></figure>
    <figure><img src="img/teamday-blanket.jpg" alt="A team balancing together on a blanket" loading="lazy" style="object-position:50% 55%"></figure>
    <figure><img src="img/teamday-arch.jpg" alt="Colleagues raising their poles together to form an arch" loading="lazy" style="object-position:50% 35%"></figure>
    <figure><img src="img/teamday-pipe.jpg" alt="A team guiding a ball along a length of pipe" loading="lazy" style="object-position:50% 35%"></figure>
    <figure><img src="img/teamday-laugh.jpg" alt="Colleagues in team bibs sharing a laugh at the team day" loading="lazy" style="object-position:50% 34%"></figure>
    <figure><img src="img/teamday-thumbs.jpg" alt="A smiling colleague in bee antennae and glasses" loading="lazy" style="object-position:50% 60%"></figure>
  </div>
  <div style="margin:32px auto 0;max-width:760px">{quote("We did the exercises. We challenged each other. We laughed.", "From our hospital team day", light=True)}</div>
</div></section>
<section class="band navy short"><div class="im rating"><div class="rbox"><span class="k">Food hygiene rating</span><span class="big">5</span><span class="of">out of 5, very good</span><span class="s">The kitchen at Hawthorne House, inspected on 2 October 2026</span></div></div>
  <div class="tx on-navy"><div class="spot"><img class="round" src="img/hh-chef-manager.jpg" alt="Alan, Head Chef, with the Registered Manager of Hawthorne House, holding the 5 food hygiene rating" loading="lazy" style="object-position:50% 14%"><div style="display:flex;flex-direction:column;gap:8px"><span class="eyebrow">Hawthorne House, Head Chef</span><h2 class="h2">Celebrating <em>Alan.</em></h2></div></div><p class="lede" style="color:var(--on-navy)">We are incredibly proud to celebrate Alan, our Head Chef, following our fantastic five star food hygiene rating.</p><p style="color:var(--on-navy)">His hard work, attention to detail and commitment to compliance have been instrumental in achieving this result. Alan takes enormous pride in the kitchen and the service he provides.</p><p style="font-size:.875rem;color:var(--blue-lt)">Pictured: Alan, Head Chef, with the Registered Manager of Hawthorne House.</p><a class="textlink" href="#news-kitchen">Read the story {ar()}</a></div></section>
<section class="sec"><div class="wrap"><div class="twocol" style="align-items:center">
  {quote("I’m passionate about helping our residents stay active, independent and confident. Movement really does matter.", "Mercy Joy, Assistant Practitioner and Falls Champion, Hawthorne House")}
  <div style="display:flex;flex-direction:column;gap:14px"><div class="spot"><img class="round" src="img/team-nurses.jpg" alt="Mercy Joy with her manager at Hawthorne House" loading="lazy"><div style="display:flex;flex-direction:column;gap:8px"><span class="eyebrow">Staff spotlight</span><h2 class="h2">Meet <em>Mercy Joy.</em></h2></div></div><p>Mercy is our Falls Champion at Hawthorne House, helping to promote safety, confidence and independence for residents. She is piloting a project with Arthritis Action, exploring why movement matters, and has shared her knowledge of falls prevention on a podcast.</p></div>
</div></div></section>
<section class="sec cream" id="careers-roles"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Where you could work</span><h2 class="h2">Ten services. <em>Many ways in.</em></h2><p class="lede">Roles across our two hospitals and eight nursing homes in Northamptonshire, Coventry and East Sussex. Choose an area of work to send a short enquiry to our recruitment team.</p></div>
  <div class="routes">{rl}</div>
  {jobhelp}
</div></section>
<section class="sec navy"><div class="wrap"><div class="sec-head"><span class="eyebrow">Our values</span><h2 class="h2">Six values. <em>One culture.</em></h2></div>{vcards()}</div></section>
</section>'''

def v_contact():
    addr = "".join(f'<li><a href="#{s["id"]}"><span class="n">{H(s["name"])}</span><span class="m">{H(s["address"])}</span></a></li>' for s in SERVICES)
    return f'''<section class="view" data-view="contact" aria-label="Contact" hidden>
<div class="phero navy"><div class="wrap on-navy"><div class="crumbs"><a href="#home">Home</a><span aria-hidden="true">/</span><span>Contact</span></div><span class="eyebrow">Contact</span><h1 class="h1">Talk to us.<span class="ser">One line, every service.</span></h1><p class="lede">Referrals, enquiries and visits all start in the same place, so nothing waits in the wrong inbox.</p></div></div>
<section class="sec"><div class="wrap"><div class="twocol">
  <div class="panel dark" style="padding:32px"><span class="k">Referral line</span><span class="big" style="font-size:2.6rem">{REF_PHONE}</span><span class="k" style="margin-top:14px">Referral email</span>{email_inline()}<span class="sm">For referrals, enquiries and to arrange a visit to any service.</span><a class="btn btn-light" href="#refer-form" style="justify-content:center;margin-top:10px">Start a referral {ar()}</a></div>
  <div style="display:flex;flex-direction:column;gap:16px"><span class="eyebrow">Arrange a visit</span><h2 class="h2">See it <em>for yourself.</em></h2><p>Commissioners and families are welcome to visit. Call or email, tell us which service you would like to see, and we will arrange it with the service.</p><span class="eyebrow" style="margin-top:12px">Registered office</span><p>{H(GROUP["office"])}</p><span class="eyebrow" style="margin-top:12px">Careers</span><p>Enquiries about working with us go to our recruitment team at <a class="brk" href="mailto:{REC_EMAIL}">{REC_EMAIL}</a>.</p><a class="textlink" href="#careers-roles">Roles across our services {ar()}</a></div>
</div></div></section>
<section class="sec cream"><div class="wrap"><div class="where">
  <div class="mapbox">{map_svg(interactive=False)}</div>
  <div class="region"><h3><span>Our addresses</span><span>10 services</span></h3><ul>{addr}</ul></div>
</div></div></section>
</section>'''

PRIVACY_UPDATED = "6 October 2026"

def v_privacy():
    sec = lambda h, body: f'<section class="lg"><h2 class="h3">{h}</h2>{body}</section>'
    return f'''<section class="view" data-view="privacy" aria-label="Privacy and cookies" hidden>
<div class="phero navy"><div class="wrap on-navy"><div class="crumbs"><a href="#home">Home</a><span aria-hidden="true">/</span><span>Privacy and cookies</span></div><span class="eyebrow">Privacy and cookies</span><h1 class="h1">Your information.<span class="ser">How this website handles it.</span></h1><p class="lede">What happens to information when you use this website, including our referral and careers enquiry forms.</p></div></div>
<section class="sec"><div class="wrap"><div class="legal">
{sec("Who we are", f"<p>This website is run by St Matthews Ltd, trading as St Matthews Healthcare, registered in England, company number 4611507. Our registered office is {H(GROUP['office'])}.</p><p>St Matthews Ltd is responsible, as the data controller, for information you send us through this website.</p>")}
{sec("What this website collects on its own", "<p>Nothing about you. This website does not use cookies, visitor statistics or any kind of tracking, and it does not load fonts, maps or videos from other companies.</p><p>The one exception is the official ratings widget from the Care Quality Commission on each service page, which the law asks us to show. It loads from the CQC website, and the CQC&#x27;s own privacy notice covers it.</p><p>Like every website, the company that hosts this one may keep standard technical records, such as the address of the device that asked for a page, to keep the site secure and running.</p>")}
{sec("Your text size setting", "<p>If you change the text size, your browser remembers your choice on your own device so the site opens at the same size next time. It is never sent to us. Clearing your browser history removes it.</p>")}
{sec("Our referral and careers forms", f"<p>Our forms do not send or store anything on the website. When you press Send referral or Send enquiry, the form opens your own email app with a message addressed to us. Nothing reaches us unless you send that email yourself.</p><p>Referrals go to our referral team at {REF_EMAIL}. Careers enquiries go to our recruitment team at {REC_EMAIL}. We use what you send to respond to your referral or enquiry, and to arrange an assessment, a visit or an interview if you would like to go ahead.</p><p>Please do not include the name, date of birth or NHS number of the person you are referring. We will ask for those securely when we speak.</p>")}
{sec("Why we can use your details", "<p>We use the details in your email because we have a legitimate interest in responding to enquiries about our services and about working with us. For careers enquiries, we also use them to take the steps you ask us to take before any offer of employment.</p>")}
{sec("Who we share them with", "<p>We do not sell your information or share it for marketing. We only share it where we need to in order to deal with your referral or enquiry, or where the law requires us to.</p>")}
{sec("How long we keep them", "<p>We keep enquiry emails only for as long as we need them to deal with your referral or enquiry, in line with our records retention policy.</p>")}
{sec("Your rights", f"<p>You can ask for a copy of the information we hold about you, and ask us to correct it, delete it, limit how we use it or stop using it. To make a request, write to Data protection, St Matthews Ltd, {H(GROUP['office'])}.</p><p>If you are unhappy with how we have handled your information, you can complain to the Information Commissioner&#x27;s Office at <a href='https://ico.org.uk'>ico.org.uk</a>.</p>")}
{sec("Cookies", "<p>This website does not set any cookies of its own, so there is no cookie banner. If that changes, for example if we add visitor statistics, we will update this notice and ask for your consent where the law requires it.</p>")}
<p class="muted lg-date">This notice was last updated on {PRIVACY_UPDATED}.</p>
</div></div></section>
</section>'''

TOAST = '<div class="toast" id="toast" role="status" hidden></div>'

def all_views():
    return [v_home(), v_services(), v_refer(), v_families(), v_about(), v_news(), v_careers(), v_contact(), v_privacy()] + [v_service(s) for s in SERVICES]

def viewer_html():
    return (f'<div class="viewer" id="viewer" role="dialog" aria-modal="true" aria-labelledby="viewer-t" hidden>'
              f'<div class="vbar"><div class="vtt"><span class="vk">Brochure</span><span class="vt" id="viewer-t"></span></div>'
              f'<div class="vact"><a class="btn btn-light vdl" id="viewer-dl" href="#" data-dl="">{ic("download")}<span class="lbl">Download PDF</span><span class="lbs">PDF</span></a>'
              f'<button class="vx" type="button" id="viewer-x" aria-label="Close the brochure">{ic("x")}</button></div></div>'
              f'<div class="vbody" id="viewer-body"><p class="vload">Opening the brochure</p><img id="viewer-img" alt=""></div></div>')

def job_html():
    roles = ["Nursing", "Care and support", "Therapies", "Activities and wellbeing", "Kitchen and hospitality", "Support services"]
    ropts = "".join(f'<option>{H(r)}</option>' for r in roles)
    areas = "".join(f'<option>{a}</option>' for a in ("Northamptonshire", "Coventry", "East Sussex"))
    sopts = "".join(f'<option>{H(x["name"])}, {H(x["place"].split(",")[0])}</option>' for x in SERVICES)
    return (f'<dialog class="dlg" id="jobdlg" aria-labelledby="job-t">'
           f'<div class="dlg-bar"><div class="vtt"><span class="vk">Careers enquiry</span><span class="vt" id="job-t">Enquire about a role</span></div>'
           f'<button class="vx" type="button" id="job-x" aria-label="Close the enquiry form">{ic("x")}</button></div>'
           f'<div class="dlg-body">'
           f'<form class="ref" id="jobform" novalidate>'
           f'<p class="full muted dlg-intro">Tell us a little about yourself and our recruitment team will be in touch. Fields marked <span class="req" aria-hidden="true">*</span> are needed so we can reply.</p>'
           f'<div class="field full"><label for="j-role">Area of work</label><select id="j-role"><option value="">Not sure yet</option>{ropts}</select></div>'
           f'<div class="field"><label for="j-name">Your name <span class="req" aria-hidden="true">*</span></label><input id="j-name" autocomplete="name" required></div>'
           f'<div class="field"><label for="j-email">Email <span class="req" aria-hidden="true">*</span></label><input id="j-email" type="email" autocomplete="email" required></div>'
           f'<div class="field"><label for="j-tel">Telephone</label><input id="j-tel" type="tel" autocomplete="tel"></div>'
           f'<div class="field"><label for="j-where">Where you would like to work</label><select id="j-where"><option value="">Anywhere in the group</option><optgroup label="By area">{areas}</optgroup><optgroup label="A particular service">{sopts}</optgroup></select></div>'
           f'<div class="field"><label for="j-exp">Your experience</label><select id="j-exp"><option value="">Choose one</option><option>Registered professional, for example a nurse or therapist</option><option>Experienced in care or a related role</option><option>New to care</option><option>Student or newly qualified</option></select></div>'
           f'<div class="field"><label for="j-hours">Hours</label><select id="j-hours"><option value="">Not sure yet</option><option>Full time</option><option>Part time</option><option>Bank or flexible</option></select></div>'
           f'<div class="field full"><label for="j-msg">A little about you</label><textarea id="j-msg" placeholder="Your experience, the kind of role you are looking for, and when you could start."></textarea></div>'
           f'<p class="err full" id="j-err" role="alert" hidden>Please add your name and a valid email address so we can reply.</p>'
           f'<div class="full sendrow"><button class="btn btn-navy" type="submit">{ic("send")}<span>Send enquiry</span></button><span class="sendnote">Opens your email app with your enquiry addressed to {REC_EMAIL}. You can attach your CV before you send it. <a href="#privacy">How we use your details</a></span></div>'
           f'</form>'
           f'<div class="jdone" id="jobdone" hidden tabindex="-1" aria-labelledby="jobdone-t">'
           f'<div class="dhead">{ico("circle-check")}<div class="dtt"><span class="eyebrow" id="jobdone-k">Nearly there</span><h3 class="h3" id="jobdone-t">Your enquiry is ready to send.</h3></div></div>'
           f'<p id="jobdone-p">Your email app should now be open with your enquiry addressed to <b>{REC_EMAIL}</b>. Attach your CV if you would like to, then press send.</p>'
           f'<p class="dlong" id="joblong" hidden>Your note was long, so the email holds a shortened version. Copy your enquiry and paste it into the email in full.</p>'
           f'<div class="btns"><a class="btn btn-navy" id="jobmail" href="mailto:{REC_EMAIL}">{ic("mail")}<span>Open the email again</span></a><button class="btn btn-line" type="button" id="jobcopy">{ic("copy")}<span>Copy enquiry</span></button><button class="btn btn-line" type="button" id="jobedit">{ic("pencil")}<span>Edit</span></button></div>'
           f'<span class="k">Your enquiry</span><pre id="jobsum"></pre>'
           f'<p class="sm" id="jobdone-f">Email app not opening? Copy your enquiry and send it to {REC_EMAIL}.</p>'
           f'<div class="btns"><button class="btn btn-line" type="button" id="jobclose">Close</button></div></div>'
           f'</div></dialog>')

def build_body():
    return header() + '<main id="main" tabindex="-1">' + "".join(all_views()) + '</main>' + footer() + viewer_html() + job_html() + TOAST

def typo(html_):
    parts = re.split(r'(<script.*?</script>|<style.*?</style>|<svg.*?</svg>|<select.*?</select>|<[^>]+>)', html_, flags=re.S)
    for k, t in enumerate(parts):
        if not t or t.startswith('<'): continue
        t = re.sub(r'(?<=\w)&#x27;(?=\w)', '\u2019', t)
        t = re.sub(r'(?<=s)&#x27;(?=[\s.,;:])', '\u2019', t)
        t = re.sub(r'\b([A-Z]{1,2}\d[A-Z\d]?) (\d[A-Z]{2})\b', '\\1&nbsp;\\2', t)
        t = t.replace('St Leonards-on-Sea', '<span class="nw">St Leonards-on-Sea</span>')
        t = t.replace('Speak up. Listen up. Follow up.', '<span class="nw">Speak up.</span> <span class="nw">Listen up.</span> <span class="nw">Follow up.</span>')
        if 'class="big"' not in parts[k - 1] and 'class="f"' not in parts[k - 1]: t = t.replace('01604 844 192', '01604&nbsp;844&nbsp;192')
        t = re.sub(r'\b(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December)\b', '\\1&nbsp;\\2', t)
        parts[k] = t
    return "".join(parts)

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Inter:wght@400;500;600;700&display=swap">'

if __name__ == "__main__":
    css = open(os.path.join(os.path.dirname(__file__), "site.css")).read()
    js = open(os.path.join(os.path.dirname(__file__), "site.js")).read()
    ids = json.dumps([s["id"] for s in SERVICES])
    names = json.dumps({s["id"]: s["name"] for s in SERVICES})
    body = build_body()
    body = typo(body)
    script = f'<script>window.SMHC={{ids:{ids},names:{names},views:["home","services","refer","families","about","news","careers","contact","privacy"],endpoint:{json.dumps(FORM_ENDPOINT)},refEmail:{json.dumps(REF_EMAIL)},recEmail:{json.dumps(REC_EMAIL)},refPhone:{json.dumps(REF_PHONE)}}};</script><script>{js}</script>'
    title = "<title>St Matthews Healthcare</title>"
    meta = '<meta name="description" content="Specialist mental health hospitals and nursing homes across Northamptonshire, Coventry and East Sussex. Referral line 01604 844 192.">'
    frag = f'{title}{meta}{FONTS}<style>{css}</style>{body}{script}'
    out = os.environ.get("SMHC_PREVIEW_OUT") or ("/home/claude/web/site" if os.path.isdir("/home/claude/web/site") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "preview"))
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w").write(frag)
    full = f'<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">{title}{meta}{FONTS}<style>{css}</style></head><body>{body}{script}</body></html>'
    open(os.path.join(out, "standalone.html"), "w").write(full)
    print("built", len(frag))
