#!/usr/bin/env python3
"""Draft front matter for articles from what the page and the reference index already say.

    python scripts/draft_frontmatter.py [--write] [--only FIELD,...] [files...]

Never invents: the summary is the article's own lede (hand-edit it), entities come from the
People & Companies index rows that link to the page, places from the text, related from the
page's own links. Existing values are kept unless --only names the field. Prints a report."""
import re
import sys
from collections import Counter

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from articles_lib import DOCS, articles, split_front, join_front, plain, body_prose, load_canonical  # noqa: E402

STATES = {
    "Alabama": ["Ala."], "Arizona": ["Ariz."], "Arkansas": ["Ark."], "California": ["Calif.", "Cal."], "Colorado": ["Colo."],
    "Connecticut": ["Conn."], "Delaware": ["Del."], "Florida": ["Fla."], "Georgia": ["Ga."], "Idaho": [], "Illinois": ["Ill."],
    "Indiana": ["Ind."], "Iowa": [], "Kansas": ["Kan.", "Kans."], "Kentucky": ["Ky."], "Louisiana": ["La."], "Maine": [],
    "Maryland": ["Md."], "Massachusetts": ["Mass."], "Michigan": ["Mich."], "Minnesota": ["Minn."], "Mississippi": ["Miss."],
    "Missouri": ["Mo."], "Montana": ["Mont."], "Nebraska": ["Neb.", "Nebr."], "Nevada": ["Nev."], "New Hampshire": ["N.H."],
    "New Jersey": ["N.J."], "New Mexico": ["N.M."], "New York": ["N.Y."], "North Carolina": ["N.C."], "North Dakota": ["N.D."],
    "Ohio": [], "Oklahoma": ["Okla."], "Oregon": ["Ore."], "Pennsylvania": ["Pa.", "Penn."], "Rhode Island": ["R.I."],
    "South Carolina": ["S.C."], "South Dakota": ["S.D."], "Tennessee": ["Tenn."], "Texas": ["Tex."], "Utah": [],
    "Vermont": ["Vt."], "Virginia": ["Va."], "Washington": ["Wash."], "West Virginia": ["W.Va."], "Wisconsin": ["Wis."], "Wyoming": ["Wyo."],
}
REGION_OF = {
    "California": "West", "Nevada": "West", "Utah": "West", "Arizona": "Southwest", "New Mexico": "Southwest", "Texas": "Southwest",
    "Oklahoma": "Southwest", "Colorado": "West", "Idaho": "Northwest", "Oregon": "Northwest", "Washington": "Northwest", "Montana": "Northwest",
    "Wyoming": "West", "Kansas": "Midwest", "Nebraska": "Midwest", "Iowa": "Midwest", "Missouri": "Midwest", "Illinois": "Midwest",
    "Indiana": "Midwest", "Ohio": "Midwest", "Michigan": "Midwest", "Wisconsin": "Midwest", "Minnesota": "Midwest",
    "North Dakota": "Midwest", "South Dakota": "Midwest", "Tennessee": "South", "Arkansas": "South", "Louisiana": "South",
    "Mississippi": "South", "Alabama": "South", "Georgia": "South", "Florida": "South", "Kentucky": "South", "Virginia": "South",
    "West Virginia": "South", "North Carolina": "South", "South Carolina": "South", "Pennsylvania": "Northeast", "New York": "Northeast",
    "New Jersey": "Northeast", "Maryland": "Northeast", "Delaware": "Northeast", "Connecticut": "Northeast", "Massachusetts": "Northeast",
    "Rhode Island": "Northeast", "Vermont": "Northeast", "New Hampshire": "Northeast", "Maine": "Northeast",
}
# Well-known places the prose names without a state. Each mention counts toward that state.
KNOWN_CITIES = {
    "Los Angeles": "California", "Santa Ana": "California", "Van Nuys": "California", "Downey": "California",
    "Pasadena": "California", "Glendale": "California", "Burbank": "California", "Long Beach": "California",
    "Pomona": "California", "Bakersfield": "California", "Inyokern": "California", "Muroc": "California",
    "El Mirage": "California", "Bonneville": "Utah", "Whittier": "California", "East Los Angeles": "California",
    "Hollywood": "California", "San Fernando": "California", "Gardena": "California", "Lynwood": "California",
    "Bell": "California", "Compton": "California", "San Diego": "California", "Fresno": "California",
    "Sacramento": "California", "Oakland": "California", "San Francisco": "California", "Modesto": "California",
    "Memphis": "Tennessee", "Albuquerque": "New Mexico", "Houston": "Texas", "Dallas": "Texas",
    "Minneapolis": "Minnesota", "St. Paul": "Minnesota", "Detroit": "Michigan", "Chicago": "Illinois",
    "Peoria": "Illinois", "Dayton": "Ohio", "Columbus": "Ohio", "Akron": "Ohio", "Indianapolis": "Indiana",
    "Portland": "Oregon", "Seattle": "Washington", "Woodburn": "Oregon", "Kansas City": "Missouri",
}

