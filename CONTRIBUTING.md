# Contributing

This is a research wiki: every claim is cited, conflicts are shown, and single-sourced claims are flagged. The full rules are in [docs/reference/source-standards.md](docs/reference/source-standards.md). This page covers the practical workflow, including the home-page **Highlights** slider.

## Quick start
    python -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/mkdocs serve                 # live preview
    .venv/bin/mkdocs build --strict        # must pass before pushing

## Where a new page goes (departments)
The site is organized by **topic**; sources are shown by badges and flags, not folders. Choose the department with the ten-question guide in [docs/taxonomy.md](docs/taxonomy.md) ("How to choose a department"). In short: person, company, car or technique, customs, street rodding, media and shows, strips and clubs, place, era, first-person voices, or reference. Never create a department for a source type (there is no "grassroots" folder; use the badge).

1. Put the file in the department folder (`people/`, `companies/`, `cars/`, `customs/`, `street-rodding/`, `media/`, `drag-racing/`, `places/`, `voices/`, `eras/`, `reference/`) and add it to `nav` in `mkdocs.yml` under that department (or sub-group).
2. Add a bullet on the department landing page, and a row to the People & Companies index and Timeline where they apply.
3. If you move or rename a page, add the old URL to `hooks/redirects.yml` (the build writes redirect stubs and Netlify rules) and fix links; `mkdocs build --strict` fails on broken ones. `python scripts/update_highlights.py check` fails if a highlight's link moved.
4. A genuinely new department also needs an icon and blurb in `DEPT` in `hooks/design_hook.py`.

## Writing or extending an article
1. Cite every claim with a footnote that has a URL. Add the source to `docs/bibliography.md` (new section per round; tag `[local]` for local or homegrown sources).
2. Quote verbatim, only from pages actually read, with speaker, date and context. Paraphrase the rest.
3. Mark conflicts with **⚠** and single-sourced claims with **◐**.
4. Images: public domain or openly licensed only, as `<figure markdown>` with a rich `<figcaption markdown>`, plus a row in `docs/reference/image-credits.md`. Copyrighted material is linked under "Visual references (external)".
5. Grassroots articles: if the page rests mainly on local news, oral history, obituaries, club newsletters or club-run pages, municipal or police records, historical markers, family accounts or local-history sites, start the **Source types** line of the article record with `<span class="hr-badge">Grassroots</span>`, and add any new outlet to `docs/reference/grassroots-sources.md`.

## Highlights (home-page slider)
The slider is generated at build time from `docs/data/highlights.yml` by `hooks/highlights_hook.py` (registered in `mkdocs.yml`), using `scripts/highlights_lib.py`. Without JavaScript it is a plain list of cards. With JavaScript (`docs/javascripts/highlights.js`) it becomes a carousel with arrows, dots, a pause button, swipe, keyboard support, pause on hover or focus, and no auto-rotation under `prefers-reduced-motion`.

### Adding a highlight when you add an article
Each research round adds **2-4 highlights, at least half of them grassroots**. Pick the surprising, concrete finds, not the headline facts.

    python scripts/update_highlights.py scaffold        # prints a YAML template
    python scripts/update_highlights.py add --id my-id \
        --headline "Specific, surprising, under 110 chars" \
        --teaser "One or two sentences that state only what the article states." \
        --link drag-racing/my-article.md#optional-heading \
        --evidence "verbatim phrase from the article" \
        --source-type "Local news" --confidence Medium --flag none --grassroots \
        --eras 1950s --regions "Town, State"
    python scripts/update_highlights.py check           # same validation the build runs
    python scripts/update_highlights.py list            # display order; shows what rotated out
    python scripts/update_highlights.py stats

You can also paste the template into `docs/data/highlights.yml` by hand.

