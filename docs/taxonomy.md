# How the Site Is Organized

*Departments are topics. Badges and flags say how we know.*

This page records how the wiki is divided, why, and how to decide where a new page goes. It was reworked in Round 13 after an audit found that several sections had been built from one research request at a time and mixed unrelated ideas.

## The rule: two axes

| Axis | Question | Where it shows |
|---|---|---|
| **Topic** | What is this page about? | The **department** (the folder, the nav group, the kicker above the headline) |
| **Source** | How do we know? | The **article record** (confidence, source types), the teal **Grassroots** badge, the ⚠ and ◐ flags, and the [Voices](voices/index.md) format for first-person accounts |

Each page lives in exactly one department, chosen by topic. A page built on local sources is not moved to a "grassroots" department; it keeps its topical home and wears the badge. [Grassroots Sources & the Badge](reference/grassroots-sources.md) lists every badged page automatically.

## Audit of the old structure (through Round 12)

| Old group | Pages | Coherent? | Problem |
|---|---|---|---|
| Eras | 6 | Yes | A calendar axis. Kept. |
| People & Builders | 28 | Yes | Kept. |
| Aftermarket Companies | 5 | Yes | Kept; renamed Companies & Shops. |
| Customs & Media | 3 | **No** | Mixed a style (customs) with publicity (Trend Books, kits, shows). Its only customs page was the KKOA revival. |
| Street Rodding | 3 | Mostly | A magazine about street rods sat here; the magazine is publicity, not the hobby. |
| Beyond California | 10 | **No** | Mixed regional scenes (Memphis, Texas) with individual drag strips (Cordova, Akron, Houston, Half Day). |
| Cruise Nights & Hangouts | 11 | Yes, but overlapped | Same idea as Beyond California (a place), split by an accident of history. |
| Grassroots Finds | 9 | **No** | A source type, not a topic: strips, clubs, planners, a timing association and an opinion survey, grouped only by how they were found. |
| Voices | 13 | Yes | A format (first-person accounts) with real topical range. Kept as a department because it is how readers browse it. |
| Cars | 3 | Mostly | Held a custom (Hirohata) beside streamliners and a gasser. |
| Techniques & Styles | index only | **No** | A one-page department, mostly about customizing. |
| Reference, Research Trail, Bibliography | 7 + 2 | Split | Research Trail and Bibliography sat outside Reference as lone top-level pages. |

## The new departments

| # | Department | Folder | Pages | One-line definition |
|---|---|---|---|---|
| 1 | [Eras](eras/index.md) | `eras/` | 6 | The calendar, decade by decade, from the dry lakes to Pro Street. |
| 2 | [People & Builders](people/index.md) | `people/` | 28 | Machinists, racers, publishers and the families behind them. |
| 3 | [Companies & Shops](companies/index.md) | `companies/` | 16 | Garage-born speed shops, the big aftermarket names they grew into, and the map of who connected to whom. |
| 4 | [Cars & Techniques](cars/index.md) | `cars/` | 3 | Individual cars, and how each period built them. |
| 5 | [Customs & Kustom Kulture](customs/index.md) | `customs/` | 2 | The style: lead sleds, chops and the builders of customizing. |
| 6 | [Street Rodding](street-rodding/index.md) | `street-rodding/` | 2 | The hobby of driving old cars: NSRA, the Nationals, fiberglass bodies. |
| 7 | [Media & Shows](media/index.md) | `media/` | 3 | How the hobby was publicized and sold: magazines, books, kits, shows. |
| 8 | [Drag Racing & Strips](drag-racing/index.md) | `drag-racing/` | 13 | Strips, clubs and timing associations, and the rules and arguments around them. |
| 9 | [Places & Scenes](places/index.md) | `places/` | 19 | Regional scenes beyond California, plus cruise strips and hangouts. |
| 10 | [Voices](voices/index.md) | `voices/` | 13 | In their own words: first-person accounts. |
| 11 | [Reference](reference/index.md) | `reference/` and root pages | 12 | Timeline, index, patents, credits, standards, grassroots catalog, this page, contributing, the research trail and the bibliography. |

