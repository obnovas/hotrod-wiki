# Hot Rod History Wiki

A growing, source-cited archive of lesser-known hot rodding history (1930s–today, focus pre-1990).
Content is plain Markdown in `docs/`; site built with MkDocs Material.

    pip install -r requirements.txt
    mkdocs serve

Netlify: `netlify.toml` is included (build `mkdocs build`, publish `site/`).

Editorial rules: every factual claim gets a footnote with a URL; conflicts between sources are shown, not resolved silently; single-sourced claims are flagged.

## Highlights slider and nightly standard
The home page opens with a **Highlights** carousel rendered at build time from `docs/data/highlights.yml` (hook: `hooks/highlights_hook.py`; helper CLI: `scripts/update_highlights.py`). Every nightly research round must:

- add **2-4 highlights**, at least **half grassroots** (local news, oral history, obituaries, club newsletters, municipal records, markers, family accounts, local-history sites);
- keep the newest 16 in the slider; older ones rotate to the Highlights archive automatically;
- pass `python scripts/update_highlights.py check` and `mkdocs build --strict`;
- add any new local outlet to `docs/reference/grassroots-sources.md` and mark such articles with the Grassroots badge;
- **file new pages by topic** in the right department (`people/`, `companies/`, `cars/`, `customs/`, `street-rodding/`, `media/`, `drag-racing/`, `places/`, `voices/`, `eras/`, `reference/`; see `docs/taxonomy.md`), and add a redirect line to `hooks/redirects.yml` whenever a page moves;
- **triage incoming issues** first (labels `correction`, `source-tip`, `suggestion`): label, verify, add unsettled leads to the Research Trail, credit, close (see CONTRIBUTING.md).

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.
