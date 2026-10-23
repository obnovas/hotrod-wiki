# Article Schema

*The fields every article carries, the one home for each repeated fact, and the checks that hold it all together.*

Every story page (everything inside a department folder except its `index.md`) opens with a YAML front-matter block. The build reads it to write the page's summary, search entry, meta description, related stories, "Mentioned in" list and first-mention links. `scripts/check_articles.py` runs at the start of every `mkdocs build`, and **the build fails** if any rule below is broken.

## Front matter

```yaml
---
title: 'Hog Butcher on Weekdays, Fun Capital on Sundays: the Beardstown Drag Strip (Beardstown, Ill., 1967–72)'
summary: Beardstown, a packing-house town on the Illinois River, drew 2,000 people to its new drag strip in 1967. By 1970 Garlits was on the bill.
department: drag-racing
eras: [1960s, 1970s]
years: [1967, 1972]
region: Midwest
states: [Illinois]
cities: ['Beardstown, Illinois']
people: [Ken Dobson, Don Garlits]
companies: []
places: []
clubs: []
strips: [Seward Drag strip]
tags: [drag-strips, grassroots-sources]
related: [drag-racing/semo-malden-drag-strip.md, drag-racing/quaker-city-salem.md]
canonical_for: []
---
# Hog Butcher on Weekdays, ...
```

| Field | Required | Rule |
|---|---|---|
| `title` | yes | Exactly the page's `#` heading. |
| `summary` | yes | One or two sentences, 40–330 characters, that state only what the article states, with its hedges ("by one account", "disputed"). No footnotes, no ⚠/◐ flags, no markers. Every number in it must appear in the article. It becomes the standfirst under the title, the search snippet (boosted), the meta description and the card blurb. |
| `department` | yes | The folder the page lives in: `eras`, `people`, `companies`, `cars`, `customs`, `street-rodding`, `media`, `drag-racing`, `places`, `voices`. |
| `years` | yes | `[first, last]`: the span the story covers, 1880–2030. |
| `eras` | yes | Decades the story covers (`1950s`, ...). Each must fall inside `years`. |
| `region` | yes | One of `West`, `Southwest`, `Midwest`, `South`, `Northeast`, `Northwest`, `National`. Use `National` for stories that span three or more regions or none in particular. |
| `states`, `cities` | no | Full state names; cities as `'Town, State'`. A single city shows in the story kicker. |
| `people`, `companies`, `places`, `clubs`, `strips` | no | Names as the article writes them. They drive related-story scoring. |
| `tags` | yes | From the controlled list below. Add a tag to the list in `scripts/articles_lib.py` before using it. |
| `related` | yes | Paths of other articles (`dept/page.md`). These are always shown first under "Related stories"; the build fills the remaining cards by shared people, companies, clubs, strips, places, tags, era and region. Aim for at least two. |
| `canonical_for` | no | Keys from `docs/data/canonical.yml` this page is the home of. |

Also allowed: `template`, `hide`, `era`, `deck`, `featured`, `no_hero`, `search`, `description`. Any other key fails the build.

`scripts/draft_frontmatter.py` drafts the fields for a new page from its text (`--write` to save; `--only field,field` to refresh some fields). Always read and correct its output: it guesses.

### Tags

| Tag | Use for |
|---|---|
| `drag-strips` | A drag strip: its founding, running or closing |
| `airport-strips` | Racing on airfields, air bases and runways |
| `car-clubs` | Hot rod and custom car clubs |
| `club-rules` | Club bylaws, fines, courtesy cards and codes of conduct |
| `police-and-safety` | Police, sheriffs, safety campaigns and courts |
| `town-politics` | Councils, county boards, ordinances, zoning and petitions |
| `street-racing` | Racing on public roads |
| `cruising` | Cruising, dragging Main and hangouts |
| `dry-lakes` | Muroc, El Mirage, Bonneville and land speed |
| `speed-equipment` | Speed parts makers and shops |
| `camshafts` | Cam grinders and cams |
| `aftermarket-business` | The parts business: catalogs, mail order, SEMA, buyouts |
| `customs` | Custom cars and customizers |
| `car-shows` | Car shows and show circuits |
| `street-rods` | The street rod movement, NSRA and the Nationals |
| `gassers` | Gas-class and door-slammer racing |
| `funny-cars` | Funny cars and altered-wheelbase cars |
| `dragsters` | Dragsters, diggers and slingshots |
| `sanctioning-bodies` | NHRA, AHRA, ATAA, SCTA and other bodies |
| `magazines-and-media` | Magazines, newspapers, books, kits and film |
| `women` | Women racers, club members and owners |
| `teenagers-and-schools` | Teen drivers, high schools and youth programs |
| `oral-history` | First-person recollections |
| `grassroots-sources` | Built mainly on local newspapers and other grassroots sources |
| `family-business` | Family-run shops and companies |
| `patents-and-inventions` | Patents and inventions |
| `fiberglass` | Fiberglass bodies and parts |
| `land-speed` | Land speed record attempts |

