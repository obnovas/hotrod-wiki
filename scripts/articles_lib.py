"""Shared helpers for the article front-matter schema (see docs/reference/article-schema.md).

Used by scripts/check_articles.py (the build gate), scripts/draft_frontmatter.py (the drafting tool)
and hooks/linking_hook.py (related stories, backlinks, auto-links)."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

DEPARTMENTS = ["eras", "people", "companies", "cars", "customs", "street-rodding", "media", "drag-racing", "places", "voices"]
ERAS = ["1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
REGIONS = ["West", "Southwest", "Midwest", "South", "Northeast", "Northwest", "National"]

# Controlled vocabulary. Add a tag here (and to the schema page) before using it.
TAGS = {
    "drag-strips": "A drag strip: its founding, running or closing",
    "airport-strips": "Racing on airfields, air bases and runways",
    "car-clubs": "Hot rod and custom car clubs",
    "club-rules": "Club bylaws, fines, courtesy cards and codes of conduct",
    "police-and-safety": "Police, sheriffs, safety campaigns and courts",
    "town-politics": "Councils, county boards, ordinances, zoning and petitions",
    "street-racing": "Racing on public roads",
    "cruising": "Cruising, dragging Main and hangouts",
    "dry-lakes": "Muroc, El Mirage, Bonneville and land speed",
    "speed-equipment": "Speed parts makers and shops",
    "camshafts": "Cam grinders and cams",
    "aftermarket-business": "The parts business: catalogs, mail order, SEMA, buyouts",
    "customs": "Custom cars and customizers",
    "car-shows": "Car shows and show circuits",
    "street-rods": "The street rod movement, NSRA and the Nationals",
    "gassers": "Gas-class and door-slammer racing",
    "funny-cars": "Funny cars and altered-wheelbase cars",
    "dragsters": "Dragsters, diggers and slingshots",
    "sanctioning-bodies": "NHRA, AHRA, ATAA, SCTA and other bodies",
    "magazines-and-media": "Magazines, newspapers, books, kits and film",
    "women": "Women racers, club members and owners",
    "teenagers-and-schools": "Teen drivers, high schools and youth programs",
    "oral-history": "First-person recollections",
    "grassroots-sources": "Built mainly on local newspapers and other grassroots sources",
    "family-business": "Family-run shops and companies",
    "patents-and-inventions": "Patents and inventions",
    "fiberglass": "Fiberglass bodies and parts",
    "land-speed": "Land speed record attempts",
}

REQUIRED = ["title", "summary", "department", "eras", "years", "region", "tags", "related"]
LISTS = ["eras", "states", "cities", "people", "companies", "places", "clubs", "strips", "tags", "related", "canonical_for"]
# Record-box notes: short field lines and source notes shown inside the Article record box instead of opening the
# story. Markdown strings (footnote refs [^id], links and open-question markers allowed); principal_source may be a list.
RECORD_NOTES = [("location", "Location"), ("peak", "Peak"), ("status", "Status"), ("later", "Later"), ("revival", "Revival"),
                ("principal_source", "Principal source")]
KNOWN = set(REQUIRED + LISTS + ["template", "hide", "era", "hub", "deck", "featured", "no_hero", "search", "description"]
            + [k for k, _ in RECORD_NOTES])


def record_notes_text(meta):
    """The Markdown of the record-box note fields, one per line (so checks can treat it as part of the body)."""
    out = []
    for k, _ in RECORD_NOTES:
        v = (meta or {}).get(k)
        for x in (v if isinstance(v, list) else [v] if v else []):
            out.append(str(x))
    return "\n\n".join(out)

EXEMPT_PREFIXES = ("about/", "reference/", "data/", "assets/", "stylesheets/", "javascripts/")


def is_article(rel):
    """Department pages that are stories (not section fronts, not root or reference pages)."""
    rel = str(rel)
    if rel.startswith(EXEMPT_PREFIXES) or "/" not in rel or rel.endswith("/index.md"):
        return False
    return rel.split("/")[0] in DEPARTMENTS and rel.endswith(".md")


def articles():
    return sorted(str(p.relative_to(DOCS)) for p in DOCS.rglob("*.md") if is_article(p.relative_to(DOCS)))


def split_front(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            return yaml.safe_load(text[4:end]) or {}, text[end + 5:]
    return {}, text


def join_front(meta, body):
    return "---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000) + "---\n" + body.lstrip("\n")


def load_canonical():
    f = DOCS / "data" / "canonical.yml"
    return (yaml.safe_load(f.read_text()) or {}).get("facts", {}) if f.exists() else {}


def plain(t):
    t = re.sub(r"<sup class=\"hr-q\".*?</sup>", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[\^[^\]]+\]", "", t)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*_`]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def body_prose(body):
    """Body text without footnote definitions (for grounding checks)."""
    return "\n".join(l for l in body.split("\n") if not re.match(r"^\[\^[^\]]+\]:", l))
