# Research Trail: The Investigator's Log

*Where the case stands: the rules we follow each round, what we found, and the leads still open.*

## Standing standard for every nightly round (set in Round 11)
1. **Highlights.** Each round adds **2-4 entries** to [`docs/data/highlights.yml`](https://github.com/obnovas/hotrod-wiki/blob/main/docs/data/highlights.yml) for the home-page slider, and **at least half** must be grassroots (local news, oral history, obituaries, club newsletters and club-run pages, municipal records, historical markers, family accounts, local-history sites). Teasers state only what the article states, with the same hedges and a verbatim `evidence` phrase from the article.
2. **Rotation.** The slider shows the newest 16 by date added. Older entries move to the [Highlights archive](highlights-archive.md) automatically; nothing is deleted.
3. **Grassroots first.** Prefer a local paper, historical society page, obituary, club newsletter, municipal or police record, marker or family account over an industry magazine whenever both exist. Mark such pages with the Grassroots badge in the article record's source types, and add new outlets to [Grassroots Sources](grassroots/sources.md).
4. **Check before pushing.** Run `python scripts/update_highlights.py check`, then `mkdocs build --strict`. The build fails if a highlight's evidence phrase, numbers, link, anchor, image or credit row no longer matches. Details are in [CONTRIBUTING](https://github.com/obnovas/hotrod-wiki/blob/main/CONTRIBUTING.md).

## Log, Round 12 (story-first research push; Escanaba, Kansas City, Half Day, Indiana, Woodward, Dick Wells; 2026-10-15)
- **New articles:** [The Cop and the Auto Shop (Escanaba's Drag-n's)](grassroots/escanaba-dragns.md); [The Detective Whose Son Was a Dragster (Kansas City)](grassroots/kansas-city-timing-association.md); [Half Day, Illinois: The Muffler Maker's Drag Strip](regions/half-day-ataa-maremont.md); [March 1957: America Argues About Drag Strips](grassroots/march-1957-drag-strip-survey.md); [Hoosier Road Runners](grassroots/indiana-small-town-clubs.md); [Dick Wells](people/dick-wells.md); [Woodward: The City That Banned the Drive-Ins It Didn't Have](cruising/woodward-ordinances.md).
- **Expanded (additive only):** [Bob Bartel](people/bob-bartel.md), [Detroit/Cordova](regions/detroit-cordova.md), [Akron Fulton Airport](regions/akron-fulton-airport.md), [Memphis](regions/memphis.md) (June 1955 *Motor Age* detail); [NSRA early Nationals](street-rodding/nsra-early-nationals.md); [Doris Herbert](people/doris-herbert.md); [planners' report](grassroots/planners-report-1955.md); [Woodward](cruising/woodward.md).
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
- **New UI and automation:** the home-page [Highlights](index.md) carousel, rendered at build time from `docs/data/highlights.yml` by a small MkDocs hook, with a static-list fallback without JavaScript; `scripts/update_highlights.py`; the [Highlights archive](highlights-archive.md); the [Grassroots Sources](grassroots/sources.md) catalog. 16 highlights were seeded from existing articles, 11 of them grassroots.
- **New grassroots articles:** [Pomona's Choppers & the Fontana strip](grassroots/pomona-choppers-fontana.md) (police chief's 1951 account); [What the City Planners Wrote (1955)](grassroots/planners-report-1955.md); [Modesto's Century Toppers](grassroots/modesto-century-toppers.md); [Inyokern: the Sheriff's Strip and the Dust Devils](grassroots/inyokern-dust-devils.md); [Great Bend, Kansas: the SRCA and the first Nationals](grassroots/great-bend-srca.md). Index: [Grassroots Finds](grassroots/index.md).
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
- **New articles:** [Gene Snow](people/gene-snow.md); [Bob Bartel](people/bob-bartel.md); [The Ohio Gassers](regions/ohio-gassers.md); [Akron Fulton Airport & Otie Smith](regions/akron-fulton-airport.md); [*Street Rod* magazine (Portland)](street-rodding/street-rod-magazine-portland.md); Voices: [Strip Owners & Door-Slammers](voices/strip-owners-and-door-slammers.md).
- **Expanded:** [Peggy Hart](people/peggy-hart.md) (her cars in order, the 1954 130-mph dragster, the Bonneville attempt, the Long & Tuttle pamphlet); [Houston Freeway](regions/houston-freeway-dragstrip.md) (the Gay family years); notes added to [Santa Ana](eras/1950s-santa-ana-drags.md), [Detroit & Cordova](regions/detroit-cordova.md), [NSRA](street-rodding/nsra-early-nationals.md) and [Founding Street Rodder](voices/street-rodder-founding.md).
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
- **New articles:** [Logghe Stamping](companies/logghe-stamping.md); [Stu Hilborn](people/stu-hilborn.md); [Fran Hernandez](people/fran-hernandez.md); [Al Bergler](people/al-bergler.md); [Malcolm Durham](people/malcolm-durham.md); [Houston Freeway Dragstrip](regions/houston-freeway-dragstrip.md); Voices [Injection, Factory Racing & Detroit Tin](voices/injection-and-tin.md).
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