Page counts exclude each department's landing page. Departments 1–10 are topical; 11 is the toolbox. Two departments have sub-groups that appear as headings on their landing page and in the Contents panel:

- **Drag Racing & Strips:** Strips; Clubs & timing associations; Rules, safety & public opinion.
- **Places & Scenes:** Regional scenes; Cruising & hangouts.

## Where pages moved

| Old page | New page |
|---|---|
| `customs/trend-books-kits-roth`, `customs/show-circuit` | `media/` (same names) |
| `street-rodding/street-rod-magazine-portland` | `media/street-rod-magazine-portland` |
| `cars/hirohata-mercury` | `customs/hirohata-mercury` |
| `techniques/` | `cars/techniques-and-styles` |
| `regions/` (landing) | `places/regional-scenes` |
| `regions/midwest-east`, `ohio-gassers`, `memphis`, `texas`, `pacific-northwest`, `upper-midwest` | `places/` (same names) |
| `regions/detroit-cordova`, `akron-fulton-airport`, `houston-freeway-dragstrip`, `half-day-ataa-maremont` | `drag-racing/` (same names) |
| `cruising/` (landing) | `places/cruising-overview` |
| `cruising/*` (11 pages) | `places/` (same names) |
| `grassroots/pomona-choppers-fontana`, `planners-report-1955`, `modesto-century-toppers`, `inyokern-dust-devils`, `great-bend-srca`, `escanaba-dragns`, `kansas-city-timing-association`, `march-1957-drag-strip-survey`, `indiana-small-town-clubs` | `drag-racing/` (same names) |
| `grassroots/` (landing) and `grassroots/sources` | `reference/grassroots-sources` |

Every old URL redirects to its new address (`hooks/redirects.yml`, read by `hooks/redirects_hook.py`, which also writes Netlify `_redirects` rules). The Timeline, the People & Companies index, the Highlights slider and the Bibliography point to the new addresses.

## How to choose a department

Ask in this order and stop at the first yes:

1. Is it **one person or family**? → [People & Builders](people/index.md). (A first-person account of them goes in [Voices](voices/index.md); the biography stays in People.)
2. Is it **one company or shop**? → [Companies & Shops](companies/index.md).
3. Is it **one car**, or a **build technique or period style**? → [Cars & Techniques](cars/index.md). If the car or style is a custom, → [Customs & Kustom Kulture](customs/index.md).
4. Is it about **street rodding as a hobby** (NSRA, Nationals, bodies, parts for old cars)? → [Street Rodding](street-rodding/index.md).
5. Is it about **how the hobby was covered or sold**: a magazine, a book, a kit, a show, a film? → [Media & Shows](media/index.md).
6. Is it a **strip, a club or timing association, a race series, or a safety rule or public debate about racing**? → [Drag Racing & Strips](drag-racing/index.md).
7. Is it a **city, region or cruising spot**? → [Places & Scenes](places/index.md). If the page is mainly about a strip in that place, it goes in Drag Racing & Strips and links to the place page.
8. Is it a **decade** overview? → [Eras](eras/index.md).
9. Is it a **first-person account** gathered from one source family (interviews, recollections)? → [Voices](voices/index.md).
10. Is it a lookup, a standard or a log? → [Reference](reference/index.md).

When a page could fit two departments, file it under the one a reader would look in first, then link it from the other department's landing page. Put the source-based decision in the article record, not the folder: if the page rests mainly on local news, obituaries, club or municipal records, markers or family accounts, add the Grassroots badge.

## When you add or move a page

1. Put the file in the department folder and add it to `nav` in `mkdocs.yml` under that department (or the right sub-group).
2. Add a bullet to the department's landing page and, if it is a new person, company or place, a row to the [index](reference/index-people-companies.md) and the [timeline](reference/timeline.md).
3. If you move or rename a page, add a line to `hooks/redirects.yml` and update links (`mkdocs build --strict` fails on broken ones).
4. A new department needs an icon and a one-line blurb in `DEPT` in `hooks/design_hook.py`; the home page tile, Contents panel and footer pick it up from `nav`.
