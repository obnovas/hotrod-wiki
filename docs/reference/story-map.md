---
title: "The Story Map: Where It Happened"
description: An interactive map of the Hot Rod History Wiki. One pin for every town in the stories, filter by era and region, and see which states the archive covers, from the dry lakes to the Georgia drag strips.
search:
  boost: 2
---
# The Story Map: Where It Happened

*Every town in the archive, one pin each. Pick an era and watch the scene move.*

Hot rodding wasn't only a Southern California story, and this map shows it. Each pin is a town that a story is set in, and the number on a pin is how many stories are set there. States are shaded by how many stories touch them. Tap a pin for that town's stories, each with a one-line summary and a link to the full story. The era buttons show the stories that cover that decade, and the region buttons narrow the map to one part of the country.

<!-- hr:story-map -->

## How the pins are placed

- **One pin per town.** A pin stands at the town's Census Bureau internal point, from the [2024 Census Gazetteer](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html). For a few neighborhoods and named places that are not Census places, such as Van Nuys, Hollywood and the Bonneville Salt Flats, it comes from the USGS [Geographic Names Information System](https://www.usgs.gov/us-board-on-geographic-names/download-gnis-data). Both are public-domain federal datasets. We never take a point from memory or from a map app.
- **Strips and airports sit on their town.** A drag strip or an airport strip is pinned at the town it was in or near, not at a spot on the ground, unless an article gives the exact location. The sheet for each pin says which kind of point it is.
- **What isn't pinned.** Places outside the United States, districts with no federal gazetteer point (Toluca Lake, Shawnee Mission) and strips whose town our articles don't give are listed in `docs/data/geo.yml` with the reason. They are left off rather than guessed.
- **What counts toward a state.** A story counts for every state in its front matter, whether or not it has a pin there. A story about a national company counts in each state it names.
- **The map.** State outlines come from the Census Bureau's cartographic boundary files (2017), as packaged in [us-atlas](https://github.com/topojson/us-atlas), and they're drawn into the page itself. There are no map tiles, outside servers or tracking.

Something in the wrong place, or a town we missed? [Tell us](https://github.com/obnovas/hotrod-wiki/issues/new?template=suggestion-feedback.yml). For the stories by region, see [Regional Scenes](../places/regional-scenes.md). For the stories in time order, see the [Timeline](timeline.md).