TAG_RULES = [
    ("drag-strips", r"drag ?strip|dragway|quarter.mile|the strip\b", 3),
    ("airport-strips", r"airport|air base|airfield|runway|air ?strip|naval air", 2),
    ("car-clubs", r"\bclubs?\b", 4),
    ("club-rules", r"bylaw|\bfined?\b|\bfines\b|courtesy card|suspend|club rules|club court", 2),
    ("police-and-safety", r"police|sheriff|highway patrol|safety|\bcourt\b|\bjudge\b|ticket", 3),
    ("town-politics", r"city council|council|ordinance|supervisors?\b|commission|zoning|petition|mayor|township", 3),
    ("street-racing", r"street rac|racing on (?:the )?(?:street|highway|road)|illegal(?:ly)? rac|drag rac\w+ on", 2),
    ("cruising", r"cruis|dragging main|drag(?:ging|gin') (?:main|10th)|drive-in|hangout", 3),
    ("dry-lakes", r"muroc|el mirage|bonneville|dry lakes?|\bscta\b|the lakes\b", 3),
    ("speed-equipment", r"speed shop|speed equipment|speed parts|intake|manifold|cylinder head|\bheads\b|carburet", 3),
    ("camshafts", r"\bcams?\b|camshaft|cam grind", 4),
    ("aftermarket-business", r"\bsema\b|catalog|mail.order|aftermarket|acquired|buyout|warehouse", 3),
    ("customs", r"\bcustoms?\b|customiz|lead sled|chopped", 4),
    ("car-shows", r"car show|roadster show|autorama|rod show|custom show|home show", 2),
    ("street-rods", r"street rod", 3),
    ("gassers", r"gasser|\b[a-c]/gas\b|willys", 3),
    ("funny-cars", r"funny car|altered.wheelbase", 2),
    ("dragsters", r"dragster|digger|slingshot", 3),
    ("sanctioning-bodies", r"\bnhra\b|\bahra\b|\bataa\b|\bscta\b|\buhra\b|\bihra\b|national hot rod association", 4),
    ("magazines-and-media", r"magazine|\bdrag news\b|trend book|\bkits?\b|newspaper|serial|publisher", 5),
    ("women", r"\bwom[ae]n\b|\bgirls?\b|gas-ketts|powder puff|wife", 3),
    ("teenagers-and-schools", r"teen|high school|youth|juvenile|students|yearbook", 3),
    ("patents-and-inventions", r"patent", 2),
    ("fiberglass", r"fiberglass", 2),
    ("land-speed", r"bonneville|land speed|streamliner|belly tank", 2),
    ("family-business", r"his father|father's|brothers|family business|his son|sons\b", 3),
]
CLUB = re.compile(r"club|rodders|association|igniters|drag-?o?n'?s|gear jammers|road runners|toppers|kouriers|deacons|gas-ketts|nightcrawlers|choppers|ridge runners|strokers|stokers|throttlers|night flyers|dukes|turtles|chaparral|slo-pokes|kemps|rebels|sidewinders|low flyers|road kings|flaming carbs|fly-wheels|pistons|push rods|igniters|timing assn|\bsrca\b", re.I)
STRIP = re.compile(r"drag ?strip|dragway|raceway|speedway|\bstrip\b|sports arena|motorsports park|drag-a-way|lodge", re.I)
PLACE = re.compile(r"avenue|boulevard|blvd|\bstreet\b|\broad\b|airport|air base|\bfield\b|broiler|big boy|drive-in|dry lake|lake\b|fairgrounds", re.I)