### Rules enforced automatically (the build fails otherwise)
- **Required fields:** `id`, `headline`, `teaser`, `link`, `evidence`, `source_type`, `confidence`, `flag`, `added`, `grassroots`.
- **Accuracy:** each `evidence` phrase must appear verbatim in the linked article, and every number in the headline and teaser must appear in the article. If someone later rewrites the article, the build tells them to fix or retire the highlight.
- **Links:** the article and any `#anchor` must exist.
- **Images (optional):** the file must exist in `docs/assets/images` and have a row in `docs/reference/image-credits.md`. Add `image_alt`, and an `image_note` when the photo only gives context (for example "Orange County Airport runway, not Mile Square").
- **Flags:** `flag: conflict` when the article marks a ⚠ conflict, `single-source` when the claim is ◐, else `none`. The chip shows it. Do not soften a flag in the teaser.
- **Style:** headline up to 110 characters, teaser up to 320 characters and at most two sentences.
- **Source types:** Local news, Oral history, Obituary, Club newsletter, Municipal record, Historical marker, Family account, Local history site, Forum post, Archive, Patent, Trade press, Museum / HOF. `grassroots: true` should go with at least one of the first nine.

### Rotation
The slider shows the newest 16 highlights (`settings.max_featured`), newest `added` date first. Older ones move to the **Highlights archive** page automatically. Never delete a highlight to make room.

## Web of Influence (connections map)
The map on [Companies & Shops → Web of Influence](docs/companies/web-of-influence.md) is drawn at build time from `docs/data/connections.yml` by `hooks/connections_hook.py` (using `scripts/connections_lib.py`). No JavaScript library is involved; the layout is computed in Python and written as an SVG with a full text table beneath it.

- **Nodes** have an `id`, `label`, `type` (company, person, place, club, institution) and a `page` (a `.md` path under `docs/`). Companies also have a `group`: `big-names` or `garage-born`.
- **Edges** have `from`, `to`, `type` (founded, partnered, employed, customer, acquired, patent, promotion, mentor, scene, hometown), a short `label`, a `page` that documents the tie, and an `evidence` phrase that appears **verbatim** in that page (footnote markers, link markup and curly quotes are ignored when matching). Add `flag: conflict` or `flag: single-source` when the page flags the tie with ⚠ or ◐.
- **A line cannot appear until an article earns it.** Write the sentence and its footnote in the article first, then add the edge.
- **Every company page must be a node.** A new `docs/companies/*.md` page with no matching company node fails the check.

```bash
python scripts/check_connections.py         # validates; exits non-zero on any error
python scripts/check_connections.py --list  # prints nodes and edges
```

The build runs the same check and stops on failure. Warnings (for example, a disconnected island) do not stop it, but fix them: an island means the map has a gap.

## Incoming issues (triage)
Readers send corrections, source tips and suggestions through the issue forms in `.github/ISSUE_TEMPLATE/` (buttons at the end of every article, the Contribute page, the footer and the masthead). Labels to create once in the repository: `correction`, `source-tip`, `suggestion`, `triage`. Handle every issue the same way, and never let a reader's say-so change a page without a source:
1. **Label** it (`correction`, `source-tip` or `suggestion`; keep `triage` until handled).
2. **Verify**: find and read the cited source yourself, check it against [source standards](docs/reference/source-standards.md), and treat a reader's recollection as a ◐ single-source lead. Show ⚠ conflicts instead of picking silently.
3. **Add to the Research Trail**: anything useful but unsettled goes under "Next breadcrumbs" in `docs/research-trail.md`, so a later round picks it up.
4. **Credit**: name the reader (as they asked, or "a reader") in that round's Research Trail log and cite the source in the footnotes. Never publish a name they declined.
5. **Close** the issue with a one-line note: fixed, added as a lead, needs a second source, or declined and why. Then remove `triage`.

### Nightly routine checklist
0. Start by triaging open issues labeled `triage` (the steps above); fold verified items into this round's work.
1. Research and write; keep local and homegrown sources first. File each new page in the right department (see above).
2. Add 2-4 highlights (at least half grassroots); update `docs/reference/grassroots-sources.md` with any new outlet.
3. `python scripts/check_connections.py` when a round touched `docs/data/connections.yml` or added a company page, then `python scripts/update_highlights.py check` (it also reports the round's batch against the standard). Log credited reader contributions in the Research Trail round entry.
4. `.venv/bin/mkdocs build --strict`.
5. `git pull --rebase origin main`, commit, push. Do not deploy from the routine.
