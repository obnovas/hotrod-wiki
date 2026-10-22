---
title: 'The Web of Influence: Who Fed Whom'
summary: 'An interactive map of who fed whom: every line between two names is backed by a quoted passage on one of this wiki''s pages, checked at every build.'
department: companies
eras:
- 1960s
- 1970s
- 1980s
- 1990s
- 2000s
- 2010s
years:
- 1961
- 2015
region: National
states:
- Pennsylvania
- Florida
- Ohio
cities: []
people:
- Arlen Vanke
- Ed Winfield
- Ed "Isky" Iskenderian
companies:
- Web of Influence (map)
places: []
clubs: []
strips: []
tags:
- patents-and-inventions
related:
- companies/hurst-campbell.md
- people/arlen-vanke.md
- companies/mickey-thompson.md
- people/ed-winfield.md
- people/ed-iskenderian.md
canonical_for: []
---
# The Web of Influence: Who Fed Whom

*Companies, shops, people, strips and clubs, and the lines between them that a wiki page can prove*

!!! abstract "Article record"
    **Confidence:** Medium · **Source types:** the wiki's own cited articles, one per connection (see the table); no new claims are made on this page · **Last verified:** 2026-10-16 (Round 15) · **Open issues:** each line carries the confidence of the page behind it, and its ⚠ and ◐ marks repeat that page's flags; the map shows only what the wiki has documented, so an absent line means "not yet documented," not "no tie"; many Big Names still lack a profile (see the Research Trail) · [How we rate this](../reference/source-standards.md)

Every line on this page is a promise. It says: *a page on this wiki documents that these two names are connected, and quotes the passage.* The map is built from `docs/data/connections.yml`. When you build the site, a script reads each connection, opens the page it points to and looks for the exact phrase that supports it. If the phrase isn't there, the build stops. So a line cannot appear on the map until some article, with a footnote of its own, has earned it.

<!-- hr:connections-stats -->

Hover over a name, or tab to it, to light up its lines. Click it to open its page. The filters switch relationship types on and off. Dashed red lines are connections whose sources conflict (⚠); dotted gold lines rest on a single source (◐).

<!-- hr:connections-graph -->

## Five threads worth pulling

**1. A Pennsylvania garage that talked Detroit into it.** [Hurst-Campbell](hurst-campbell.md) started in a two-car garage in Abington, Pa., and a local county magazine watched its plant go up. A 1961 meeting with Pontiac put a Hurst shifter in the Super Duty Catalina. The same Pontiac era sold [Arlen Vanke](../people/arlen-vanke.md) a Super Duty Catalina at an Akron dealership, and it is the year [Mickey Thompson](mickey-thompson.md) took four Pontiac-powered cars to March Air Force Base for record runs. Follow the Pontiac node.

**2. A family tree of cam grinders.** [Ed Winfield](../people/ed-winfield.md) mentored [Ed Iskenderian](../people/ed-iskenderian.md). Isky's 1958 lifter-guide patent is cited by [Harvey Crane](crane-cams.md)'s 1963 roller-tappet patent. Crane's shop foreman, [Tom Woitesek](comp-cams-rhs.md), left Florida for a Memphis head shop that became COMP Cams, and by 2020 COMP and Edelbrock were the same group.

**3. Ohio, from trunk to bellhousing.** [Mr. Gasket](mr-gasket.md) began in the trunk of a '57 Chevy; [Lakewood](lakewood-industries.md) began in the Cleveland suburb of that name. One of the Ohio Gassers, [Ron Hassel](../places/ohio-gassers.md), went to Crane Cams in 1965 and later returned as Mr. Gasket's sales manager. Lakewood's founder lost his first race to the Arfons brothers on the Akron strip where Vanke raced; Hooker Headers later ran an ad saluting Vanke. [Summit](summit-racing.md) grew in the same part of the state.

**4. Holley, the collector.** [Holley](holley.md) began as a bicycle-motor shop in Bradford, Pa. Per the pages here, it now owns Mr. Gasket (2015), Hooker (2000, though the Pennsylvania marker says the 1990s<sup class="hr-q" id="qr-1"><a href="#q-1" title="Sources disagree: see Open questions">⚠</a></sup>), Lakewood and, per a Wikipedia summary, Hilborn<sup class="hr-q" id="qr-2"><a href="#q-2" title="Single source so far: see Open questions">◐</a></sup>. Most of the garages on this map are brands today, and many of them are Holley's.

**5. Strip owners and the people who ran them.** Mickey Thompson, by his own account, built and ran Lions in Southern California; a Santa Ana hot rodder named his slingshot; a Houston strip owner booked his Pontiac in 1961; and Santa Ana's Hart succeeded him at Lions in 1965. The strip, not the factory, is where these connections happened.

## What's not on the map, and why

- Offenhauser, Cragar, American Racing, Mallory, Weiand's later years and Edelbrock after 1962 are in the department's backlog because their sources are still thin; see the [Research Trail](../research-trail.md).
- A tie we suspect but cannot prove stays off the map. For example, Moroso's Palm Beach track and Crane's South Florida base are linked here only through Ron Hassel's photo.

## All connections (text version)

The same data as a table, for screen readers and for anyone who would rather read than hover. Each row's last column links the page that documents it.

<!-- hr:connections-table -->

## Add a connection

Open `docs/data/connections.yml`, add the two names under `nodes` if they are new, and add an edge with a `page` and `evidence`. The evidence must be a phrase that already appears in that page, so write the article first. Run `python scripts/check_connections.py`; the same check runs in the build. Suggest a connection with the [feedback form](https://github.com/obnovas/hotrod-wiki/issues/new?template=suggestion-feedback.yml).

## Open questions & disputed details

*From the detective's notebook: where the sources disagree, where we have only one, and what we are still looking for. Each item links back to its place in the story.*

<a id="q-1" class="hr-q-anchor"></a>**Disputed:** Gasket (2015), Hooker (2000, though the Pennsylvania marker says the 1990s ), Lakewood and, per a Wikipedia summary, Hilborn . <a class="hr-q-back" href="#qr-1" title="Back to the story">↩</a>

<a id="q-2" class="hr-q-anchor"></a>**Single source so far:** Gasket (2015), Hooker (2000, though the Pennsylvania marker says the 1990s), Lakewood and, per a Wikipedia summary, Hilborn . <a class="hr-q-back" href="#qr-2" title="Back to the story">↩</a>
