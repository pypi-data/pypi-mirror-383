from collections import OrderedDict
import copy
import datetime
import logging
from typing import Optional

import numpy as np
import numpy.ma as ma
from pyproj import CRS
import pystac
from pystac.version import get_stac_version
from shapely.geometry import box, mapping

from mapchete.errors import ReprojectionFailed
from mapchete.io import MPath
from mapchete.io.raster import write_raster_window
from mapchete.geometry import reproject_geometry
from mapchete.tile import BufferedTilePyramid
from mapchete.bounds import Bounds

logger = logging.getLogger(__name__)

OUT_PIXEL_SIZE = 0.28e-3
UNIT_TO_METER = {"mercator": 1, "geodetic": 111319.4907932732}
KNOWN_MATRIX_PROPERTIES = {
    "geodetic": {
        "name": "WorldCRS84Quad",
        "url": "http://schemas.opengis.net/tms/1.0/json/examples/WorldCRS84Quad.json",
        "title": "CRS84 for the World",
        "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
        "supportedCRS": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
        "wellKnownScaleSet": "http://www.opengis.net/def/wkss/OGC/1.0/GoogleCRS84Quad",
    },
    "mercator": {
        "name": "WebMercatorQuad",
        "url": "http://schemas.opengis.net/tms/1.0/json/examples/WebMercatorQuad.json",
        "title": "Google Maps Compatible for the World",
        "crs": "http://www.opengis.net/def/crs/EPSG/0/3857",
        "supportedCRS": "http://www.opengis.net/def/crs/EPSG/0/3857",
        "wellKnownScaleSet": "http://www.opengis.net/def/wkss/OGC/1.0/GoogleMapsCompatible",
    },
}


