from __future__ import annotations
from collections.abc import Callable
import logging
import math
import folium
import numpy as np
from scipy.spatial import SphericalVoronoi

from parkrun.models.event import Event

logger = logging.getLogger(__name__)

# Maximum angle in degrees between consecutive points when drawing the edges of
# Voronoi cells. Edges are great circle arcs, which aren't straight on the map,
# so they're drawn as many short straight lines.
VORONOI_EDGE_STEP_DEGREES: float = 0.5

# A GeoJSON ring: closed list of [long, lat] in degrees
Ring = list[list[float]]


def voronoi_layer(events: list[Event], colour: Callable[[Event], str]) -> folium.GeoJson:
    """
    A layer shading the area closest to each event in its colour, i.e. the
    spherical Voronoi diagram of the events. Events at the same location share a
    cell, coloured by the first one.
    """

    # Voronoi cells are per location, and SphericalVoronoi rejects duplicate
    # points, so keep only the first event at each location
    event_by_location: dict[tuple[float, float], Event] = {}
    for event in events:
        if (event.lat, event.long) not in event_by_location:
            event_by_location[event.lat, event.long] = event

    features: list[dict] = []

    # SphericalVoronoi needs at least 4 points not all on one great circle
    if len(event_by_location) < 4:
        logger.warning("Too few event locations to draw a Voronoi diagram")
    else:
        for event, rings in zip(event_by_location.values(), voronoi_cells(list(event_by_location))):
            features.append({
                "type": "Feature",
                "properties": {"colour": colour(event)},
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [[ring] for ring in rings],
                },
            })

    return folium.GeoJson(
        {"type": "FeatureCollection", "features": features},
        style_function=lambda feature: {
            "fillColor": feature["properties"]["colour"],
            "fillOpacity": 0.2,
            "color": "white",
            "weight": 1,
            "opacity": 1,
        },
        # Don't capture mouse events meant for the map or markers
        interactive=False,
    )


def voronoi_cells(locations: list[tuple[float, float]]) -> list[list[Ring]]:
    """
    The spherical Voronoi diagram of the given unique (lat, long) locations in
    degrees: for each location, the area closer to it than any other by great
    circle distance. Needs at least 4 locations not all on one great circle.

    Each cell is given as rings to draw on a Leaflet map. Leaflet only draws a
    polygon where its coordinates are, so rather than splitting cells that
    cross the antimeridian, each is a copy of the same ring shifted by each
    whole turn of longitude that overlaps [-180, 180]. The cells containing
    the poles are instead one ring stretching across the whole map.
    """

    # Convert to 3D points on the unit sphere (x towards (0, 0), y towards
    # (0, 90) and z towards the north pole). The great circle distance between
    # two unit vectors is the angle between them, arccos of their dot product,
    # so the closest location to any point is the one with the largest dot
    # product with it.
    lat_long = np.radians(np.array(locations))
    points = np.column_stack([
        np.cos(lat_long[:, 0]) * np.cos(lat_long[:, 1]),
        np.cos(lat_long[:, 0]) * np.sin(lat_long[:, 1]),
        np.sin(lat_long[:, 0]),
    ])
    # sv.vertices are the corners of all the cells: unit vectors equally far
    # from the 3 or more closest locations. sv.regions[i] lists the indices of
    # the corners of the cell of points[i], which start in no particular order
    # until sorted to go round the cell.
    sv = SphericalVoronoi(points)
    sv.sort_vertices_of_regions()
    # The dot product with the north pole (0, 0, 1) is just z, so the location
    # closest to it (and whose cell contains it) has the largest z
    north_index: int = int(np.argmax(points[:, 2]))
    south_index: int = int(np.argmin(points[:, 2]))

    return [
        _cell_rings(sv.vertices[region], centre_long, 90 if i == north_index else -90 if i == south_index else None)
        for i, ((_, centre_long), region) in enumerate(zip(locations, sv.regions))
    ]


