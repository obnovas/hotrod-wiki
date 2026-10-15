# Contributing

This is a research wiki: every claim is cited, conflicts are shown, and single-sourced claims are flagged. The full rules are in [docs/reference/source-standards.md](docs/reference/source-standards.md). This page covers the practical workflow, including the home-page **Highlights** slider.

## Quick start
    python -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/mkdocs serve                 # live preview
    .venv/bin/mkdocs build --strict        # must pass before pushing

## Writing or extending an article
1. Cite every claim with a footnote that has a URL. Add the source to `docs/bibliography.md` (new section per round; tag `[local]` for local or homegrown sources).
2. Quote verbatim, only from pages actually read, with speaker, date and context. Paraphrase the rest.
3. Mark conflicts with **⚠** and single-sourced claims with **◐**.
4. Images: public domain or openly licensed only, as `<figure markdown>` with a rich `<figcaption markdown>`, plus a row in `docs/reference/image-credits.md`. Copyrighted material is linked under "Visual references (external)".
5. Grassroots articles: if the page rests mainly on local news, oral history, obituaries, club newsletters or club-run pages, municipal or police records, historical markers, family accounts or local-history sites, start the **Source types** line of the article record with `<span class="hr-badge">Grassroots</span>`, and add any new outlet to `docs/grassroots/sources.md`.

## Highlights (home-page slider)
The slider is generated at build time from `docs/data/highlights.yml` by `hooks/highlights_hook.py` (registered in `mkdocs.yml`), using `scripts/highlights_lib.py`. Without JavaScript it is a plain list of cards. With JavaScript (`docs/javascripts/highlights.js`) it becomes a carousel with arrows, dots, a pause button, swipe, keyboard support, pause on hover or focus, and no auto-rotation under `prefers-reduced-motion`.

### Adding a highlight when you add an article
Each research round adds **2-4 highlights, at least half of them grassroots**. Pick the surprising, concrete finds, not the headline facts.

    python scripts/update_highlights.py scaffold        # prints a YAML template
    python scripts/update_highlights.py add --id my-id \
        --headline "Specific, surprising, under 110 chars" \
        --teaser "One or two sentences that state only what the article states." \
        --link grassroots/my-article.md#optional-heading \
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

### Nightly routine checklist
1. Research and write; keep local and homegrown sources first.
2. Add 2-4 highlights (at least half grassroots); update `docs/grassroots/sources.md` with any new outlet.
3. `python scripts/update_highlights.py check` (it also reports the round's batch against the standard).
4. `.venv/bin/mkdocs build --strict`.
5. `git pull --rebase origin main`, commit, push. Do not deploy from the routine.
