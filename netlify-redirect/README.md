# Netlify cutover (not in use)

This folder is not read by Netlify or by Cloudflare. The root `netlify.toml` is unchanged.

`hooks/redirects_hook.py` writes `site/_redirects` from `hooks/redirects.yml` on every `mkdocs build`. A hand-written `docs/_redirects` would be overwritten, and it would not carry a host-to-host rule. New internal path moves belong in `hooks/redirects.yml`.

At cutover, paste the `[[redirects]]` blocks from `netlify.toml.cutover` into the root `netlify.toml`, above any other redirect rules. That 301s every path on `hotrod-wiki.netlify.app` to the same path on `https://hotroddinghistory.com`. Leave the build command and publish directory as they are.

DNS already 301s `www` and `.org` to the apex. Do not add those hosts here.