def _cell_rings(vertices: np.ndarray, centre_long: float, pole: float | None) -> list[Ring]:
    """
    Convert the vertices of a spherical polygon (unit vectors in order around
    it) into closed GeoJSON rings of [long, lat] in degrees, following the
    great circle arcs between them, that together cover it on the map
    [-180, 180]. Longitudes are kept continuous rather than wrapped into
    [-180, 180], starting near the given longitude, so a ring may cross the
    antimeridian. If the polygon contains a pole, give its latitude (90 or
    -90) so the ring can go round the edge of the map via it.
    """

    # Points along each edge, excluding its end which starts the next edge.
    # Pairing each vertex with the next (rolled round so the last pairs with
    # the first) gives every edge.
    points: list[np.ndarray] = []
    for start, end in zip(vertices, np.roll(vertices, -1, axis=0)):
        # Clip as rounding can take the dot product just outside arccos's domain
        angle: float = float(np.arccos(np.clip(np.dot(start, end), -1, 1)))
        steps: int = max(1, int(np.ceil(np.degrees(angle) / VORONOI_EDGE_STEP_DEGREES)))
        for t in np.arange(steps) / steps:
            if angle == 0:
                # Two corners at the same place, where 4 or more cells meet
                points.append(start)
            else:
                # Spherical linear interpolation (slerp): the point a fraction
                # t of the way along the great circle arc from start to end.
                # Unlike interpolating in a straight line, it stays on the
                # sphere and moves at a constant speed.
                points.append((np.sin((1 - t) * angle) * start + np.sin(t * angle) * end) / np.sin(angle))

    ring: Ring = []
    for x, y, z in points:
        lat: float = float(np.degrees(np.arcsin(np.clip(z, -1, 1))))
        long: float = float(np.degrees(np.arctan2(y, x)))
        # Unwrap: arctan2 gives [-180, 180], so a ring crossing the
        # antimeridian would jump from 179 to -179 and be drawn the long way
        # round the world. Instead, add the whole number of turns that brings
        # it closest to (within 180 degrees of) the previous longitude.
        previous: float = ring[-1][0] if ring else centre_long
        long += 360 * round((previous - long) / 360)
        ring.append([long, lat])

    first_long, first_lat = ring[0]
    turn: float = 360 * round((ring[-1][0] - first_long) / 360)
    if pole is not None and turn != 0:
        # Going round a pole, the longitude ends a whole turn away from where
        # it started, so the edge repeats every turn along the map. On the
        # map, the pole is the whole top (or bottom) edge, so the cell is the
        # area between the edge and it. Copies of the ring side by side would
        # have their outlines drawn down from the pole where they meet,
        # splitting the cell in two, so instead make one ring that repeats the
        # edge enough to cross the whole map, then closes by going straight up
        # to the pole, along it back, and down to the start, outside the map.
        # Leaflet clips latitudes to about 85 degrees, where its (Web
        # Mercator) map ends.
        if turn < 0:
            # Go round the other way so the longitude increases
            ring = [[first_long + turn, first_lat]] + ring[:0:-1]
            first_long += turn
        # The edge starts at first_long + 360 * turns and ends a turn later,
        # so start at or left of -180 and end at or right of 180
        turns_range = range(math.floor((-180 - first_long) / 360), math.ceil((180 - first_long) / 360))
        ring = [[long + 360 * turns, lat] for turns in turns_range for long, lat in ring]
        start_long: float = ring[0][0]
        end_long: float = first_long + 360 * turns_range.stop
        ring += [[end_long, first_lat], [end_long, pole], [start_long, pole], ring[0]]
        return [ring]

    ring.append(ring[0])
    # Shifting the ring by 360 * turns overlaps [-180, 180] when
    # min + 360 * turns <= 180 and max + 360 * turns >= -180
    longs: list[float] = [long for long, _ in ring]
    return [
        [[long + 360 * turns, lat] for long, lat in ring]
        for turns in range(
            math.ceil((-180 - max(longs)) / 360),
            math.floor((180 - min(longs)) / 360) + 1,
        )
    ]