def tile_directory_stac_item(
    item_id=None,
    tile_pyramid=None,
    zoom_levels=None,
    item_path=None,
    asset_basepath=None,
    relative_paths=False,
    item_metadata=None,
    bounds=None,
    bounds_crs=None,
    bands_type="image/tiff; application=geotiff",
    band_asset_template="{zoom}/{row}/{col}.tif",
    crs_unit_to_meter=1,
):
    """
    Create STAC item from a Tile Directory using the tiled-assets.

    Currently only works for one asset.

    Parameters
    ----------
    item_id : str
        Unique item ID. (required)
    tile_pyramid : mapchete.tile.BufferedTilePyramid
        Tile pyramid of tiled asset. (required)
    zoom_levels : list
        List of zoom levels. (required)
    item_path : str
        Path of stac item.
    asset_basepath : str
        Base path of asset.
    relative_paths : bool
        Interpret asset path schema as being relative to item. If not set, one of item_path
        or asset_basepath has to be set. (default: False)
    item_metadata : dict
        Optional additional item metadata to be appended.
    bounds : list or tuple
        Tile directory bounds. (default: tile_pyramid.bounds)
    bounds_crs : CRS
        CRS of bounds. (default: tile_pyramid.crs)
    bands_type : str
        Media typ of tile directory tiles. (default: "image/tiff; application=geotiff")
    crs_unit_to_meter : int or float
        Factor to convert CRS units to meter if tile pyramid grid is not "geodetic" or "mercator". (default: 1)

    Returns
    -------
    pystac.Item
    """
    if item_id is None:
        raise ValueError("item_id must be set")
    if zoom_levels is None:
        raise ValueError("zoom_levels must be set")
    if tile_pyramid is None:
        raise ValueError("tile_pyramid must be set")

    asset_basepath = MPath.from_inp(asset_basepath) if asset_basepath else None
    item_path = MPath.from_inp(item_path) if item_path else None

    if item_path in ["./", "."]:
        item_path = item_path.absolute_path().joinpath(f"{item_id}.json")

    item_metadata = _cleanup_datetime(item_metadata or {})
    timestamp = (
        item_metadata.get("properties", {}).get("start_datetime")
        or item_metadata.get("properties", {}).get("end_datetime")
        or str(datetime.datetime.now(datetime.timezone.utc))
    )
    tp_grid = tile_pyramid.grid.type

    # thumbnail_href = thumbnail_href or "0/0/0.tif"
    # thumbnail_type = thumbnail_type or "image/tiff; application=geotiff"
    # replace zoom, row and col names with STAC tiled-assets definition
    band_asset_template = (
        band_asset_template.replace("{zoom}", "{TileMatrix}")
        .replace("{row}", "{TileRow}")
        .replace("{col}", "{TileCol}")
        .replace("{extension}", "tif")
    )
    if asset_basepath:
        band_asset_template = asset_basepath / band_asset_template
    elif not relative_paths:
        if item_path is None:
            raise ValueError("either alternative_basepath or item_path must be set")
        band_asset_template = item_path.parent / band_asset_template

    # use bounds provided or fall back to tile pyramid bounds
    bounds = bounds or tile_pyramid.bounds
    bounds_crs = bounds_crs or tile_pyramid.crs

    # bounds in tilepyramid CRS
    tp_bbox = reproject_geometry(
        box(*bounds), src_crs=bounds_crs, dst_crs=tile_pyramid.crs
    )
    # make sure bounds are not outside tile pyramid bounds
    left, bottom, right, top = tp_bbox.bounds
    left = tile_pyramid.left if left < tile_pyramid.left else left
    bottom = tile_pyramid.bottom if bottom < tile_pyramid.bottom else bottom
    right = tile_pyramid.right if right > tile_pyramid.right else right
    top = tile_pyramid.top if top > tile_pyramid.top else top

    try:
        # bounds in lat/lon
        geometry_4326 = reproject_geometry(
            box(*bounds), src_crs=bounds_crs, dst_crs="EPSG:4326"
        )
    except ReprojectionFailed as exc:  # pragma: no cover
        raise ReprojectionFailed(
            f"cannot reproject geometry to EPSG:4326 required by STAC: {str(exc)}"
        )
    bounds_4326 = [*geometry_4326.bounds]

    # tiles:tile_matrix_set object:
    # http://schemas.opengis.net/tms/1.0/json/tms-schema.json
    if tp_grid in KNOWN_MATRIX_PROPERTIES:
        tile_matrix_set_identifier = KNOWN_MATRIX_PROPERTIES[tp_grid]["name"]
        crs = KNOWN_MATRIX_PROPERTIES[tp_grid]["crs"]
        tile_matrix_set = {
            "type": "TileMatrixSetType",
            "title": KNOWN_MATRIX_PROPERTIES[tp_grid]["title"],
            "identifier": tile_matrix_set_identifier,
            "supportedCRS": KNOWN_MATRIX_PROPERTIES[tp_grid]["supportedCRS"],
            "wellKnownScaleSet": KNOWN_MATRIX_PROPERTIES[tp_grid]["wellKnownScaleSet"],
        }
    else:
        tile_matrix_set_identifier = "custom"  # ???
        if tile_pyramid.crs.to_authority() is None:  # pragma: no cover
            # try with pyproj
            crs = CRS.from_string(tile_pyramid.crs.to_string())
            if crs.to_authority() is None:
                raise ValueError("cannot convert SRS to urn string")
            else:
                authority, code = crs.to_authority()
        else:
            authority, code = tile_pyramid.crs.to_authority()
        crs = f"urn:ogc:def:crs:{authority}::{code}"
        # from http://schemas.opengis.net/tms/1.0/json/tms-schema.json
        # "required": ["type", "identifier", "supportedCRS", "tileMatrix"],
        tile_matrix_set = {
            "type": "TileMatrixSetType",
            "identifier": tile_matrix_set_identifier,
            "supportedCRS": crs,
        }
    tile_matrix_set.update(
        tileMatrix=[
            {
                "type": "TileMatrixType",
                "identifier": str(zoom),
                "scaleDenominator": _scale(
                    tp_grid,
                    tile_pyramid.pixel_x_size(zoom),
                    default_unit_to_meter=crs_unit_to_meter,
                ),
                "topLeftCorner": [tile_pyramid.bounds.left, tile_pyramid.bounds.top],
                "tileWidth": tile_pyramid.tile_width(zoom),
                "tileHeight": tile_pyramid.tile_height(zoom),
                "matrixWidth": tile_pyramid.matrix_width(zoom),
                "matrixHeight": tile_pyramid.matrix_height(zoom),
            }
            for zoom in zoom_levels
        ],
        boundingBox={
            "type": "BoundingBoxType",
            "crs": crs,
            "lowerCorner": [tile_pyramid.bounds.left, tile_pyramid.bounds.bottom],
            "upperCorner": [tile_pyramid.bounds.right, tile_pyramid.bounds.top],
        },
    )

    # tiles:tile_matrix_links object:
    tile_matrix_links = {
        "url": f"#{tile_matrix_set_identifier}",
        "limits": {
            str(zoom): {
                "min_tile_col": tile_pyramid.tile_from_xy(
                    left, top, zoom, on_edge_use="rb"
                ).col,
                "max_tile_col": tile_pyramid.tile_from_xy(
                    right, bottom, zoom, on_edge_use="lt"
                ).col,
                "min_tile_row": tile_pyramid.tile_from_xy(
                    left, top, zoom, on_edge_use="rb"
                ).row,
                "max_tile_row": tile_pyramid.tile_from_xy(
                    right, bottom, zoom, on_edge_use="lt"
                ).row,
            }
            for zoom in zoom_levels
        },
    }

    stac_extensions = [
        # official schema since STAC 1.0.0
        "https://stac-extensions.github.io/tiled-assets/v1.0.0/schema.json",
    ]
    if "eo:bands" in item_metadata:
        stac_extensions.append(
            "https://stac-extensions.github.io/eo/v1.1.0/schema.json"
        )

    out = {
        "stac_version": get_stac_version(),
        "stac_extensions": stac_extensions,
        "id": item_id,
        "type": "Feature",
        "bbox": bounds_4326,
        "geometry": mapping(geometry_4326),
        "properties": {
            **item_metadata.get("properties", {}),
            "datetime": timestamp,
            "collection": item_id,
            "tiles:tile_matrix_links": {tile_matrix_set_identifier: tile_matrix_links},
            "tiles:tile_matrix_sets": {tile_matrix_set_identifier: tile_matrix_set},
        },
        "asset_templates": {
            "bands": {
                "href": str(MPath(band_asset_template).absolute_path()),
                "type": bands_type,
            }
        },
        "assets": {
            # "thumbnail": {
            #     "href": thumbnail_href,
            #     "title": "Overview of the whole tiled dataset.",
            #     "type": thumbnail_type,
            # }
        },
    }
    if "eo:bands" in item_metadata:
        out["asset_templates"]["bands"]["eo:bands"] = item_metadata["eo:bands"]
        # out["assets"]["thumbnail"]["eo:bands"] = item_metadata["eo:bands"]
    out["links"] = item_metadata.get("links", [])
    if item_path and relative_paths is not True:
        out["links"].extend([{"rel": "self", "href": str(item_path)}])
        self_href = next(
            (link["href"] for link in out["links"] if link["rel"] == "self"), None
        )
        out_item = pystac.read_dict(out, href=self_href)
    elif item_path and relative_paths is True:
        out["links"].extend([{"rel": "self", "href": str(item_path.name)}])
        # For the read_dict pystac function as it needs the param to out proper self path
        self_href = next(
            (link["href"] for link in out["links"] if link["rel"] == "self"), None
        )
        out_item = make_stac_item_relative(pystac.read_dict(out, href=self_href))
    else:
        out_item = pystac.read_dict(out)

    return out_item


