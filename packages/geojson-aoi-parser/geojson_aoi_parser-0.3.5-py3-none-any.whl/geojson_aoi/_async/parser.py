# Copyright (c) Humanitarian OpenStreetMap Team
# This file is part of geojson-aoi-parser.
#
#     geojson-aoi-parser is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     geojson-aoi-parser is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with geojson-aoi-parser.  If not, see <https:#www.gnu.org/licenses/>.
#

"""Parse various AOI GeoJSON formats and normalize."""

import json
import logging
import warnings
from pathlib import Path

from psycopg import AsyncConnection

from geojson_aoi._async.postgis import AsyncPostGis
from geojson_aoi.types import Feature, FeatureCollection, GeoJSON

AllowedInputTypes = [
    "Polygon",
    "MultiPolygon",
    "Feature",
    "FeatureCollection",
    "GeometryCollection",
]

log = logging.getLogger(__name__)


def check_crs(geojson: GeoJSON) -> None:
    """Warn the user if an invalid CRS is detected.

    Also does a rough check for one geometry, to determine if the
    coordinates are range 90/180 degree range.

    Args:
        geojson (GeoJSON): a GeoJSON.

    Returns:
        None
    """

    def is_valid_crs(crs_name: str) -> bool:
        valid_crs_list = [
            "urn:ogc:def:crs:OGC:1.3:CRS84",
            "urn:ogc:def:crs:EPSG::4326",
            "WGS 84",
        ]
        return crs_name in valid_crs_list

    def is_valid_coordinate(coord: list[float]) -> bool:
        return len(coord) == 2 and -180 <= coord[0] <= 180 and -90 <= coord[1] <= 90

    crs = geojson.get("crs", {}).get("properties", {}).get("name")
    if crs and not is_valid_crs(crs):
        warning_msg = (
            "Unsupported coordinate system. Use WGS84 (EPSG 4326) for best results."
        )
        log.warning(warning_msg)
        warnings.warn(UserWarning(warning_msg), stacklevel=2)

    geom = {}
    if "geometry" in geojson and geojson.get("geometry") is not None:
        geom = geojson.get("geometry", {})
    else:
        features = geojson.get("features", [])
        if features:
            geom = features[-1].get("geometry", {}) or {}
        else:
            geom = {}

    coordinates = geom.get("coordinates", [])

    # Drill down into nested coordinates to find the first coordinate
    # Guard against empty coordinate lists
    while (
        isinstance(coordinates, list)
        and len(coordinates) > 0
        and isinstance(coordinates[0], list)
    ):
        coordinates = coordinates[0]

    if (
        not isinstance(coordinates, list)
        or not coordinates
        or not is_valid_coordinate(coordinates)
    ):
        warning_msg = "Invalid coordinates in GeoJSON. Ensure the file is not empty."
        log.warning(warning_msg)
        warnings.warn(UserWarning(warning_msg), stacklevel=2)


def strip_featcol(geojson_obj: GeoJSON | Feature | FeatureCollection) -> list[GeoJSON]:
    """Remove FeatureCollection and Feature wrapping.

    Args:
        geojson_obj (dict): a parsed geojson.

    Returns:
        list[GeoJSON]: a list of geometries.
    """
    if geojson_obj.get("crs"):
        # Warn the user if invalid CRS detected
        check_crs(geojson_obj)

    geojson_type = geojson_obj.get("type")

    # Helper to create polygon from a sequence of coordinates (for MultiPolygon)
    def polygon_from_coords(coords):
        return {"type": "Polygon", "coordinates": coords}

    if geojson_type == "FeatureCollection":
        geoms = []
        for feature in geojson_obj.get("features", []):
            geom = feature.get("geometry", {})
            if not geom:
                continue

            gtype = geom.get("type")
            if gtype == "GeometryCollection":
                # extend with contained geometries
                for item in geom.get("geometries", []):
                    if item:
                        geoms.append(item)
            elif gtype == "MultiPolygon":
                # split MultiPolygon into separate Polygons
                for coordinate in geom.get("coordinates", []):
                    geoms.append(polygon_from_coords(coordinate))
            else:
                geoms.append(geom)

    elif geojson_type == "Feature":
        geoms = [geojson_obj.get("geometry")]

    elif geojson_type == "GeometryCollection":
        geoms = geojson_obj.get("geometries", [])

    elif geojson_type == "MultiPolygon":
        # MultiPolygon should parse out into List of Polygons and maintain properties.
        temp_geoms = []
        for coordinate in geojson_obj.get("coordinates", []):
            temp_geoms.append({"type": "Polygon", "coordinates": coordinate})

        geoms = temp_geoms

    else:
        geoms = [geojson_obj]

    return geoms