def index_rows():
    rows = []
    t = (DOCS / "reference/index-people-companies.md").read_text()
    for line in t.splitlines():
        if not line.startswith("| ") or line.startswith("| Name") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        name = re.sub(r"\s*[⚠◐]", "", plain(cells[0])).strip()
        links = [re.sub(r"^\.\./", "", h.split("#")[0]) for h in re.findall(r"\]\(([^)]+)\)", cells[2])]
        links = [("reference/" + h if "/" not in h else h) for h in links]
        rows.append((name, plain(cells[1]), links))
    return rows


def person_name(name):
    m = re.match(r"^([^,]+), (.+)$", name)
    if not m:
        return None
    last, first = m.group(1), m.group(2)
    if re.search(r"\b(Inc|Co|Corp|Ltd)\b", first):
        return None
    first = re.sub(r"^(Sheriff|Chief|Dr\.|Rev\.|Judge|Mayor|Capt\.|Sgt\.|Lt\.|Maj\.) ", "", first)
    jr = ""
    if re.search(r",? Jr\.?$", first):
        first, jr = re.sub(r",? Jr\.?$", "", first), " Jr."
    return f"{first} {last}{jr}".strip()


def years_of(title, prose):
    m = re.search(r"\b(1[89]\d\d|20\d\d)\s*[–-]\s*(\d{2,4})\b", title)
    if m:
        a = int(m.group(1)); b = m.group(2)
        b = int(b) if len(b) == 4 else int(str(a)[:2] + b) if len(b) == 2 else a
        return [a, b]
    m = re.search(r"\b(1[89]\d\d|20[012]\d)\b", title)
    ys = sorted(int(y) for y in re.findall(r"\b(19[0-9]\d|20[0-2]\d)\b", prose))
    if m and not ys:
        return [int(m.group(1))] * 2
    if not ys:
        return None
    lo = ys[int(len(ys) * 0.08)]
    hi = ys[min(len(ys) - 1, int(len(ys) * 0.85))]
    if m:
        lo = min(lo, int(m.group(1)))
    return [lo, hi]