def _scale(grid, pixel_x_size, default_unit_to_meter=1):
    return (
        UNIT_TO_METER.get(grid, default_unit_to_meter) * pixel_x_size / OUT_PIXEL_SIZE
    )


def _cleanup_datetime(d):
    """Convert datetime objects in dictionary to strings."""
    return OrderedDict(
        (k, _cleanup_datetime(v))
        if isinstance(v, dict)
        else (k, str(v))
        if isinstance(v, datetime.date)
        else (k, v)
        for k, v in d.items()
    )


def update_tile_directory_stac_item(
    item_id=None,
    tile_pyramid=None,
    item_path=None,
    zoom_levels=None,
    item=None,
    bounds=None,
    item_metadata=None,
    bands_type=None,
    band_asset_template="{TileMatrix}/{TileRow}/{TileCol}.tif",
    crs_unit_to_meter=1,
):
    """
    Create STAC item from a Tile Directory using the tiled-assets.

    Currently only works for one asset.

    Parameters
    ----------
    item_id : str
        Unique item ID. (required)
    tile_pyramid : mapchete.tile.BufferedTilePyramid
        Tile pyramid of tiled asset. (required)
    item_path : str
        Path of stac item.
    zoom_levels : list
        List of zoom levels. (required)
    item : pystac.Item
        Existing Item to be extended. (optional)
    asset_basepath : str
        Base path of asset.
    relative_paths : bool
        Interpret asset path schema as being relative to item. If not set, one of item_path
        or asset_basepath has to be set. (default: False)
    item_metadata : dict
        Optional additional item metadata to be appended.
    bounds : list or tuple
        Tile directory bounds. (default: tile_pyramid.bounds)
    bounds_crs : CRS
        CRS of bounds. (default: tile_pyramid.crs)
    bands_type : str
        Media typ of tile directory tiles. (default: "image/tiff; application=geotiff")
    crs_unit_to_meter : int or float
        Factor to convert CRS units to meter if tile pyramid grid is not "geodetic" or "mercator". (default: 1)

    Returns
    -------
    pystac.Item
    """
    item_path = MPath.from_inp(item_path) if item_path else None
    # from existing item
    if item is not None:
        zoom_levels = zoom_levels or []
        zoom_levels = sorted(list(set(zoom_levels + zoom_levels_from_item(item))))
        existing_tile_pyramid = tile_pyramid_from_item(item)
        if tile_pyramid and tile_pyramid != existing_tile_pyramid:
            raise TypeError(
                "existing tile pyramid definition differs from new tile pyramid definition"
            )
        tile_pyramid = tile_pyramid or existing_tile_pyramid

        # merge bounds
        existing_bounds = Bounds(*item.bbox)
        if bounds:
            bounds = Bounds(
                left=min(bounds.left, existing_bounds.left),
                bottom=min(bounds.bottom, existing_bounds.bottom),
                right=max(bounds.right, existing_bounds.right),
                top=max(bounds.top, existing_bounds.top),
            )
        else:
            bounds = existing_bounds

        # other properties
        item_id = item_id or item.id

    return tile_directory_stac_item(
        item_id=item_id,
        tile_pyramid=tile_pyramid,
        zoom_levels=zoom_levels,
        item_path=item_path,
        asset_basepath=item_path.parent if item_path else None,
        relative_paths=True,
        item_metadata=item_metadata,
        bounds=bounds,
        bands_type=bands_type,
        band_asset_template=band_asset_template,
        crs_unit_to_meter=crs_unit_to_meter,
    )


