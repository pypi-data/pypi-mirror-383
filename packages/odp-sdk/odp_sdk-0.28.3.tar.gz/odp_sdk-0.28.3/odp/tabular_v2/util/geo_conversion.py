from typing import Callable

import pyarrow as pa
import shapely


def has_geometry(schema: pa.Schema) -> str | list | None:
    """
    Returns the first field that is geometry, or a list of [lonfield, latfield] if both are found
    or None if no geometry fields are found
    """
    latfield = None
    lonfield = None
    for field in schema:
        meta = field.metadata or {}
        if b"isGeometry" in meta:
            return field.name
        if b"class" in meta:
            if meta[b"class"] == b"geometry":
                return field.name
            if meta[b"class"] == b"latitude":
                latfield = field.name
            elif meta[b"class"] == b"longitude":
                lonfield = field.name
    if latfield is not None and lonfield is not None:
        return [lonfield, latfield]
    return None


def geo_decoder(schema: pa.Schema) -> Callable[[dict], shapely.Geometry | None]:
    """
    Returns a function that decodes a row dict into a shapely geometry
    """
    lat_field, lon_field = None, None
    for field in schema:
        meta = field.metadata or {}
        if b"isGeometry" in meta:
            if pa.types.is_binary(field.type):

                def f(row) -> shapely.Geometry | None:
                    g = row[field.name]
                    del row[field.name]
                    if g is None:
                        return None
                    return shapely.from_wkb(g)

                return f
            if pa.types.is_string(field.type):

                def f(row) -> shapely.Geometry | None:
                    g = row[field.name]
                    del row[field.name]
                    if g is None:
                        return None
                    return shapely.from_wkt(g)

                return f
            raise ValueError(f"unsupported geometry type {field.type}")
        if b"class" in meta:
            if meta[b"class"] == b"latitude":
                lat_field = field.name
            elif meta[b"class"] == b"longitude":
                lon_field = field.name
    if lat_field is not None and lon_field is not None:

        def f(row) -> shapely.Geometry | None:
            lat, lon = row[lat_field], row[lon_field]
            # remove lat/lon fields from the properties
            del row[lat_field]
            del row[lon_field]
            if lat is None or lon is None:
                return None
            return shapely.Point(lon, lat)

        return f
    raise ValueError("no geometry field found")


def to_geodataframe(table: pa.Table):
    """
    Convert a pyarrow table to a GeoPandas geodataframe
    """
    try:
        import geopandas as gpd
    except Exception as e:
        raise ImportError("geopandas is required for to_geodataframe()") from e

    geom_spec = has_geometry(table.schema)
    if geom_spec is None:
        # geodf without active geometry
        return gpd.GeoDataFrame(table.to_pandas())

    decoder = geo_decoder(table.schema)
    rows = table.to_pylist()
    geoms = [decoder(r) for r in rows]

    df = table.to_pandas()

    if isinstance(geom_spec, str):
        drop_cols = [geom_spec] if geom_spec in df.columns else []
    elif isinstance(geom_spec, (list, tuple)) and len(geom_spec) == 2:
        drop_cols = [c for c in geom_spec if c in df.columns]
    else:
        drop_cols = []

    if drop_cols:
        df = df.drop(columns=drop_cols)

    return gpd.GeoDataFrame(df, geometry=geoms, crs="EPSG:4326")
