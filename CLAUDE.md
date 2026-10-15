# St Matthews Healthcare website

The public website for St Matthews Healthcare at https://smhc.uk.com. It belongs to
Phil Tattersall, National Business Development Director. Blue Moon Solutions host it and
sync the `main` branch of this repository to the live site.

## Branches

- `source`: work here. Content, build scripts, photographs and brochures.
- `main`: exactly the live files. Only `source/publish.py` writes to it. Never commit to it by hand.

## Layout of the source branch

- `source/data.py`: all the content. Services, beds, contacts, news, form settings. Most changes are here.
- `source/build.py`: the page templates for every section, and the single page preview.
- `source/launch.py`: builds the live multi page site into `site/`: pages, redirects from the old
  WordPress addresses, security headers, sitemap, social share images and the CQC ratings widget.
- `source/site.css`, `source/site.js`, `source/icons.py` (Lucide icons, ISC), `source/fonts/`
  (Inter and Cormorant Garamond, OFL), `source/map.json`.
- `site/`: the built website, including `site/img/` (photographs) and `site/brochures/` (PDFs, with
  `view/` page images 1240 px wide and `thumb/` covers 460 px wide).
- `redirects.csv`: every old smhc.uk.com address and where it now goes.

## Starting in a new session

The repository is `smhc573/smhc-website` on GitHub (private). A fresh clone lands on `main`, so
fetch this branch first: `git fetch origin source && git checkout -b source origin/source`.
Publishing pushes to GitHub, and Blue Moon Solutions (Richard Foster) sync `main` to the live site.

## Making a change

1. `git checkout source`
2. Edit `source/data.py`, or `source/build.py` and `source/site.css` for layout.
3. A new photograph goes in `site/img/` and is referred to by its file name in `data.py`.
   A new brochure PDF goes in `site/brochures/`, with its page image and cover made by
   `pdftoppm -jpeg -singlefile -scale-to-x 1240 -scale-to-y -1 X.pdf site/brochures/view/X` and
   `pdftoppm -jpeg -singlefile -scale-to-x 460 -scale-to-y -1 X.pdf site/brochures/thumb/X`.
4. `python3 source/launch.py` rebuilds `site/` (needs Python 3 and Pillow).
5. Check it: `python3 -m http.server -d site 8765`, then look at every changed page at phone and
   laptop widths. No text may overlap or run off the screen.
6. `python3 source/publish.py "what changed"` commits `source`, updates `main` and pushes both.
   The change is live once the host syncs.

## House rules, never broken

- Contacts: the referral line 01604 844 192 and smhc.referrals@nhs.net for referrals, and
  recruitment@smhc.uk.com for careers. Each service also shows its own main number (`phone` in
  `data.py`, from Phil's Site Addresses list, 15 October 2026) in its page header, its Address
  panel and the Contact page list. No other phone numbers, no manager names or emails, no direct dials.
- No fees or prices anywhere.
- Never type a CQC rating by hand. The official CQC widget on every service page stays: the law
  (Regulation 20A) requires current ratings on the website.
- No learning disability or autism claims.
- Never name the specific step down service, and never name a ward or unit that has not been
  announced publicly. Say a step down exists within our own services, or "two further wards".
- Bed numbers come from the finance pack. The group total is calculated from the ten services
  (531 in October 2026, with Althorp Grange at 99). Never type the total by hand.
- No em dashes or en dashes. British spelling. "Nursing homes", never "care homes".
  "Wincent", never "Vincent". Paul Allam is spelt A, L, L, A, M.
- Quotes are verbatim, including punctuation. Gender neutral copy. No published frequencies.
- Nothing invented. If a fact is not confirmed, ask Phil before it goes on the site.
- The referral form keeps its warning not to include the person's name, date of birth or NHS number.
- The privacy page was approved by Paul Allam. Before adding anything that loads from another
  company (visitor statistics, a form service, maps, video), update the privacy page and the
  Content Security Policy in `launch.py`, and check with Phil.
- Phil reads replies aloud on his phone: keep replies to him short, in plain prose.
