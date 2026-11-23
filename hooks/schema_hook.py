"""JSON-LD for Organization, WebSite, BreadcrumbList, Article, and Place.

Place nodes are added only for drag-racing and places stories whose towns are in
docs/data/geo.yml (map_hook puts those points on hr.geo_places). Adventure Equity LLC
is not included here; the publisher name stays in the footer.
"""
import html
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

from mkdocs.exceptions import PluginError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_launch_seo  # noqa: E402


def _abs(config, url):
    base = (config.get("site_url") or "").rstrip("/") + "/"
    return urljoin(base, url or "")


def _text(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", str(value or "")))).strip()


def _verified(hr, context):
    rec = (hr or {}).get("record") or {}
    for key, val in rec.get("fields") or []:
        if str(key).lower() == "last verified":
            m = re.search(r"\d{4}-\d{2}-\d{2}", _text(val))
            if m:
                return m.group(0)
    built = (context.get("hr_site") or {}).get("built")
    if built is not None and hasattr(built, "isoformat"):
        return built.isoformat()
    return None


def build_ld(context, page, config):
    hr = context.get("hr") or {}
    kind = hr.get("kind") or ""
    if kind == "404" or page is None:
        return None
    base = (config.get("site_url") or "").rstrip("/") + "/"
    if not base.startswith("http"):
        return None
    org_id = base + "#organization"
    site_id = base + "#website"
    name = config.get("site_name") or "Hot Rodding History"
    desc = config.get("site_description") or ""
    logo = _abs(config, "assets/logo-512.png")
    graph = [
        {
            "@type": "Organization",
            "@id": org_id,
            "name": name,
            "url": base,
            "description": desc,
            "logo": {"@type": "ImageObject", "url": logo, "width": 512, "height": 512},
        },
        {
            "@type": "WebSite",
            "@id": site_id,
            "url": base,
            "name": name,
            "description": desc,
            "publisher": {"@id": org_id},
            "potentialAction": {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": base + "?q={search_term_string}"},
                "query-input": "required name=search_term_string",
            },
        },
    ]
    crumbs = list(hr.get("crumbs") or [])
    canonical = getattr(page, "canonical_url", None) or _abs(config, getattr(page, "url", "") or "")
    items = []
    for crumb in crumbs:
        label = _text(crumb.get("t"))
        if not label:
            continue
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": label, "item": _abs(config, crumb.get("u") or "")})
    page_name = _text(getattr(page, "title", "") or name)
    if not items or items[-1].get("item") != canonical:
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": page_name, "item": canonical})
    if kind != "home" and items:
        graph.append({"@type": "BreadcrumbList", "itemListElement": items})
    if kind == "story":
        meta = page.meta or {}
        article = {
            "@type": "Article",
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "headline": page_name,
            "description": _text(meta.get("description") or desc),
            "author": {"@id": org_id},
            "publisher": {"@id": org_id},
            "isAccessibleForFree": True,
            "isBasedOn": {"@type": "CreativeWork", "url": canonical.split("#", 1)[0] + "#hr-sources"},
        }
        image = hr.get("thumb") or hr.get("thumb_url") or "assets/og-default.png"
        article["image"] = image if str(image).startswith("http") else _abs(config, image)
        modified = _verified(hr, context)
        if modified:
            article["dateModified"] = modified
        about = []
        for place in hr.get("geo_places") or []:
            node = {
                "@type": "Place",
                "name": place["name"],
                "geo": {"@type": "GeoCoordinates", "latitude": place["lat"], "longitude": place["lon"]},
            }
            about.append(node)
        if about:
            article["about"] = about
        graph.append(article)
    return {"@context": "https://schema.org", "@graph": graph}


def on_page_context(context, page, config, nav):
    context["hr_ld"] = build_ld(context, page, config)
    return context


def on_post_build(config, **kwargs):
    errors = check_launch_seo.check(config["site_dir"])
    if errors:
        raise PluginError("Launch SEO check failed:\n  " + "\n  ".join(errors[:30]))
