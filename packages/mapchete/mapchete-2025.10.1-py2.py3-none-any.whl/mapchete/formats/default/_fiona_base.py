"""
Baseclasses for all drivers using fiona for reading and writing data.
"""

import logging
import types

from mapchete.formats import base
from mapchete.formats.protocols import VectorInput
from mapchete.io import MPath, fiona_open
from mapchete.io.vector import write_vector_window
from mapchete.tile import BufferedTile
from mapchete.validate import validate_values

logger = logging.getLogger(__name__)


class OutputDataReader(base.TileDirectoryOutputReader):
    """
    Output reader base class for vector drivers.

    Parameters
    ----------
    output_params : dictionary
        output parameters from Mapchete file

    Attributes
    ----------
    path : string
        path to output directory
    file_extension : string
        file extension for output files
    output_params : dictionary
        output parameters from Mapchete file
    pixelbuffer : integer
        buffer around output tiles
    pyramid : ``tilematrix.TilePyramid``
        output ``TilePyramid``
    crs : ``rasterio.crs.CRS``
        object describing the process coordinate reference system
    srid : string
        spatial reference ID of CRS (e.g. "{'init': 'epsg:4326'}")
    """

    def read(self, output_tile, **kwargs):
        """
        Read existing process output.

        Parameters
        ----------
        output_tile : ``BufferedTile``
            must be member of output ``TilePyramid``

        Returns
        -------
        process output : list
        """
        try:
            with fiona_open(self.get_path(output_tile), "r") as src:
                return list(src)
        except FileNotFoundError:
            return self.empty(output_tile)

    def is_valid_with_config(self, config):
        """
        Check if output format is valid with other process parameters.

        Parameters
        ----------
        config : dictionary
            output configuration parameters

        Returns
        -------
        is_valid : bool
        """
        validate_values(config, [("schema", dict), ("path", (str, MPath))])
        validate_values(config["schema"], [("properties", dict), ("geometry", str)])
        if config["schema"]["geometry"] not in [
            "Geometry",
            "Point",
            "MultiPoint",
            "Line",
            "LineString",
            "MultiLine",
            "Polygon",
            "MultiPolygon",
            "Unknown",
        ]:  # pragma: no cover
            raise TypeError("invalid geometry type")
        return True

    def empty(self, process_tile=None):
        """
        Return empty data.

        Parameters
        ----------
        process_tile : ``BufferedTile``
            must be member of process ``TilePyramid``

        Returns
        -------
        empty data : list
        """
        return []

    def for_web(self, data):
        """
        Convert data to web output (raster only).

        Parameters
        ----------
        data : array

        Returns
        -------
        web data : array
        """
        return list(data), "application/json"

    def open(self, tile, process):
        """
        Open process output as input for other process.

        Parameters
        ----------
        tile : ``Tile``
        process : ``MapcheteProcess``
        """
        return InputTile(tile, process)


class OutputDataWriter(base.TileDirectoryOutputWriter, OutputDataReader):
    def write(self, process_tile, data):
        """
        Write data from process tiles into vector file(s).

        Parameters
        ----------
        process_tile : ``BufferedTile``
            must be member of process ``TilePyramid``
        """
        if data is None or len(data) == 0:
            return
        if not isinstance(data, (list, types.GeneratorType)):  # pragma: no cover
            raise TypeError(
                "vector driver data has to be a list or generator of GeoJSON objects"
            )

        data = list(data)
        if not len(data):  # pragma: no cover
            logger.debug("no features to write")
        else:
            # Convert from process_tile to output_tiles
            for tile in self.pyramid.intersecting(process_tile):
                out_path = self.get_path(tile)
                self.prepare_path(tile)
                out_tile = BufferedTile(tile, self.pixelbuffer)
                write_vector_window(
                    in_data=data,
                    out_driver=self.METADATA["driver_name"],
                    out_schema=self.output_params["schema"],
                    out_tile=out_tile,
                    out_path=out_path,
                    allow_multipart_geometries=(
                        self.output_params["schema"]["geometry"].startswith("Multi")
                    ),
                )


class InputTile(base.InputTile, VectorInput):
    """
    Target Tile representation of input data.

    Parameters
    ----------
    tile : ``Tile``
    process : ``MapcheteProcess``

    Attributes
    ----------
    tile : ``Tile``
    process : ``MapcheteProcess``
    """

    def __init__(self, tile, process):
        """Initialize."""
        self.tile = tile
        self.process = process
        self._cache = {}

    def read(self, validity_check=True, no_neighbors=False, **kwargs):
        """
        Read data from process output.

        Parameters
        ----------
        validity_check : bool
            run geometry validity check (default: True)
        no_neighbors : bool
            don't include neighbor tiles if there is a pixelbuffer (default:
            False)

        Returns
        -------
        features : list
            GeoJSON-like list of features
        """
        if no_neighbors:  # pragma: no cover
            raise NotImplementedError()
        return self._from_cache(validity_check=validity_check)

    def is_empty(self, validity_check=True):  # pragma: no cover
        """
        Check if there is data within this tile.

        Returns
        -------
        is empty : bool
        """
        return len(self._from_cache(validity_check=validity_check)) == 0

    def _from_cache(self, validity_check=True):
        if validity_check not in self._cache:
            self._cache[validity_check] = self.process.get_raw_output(self.tile)
        return self._cache[validity_check]

    def __enter__(self):
        """Enable context manager."""
        return self

    def __exit__(self, t, v, tb):
        """Clear cache on close."""
        self._cache = {}