async def parse_aoi_async(
    db: str | AsyncConnection, geojson_raw: str | bytes | dict, merge: bool = False
) -> FeatureCollection:
    """Parse a GeoJSON file or data struc into a normalized FeatureCollection.

    Args:
        db (str | AsyncConnection): Existing db connection, or connection string.
        geojson_raw (str | bytes | dict): GeoJSON file path, JSON string, dict,
            or file bytes.
        merge (bool): If any nested Polygons / MultiPolygon should be merged.

    Returns:
        FeatureCollection: a FeatureCollection.
    """
    # We want to maintain this list for input control.
    valid_geoms = ["Polygon", "MultiPolygon", "GeometryCollection"]

    # Parse different input types
    if isinstance(geojson_raw, bytes):
        geojson_parsed = json.loads(geojson_raw)

    elif isinstance(geojson_raw, str):
        if Path(geojson_raw).exists():
            log.debug(f"Parsing geojson file: {geojson_raw}")
            with open(geojson_raw, "rb") as geojson_file:
                geojson_parsed = json.load(geojson_file)
        else:
            geojson_parsed = json.loads(geojson_raw)

    elif isinstance(geojson_raw, dict):
        geojson_parsed = geojson_raw
    else:
        raise ValueError("GeoJSON input must be a valid dict, str, or bytes")

    # Throw error if no data
    if geojson_parsed is None or geojson_parsed == {} or "type" not in geojson_parsed:
        raise ValueError("Provided GeoJSON is empty")

    # Throw error if wrong geometry type
    if geojson_parsed["type"] not in AllowedInputTypes:
        raise ValueError(f"The GeoJSON type must be one of: {AllowedInputTypes}")

    # Store properties in formats that contain them.
    properties = []
    if (
        geojson_parsed.get("type") == "Feature"
        and geojson_parsed.get("geometry")
        and geojson_parsed.get("geometry").get("type") in valid_geoms
    ):
        properties.append(geojson_parsed.get("properties"))

    elif geojson_parsed.get("type") == "FeatureCollection":
        for feature in geojson_parsed.get("features", []):
            geom = feature.get("geometry", {})
            gtype = geom.get("type")
            # Append a copy of the properties list for each coordinate set
            # in the MultiPolygon. This ensures the split Polygons maintain
            # these properties.
            if gtype == "MultiPolygon":
                for _coordinate in geom.get("coordinates", []):
                    properties.append(feature.get("properties"))
            elif gtype in valid_geoms:
                properties.append(feature.get("properties"))

    # The same MultiPolygon handling as before.
    # But applied to top-level MultiPolygons.
    elif geojson_parsed.get("type") == "MultiPolygon":
        # If the top-level MultiPolygon object carries properties,
        # reuse them for each polygon.
        top_props = geojson_parsed.get("properties")
        for _coordinate in geojson_parsed.get("coordinates", []):
            properties.append(top_props)

    # Extract from FeatureCollection (or other types) into a
    # list of Polygon geometries
    geoms = strip_featcol(geojson_parsed)

    # Strip away any geom type that isn't a Polygon
    geoms = [geom for geom in geoms if geom and geom.get("type") == "Polygon"]

    async with AsyncPostGis(db, geoms, merge) as result:
        # Remove any properties that AsyncPostGIS might have assigned.
        for feature in result.featcol["features"]:
            feature.pop("properties", None)

        # Restore saved properties.
        if properties:
            feat_count = 0
            for feature in result.featcol["features"]:
                # Guard: only assign if we have a corresponding saved
                # property entry.
                if feat_count < len(properties):
                    feature["properties"] = properties[feat_count]
                else:
                    # If for some reason counts mismatch, set to
                    # None rather than crashing.
                    feature["properties"] = None
                feat_count += 1

        return result.featcol