## One home for each repeated fact

When more than one article tells the same fact or story, one article is its **canonical** home: that page carries the full story, every footnote and the ⚠/◐ flags. Everywhere else gives a short mention and links to it ("Full story: ..."), or includes the shared snippet:

```markdown
--8<-- "club-fine-rules.md"
```

Snippets live in `snippets/` at the repository root. Each is one paragraph, has no footnotes and ends with a "Full story:" link to the canonical anchor. **To correct a shared fact, edit the canonical page and its snippet, not the copies.**

The registry is `docs/data/canonical.yml`. For each fact it names the page, anchor, snippet, the agreed value (with its flags), and a `detect` pattern. The build fails if the page, anchor or snippet is missing, if the canonical page does not list the key in `canonical_for`, or if any other article matches `detect` without linking the canonical page or including the snippet. The flags must match too: a `value` with ⚠ or ◐ lists in `oq` the canonical page's Open questions items behind it, and the build fails if one is gone, is of the other kind, or if the value carries a flag the page does not.

| Key | Canonical page | Snippet | Agreed value |
|---|---|---|---|
| `santa-ana-bayonets` | [eras/1950s-santa-ana-drags.md](../eras/1950s-santa-ana-drags.md#routed-by-bayonets) | `snippets/santa-ana-bayonets.md` | late 1940s; one source (MSHF biography) |
| `muroc-1941-jeeps` | [people/kong-jackson.md](../people/kong-jackson.md#muroc-1941) | `snippets/muroc-1941-jeeps.md` | 1941, Kong Jackson's recollection via Medley and Fuel Curve |
| `isky-winfield` | [people/ed-iskenderian.md](../people/ed-iskenderian.md#cams-and-trouble) | `snippets/isky-winfield.md` | Hagerty: Winfield mentored Isky; Engle family: both bought first cams from Winfield |
| `kansas-city-strip-1955` | [drag-racing/kansas-city-timing-association.md](../drag-racing/kansas-city-timing-association.md#the-strip) | `snippets/kansas-city-strip-1955.md` | opened July 17, 1955 (Pond) or July 15 (AP) ⚠; 3,850 ft (Pond) or 4,850 ft (AP) ⚠ |
| `club-fine-rules` | [drag-racing/belleville-gear-jammers.md](../drag-racing/belleville-gear-jammers.md#the-club-with-the-half-fine-rule) | `snippets/club-fine-rules.md` | Belleville half; Sedalia one-half plus club trial; Stroudsburg up to one-half; Escanaba 30-day suspension |
| `joe-lunati-birth` | [people/joe-lunati.md](../people/joe-lunati.md#a-memphis-kid) | `snippets/joe-lunati-birth.md` | Memphis, Aug 7, 1935 (family, company) ⚠ vs New Orleans, 1939 (NHRA) |
| `rhs-founding-1967` | [companies/comp-cams-rhs.md](../companies/comp-cams-rhs.md) | `snippets/rhs-founding-1967.md` | 1967, Smiltnieks basement, Memphis (company history ◐) |
| `hurst-almquist-1959` | [people/ed-almquist.md](../people/ed-almquist.md#shifters-shifts-in-the-market) | `snippets/hurst-almquist-1959.md` | 1959 partnership dissolved (Port Jervis paper ◐) |
| `snow-200-mph` | [people/gene-snow.md](../people/gene-snow.md#the-first-200-mph-one-pass-three-dates) | `snippets/snow-200-mph.md` | 200.88 mph at Dickinson; Aug 17, 1968 (NHRA Top 50) ⚠ vs 1969 |
| `nsra-first-president` | [people/dick-wells.md](../people/dick-wells.md#the-street-rod-years-and-the-president-question) | `snippets/nsra-first-president.md` | Wells (four sources) ⚠ vs Miller (99W); open |
| `ataa-absorbed-1957` | [drag-racing/half-day-ataa-maremont.md](../drag-racing/half-day-ataa-maremont.md#what-changed-by-1957) | `snippets/ataa-absorbed-1957.md` | 1957, Bartel tribute only ◐ |
| `garlits-cordova-1957` | [drag-racing/detroit-cordova.md](../drag-racing/detroit-cordova.md#1957-the-garlits-upset) | `snippets/garlits-cordova-1957.md` | Aug 21–25, 1957; Postoian beat Garlits in the 1957 and 1958 ATAA World Series finals |
| `scta-founding` | [eras/1930s-dry-lakes-scta.md](../eras/1930s-dry-lakes-scta.md#may-or-march) | `snippets/scta-founding.md` | founded late 1937 (Nov 1937 per Coachbuilt) ⚠ Kong Jackson: 1938; first meet May 15, 1938 (Road Runners) ⚠ March 15 (StreetMuscle) |
| `hooker-to-holley` | [companies/hooker-headers.md](../companies/hooker-headers.md#what-it-became) | `snippets/hooker-to-holley.md` | 2000 (Holley) ⚠ vs the 1990s (Pennsylvania marker) |
| `modesto-cruise-ban` | [places/modesto.md](../places/modesto.md#policing) | `snippets/modesto-cruise-ban.md` | Mar 27, 1990 ⚠ marker says 1993 |
| `peoria-1970-turnout` | [eras/1970s-street-rod-nationals.md](../eras/1970s-street-rod-nationals.md#the-numbers) | `snippets/peoria-1970-turnout.md` | Aug 14–16, 1970; 600 street rods (Hagerty citing MotorTrend), other accounts smaller ⚠ |

## Links the build adds

- **First-mention links.** `docs/data/entities.yml` maps each person, company, club, strip and place article to the names it goes by. The first mention of one of those names in another article's body is linked to it, unless the page already links there earlier. Headings, captions, quotes in code, footnotes and the open-questions section are skipped. Add a page here when you create it.
- **Related stories** (four cards) and **Mentioned in** (every story that links to the page) appear at the foot of each story.
- **Orphans.** After a build, `python scripts/link_report.py 1` lists articles with one or fewer inbound links from other articles. Fix any it lists with a genuine link or a *See also:* line.

## The open-questions section

Uncertainty is not argued in the middle of the story. The claim stays where it is, with its footnote, and gets a superscript marker (⚠ sources disagree, ◐ single source so far) that jumps to the last section of the page, **Open questions & disputed details**. There each item says what is unsettled and which sources say what, and links back to the story. `scripts/move_unknowns.py` builds the section from inline flags; `scripts/move_unknowns.py --check --all` verifies every marker has its item and every item its marker.

The build checks the pairing: every marker `qr-N` must have its item `q-N` in Open questions and every item its marker, or `check_articles.py` fails with an "orphan open-question" error. When a question is answered, both go: the answer moves into the story with its citations, the [Research Trail](../research-trail.md#resolved) logs it under **Resolved**, and any [Quick answer](quick-answers.md) that flagged it drops its ⚠/◐ (the Quick Answers check fails until it does).

## Checks to run before pushing

```bash
python scripts/check_articles.py          # front matter, links, anchors, canonical facts (also runs inside the build)
python scripts/move_unknowns.py --check --all
python scripts/update_highlights.py check
python scripts/check_connections.py
python scripts/check_quick_answers.py  # Quick Answers: numbers, links, flags still open (also runs inside the build)
mkdocs build --strict
python scripts/link_report.py 1           # after the build: orphan and under-linked pages
```
