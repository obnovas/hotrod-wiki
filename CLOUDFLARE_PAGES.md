# Cloudflare Pages

Build command:

    pip install -r requirements.txt && mkdocs build --strict

Output directory: `site`

Python is pinned in `.python-version` to 3.12.3. Pages reads `.python-version` and can install that version.

`site/` is gitignored. The build creates it. `requirements.txt` pins the packages the build installs.

`docs/robots.txt` is copied to the site root. It allows crawling, skips `/search/`, and points at `https://hotroddinghistory.com/sitemap.xml`. MkDocs writes that sitemap from `site_url`.

`docs/_headers` is copied to `site/_headers` for cache and security headers.

The canonical host is the apex, `https://hotroddinghistory.com/`. DNS 301s `www` and `.org` to it. Do not add those redirects in the repo.

Reader mail is `corrections@hotroddinghistory.com` only. Webby still needs to route that mailbox before it receives mail.

Cloudflare Web Analytics: set `extra.cf_analytics_token` in `mkdocs.yml`. The beacon is omitted while the token is empty.

The wordmark and favicon are placeholders. Paths live only in `mkdocs.yml` under `extra.logo` and `extra.favicon`. See the README to drop in a new SVG and favicon set. `docs/assets/og-default.png` (1200×630) is the default social image and is separate from that set.

Letterforms on the current placeholder are Alfa Slab One, already self-hosted under the SIL Open Font License. The mark is upright title case. It is not a stand-in for the Hearst magazine logo.

`netlify.toml` is unchanged. The unused Netlify cutover snippet is in `netlify-redirect/`.
