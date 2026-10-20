# Research Trail: The Investigator's Log

*Where the case stands: the rules we follow each round, what we found, and the leads still open.*

## Standing standard for every nightly round (set in Round 11)
1. **Highlights.** Each round adds **2-4 entries** to [`docs/data/highlights.yml`](https://github.com/obnovas/hotrod-wiki/blob/main/docs/data/highlights.yml) for the home-page slider, and **at least half** must be grassroots (local news, oral history, obituaries, club newsletters and club-run pages, municipal records, historical markers, family accounts, local-history sites). Teasers state only what the article states, with the same hedges and a verbatim `evidence` phrase from the article.
2. **Rotation.** The slider shows the newest 16 by date added. Older entries move to the [Highlights archive](highlights-archive.md) automatically; nothing is deleted.
3. **Grassroots first.** Prefer a local paper, historical society page, obituary, club newsletter, municipal or police record, marker or family account over an industry magazine whenever both exist. Mark such pages with the Grassroots badge in the article record's source types, and add new outlets to [Grassroots Sources](reference/grassroots-sources.md).
4. **Check before pushing.** Run `python scripts/update_highlights.py check`, then `mkdocs build --strict`. The build fails if a highlight's evidence phrase, numbers, link, anchor, image or credit row no longer matches. Details are in [CONTRIBUTING](https://github.com/obnovas/hotrod-wiki/blob/main/CONTRIBUTING.md).
5. **File by topic.** Each new page goes in the one department that matches its subject (see [How the Site Is Organized](taxonomy.md#how-to-choose-a-department)). Sources are shown by the Grassroots badge and the ⚠ and ◐ flags, never by folder. If a page moves, add its old URL to `hooks/redirects.yml`.
6. **Triage reader mail first.** Open issues labeled `triage` (corrections, source tips, suggestions) are handled before new research: label, verify, add unsettled leads to the breadcrumbs below, credit the reader in the round log, close with a note. See [Contribute](contribute.md) and `CONTRIBUTING.md`.

## Log, Round 18 (where a Pocono hot rodder could race; dragging Main in four towns; a 1957 New York panel; Escanaba's small print; JEGS; 2026-10-20)
- **Reader mail:** no open `triage` issues this round (checked on GitHub).
- **Why there was no round on Oct 19:** the shared research machine was offline from about 8:25 a.m. CDT on Oct 18 until 11:50 p.m. CDT on Oct 19, so the scheduled run never reached it. A partial Round 18 begun on the morning of Oct 18 was cut off mid-way. The site's local build environment (`.venv`) was also missing and has been rebuilt from `requirements.txt`.
- **Salvaged from the interrupted attempt (re-verified line by line against the sources before use):** the Escanaba expansion, the 1957 New York panel page and the JEGS profile. Its claim that four Escanaba issues were "empty stubs" was wrong: the 1955 run simply ends at June 30, and four earlier issues return server errors. Its draft profiles of Weiand, Cragar, Offenhauser, American Racing and Mallory rest on company and trade sources we have not yet checked, so they stay out of the wiki for now.
- **New articles:** [Where Could a Pocono Hot Rodder Race?](drag-racing/pocono-strips.md) (Strips; grassroots); [Dragging Main](places/dragging-main.md) (Cruising & hangouts; grassroots); ["Opinions Differ on Hot Rods" (1957)](drag-racing/new-york-towns-panel-1957.md) (Rules, safety & public opinion; grassroots); [JEGS](companies/jegs.md) (Companies, The Big Names).
- **Expanded (additive only):** [The Ridge Runners of Stroudsburg](drag-racing/stroudsburg-ridge-runners.md) (the 1964 letter: incorporated, NHRA, eighteen members, the constitution and bylaws); [Escanaba](drag-racing/escanaba-dragns.md) (a teen safety conference's hot rod resolutions, three meeting notices and a "drag racing" ticket, Jan–Jun 1955); [Midwest & East Threads](places/midwest-east.md) (link to the JEGS profile).
- **Found:** a borough council padlocking a flood-control levee that cars had been using "as a drag strip" (1962); a club bylaw fining members "twenty-five cents per word" for swearing in council meeting; a mother's offer to hand drag race proceeds to the Mount Pocono Airport Authority; 220 drivers at the Pocono Drag Lodge on one August Sunday in 1968; four towns' accounts of dragging Main, from a 1957 senior's hobby list to a 1987 yearbook's full route map; the county resolution that fixes JEGS's 1960 address.
- **Resolved or narrowed:** the half-fine rule now has a third club (Stroudsburg, 1964), but still no common source; JEGS's founding address is fixed by a government record, not only company history; the Escanaba 1955 run's end is now known (June 30).
- **New conflicts or single-source flags:** Mountain View's first season (1960 inferred) ◐; the Mount Pocono letter writer's first name (garbled) ◐; Hays's route start, Thirteenth vs "about Eighth" ⚠; JEGS handoff, 27 years vs "nearly 30" vs the early 1990s ⚠; JEGS staff and floor-space figures ⚠; Richmond's memory of uneven ticketing (one witness, no council minutes yet) ◐.
- **Blocked or unavailable (not bypassed):** the Colbert, Okla., 1955 yearbook and four Escanaba issues (Jan 1, Feb 12, Feb 21, May 30, 1955) returned HTTP 500 on every try; a lending-library book on speedway history returned HTTP 401; the JEGS help center is now behind a bot check (the same text is on TeamJEGS).

## Next breadcrumbs (Round 18)
- **Poconos:** Mountain View's owners and opening day (the *Easton Express*, Wind Gap borough); the Pocono Drag Lodge's first season and owners (Luzerne County papers); the Mount Pocono Airport Authority's 1964 minutes; whether Pocono International's drag strip opened; the letter writer's full name; the Northeastern Pennsylvania Timing Association's member clubs.
- **Dragging Main:** the *Hays Daily News* and the *Star-Herald* (Scottsbluff) for the adult side of the story; Richmond, Calif., council minutes for the 1950s cruising complaints; Colbert, Okla. (1955 yearbook, retry); more yearbooks with "dragging Main" in senior pages.
- **JEGS:** the paywalled *Columbus Dispatch* 50th-anniversary story; a dated 1960s Columbus city directory listing for 751 E. 11th Ave.; Jeg Sr.'s 1959 first national event win.
- **New York:** the Association of Towns' own proceedings for 1957; Glen Cove's $1,600 race for the Community Chest.
- **Company backlog:** the draft Weiand, Cragar, Offenhauser, American Racing and Mallory pages need local or independent second sources before they go in.
- **Carried from Round 17:** the Big S.I.R.'s fate (*Sedalia Democrat* 1970–72; nothing new found this round); Kansas City's opening day; the Sedalia Drag-Ons' 1957 founding; the Kingston PAL club; Hurst's Glenside directory listing; Escanaba after June 1955 (not on the archive); the Denver county strip; Des Moines Dragway's opening year; Peggy Hart's own words.

## Log, Round 17 (strip-hunting clubs: Sedalia and the Big S.I.R., Stroudsburg, Kingston; Kansas City's strip found; Hurst's paper trail; 2026-10-18)
- **Reader mail:** no open `triage` issues this round (checked on GitHub).
- **New articles:** [The Sedalia Drag-Ons](drag-racing/sedalia-drag-ons.md) (Clubs; grassroots); [The Big S.I.R.: Sedalia's Eleven-Year Drag Strip Chase](drag-racing/sedalia-big-sir.md) (Strips; grassroots); [The Ridge Runners of Stroudsburg](drag-racing/stroudsburg-ridge-runners.md) (Clubs; grassroots); [The Kingston Igniters](drag-racing/kingston-igniters.md) (Clubs; grassroots).
- **Expanded (additive only):** [Kansas City](drag-racing/kansas-city-timing-association.md) (second witnesses: a 1957 Sedalia club visit, a 1959 *Kansas City Star*/AP feature, a 1966 AHRA-sanctioned meet and a 1969 site description); [Hurst-Campbell](companies/hurst-campbell.md) (a 1962 Glenside address in a Dodge brochure, 1962–63 copyright registrations, a 1966–68 AMC Warminster listing).
- **Resolved or narrowed:** Kansas City's strip now has a name, a place and a later life: "the Kansas City Timing Association drag strip" at Chouteau Trafficway and Front Street (1966), near the Chouteau Bridge (1969), on railroad land at $2 a year (1959), still running under AHRA sanction in 1966. Hurst's Warminster date is narrowed: the company printed a Glenside address in the 1962 model year, which favors the magazines' mid-1960s move over "opened for business in 1959" in Warminster, though it doesn't rule out an earlier Warminster shop.
- **Found:** a Sedalia club courtesy card ("You Have Been Helped By The DRAG-ONS of SEDALIA"); a club president's letter hoping to make Sedalia "the safest city in the state"; a 1964 hot rod club rebuilding a truck for a boys' ranch, with bylaws charging half of any court fine; an oil men's association, a police chief and five clubs planning a strip in 1962; a 1969 strip that broke ground with an AHRA world final promised and ended "one-half completed"; a Pocono club that tried two members and sentenced them to a work detail, then offered to buy its own strip; a Hudson Valley club that showed a rebuilt 1931 Ford at a home show and became a motor club in 1959; Kansas City's all-girl Dragettes running the concession stand (1959); Hurst-Campbell in a 1962 Dodge supplier list beside Edelbrock, Isky and Weiand.
- **New conflicts or single-source flags:** Kansas City opening day July 15 vs 17 ⚠ and length 3,850 vs 4,850 ft ⚠; "first drag strip built in Missouri" ◐; Weatherly Sr./Jr. and September vs Oct. 3–5 for the lost World Points Finale ⚠; whether the Big S.I.R. ever opened ◐; Carl Cline vs Carl Kline ◐; the Ridge Runners' NHRA "Safety High Point Award" ◐.
- **Blocked or unavailable (not bypassed):** a few Internet Archive downloads returned HTTP 500 (including the *Sedalia Democrat* of Aug. 6, 1969), and one came back empty; we used other issues instead. Several passages were too garbled in OCR to quote (Stroudsburg's National Safety Council figures, the Allegheny County judge's first name, Sedalia's Jan. 1970 review), so they are paraphrased or left out.

## Next breadcrumbs (Round 17)
- **Big S.I.R.:** *Sedalia Democrat* 1970–72 for whether the strip ever opened; where the AHRA's 1969 World Points Finals were held; Pettis County lease or deed records for the Highway 65 site.
- **Kansas City:** the *Kansas City Star* and *Times* of July 1955 (July 15 or 17); when the KCTA strip closed; the Dragettes' names; Kansas City International Raceway's opening year.
- **Sedalia Drag-Ons:** the 1957 founding; the Marshall *Democrat-News* on the Push Rods; Butterfield Youth Services' own history for the 1964 truck; Whiteman AFB's 1958 drags.
- **Stroudsburg:** the Northeastern Pennsylvania Timing Association (a *Car Craft*, Dec. 1959 item mentions a booth it built); Wind Gap's Mountain View strip and the Nazareth Fairgrounds strip; the Ridge Runners' officers.
- **Kingston:** the Poughkeepsie PAL club (1956); whether any Ulster County strip was built; the Igniters after 1959.
- **Hurst:** a Philadelphia-area city directory for 341 W. Glenside Ave.; the "Hurst mystery shifter" sheets of 1962–63; the first Warminster address in a dated catalog or ad.
- **Half-fine rule:** whether Belleville's and Sedalia's identical penalty came from a common NHRA model.
- **Carried:** Escanaba July–Aug 1955; the Denver county strip; Des Moines Dragway's opening year; Wilmington Automotive Activities; more school-club yearbooks; Peggy Hart's own words.

## Log, Round 16 (club-built strips and small-town clubs: Ames, Belleville and St. Louis, Portsmouth; Twin Falls and Circleville; 2026-10-17)
- **Numbering note:** the Companies & Shops push on Oct 16 was committed as "Round 15," so this nightly round is Round 16.
- **Reader mail:** no open `triage` issues this round.
- **New articles:** [The Professor's Drag Strip: Ames, Iowa, and the Nightcrawlers](drag-racing/ames-drag-strip-nightcrawlers.md) (Strips; grassroots); [Belleville's Gear Jammers and the St. Louis Strip Hunt](drag-racing/belleville-gear-jammers.md) (Clubs; grassroots); [Portsmouth, Ohio, 1956: The Hot Rod Club That Carried the Messages](drag-racing/portsmouth-kustom-kouriers.md) (Clubs).
- **Expanded (additive only):** [Twin Falls](places/twin-falls-main-avenue.md) (the MVTA in 1961–64: Road Lords and Coachmen lineage, the Timettes, officers, a blood drive and a Redheads basketball benefit); [Hot Rod Club, Third Row](drag-racing/high-school-hot-rod-clubs.md) (Sherman, Tex., 1956 yearbook with marks back to '53; Circleville's Devastators, 1964–65; Logan Elm, 1967).
- **Advanced:** the Round 14 Twin Falls lead. The *Times-News* shows the MVTA still aiming to build a strip in Aug 1961, discussing land in Sept 1962, and a new club formed in 1964 "to get a drag strip," so the Joslin Field lease likely never produced one. Still ◐: no item says the lease was dropped.
- **Found:** an Iowa State math professor who served as "track steward" for a club-run strip, and a club member who paid his parking ticket; ATAA sanction still cited in Ames in June 1958, after the ATAA was reportedly absorbed by NHRA in 1957 ◐; a Belleville club that made members pay half of any traffic fine into its treasury; St. Louis "needs a drag strip" bumper stickers (1958); a Normandy, Mo., club selling a crated WWI Hispano Suiza; a Portsmouth, Ohio, hot rod club, renamed the Kustom Kouriers, running messages during a 61-day telephone blackout; a county juvenile probation officer advising Circleville's hot rod club.
- **New conflicts or single-source flags:** Ames grandstand ⚠, land ownership ⚠, "1st quarter-mile strip in Iowa" vs Des Moines ⚠, closing reason ◐; Walston Field vs Parks Airport naming ⚠; Mehrtens vs Mertens ⚠; the Drag-ons' engine specifications ◐; which Portsmouth blackout the couriers served ⚠; Sherman year marks ◐.
- **Blocked or unavailable (not bypassed):** an Ames History Museum PDF memoir (download stalled; not retried); one Internet Archive item returned HTTP 401 (skipped).

## Next breadcrumbs (Round 16)
- **Ames:** the *Ames Tribune* originals for 1957–59 (opening day, the grandstand, the 1959 closing); Dr. Robert Lambert's later life or obituary; the Nevada, Iowa, airport drags he first entered; Dragzine's 2011 "Flashback Friday" photos (trade press, for leads only).
- **Des Moines Dragway:** a primary source for its opening year, to test the museum's "first quarter-mile strip in Iowa" claim; ties to the Iowa Timing Association.
- **ATAA after 1957:** other ATAA-sanctioned strips still advertising in 1958–59 (Ames is one); what "absorbed" meant in practice.
- **St. Louis:** whether the Missouri side got a strip by 1960, and where; the Gear Jammers after Parks Airport closed in 1959; *Hot Rod*'s Jan 1959 Club of the Month write-up; the *New Leader* (June 25, 1956) and Granite City *Press-Record* mentions; Sedalia's Drag-On's and the club forming at Marshall, Mo. (*Sedalia Democrat*, Mar 9, 1958). *(Done in Round 17: [The Sedalia Drag-Ons](drag-racing/sedalia-drag-ons.md); Marshall's club was the Push Rods.)*
- **Portsmouth:** the *Portsmouth Times*, Sept–Dec 1956, for the club's members and its new name; any later Kustom Kouriers notices.
- **Twin Falls:** the 1964 Redheads game result; whether the MVTA ever got a strip after 1965; the Burley Charger and Buhl Syndicate clubs.
- **Circleville:** the *Herald* 1964–67 for Devastators meets or a drag strip trip; Lancaster and Columbus clubs at the 1964 fair exhibit.
- **Carried:** Kansas City's strip after 1955 *(advanced in Round 17: named, placed and still running in 1966)*; Escanaba July–Aug 1955; the Denver county strip; Wilmington Automotive Activities in Delaware papers; more school-club yearbooks (Natick, Brockton, Fryeburg, Katy, Alamo Heights, Velma-Alma, West Bend, Ypsilanti); Peggy Hart's own words.

## Log, Round 15 (Companies & Shops: ten profiles and the Web of Influence; 2026-10-16)
- **Reader mail:** no open `triage` issues this round.
- **New articles (all in [Companies & Shops](companies/index.md)):** [Hurst-Campbell](companies/hurst-campbell.md) (grassroots, built on two Bucks County magazines); [Moon Equipment](companies/moon-equipment.md); [Holley](companies/holley.md); [Summit Racing](companies/summit-racing.md); [COMP Cams & Racing Head Service](companies/comp-cams-rhs.md); [Crane Cams](companies/crane-cams.md) (grassroots, built on a local newspaper and a funeral-home obituary); [Lakewood Industries](companies/lakewood-industries.md); [Moroso](companies/moroso.md); [Hooker Headers](companies/hooker-headers.md); [Mickey Thompson](companies/mickey-thompson.md). The department now has two groups, "The Big Names" and "Garage-born Shops."
- **New tool:** the [Web of Influence](companies/web-of-influence.md) map, drawn at build time from `docs/data/connections.yml`. Every line names a wiki page and a verbatim phrase from it; `python scripts/check_connections.py` (and the build) fail if the phrase is missing, a node is orphaned, or a company page is missing from the graph. 56 names, 71 connections at launch.
- **Updated:** [Patents](reference/patents.md) (Crane's US3108580 and the Isky to Crane to COMP citation chain, with drawing); [Timeline](reference/timeline.md); [Index](reference/index-people-companies.md); [Memphis](places/memphis.md) (a pointer to COMP's Union and Marshall claim); [Grassroots Sources](reference/grassroots-sources.md); [Image Credits](reference/image-credits.md); [Bibliography](bibliography.md); four new highlights.
- **Found:** a Bucks County magazine calling Hurst-Campbell a company with "no employees" in 1965 and placing its start in a converted Abington garage; a Cleveland gasser racer who left Ohio in 1965 to run Crane Cams' sales in Florida; Crane's shop foreman leaving for Memphis and becoming a COMP co-founder; a 1978 Little Rock yearbook ad for a Memphis head shop; an Akron racer saluted in a Hooker ad; the name "slingshot" coming from a Santa Ana hot rodder; Holley later owning Mr. Gasket, Hooker, Lakewood and Hilborn ◐.
- **New conflicts or single-source flags:** when Hurst-Campbell reached Warminster, its incorporation date and its 1965 sales figure ⚠; who conceived the rescue tool ⚠; Almquist's role in the Hurst shifter ◐; Crane's birthplace-year and "retired" versus ousted in 1989, Ojus versus Hallandale, 98 versus about 100 SEMA booths ⚠; when Lakewood started (1959 versus the mid-1960s) ⚠ and 20 versus 24 seconds on the hydroform press ⚠; Hooker's start (1962 Sioux City per his site) ⚠; whether RHS's Union and Marshall shop was Sun Studio's corner ◐; Summit's Stow basement versus Akron and Cuyahoga Falls ⚠; the 1963 Brighton story told two ways ⚠.
- **Blocked or unavailable (not bypassed):** Hemmings (Cloudflare); the *Akron Beacon Journal* (paywall); RACER's 2017 Summit profile (bot check); Google Patents through `curl` (rate limit; the pages were read through the fetch tool instead); the Holley Foundation's history page (404); Moroso's "Where It All Started" PDF (no text layer); the Automotive Hall of Fame's Mickey Thompson page (empty).

## Next breadcrumbs (Round 15)
- **Companies not yet profiled:** Weiand (Holley acquisition and merger dates, from excerpts only so far); Offenhauser and Meyer-Drake; Cragar; American Racing; Mallory; JEGS; Mr. Gasket's ownership chain after Hagerty's summary ◐; Edelbrock beyond the slingshot page; Cal Custom and Cal Automotive; B&M and TCI.
- **Summit:** local Stow, Cuyahoga Falls and Akron papers for the first shop; the 2017 RACER profile; early catalogs.
- **Hurst:** the Warminster move (1959 versus 1965) *(narrowed in Round 17: Glenside address in 1962)*; a Philadelphia or Bucks County paper on the rescue tool; Joe Schubeck's driving of the Hairy Olds in a period source.
- **Lakewood:** a Cleveland business listing or catalog for the start date; Prestolite and Quick Time ownership; whether the 2004 "Schubeck Joseph J" roller-lifter application is his (US20060005797A1).
- **COMP:** a Memphis city directory for 706 Union and Marshall in 1968–70; Memphis papers on RHS's founders.
- **Moroso:** the Guilford factory (1978) and the "Where It All Started" PDF; Connecticut papers on the Greenwich basement years.
- **Hooker:** a contemporary 1964–66 Super Stock source for the "six of the top 10" claim ◐; Pomona Progress-Bulletin items.
- **Mickey Thompson:** who owns the Thompson tire and wheel brands now; Santa Ana Register on LeRoy Neumayer.
- **Web of Influence:** add people and clubs from the existing street-rodding and cruising pages (the map is thin outside drag racing and Ohio, Pennsylvania, Florida, Tennessee and California).

## Log, Round 14 (Twin Falls; *Street Rod* serial; high school clubs; recreation debate; 2026-10-16)
- **Reader mail:** no open `triage` issues this round.
- **New articles:** [Twin Falls, Idaho: The Main Avenue "Drag Strip"](places/twin-falls-main-avenue.md); [*Street Rod* in the Small-Town Paper](media/street-rod-newspaper-serial.md); [Hot Rod Club, Third Row: The High School Car Clubs](drag-racing/high-school-hot-rod-clubs.md); [Would You Rather Have a Picnic? (June 1957)](drag-racing/recreation-1957-pro-and-con.md).
- **Expanded (additive only):** [The Ohio Gassers](places/ohio-gassers.md) (Chuck Finders's death date); [cruising overview](places/cruising-overview.md) (Twin Falls rows).
- **Resolved:** Chuck Finders died **Sunday, May 17, 2009**, not May 27; a BangShift item dated May 26, 2009 and a UK forum post dated May 19 both predate the 27th (the forum seen only as a search excerpt ◐).
- **Found:** a small-town paper calling its own main street a "drag strip" (Twin Falls, 1957), and a downstate Illinois paper using the same nickname for a county road in a missing-tombstone story; a Twin Falls timing association whose city commission voted to lease it a strip site at Joslin Field (1960); NEA serializing Felsen's *Street Rod* in small-town dailies in 1954; school hot rod clubs in yearbooks from Florida to Oregon, including a Portland school paper that praised its car club and then scolded the drivers; a 1957 recreation-journal pro-and-con naming eight sponsoring communities and Wilmington's incorporated club.
- **New conflicts or single-source flags:** which Felsen book carries the Iowa Timing Association dedication ⚠ (*Street Rod* per scans and a review; *Hot Rod* per a 2009 blog); whether the Joslin Field strip was ever built ◐; the 1960 council story's dollar figure and the judge's name (OCR unreadable); the 1961 Pocatello model years ◐; the Harrisburg tombstone story rests on one item ◐; *Recreation*'s quotes from *Life*, the National Safety Council and others are second-hand ◐.
- **Blocked or unavailable (not bypassed):** Internet Archive lending-library books (scanned *Street Rod*, Faunce) refuse text download; NSRA (UK) forum bot check.

## Next breadcrumbs (Round 14)
- **Twin Falls:** *Times-News* 1961–63 for the Joslin Field lease and any strip opening; the Magic Valley Timing Association's later years; the Avenger club; a cleaner scan of the Aug 30, 1960 council story. *(Advanced in Round 16: 1961–64 read; no strip found.)*
- **Iowa Timing Association:** members, meets and strips before Des Moines Dragway (1957); a first-edition check of the dedications in *Hot Rod* (1950) and *Street Rod* (1953).
- **Wilmington Automotive Activities:** Delaware newspapers or club records; whether its drag-strip use was at a named strip.
- **School clubs** *(partly advanced in Round 16: Sherman, Circleville, Logan Elm)*: more yearbook club pages (Natick, Brockton, Fryeburg, Katy, Alamo Heights, Velma-Alma, West Bend and Ypsilanti search hits not yet read); the Ram Rods after 1957.
- **Hope Star and Harrisburg Daily Register:** local hot rod and drag strip items beyond the serial.
- **Carried from Round 12:** Peggy Hart's own words (CDNC blocked); Kansas City's strip after 1955; Escanaba July–Aug 1955; the Denver county strip; the ATAA and NHRA; the 1957 National Safety Council statement; Decatur Road Runners after 1957.

## Log, Round 13 (taxonomy; 2026-10-15)
- **Restructured** the site into 10 topical departments plus Reference, separating topic from source. Old groups that mixed ideas were split: Customs & Media (into Customs & Kustom Kulture and Media & Shows), Beyond California and Cruise Nights (into Places & Scenes, with the strips moved to Drag Racing & Strips), Grassroots Finds (nine articles filed by topic; the badge and a catalog page remain), Cars and Techniques (merged). See [How the Site Is Organized](taxonomy.md) for the audit, the moved pages and the rules.
- **Redirects** from every old URL to its new one (`hooks/redirects.yml`).
- **Reader block** at the end of articles, plus a Contribute page, issue forms and footer and masthead links for corrections, source tips and suggestions or feedback.

## Log, Round 12 (story-first research push; Escanaba, Kansas City, Half Day, Indiana, Woodward, Dick Wells; 2026-10-15)
- **New articles:** [The Cop and the Auto Shop (Escanaba's Drag-n's)](drag-racing/escanaba-dragns.md); [The Detective Whose Son Was a Dragster (Kansas City)](drag-racing/kansas-city-timing-association.md); [Half Day, Illinois: The Muffler Maker's Drag Strip](drag-racing/half-day-ataa-maremont.md); [March 1957: America Argues About Drag Strips](drag-racing/march-1957-drag-strip-survey.md); [Hoosier Road Runners](drag-racing/indiana-small-town-clubs.md); [Dick Wells](people/dick-wells.md); [Woodward: The City That Banned the Drive-Ins It Didn't Have](places/woodward-ordinances.md).
- **Expanded (additive only):** [Bob Bartel](people/bob-bartel.md), [Detroit/Cordova](drag-racing/detroit-cordova.md), [Akron Fulton Airport](drag-racing/akron-fulton-airport.md), [Memphis](places/memphis.md) (June 1955 *Motor Age* detail); [NSRA early Nationals](street-rodding/nsra-early-nationals.md); [Doris Herbert](people/doris-herbert.md); [planners' report](drag-racing/planners-report-1955.md); [Woodward](places/woodward.md).
- **Method change:** the Internet Archive's full-text search plus page OCR (including NewspaperArchive's *Escanaba Daily Press* and period safety and trade journals), Hoosier State Chronicles and Oregon page OCR turned out to be readable. Quotes use only phrases that read cleanly in OCR.
- **Found:** the National Safety Council moving from praising supervised hot rodding (1955-56) to "in direct opposition to drag racing, supervised or otherwise" by March 1957; the ATAA's own 1954 numbers and a period source that places the first World Series in Oct 1954; a 1966 Birmingham ordinance against drive-ins the city did not have.
- **Conflicts:** ATAA start (1952 vs 1953); St. Charles meet figures (140/1,500 vs "more than 200"/2,000); the identity of a county-built strip near Denver in 1957; NSRA's "first president" (Wells "first active" vs Miller vs Wikipedia's "first president and CEO"); the first World Series (narrowed toward Oct 1954 but still sponsor-sourced).
- **Blocked or unavailable (not bypassed):** *Detroit News* 2023 (paywall; excerpt only); CDNC (so Peggy Hart's own words are still out of reach); Washington, Utah, DigitalNC and Michigan newspaper sites; Escanaba's July-August 1955 issues errored on fetch.

## Next breadcrumbs (Round 12)
- **Peggy Hart's own words:** still needs CDNC (blocked) or another reachable California archive.
- **Commercial Appeal / Summer Avenue; Gasser Gossip / Chuck Finders; St. Louis and Springfield, Mo. cruising:** not started this round.
- **Kansas City:** *Kansas City Star* / *Times* coverage of the July 1955 opening and Landon Laird's column (the Barons anecdote); what happened to the strip.
- **Woodward:** the Royal Oak and Birmingham ordinance texts, and a second source for the 1967 Sass case.
- **Escanaba:** July-August 1955 issues for the Drag-n's road-race result, the auto show and the strip.
- **Denver:** which county-built strip was meant in March 1957 (county commission records; Denver Timing Association).
- **ATAA and the NHRA:** the 1957 purchase of the ATAA; a Lawrenceville World Series program or ad; Mel Bayshore's strip list.
- **National Safety Council:** its 1957 statement, which the UPI story paraphrases.
- **Decatur Road Runners** after Feb 1957; the Detroit Modified Rod and Custom Club.

## Log, Round 11 (Highlights slider; Grassroots finds; 2026-10-15)
- **New UI and automation:** the home-page [Highlights](index.md) carousel, rendered at build time from `docs/data/highlights.yml` by a small MkDocs hook, with a static-list fallback without JavaScript; `scripts/update_highlights.py`; the [Highlights archive](highlights-archive.md); the [Grassroots Sources](reference/grassroots-sources.md) catalog. 16 highlights were seeded from existing articles, 11 of them grassroots.
- **New grassroots articles:** [Pomona's Choppers & the Fontana strip](drag-racing/pomona-choppers-fontana.md) (police chief's 1951 account); [What the City Planners Wrote (1955)](drag-racing/planners-report-1955.md); [Modesto's Century Toppers](drag-racing/modesto-century-toppers.md); [Inyokern: the Sheriff's Strip and the Dust Devils](drag-racing/inyokern-dust-devils.md); [Great Bend, Kansas: the SRCA and the first Nationals](drag-racing/great-bend-srca.md). Index: [Grassroots Finds](reference/grassroots-sources.md).
- **New conflicts:** Century Toppers founding (late 1947 vs 1946); date of Inyokern's last race (April 9, 2005 vs mid-October 2005 or later); Great Bend's top speed (146.16 vs 145.16 mph) and the meaning of "first"; the 1955 report's unsourced Muroc "twenty-seven killed" figure (unverified).
- **Image Credits:** six new Commons files (Winfield 2013, *Reactor*, Inyokern Airport, Pomona drag strip, Great Bend 1943 and 2006).
- **Blocked (not bypassed):** California Digital Newspaper Collection (Cloudflare); Illinois Digital Newspaper Collections, NYS Historic Newspapers and Colorado Historic Newspapers (403); Library of Congress (timeouts); Portal to Texas History (bot check); the Lompoc Record and a Ridgecrest news release behind a paywall (only the readable lines were used).

## Next breadcrumbs (Round 11)
- **Local-paper archives, once reachable:** Pomona *Progress-Bulletin* and *Compton Herald* (1949-53) for the Choppers and Fontana openings; *Modesto Bee* for the Century Toppers' 1949-50 items; *Columbia Daily Tribune* (the June 1954 Motor Sports Club); *Sioux Falls Argus Leader* ("Igniters"); Glen Cove *Record-Pilot* ("Road Panthers"); *Kerrville Daily Times* via the Portal to Texas History (Drag-Uns, March 29, 1953).
- **Inyokern:** the FAA order or a Dust Devils record that dates the last race; Mark Pahuta's film *The Hot Rod Years* (HSUMD, 2025); a second source for Bernie Partridge's "Big Daddy" nickname claim.
- **Great Bend:** the 1955 Hot Rod announcement and a Great Bend Tribune 1955 report; the 146.16 vs 145.16 speed.
- **Pomona:** the date the Choppers moved from Fontana to the fairgrounds; the officer's full name (Coons).
- **Planners' report:** the Muroc "27 killed" claim and the 1947 California law's actual date and statute.
- Carry: all Round 10 breadcrumbs below.

## Log, Round 10 (Ohio & Midwest strips; Snow/Bartel/Gay; *Street Rod*; Peggy Hart; 2026-10-15)
- **New articles:** [Gene Snow](people/gene-snow.md); [Bob Bartel](people/bob-bartel.md); [The Ohio Gassers](places/ohio-gassers.md); [Akron Fulton Airport & Otie Smith](drag-racing/akron-fulton-airport.md); [*Street Rod* magazine (Portland)](media/street-rod-magazine-portland.md); Voices: [Strip Owners & Door-Slammers](voices/strip-owners-and-door-slammers.md).
- **Expanded:** [Peggy Hart](people/peggy-hart.md) (her cars in order, the 1954 130-mph dragster, the Bonneville attempt, the Long & Tuttle pamphlet); [Houston Freeway](drag-racing/houston-freeway-dragstrip.md) (the Gay family years); notes added to [Santa Ana](eras/1950s-santa-ana-drags.md), [Detroit & Cordova](drag-racing/detroit-cordova.md), [NSRA](street-rodding/nsra-early-nationals.md) and [Founding Street Rodder](voices/street-rodder-founding.md).
- **Corrections:** Houston Freeway was bought by **Carl & Marie Gay** (NHRA 2015), not Don Gay "in 1960" (Don was about 13 then). The Round 9 carry-over's "IDAA" is the **ATAA** (Automobile Timing Association of America). The Bruce Miller *Street Rod* thread is now documented (20 issues, Oct 1971–Jul 1973).
- **New conflicts:** Snow's first 200 mph (Aug 17, 1968; "early 1969"; "autumn 1969"); first World Series (1954 vs 1956 vs 1953); Bartel's birthplace (Sterling, per the obituary, vs "Moline native"); NSRA first president (Bruce Miller vs Dick Wells); 99W's "first Nationals in Memphis 1970" (it was Peoria); Hassel's 1963 class (B/Gas vs C/Gas); who built the 1968 Mr. Gasket Camaro (Meal vs "Hrudka Bros."); Chuck Finders's death date (May 17 vs 27, 2009); Hill brothers (Bill vs Tom); Santa Ana opening (June 19, a Monday, vs first race Sunday July 2, 1950); Hart's Lions start ('63 vs '65, in the same 1980 article); the Akron marker's "1959 championship" vs Middle Eliminator.
- **Images:** six new Commons files: three *Rambunctious* photos, the George Field and Tri-Cities postcards, and Sellwood. Reused: the Willys gassers and the Akron aerial.
- **Blocked:** CDNC (Cloudflare), so no 1950s Peggy Hart papers; qconline (429), so the Bartel 2009 interview is from a search excerpt only; chuckfinders.com (404, empty Wayback copy); the WFAA 2007 archive (the Snow legal note in Wikipedia is unverified); the Akron *Beacon Journal* Otie Smith obituary (402); Google Patents (non-JSON), so no Crowerglide patent was found.

## Next breadcrumbs (Round 10)
- **Snow 200.88:** a period *Drag News* or *National Dragster* report or a timing slip that dates the Dickinson pass (1968 vs 1969).
- **Bartel:** read the Aug 2009 *Dispatch-Argus* interview and a 1954–56 Lawrenceville World Series program or ad; any NHRA record of buying the ATAA in 1957; the National Association of Drag Strips.
- **Gay family:** the deed or year of the Freeway purchase; a Houston Chronicle closing notice (1987?).
- **Peggy Hart:** a copy of Long & Tuttle, *Every Sunday Drag Races*; *Santa Ana Register* 1950–56 via another archive (newspapers.com is paywalled, CDNC blocked); SCTA Bonneville records for a Hart entry.
- **Ohio:** the *Gasser Gossip* "Original Darkhorse" articles (jrthompson PDFs); a Chuck Finders obituary to settle May 17 vs 27; the 1963 Nationals class-winner list (Hassel); Hill brothers' first names from a period source.
- **NSRA:** a 1970–72 NSRA document naming the first president; the *Street Rod* tables of contents (99W) for a Miller editorial.
- **Akron:** Randy Lipscomb's 2013 Otie Smith video; the strip's closing year.
- Carry: Mercer Miller oral; Commercial Appeal; Woodward ordinances; Roberto Rodriguez Mar 23, 1979; Kong Jackson death; Detroit News Hernandez obituary on its own site; Hilborn *Hot Rod* Apr 1948.

## Log, Round 9 (Detroit chassis & tin; Hilborn/Hernandez; Houston strip; AB 436; 2026-10-14)
- **New articles:** [Logghe Stamping](companies/logghe-stamping.md); [Stu Hilborn](people/stu-hilborn.md); [Fran Hernandez](people/fran-hernandez.md); [Al Bergler](people/al-bergler.md); [Malcolm Durham](people/malcolm-durham.md); [Houston Freeway Dragstrip](drag-racing/houston-freeway-dragstrip.md); Voices [Injection, Factory Racing & Detroit Tin](voices/injection-and-tin.md).
- **Resolved / strengthened:** California cruising-ban repeal identified as **AB 436** (Ch. 803, 2023; effective Jan 1, 2024). Fran Hernandez death **Jan 5, 2011** (Detroit News via H.A.M.B.) vs Hemmings "2005" (flagged erroneous). Kong Jackson death still **2000** on list evidence; no newspaper obit yet.
- **New conflicts:** Logghe founding **1946** (Hot Rod) vs **1947** (MMSHOF); Hilborn Model A lakes speed **120** vs **123**; Durham Top 50 rank **46** vs **48**; Houston Freeway close **1987** (forum) vs "unknown"; Garlits Museum page still said Gene Logghe "resides" after MMSHOF listed Aug 2021 death.
- **Images:** three Mercury Comet Commons photos, four Offenhauser Commons photos (hosted), two Hilborn patent drawings; re-used SOHC, El Mirage, Autorama, Garlits, Houston-from-Westheimer.
- **Skipped / thin:** Mercer Museum Leonard Miller oral / *Silent Thunder*; Peggy Hart 1950s papers; Commercial Appeal Summer Ave; Woodward council minutes; Springfield MO / Denver Colfax / St. Louis cruising.

## Next breadcrumbs (Round 9)
- Read the **Detroit News** Fran Hernandez obituary on the paper's own site (currently via H.A.M.B. paste).
- **Gene Snow** first official 200 mph Funny Car in Logghe Charger *Rambunctious*—primary timing slip or NHRA note.
- **Don Gay** purchase records for Houston Freeway (1960 claim) and a Chronicle closing notice for 1987.
- **Hilborn** *Hot Rod* Apr 1948 cover story and July 1948 SCTA El Mirage entry list (Wilson 150.5).
- **Al Bergler** Ridler / Autorama 1964 results sheet; Motown Shaker Logghe serials.
- **Malcolm Durham** full oral (Drag Race Central "Fast Five" was blocked this round).
- Carry: Mercer Miller oral; Commercial Appeal; Woodward ordinances; Roberto Rodriguez Mar 23, 1979; Bruce Miller Portland *Street Rod* (1972); Ohio Finders/Meal/Hassel; Bob Bartel / IDAA programs.

## Log, Round 8 (Cruise Nights & Hangouts; reframing; 2026-10-13)
- **Editorial reframing:** Voices titles, intros and the index are now organized by story, place and contribution instead of ethnicity. The Voices index is grouped by Dry lakes, Drag strips, Customs/shows and Street rodding. Leonard Miller's title is now "From a Paoli Junkyard to Team Owner" and the Ruelas page is "A South LA Family Shop." Speakers' own words about their neighborhoods are kept, and no content was deleted.
- **New section:** `cruising/`, with a landing page and 10 spots: Woodward, Van Nuys, Bob's Big Boy / River Road, Harvey's Broiler, Whittier Blvd, Modesto, Summer Ave, Lake St / University, Westheimer and Central Ave (later). There are 13 new open-licensed images.
- **Conflicts marked:** Van Nuys closure year (1980, 1981 or 1983); Whittier closure date (Mar 23 or Aug 31, 1979); Harvey's sale year (1965 or 1968); Modesto's "banned 1993" marker vs. the 1990 ordinance.
- **Skipped (no usable sources):** Denver's Colfax Ave and St. Louis cruising.

## Next breadcrumbs (Round 8)
- Identify the specific late-1960s Woodward cruising and parking ordinances (Royal Oak, Birmingham and Ferndale council minutes).
- Commercial Appeal (1955–70) on Summer Ave policing, and whether Robilio's was connected to Marshall Robilio (unverified).
- Robert Genat, *Woodward Avenue: Cruising the Legendary Strip* (CarTech), for primary interviews.
- Roberto Rodriguez's own published account of March 23, 1979 and the *Lowrider* magazine archive.
- Pre-1990 Albuquerque (Central/Fourth St), Springfield, MO (Kearney St), Denver (Colfax) and St. Louis cruising.
- ~~The bill number and text of the 2024 California law ending cruising bans~~ (**done Round 9:** AB 436 / Ch. 803, 2023).
- Houston Press archives or HAIF threads that date the 1986 Westheimer roadblocks.

## Log, Round 7 (Voices; 2026-10-13)
- We added the **Voices** section: 11 narrative pages and a method page, plus 13 "In their own words" pull-quotes in existing articles.
- Every quote was checked by script against the text of the fetched page. Pages read through the fetch tool (wediditforlove, Memphis Rodders) were checked by eye.
- New conflicts: Halls start year (Godman/NHRA 1953 vs 1955); Drag Safari month ("summer" vs September); Gold's "hot rod" etymology and his "first '32" claim; Burns' "GM 1938 first striping"; the OC Register calling Peggy Hart "the only woman racer."
- Round 6 leads followed up: the Commercial Appeal (only the 2008 Lakeland piece, via the Rodders blog; not yet read); Street Rodder's founding (done); Von Dutch (the 1965 quote is real but the magazine is unidentified).

## Next breadcrumbs (Round 7)
- Read the **Mercer Museum 2015 oral history** of Leonard Miller and his book *Silent Thunder*. Find first-person **Malcolm Durham** material.
- **Peggy Hart's own words** in 1950s newspapers (Santa Ana Register) and *Drag News*.
- Coachbuilt's Ruelas/Dukes profile (Julio's 1999 interview); LA club histories (the Professionals, the Imperials, the Clique, the Igniters).
- Identify the **1965 Von Dutch magazine** (possibly *Car Craft* or *Rod & Custom*).
- The **Commercial Appeal 2008** Lakeland feature and Memphis Public Library newspaper archives.
- Bruce Miller's Portland ***Street Rod*** magazine (1972).
- Pancho Barnes book *Voices from the Happy Bottom Riding Club*: is it published?
- The Petersen, Revs and AHRF oral history catalogs: searched, nothing usable found online this round.

## Log, Round 6 (customs, street rodding, regions; 2026-10-13)
- This round added 9 articles and 3 landing pages (Customs & Media, Street Rodding, Beyond California), plus 14 images.
- Conflicts flagged: Oakland 1950 attendance (27,625 vs 25,000+); first Lead Sled Spectacular (300+ vs 400); the start year of the Halls drags (1953 vs 1955) and who won the 1955 meet; AMT vs SMP as inventor of the 3-in-1; 1970 Peoria count.
- Sun Records: we found no documented car-builder link, and the page says so plainly.

## Next breadcrumbs (Round 6)
- Memphis: Commercial Appeal archive (1952–79) on Halls and Lakeland; the 1971 Nationals count from Street Rodder or *Street Scene*; a primary source for the 1992 Fastest Street Car Shootout.
- Street Rodder's founding (1972, McMullen?), IFS suppliers (Mustang II swaps, Heidts, Pete & Jake's), and NSRA rulebooks on the 1948 and 30-year rules.
- Carolinas and Southeast (Shadyside? Piedmont strips), New England (Sanford, Maine, and Connecticut clubs), and Houston Freeway Dragstrip (1957).
- Media: *Hot Rod Gang*, *Drag Strip Girl*, *American Graffiti* and their car sources; Von Dutch from primary sources; Rod & Custom's "little" magazines.
- Hemmings on Roth's royalty figure (the site was blocked by Cloudflare).

## Log, Round 1 (2026-10-12)
- Started with founders of small prewar and postwar speed businesses. The richest first-hand material so far: **AHRF pioneer bios** (Tony Thacker), **Kustomrama** family interviews (Sondre Kvipt), the **Road Runners club research packet**, the **Motorsports Hall of Fame** oral-style bios, and **Ford Barn / H.A.M.B.** owner threads.
- Recurring cross-links: Fairfax High / Melrose Ave. (Summers ↔ Xydias); Glendale Strokers (Navarro ↔ Beatty ↔ Doane Spencer); Doane Spencer ↔ Jack Dorn ↔ Summers; Veda Orr as photographer for *California Timing News*.

## Log, Round 2 (2026-10-13)
- Chased the WWII home front (Veda Orr), prewar customizers (Hagy, DuVall), the Glendale club (Beatty), the 1960s independent press (Doris Herbert, the drag rags), and a non-California founder (Ed Almquist).
- **Verified by reading the pages:** the Santa Ana backers (Press-Enterprise), the Beast III speed and driver (Kustomrama), the Peoria dates and attendance (Hagerty).
- **Corrections and new conflicts:**
    - Santa Ana admission: 50¢ for all vs 50¢/$1.
    - C.J. Hart death date: June 25 vs 26, 2004.
    - Winfield birth year: 1901 vs 1910 (IDRHOF).
    - Edelbrock birth year: 1912 vs 1913.
    - Glendale "Strokers" vs "Stokers."
    - Beatty 1951 speed: 185.80 vs 188.284.
    - Veda Orr's SCTA membership: prewar vs postwar.
    - Almquist Engineering founded 1946 vs 1947.
- **Lost the ESPN Hart story** (404). Hemmings' Almquist page and the Times Herald-Record obituary blocked direct fetches, so I used search excerpts, marked ◐.
- ~~**Isky:**~~ (verified Round 3) the IDRHOF lists Ed Iskenderian as "1921–2026." That suggests he died this year. **Not yet verified.** It would need an obituary before any page uses it.
- New cross-links: Medley drew Veda's covers, then co-founded Peoria (1970). Steve Reyes, who named Pro Street (1979), is in IDRHOF 2002. Art Chrisman links Santa Ana, Beast III and Chrisman & Sons. Almquist's pamphlet influenced the customizers.

## Log, Round 5 (images, 2026-10-13)
- Images went from 16 to 40 hosted files (59 figures), all wrapped in `<figure>`. Every article now has a "Visual references (external)" list where key images are copyrighted. Rejected candidates are listed on Image Credits.
- **Image leads:** Orange County Archives on Flickr (CC BY, many 1950s airport views; look for drag-strip shots); Detroit News/Wayne State Reuther Library (dragway); the Akron Beacon Journal archive; HAER/HABS for other National Historic Vehicle Register cars.

## Log, Round 4 (2026-10-13)
- **Structure:**
    - Image layer: 9 Commons photos and 7 USPTO patent drawings, every one captioned, plus an [Image Credits](reference/image-credits.md) page.
    - An article record box on all 36 articles.
    - New pages: [Timeline](reference/timeline.md), [People & Companies Index](reference/index-people-companies.md), [Patents](reference/patents.md) and [Source Standards](reference/source-standards.md).
    - glightbox plugin.
- **New articles:** Howard Johansen, Jack Engle, Kong Jackson, Arlen Vanke, Eddie Schartman, the Hill Bros. Red Baron, and Detroit Dragway & Cordova.
- **Patent finds:**
    - Almquist Engineering's own "Gear shift," US 3,082,639 (filed Sept 1962), a month before Hurst & Campbell's US 3,172,301. This bears on open question #14.
    - Ten Winfield patents (1928–45).
    - Isky's 1956 lifter-guide patent, which names him at Inglewood.
    - A 1960 carb-linkage patent by Vic Edelbrock **Jr.**
    - Navarro's turbo patents (Glendale).
- **News:** Joe Hrudka died May 24, 2026 (NHRA). The Mr. Gasket page is updated.
- **New conflicts:**
    - Kong Jackson's death: Sept 4, 2000 (contemporaneous list post) vs 2002 (Fuel Curve).
    - Jackson's "SCTA formed in 1938."
    - Engle's founding date: 1939/41/42/47/50.
    - Vanke's first race: 1951 vs 1953.
    - Vanke at Knafel: service manager vs salesman.
    - Johansen's 1954 engine: Dodge vs DeSoto.
    - Cordova's opening: 1955 vs 1956.
    - Detroit Dragway's closing: 1997 vs 1998.
- **Not read first-hand:** Ganahl's "The Mystery Wagon" (RJ #36) and Post's *High Performance*. Both are flagged; neither is cited for specifics.

## Log, Round 3 (2026-10-13)
- **Isky verified:** died Feb 4, 2026, at 104 (NHRA, Hagerty, Car and Driver, SEMA, Legacy). Article added.
- **Resolved:**
    - Santa Ana admission: spectators 50¢ (later $1), racers $1.
    - C.J. Hart's death date: June 25, 2004. Five obituaries agree, and the son is quoted.
    - The Sept 1958 Hot Rod ad: Howard Johansen's hero ad on Doug Cook's defection from Isky, per Isky in a 1994 interview.
- **New conflicts:**
    - Hart at Lions: 1965–71 vs 1963–70.
    - Doty's purchase of the DuVall patterns: 1946 vs "late 1940s."
    - Mr. Gasket founding and incorporation: 1964 / 1965 / 1967.
    - Mr. Gasket's sale to Grace: $17M vs $6M realized.
    - Slo-Pokes vs Slo Poks.
    - Peoria Best Car: Orv Elgie (drove 8,000 mi) vs Brizio's "trailer" complaint.
    - Postoian's "Riverside Nationals 1953–56" claim (MMSHOF) looks doubtful and needs checking.
- **Thread found:** Coachbuilt.com's census-based bios (DuVall, DeBell, Doty dates) are a strong secondary genre. They use census records, city directories and yearbooks.
- **Blocked:** Columbus Dispatch (JEGS) and the Times Herald-Record (Almquist) are paywalled.

## Open questions
1. **SCTA founding clubs:** identify "Drake, *Flat Out*" and "Carrol's book" cited by the Road Runners. Is there a period SCTA minutes book?
2. **First SCTA meet date:** May 15 vs March 15, 1938. Find a period entry list or program.
3. **Edelbrock's 1941 speed:** 112 vs 121.4 mph, and Muroc vs Bonneville. Find SCTA 1941 record lists.
4. **Winfield and Indy:** which year span is right (1927–37 or 1933–46)? Check Indy winners' carb specs.
5. **Hirohata build time:** 14 vs 97 days.
6. **"Wight" vs "Wright":** check the Bell, CA business directory and Wight's 1943 obituary.
7. **Steve Reyes's 1979 "Pro Street" article:** which magazine and issue?
8. ~~Santa Ana backers~~ (confirmed Round 2).
9. **Phil Weiand's first intake:** is the Navarro story corroborated by Weiand family sources?
10. **Riley's WWII drone engine:** look for a government contract record.

11. **Glendale Strokers vs Stokers:** period SCTA entry lists or a plaque photo.
12. **Veda Orr's SCTA membership date:** SCTA minutes or a 1946 Racing News.
13. **Tom Beatty's death year** and SCTA/BNI record lists to check the RM Auctions catalog claims.
14. **Almquist and the Hurst shifter:** check Hurst company histories for the 1959 partnership. *Round 4:* Almquist Engineering's gear-shift patent US 3,082,639 (1962) was found. Compare its claims with Hurst's US 3,172,301 and read both citation lists.
15. ~~Isky's death~~ (verified Round 3).

16. **Kong Jackson's death:** 2000 vs 2002. Find an LA Times or Daily News obituary for Sept 2000.
17. **Chester L. Herbert (US 4,071,000):** is this Chet Herbert? Check against an obituary that gives his legal name.
18. **George H. DuVall Jr.'s 1945 wheel-lock patent:** check the residence in the patent text.
19. **Twin Bears at the first Winternationals (1961):** check NHRA results.

## Next breadcrumbs (Round 5)
- **Post, *High Performance*** (1994): get a copy and check the timeline against it.
- **The Rodder's Journal #36** (Mystery Wagon): request it from a back-issue dealer or library.
- **Tom Medley's 1988 Kong Jackson interview** in Tex Smith's *Hot Rod History*.
- **Bob Bartel / ATAA:** look for 1954–58 World Series programs (Quad-City Times archives).
- **Ohio:** Chuck Finders, Dave Meal, Otie Smith, Ron Hassel; Akron airport marker text (Ohio History Connection).
- **The Logghe brothers** and Al Bergler, Detroit's funny car tin men.
- **Read Winfield's patents in full** for engineering detail; search more names (Kong Jackson, Stu Hilborn, Phil Weiand, Fran Hernandez).

## Next breadcrumbs (Round 4, superseded)
- Wallace's **1958 Drag Rags installment** (the Howard's five-clowns ad, the Sept '58 ad scan) and **Camgrinder Wars Part 2** (Hot Rod, Jan 2015).
- **Howard Johansen** (IDRHOF 1991, 1910–1988) and **Jack Engle** (1920–2008): stubs.
- **Kong Jackson** and the stolen traffic-signal starting lights of 1947–48: look for SCTA News issues.
- **The lost So. Cal. Plating 1935 phaeton:** Pat Ganahl's "The Mystery Wagon," *Rodder's Journal* #36.
- **Ohio Gassers:** Arlen Vanke, Eddie Schartman, Dave Meal, the Hill brothers' "Red Baron" Willys.
- **Detroit:** Farmington Speed Shop, Detroit Dragway, and the 1957–58 World Series of Drag Racing (Cordova, IL).
- **Peggy Hart's** IDRHOF bio text; Mile Square racing (Mile Square Park).
- **Orv Elgie** interview (Modern Rodding, May 2023).
- **Robert C. Post,** *High Performance* (Smithsonian curator): a scholarly anchor to cite.

## Next breadcrumbs (Round 3, carried)
- **Wallace Family Archives** (drag rag duplicates): primary 1960s source.
- **Dave Wallace's Drag Rags series** on Competition Plus: work through it season by season (Gasser Wars ad, Sept 1958 Hot Rod).
- **Julian Doty** (DuVall windshield and Jeep head patterns, 1946) and **Leonard DeBell**/So. Cal. Plating.
- **Peggy Hart** (IDRHOF 1998, 1914–1980): early woman drag racer.
- **Midwest and East:** Jeg Coughlin Sr. (Columbus, 1960), Setto Postoian, Joe Hrudka (Mr. Gasket), the Torrid Torkers (Buffalo), Kentucky Motorsports Hall of Fame NSTRA history page, the Slo-Pokes of Peoria.
- **Rod & Custom, August 1990** (DuVall), **Hop Up, Dec 1951** (Beatty tank).
- **Pike County Historical Society / Milford newspapers** for Almquist Engineering's gymnasium days.

## Round 1 breadcrumbs (status)
- **Veda Orr:** her self-published *Hot Rod Pictorial* and wartime newsletter to servicemen club members. Possibly the first woman documenting the scene. High value.
- **Roger Harrell's book on Jim White's speed shop:** a rare South LA shop history.
- **Roy Hagy:** the other prewar chopping shop (Tom Sparks interview by Pat Ganahl).
- **George DuVall:** DuVall windshield; worked with Frank Kurtis on the SoCal Plating truck.
- **Tom Beatty:** Glendale Strokers machinist; Rust Bucket; belly tank.
- **Doris Herbert & *Drag News*** (1959–): archives as a primary source for the 1960s.
- **Lions Drag Strip 1955–72** and C.J. Hart's management years.
- **Midwest and East:** Ed Almquist (PA mail-order), the Slo-Pokes of Peoria, the Minnesota Street Rod Association. Break the SoCal bias.
- **1960s gap:** Tony Nancy, early gassers, the Oakland Roadster Show and Andy Brizio.
- **Sources to mine:** Smithsonian NMAH Archives Center hot rod oral histories; Revs Institute digital library; NHRA Museum *Legends* interviews; Dry Lakes Racers Hall of Fame bios; California Digital Newspaper Collection (cdnc.ucr.edu) for 1930s–50s local press; H.A.M.B. "history" subforum.
