"""Overlap scoring between articles, from front matter. Shared by draft_frontmatter.py and hooks/linking_hook.py."""
GENERIC_TAGS = {"grassroots-sources", "oral-history", "car-clubs", "drag-strips", "magazines-and-media"}
W = {"people": 3.0, "companies": 3.0, "clubs": 3.0, "strips": 3.0, "places": 2.5, "cities": 2.0, "states": 0.6}


def _norm(v):
    return {str(x).strip().lower() for x in (v or [])}


def overlap(a, b):
    """Score and the shared entities (for a 'why related' line)."""
    s, why = 0.0, []
    for k, w in W.items():
        shared = _norm(a.get(k)) & _norm(b.get(k))
        if shared:
            s += w * len(shared)
            if k not in ("states",):
                why += sorted(shared)
    tags = (_norm(a.get("tags")) & _norm(b.get("tags"))) - GENERIC_TAGS
    s += 0.7 * len(tags)
    ea, eb = set(a.get("eras") or []), set(b.get("eras") or [])
    if ea & eb:
        s += 0.4
    if a.get("region") and a.get("region") == b.get("region") and a.get("region") != "National":
        s += 0.4
    return s, why


def rank(me_rel, metas, links_out=None, links_in=None, n=5):
    me = metas[me_rel]
    sc = {}
    for rel, m in metas.items():
        if rel == me_rel:
            continue
        s, _ = overlap(me, m)
        if links_out and rel in links_out:
            s += 2.0
        if links_in and rel in links_in:
            s += 1.5
        if rel in (me.get("related") or []):
            s += 4.0
        if s > 1.0:
            sc[rel] = s
    return sorted(sc, key=lambda r: (-sc[r], r))[:n]
