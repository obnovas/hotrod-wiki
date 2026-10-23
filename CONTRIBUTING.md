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
3. Mark conflicts with **⚠** and single-sourced claims with **◐**. Leave the claim and its footnote in the story; the flag becomes a superscript marker and the explanation goes to the page's last section, **Open questions & disputed details** (`python scripts/move_unknowns.py docs/<dept>/<page>.md` builds it). Do not argue a dispute mid-paragraph.
   Write each item as `**Disputed.**` / `**Single source so far.**` / `**Open question.**`, then a bold question, then what each source says, with its footnote (Voices pages may cite the URL inline). `move_unknowns.py --check` fails on a label ending in a colon, on an item with no citation, and on Open-questions items on a hub or index page; hubs link to the story page's item with `[⚠](page.md#q-N "…")`. A section-style "Next leads" item needs no citation.
4. Images: public domain or openly licensed only, as `<figure markdown>` with a rich `<figcaption markdown>`, plus a row in `docs/reference/image-credits.md`. Copyrighted material is linked under "Visual references (external)".
5. Grassroots articles: if the page rests mainly on local news, oral history, obituaries, club newsletters or club-run pages, municipal or police records, historical markers, family accounts or local-history sites, start the **Source types** line of the article record with `<span class="hr-badge">Grassroots</span>`, and add any new outlet to `docs/reference/grassroots-sources.md`.

6. **Front matter.** Every article opens with the YAML block described in [Article Schema](docs/reference/article-schema.md): title, summary, department, eras, years, region (and states, cities), people, companies, places, clubs, strips, tags, related, canonical_for. Draft it with `python scripts/draft_frontmatter.py --write docs/<dept>/<page>.md`, then correct it by hand. The summary is one or two sentences that say only what the article says; it is the page's standfirst, search snippet and meta description.
7. **One home per fact.** Before retelling a fact another article already tells, check `docs/data/canonical.yml`. If it is listed, give a one-line mention and link the canonical page ("Full story: ...") or include its snippet with `--8<-- "<key>.md"`. If you find a new repeated fact, give it an entry, a snippet in `snippets/` and a `canonical_for` key on its home page. Disputed numbers and dates are settled on the canonical page only.
8. **Links.** Link the first mention of anything with its own page (the build does this automatically for names in `docs/data/entities.yml`; add new person, company, club, strip and place pages there). Give the page at least two `related` entries, at least one of them in another department (the build warns otherwise). After building, `python scripts/link_report.py 1` must list nothing.
9. **Flow.** Write a single arc: short paragraphs joined by transitions, two or three subheads at most, no bullet lists in the story, no asides that break a thought. See the [Editorial Voice](docs/style-guide.md).

## When an open question is answered
Open questions lists stay clean: they hold only what is still open.

1. **Fold the answer into the story** where the marker sat, with its footnote(s). Keep the reasoning short; if two sources still disagree on a detail, it is not resolved.
2. **Remove the inline marker** (`<sup class="hr-q" id="qr-N">…</sup>`) **and the item** (`<a id="q-N" …>` and its text) from *Open questions & disputed details*. If that was the last item, remove the section. Do not renumber the other items; their anchors are linked from elsewhere.
3. **Canonical facts:** if the fact is in `docs/data/canonical.yml`, update its `value`, its `oq` list and the snippet in `snippets/`, and the flags on the canonical page. A `value` that carries ⚠ or ◐ must list in `oq` the canonical page's open items behind it (`q-N`, or a ⚠ heading's anchor), each still open and of the same kind; a `value` without one must list none. `check_articles.py` fails on any mismatch, so canonical.yml can't call a fact disputed when its article doesn't, or the other way round.
4. **Log it** in the **Resolved** list on the Research Trail (`docs/research-trail.md`): date, page and question, the answer in one line, and the source that settled it (with credit to a reader if one sent it).
5. **Quick answers:** update any answer in `docs/data/quick_answers.yml` that cites it; drop its ⚠/◐, its "see Open questions" and its `flag`.

The build enforces the mechanics: `check_articles.py` fails on an orphan marker (a marker with no item, or an item with no marker), and the Quick Answers check fails on an answer whose `flag` points at an item or ⚠ heading that is gone or no longer marks a dispute.

## Quick answers
[Quick Answers](docs/reference/quick-answers.md) is one page of short answers to the big questions that connect the site's stories. It is generated at build time from `docs/data/quick_answers.yml` by `hooks/quick_answers_hook.py` (using `scripts/quick_answers_lib.py`); each question is an H3 with a stable `id`, so it has its own anchor and its own search entry, and each article whose full story it is lists it under **Quick answers** in its Keep reading area.

- **Fields:** `id` (stable anchor; never rename one that has shipped), `q`, `a` (1-3 plain sentences), `link` (the canonical article, optional `#anchor`), `also` (0-2 related pages), and `flag` when the answer carries ⚠ or ◐ (the article's `page.md#q-N` item, or a ⚠ heading in its Open questions; a list when the answer has more than one, in the order of its "see Open questions").
- **Accuracy:** the answer says only what the linked article says, with the same hedges. Every number in it must appear in the `link` article; links and anchors must resolve; a ⚠/◐ must say "see Open questions" and match an item that is still open, of the same kind. `python scripts/check_quick_answers.py` runs the same check as the build (`--list` prints them all).
- **Nightly rounds:** when a round adds or changes an article that connects context across the site (a new strip in a town already on a Quick answer, a settled date, a new company in a family tree), add or update the Quick answer in the same commit. Aim to keep each theme scannable: roughly 5-15 questions.

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
3. `python scripts/check_articles.py` and `python scripts/move_unknowns.py --check --all` (front matter, canonical facts, links and open-questions markers), then `python scripts/check_connections.py` when a round touched `docs/data/connections.yml` or added a company page, then `python scripts/update_highlights.py check` (it also reports the round's batch against the standard). Log credited reader contributions in the Research Trail round entry.
4. Add or update Quick answers for anything the round connects or settles, and move resolved open questions to the Research Trail's **Resolved** list (see above). `python scripts/check_quick_answers.py`.
5. `.venv/bin/mkdocs build --strict` (it runs `check_articles.py` and the Quick Answers check first and fails on any error), then `python scripts/link_report.py 1`.
5a. For any page whose footnotes you touched, run `python scripts/check_external_links.py docs/<folder>/<page>.md`. It tries https first, reports dead links with a Wayback snapshot to use, and lists footnotes with no "(accessed YYYY-MM-DD)". It needs the network, so it is not part of the build and never fails it. "NO CONN" can be the box's own network; confirm in a browser before replacing a link, and keep the original URL beside the Wayback copy ("original returns 404; read in the Wayback copy of ...").
6. `git pull --rebase origin main`, commit, push. Do not deploy from the routine.