def tile_pyramid_from_item(item):
    matrix_sets = item.properties.get("tiles:tile_matrix_sets")
    if matrix_sets:
        # find out grid
        wkss = next(iter(matrix_sets.keys()))
        for grid, properties in KNOWN_MATRIX_PROPERTIES.items():
            if properties["name"] == wkss:
                break
        else:
            raise ValueError(f"STAC tiled-assets WKSS not known: {wkss}")
        matrix_set = matrix_sets[wkss]

        # find out metatiling
        metatiling_opts = [2**x for x in range(10)]
        matching_metatiling_opts = []
        for metatiling in metatiling_opts:
            tp = BufferedTilePyramid(grid, metatiling=metatiling)
            for tile_matrix in matrix_set.get("tileMatrix", []):
                zoom = int(tile_matrix.get("identifier"))
                matrix_width = tile_matrix.get("matrixWidth")
                matrix_height = tile_matrix.get("matrixHeight")
                tile_width = tile_matrix.get("tileWidth")
                tile_height = tile_matrix.get("tileHeight")
                if (
                    matrix_width == tp.matrix_width(zoom)
                    and matrix_height == tp.matrix_height(zoom)
                    and tile_width == tp.tile_width(zoom)
                    and tile_height == tp.tile_height(zoom)
                ):
                    continue
                else:
                    break
            else:
                matching_metatiling_opts.append(metatiling)
        logger.debug("possible metatiling settings: %s", matching_metatiling_opts)
        if len(matching_metatiling_opts) == 0:  # pragma: no cover
            raise ValueError("cannot determine metatiling setting")
        elif len(matching_metatiling_opts) == 1:
            metatiling = matching_metatiling_opts[0]
        else:
            metatiling = sorted(matching_metatiling_opts)[0]
            logger.warning(
                "multiple possible metatiling settings found, chosing %s", metatiling
            )

        # TODO find out pixelbuffer

        return BufferedTilePyramid(grid, metatiling=metatiling)
    else:
        raise AttributeError("STAC item does have tile matrix sets defined")


def zoom_levels_from_item(item):
    matrix_sets = item.properties.get("tiles:tile_matrix_sets")
    if matrix_sets:
        matrix_set = next(iter(matrix_sets.values()))
        zoom_levels = []
        for tile_matrix in matrix_set.get("tileMatrix", []):
            try:
                zoom_levels.append(int(tile_matrix.get("identifier")))
            except ValueError:  # pragma: no cover
                logger.warning(
                    "cannot convert tile_matrix identifier %s into zoom level",
                    tile_matrix.get("identifier"),
                )
                continue
        return zoom_levels
    else:
        raise AttributeError("STAC item does have tile matrix sets defined")


