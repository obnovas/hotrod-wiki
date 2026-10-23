# us-atlas 3.0.1: states-albers-10m.json

The U.S. state shapes behind the [Story Map](../../docs/reference/story-map.md).

- **What it is:** U.S. state boundaries as TopoJSON, already projected to Albers USA (Alaska and Hawaii inset) in a 975 × 610 frame, at 1:10,000,000 detail.
- **From:** the npm package `us-atlas@3` by Mike Bostock (https://github.com/topojson/us-atlas), fetched from https://cdn.jsdelivr.net/npm/us-atlas@3/states-albers-10m.json on 2026-10-23.
- **Underlying data:** the U.S. Census Bureau's cartographic state boundaries, 2017 edition (https://www2.census.gov/geo/tiger/GENZ2017/shp/), a U.S. government work in the public domain.
- **Package licence:** ISC (see `LICENSE`), which allows use, copying and changes with the notice kept.

`hooks/map_hook.py` decodes this file at build time and writes the state outlines straight into the page as SVG. No map tiles, no third-party servers and no API keys are involved. Pins are placed with the same projection (`scripts/geo_lib.py: project`), which matches d3-geo's `geoAlbersUsa().scale(1300).translate([487.5, 305])`.
