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

The wordmark and favicon are provisional. Swap these files in place when the final art arrives:

- `docs/assets/logo.svg`
- `docs/assets/favicon.svg`
- `docs/assets/favicon-32.png`
- `docs/assets/apple-touch-icon.png` (180×180)
- `docs/assets/logo-512.png`
- `docs/assets/og-default.png` (1200×630)

Letterforms are Alfa Slab One, already self-hosted under the SIL Open Font License. The mark is upright title case. It is not a stand-in for the Hearst magazine logo.

`netlify.toml` is unchanged. The unused Netlify cutover snippet is in `netlify-redirect/`.
