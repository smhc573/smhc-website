# St Matthews Healthcare website: live files

This branch, `main`, holds exactly the files served at https://smhc.uk.com.

## For the web host

- Deploy the whole of `main` to the web root. There is no build step, no database and no
  server side code.
- Keep the hidden `.htaccess` file. It holds the redirects from the old WordPress addresses,
  https without www, the 404 page, security headers and caching.
- Changes arrive as pushes to `main`. Please do not edit files on the server, because the next
  publish would overwrite them.
- Settings for other hosts are included: `_redirects` and `_headers` (Netlify and Cloudflare
  Pages) and `staticwebapp.config.json` (Azure Static Web Apps).
- Each service page shows the official CQC ratings widget, which loads from cqc.org.uk. The law
  (Regulation 20A) requires it, and the Content Security Policy allows it.
- This read-me is hidden from visitors by `.htaccess`.

## Making changes

Content and build scripts live on the `source` branch. Changes are made there and published to
`main` by `source/publish.py`. Please do not commit to `main` by hand.

Owner: Phil Tattersall, National Business Development Director, St Matthews Healthcare.