def create_prototype_files(mp):
    # for each zoom level get tile output for 0/0
    for zoom in mp.config.init_zoom_levels:
        prototype_tile = mp.config.output_pyramid.tile(zoom, 0, 0)
        tile_path = mp.config.output.get_path(prototype_tile)
        # if tile exists, skip
        if tile_path.exists():
            logger.debug("prototype tile %s already exists", tile_path)
        # if not, write empty tile
        else:
            logger.debug("creating prototype tile %s", tile_path)
            out_profile = mp.config.output.profile(prototype_tile)
            tile_path.parent.makedirs()
            write_raster_window(
                in_grid=prototype_tile,
                in_data=ma.masked_array(
                    data=np.full(
                        (out_profile["count"],) + prototype_tile.shape,
                        out_profile["nodata"],
                        dtype=out_profile["dtype"],
                    ),
                    mask=True,
                ),
                out_profile=out_profile,
                out_grid=prototype_tile,
                out_path=tile_path,
                write_empty=True,
            )


def tile_directory_item_to_dict(item, relative_paths: bool = False) -> dict:
    item_dict = item.to_dict()

    # we have to add 'tiled-assets' to stac extensions in order to GDAL identify
    # this file as STACTA dataset
    stac_extensions = set(item_dict.get("stac_extensions", []))
    stac_extensions.add("tiled-assets")
    item_dict["stac_extensions"] = list(stac_extensions)

    if relative_paths:
        return make_stac_item_relative(item_dict)
    else:
        return item_dict


def make_stac_item_relative(stac_item, base_href: Optional[str] = None):
    """
    Convert all asset hrefs, self links, and asset_templates to relative paths.
    """

    def relpath(href: str, base_href: Optional[str] = None, is_self=False) -> str:
        if not href:  # pragma: no cover
            return href

        path = str(MPath(href).without_protocol())

        # Self link: just use filename
        if is_self:
            return MPath(path).name

        # Templates: strip everything before first '{'
        if "{" in path and "}" in path:
            first_brace_idx = path.index("{")
            return path[first_brace_idx:]

        # Normal assets: relative to base_href parent
        if base_href:  # pragma: no cover
            try:
                return str(MPath(path).relative_to(MPath(base_href).parent))
            except Exception:
                return MPath(path).name
        else:  # pragma: no cover
            return MPath(path).name

    if isinstance(stac_item, dict):
        stac_item = copy.deepcopy(stac_item)
        if base_href is None:
            self_links = [
                i for i in stac_item.get("links", []) if i.get("rel") == "self"
            ]
            base_href = self_links[0]["href"] if self_links else None

        # Patch self links
        for link in stac_item.get("links", []):
            if link.get("rel") == "self" and "href" in link:
                link["href"] = relpath(link["href"], base_href, is_self=True)

        # Patch assets
        for asset in stac_item.get("assets", {}).values():
            if "href" in asset:  # pragma: no cover
                asset["href"] = relpath(asset["href"], base_href)

        # Patch asset_templates
        for tmpl in stac_item.get("asset_templates", {}).values():
            if "href" in tmpl:
                tmpl["href"] = relpath(tmpl["href"], base_href)

        return stac_item

    elif isinstance(stac_item, (pystac.Item, pystac.Collection)):
        if base_href is None:
            base_href = stac_item.get_self_href()

        # Patch self link
        if stac_item.get_self_href():
            stac_item._self_href = relpath(
                stac_item.get_self_href(), base_href, is_self=True
            )

        # Patch assets
        for asset in stac_item.assets.values():  # pragma: no cover
            asset.href = relpath(asset.href, base_href)

        # Patch other links
        new_links = []
        for link in stac_item.links:
            if link.rel != "self":  # pragma: no cover
                new_links.append(
                    pystac.Link(
                        rel=link.rel,
                        target=relpath(link.target, base_href),
                        media_type=link.media_type,
                        title=link.title,
                    )
                )
            else:
                new_links.append(link)
        stac_item.links = new_links

        # Patch asset_templates from extra_fields if present
        if hasattr(stac_item, "extra_fields"):
            for tmpl in stac_item.extra_fields.get("asset_templates", {}).values():
                if "href" in tmpl:
                    tmpl["href"] = relpath(tmpl["href"], base_href)

        return stac_item

    else:
        raise TypeError(
            "Input must be a pystac.Item, pystac.Collection, or a STAC dict"
        )