def eras_of(years):
    a, b = years
    return [f"{d}s" for d in range(a // 10 * 10, b // 10 * 10 + 1, 10)]


def states_of(title, lede, prose):
    c = Counter()
    for st, abbrs in STATES.items():
        pat = re.escape(st)
        n = len(re.findall(rf"\b{pat}\b(?! City| Avenue| Street| Blvd| Boulevard| Road|, D\.C\.| Dragway| Street Rod| State Fair)", prose))
        if st == "Washington":
            n = len(re.findall(r"\bWashington\b(?=, |\.| state)(?!, D\.C\.)", prose))
        if st == "Virginia":
            n -= len(re.findall(r"West Virginia", prose))
        for ab in abbrs:
            n += len(re.findall(rf", {re.escape(ab)}(?=[\s,;:)]|$)", prose))
        c[st] = n
    for city, st in KNOWN_CITIES.items():
        c[st] += len(re.findall(rf"\b{re.escape(city)}\b", prose))
        if city == "Los Angeles":
            c[st] -= len(re.findall(r"East Los Angeles", prose))
    out = []
    top = max(c.values()) if c else 0
    for st, n in c.most_common():
        if n == 0:
            break
        tl = title + " " + lede
        intitle = (re.search(rf"\b{re.escape(st)}\b", tl) or any(f", {ab}" in tl for ab in STATES[st])
                   or any(re.search(rf"\b{re.escape(cy)}\b", tl) for cy, s2 in KNOWN_CITIES.items() if s2 == st))
        if intitle or (n >= 2 and n >= 0.3 * top):
            out.append(st)
    return out[:5]


def cities_of(title, lede, prose):
    abbr = {ab: st for st, abs_ in STATES.items() for ab in abs_}
    pats = "|".join(sorted([re.escape(s) for s in STATES] + [re.escape(a) for a in abbr], key=len, reverse=True))
    c = Counter()
    for m in re.finditer(rf"\b((?:[A-Z][a-z]+\.? ){{0,2}}[A-Z][a-z]+), ({pats})(?=[\s,;:.)]|$)", prose):
        city = m.group(1)
        if city in STATES or city.split()[0] in ("In", "At", "The", "Of", "And", "From", "To", "Near", "On", "By"):
            city = " ".join(city.split()[1:]) if city.split()[0] in ("In", "At", "The", "Of", "And", "From", "To", "Near", "On", "By") else city
        if not city or city in STATES:
            continue
        st = abbr.get(m.group(2), m.group(2))
        c[f"{city}, {st}"] += 1
    have = {k.split(",")[0] for k in c}
    for city, st in KNOWN_CITIES.items():
        if city in have or city in ("Muroc", "El Mirage", "Bonneville", "Bell"):
            continue
        n = len(re.findall(rf"\b{re.escape(city)}\b", prose))
        if city == "Los Angeles":
            n -= len(re.findall(r"East Los Angeles", prose))
        if n:
            c[f"{city}, {st}"] += n
    out = [k for k, n in c.most_common() if n >= 2 or k.split(",")[0] in title + " " + lede]
    return out[:6]


def tags_of(rel, prose, body):
    low = prose.lower()
    words = max(1, len(low.split()))
    sc = {}
    for tag, rx, need in TAG_RULES:
        n = len(re.findall(rx, low))
        if n >= need:
            sc[tag] = n / words * 1000
    tags = [t for t, _ in sorted(sc.items(), key=lambda kv: -kv[1])][:6]
    if 'class="hr-badge"' in body and "grassroots-sources" not in tags:
        tags.append("grassroots-sources")
    if rel.startswith("voices/") and "oral-history" not in tags:
        tags.insert(0, "oral-history")
    if rel.startswith("customs/") and "customs" not in tags:
        tags.insert(0, "customs")
    if rel.startswith("street-rodding/") and "street-rods" not in tags:
        tags.insert(0, "street-rods")
    return tags[:8] or ["car-clubs"]


def lede_summary(body):
    for p in re.split(r"\n\s*\n", body):
        s = p.strip()
        if not s or s.startswith(("#", "!!!", "<", "|", "-", ">", "—", "    ", "[^", "*Grassroots")) or len(plain(s)) < 90:
            continue
        if re.match(r"^\*?(Principal source|Owner:|Sources?:)", s):
            continue
        t = plain(s)
        sents = re.split(r"(?:(?<=[.!?])|(?<=[.!?][\"”]))\s+(?=[A-Z\"“])", t)
        out = sents[0]
        if len(out) < 110 and len(sents) > 1 and len(out + " " + sents[1]) <= 300:
            out += " " + sents[1]
        return out
    return ""


SUMMARIES = {}


def main():
    import yaml
    sf = DOCS.parent / "scripts" / "summaries_draft.yml"
    if sf.exists():
        SUMMARIES.update(yaml.safe_load(sf.read_text()) or {})
    write = "--write" in sys.argv
    only = None
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
        args = [a for a in args if a != sys.argv[sys.argv.index("--only") + 1]]
    files = [a[5:] if a.startswith("docs/") else a for a in args] or articles()
    rows = index_rows()
    titles = {}
    for rel in articles():
        _, b = split_front((DOCS / rel).read_text())
        m = re.search(r"^# (.+)$", b, re.M)
        titles[rel] = plain(m.group(1)) if m else rel
    canon = load_canonical()
    for rel in files:
        path = DOCS / rel
        text = path.read_text()
        meta, body = split_front(text)
        prose = plain(body_prose(re.sub(r'!!! abstract "Article record".*?(?=\n\S)', "", body, flags=re.S)))
        title = titles[rel]
        lede = lede_summary(body)
        d = {}
        d["title"] = title
        d["summary"] = SUMMARIES.get(rel) or lede
        d["department"] = rel.split("/")[0]
        yrs = years_of(title, prose)
        d["years"] = yrs
        d["eras"] = eras_of(yrs) if yrs else []
        sts = states_of(title, lede, prose)
        regs = Counter(REGION_OF.get(s) for s in sts)
        d["region"] = ("National" if len([r for r in regs if r]) >= 3 else (regs.most_common(1)[0][0] if sts else "National"))
        d["states"] = sts
        d["cities"] = cities_of(title, lede, prose)
        ppl, comp, clubs, strips, places = [], [], [], [], []
        for name, role, links in rows:
            if rel not in links:
                continue
            pn = None
            if " & " in name and name.count(",") == 2:
                for part in name.split(" & "):
                    q = person_name(part.strip())
                    if q:
                        ppl.append(q)
                continue
            pn = person_name(name)
            if pn:
                ppl.append(pn)
            elif CLUB.search(name):
                clubs.append(name)
            elif STRIP.search(name):
                strips.append(name)
            elif PLACE.search(name):
                places.append(name)
            else:
                comp.append(name)
        outl = Counter()
        for h in re.findall(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", body):
            tgt = str((path.parent / h).resolve().relative_to(DOCS.resolve())) if not h.startswith("http") else None
            if tgt and tgt in titles and tgt != rel:
                outl[tgt] += 1
                if tgt.startswith("people/"):
                    pn = re.split(r":| and | \(", titles[tgt])[0].strip().strip('"')
                    if pn and pn not in ppl and len(pn.split()) <= 4:
                        ppl.append(pn)
        if rel.startswith("people/"):
            me = re.split(r":| and | \(", title)[0].strip()
            if me and me not in ppl:
                ppl.insert(0, me)
        d["people"] = ppl[:15]
        d["companies"] = comp[:10]
        d["places"] = places[:8]
        d["clubs"] = clubs[:8]
        d["strips"] = strips[:8]
        d["tags"] = tags_of(rel, prose, body)
        d["related"] = [t for t, _ in outl.most_common(5)]
        d["canonical_for"] = [k for k, v in canon.items() if v.get("page") == rel]
        new = dict(meta)
        for k, v in d.items():
            if only and k not in only:
                continue
            if k in new and not only and new[k] not in (None, "", []):
                continue
            new[k] = v
        order = ["title", "summary", "department", "eras", "years", "region", "states", "cities", "people", "companies",
                 "places", "clubs", "strips", "tags", "related", "canonical_for"]
        ordered = {k: new[k] for k in order if k in new}
        ordered.update({k: v for k, v in new.items() if k not in ordered})
        if write:
            path.write_text(join_front(ordered, body))
        else:
            print(f"== {rel}\n   {ordered.get('summary')}\n   {ordered.get('years')} {ordered.get('region')} {ordered.get('states')} {ordered.get('cities')}\n   P:{ordered.get('people')}\n   C:{ordered.get('companies')} CL:{ordered.get('clubs')} S:{ordered.get('strips')} PL:{ordered.get('places')}\n   T:{ordered.get('tags')}\n   R:{ordered.get('related')}")


if __name__ == "__main__":
    main()
