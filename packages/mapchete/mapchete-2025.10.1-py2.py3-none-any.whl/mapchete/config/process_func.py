from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
import inspect
import logging
import py_compile
import sys
from types import ModuleType
import warnings
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional, Union

from mapchete.config.models import ZoomParameters
from mapchete.errors import (
    MapcheteConfigError,
    MapcheteProcessImportError,
    MapcheteProcessSyntaxError,
)
from mapchete.log import add_module_logger
from mapchete.path import MPath, absolute_path
from mapchete.process_func_special_types import (
    TileBuffer,
    OutputNodataValue,
    OutputPath,
    Tile,
    TilePixelBuffer,
)
from mapchete.tile import BufferedTile


logger = logging.getLogger(__name__)


class ProcessFunc:
    """Abstraction class for a user process function.

    The user process can either be provided as a python module path, a file path
    or the source code as a list of strings.
    """

    path: Optional[Union[MPath, str]]
    name: str

    def __init__(self, src, config_dir=None, run_compile=True):
        self._src = src
        # for module paths and file paths
        if isinstance(src, (str, MPath)):
            if src.endswith(".py"):
                self.path = MPath.from_inp(src)
                self.name = self.path.name.split(".")[0]
            else:
                self.path = src
                self.name = self.path.split(".")[-1]

        # for process code within configuration
        else:
            self.path = None
            self.name = "custom_process"

        self._run_compile = run_compile
        self._root_dir = config_dir

        # this also serves as a validation step for the function
        logger.debug("validate process function")
        func = self._load_func()
        self.function_parameters = dict(**inspect.signature(func).parameters)

    def __call__(self, *args, **kwargs: Any) -> Any:
        return self._load_func()(*args, **self.filter_parameters(kwargs))

    def analyze_parameters(
        self, parameters_per_zoom: Dict[int, ZoomParameters]
    ) -> None:
        for zoom, config_parameters in parameters_per_zoom.items():
            # make sure parameters with no defaults are present in configuration, except of magical "mp" object
            for name, param in self.function_parameters.items():
                if name in ["mp"]:
                    warnings.warn(
                        DeprecationWarning(
                            "the magic 'mp' object is deprecated and will be removed soon"
                        )
                    )
                if param.annotation in [
                    Tile,
                    TilePixelBuffer,
                    TileBuffer,
                    OutputNodataValue,
                    OutputPath,
                ] or name in [
                    "mp",
                    "kwargs",
                    "__",
                ]:
                    continue

                elif param.default == inspect.Parameter.empty:
                    if (
                        name not in config_parameters.input
                        and name not in config_parameters.process_parameters
                    ):
                        raise MapcheteConfigError(
                            f"zoom {zoom}: parameter '{name}' is required by process function but not provided in the process configuration"
                        )
            # make sure there is no intersection between process parameters and input keys
            param_intersection = set(config_parameters.input.keys()).intersection(
                set(config_parameters.process_parameters.keys())
            )
            if param_intersection:
                raise MapcheteConfigError(
                    f"zoom {zoom}: parameters {', '.join(list(param_intersection))} are provided as both input names as well as process parameter names"
                )
            # warn if there are process parameters not available in the process
            for param_name in config_parameters.process_parameters.keys():
                if param_name not in self.function_parameters:
                    warnings.warn(
                        f"zoom {zoom}: parameter '{param_name}' is set in the process configuration but not a process function parameter"
                    )

    def filter_parameters(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Return function kwargs."""
        return {
            k: v
            for k, v in kwargs.items()
            if k in self.function_parameters and v is not None
        }

    def execute(
        self,
        parameters_at_zoom: Dict[str, Any],
        inputs: Dict[str, Any],
        process_tile: BufferedTile,
        output_params: Dict[str, Any],
    ) -> Any:
        # check for annotated special parameters
        for name, param in self.function_parameters.items():
            if param.annotation == Tile:
                parameters_at_zoom[name] = process_tile
            elif param.annotation == TilePixelBuffer:
                parameters_at_zoom[name] = process_tile.pixelbuffer
            elif param.annotation == OutputNodataValue:
                try:
                    parameters_at_zoom[name] = output_params["nodata"]
                except KeyError:  # pragma: no cover
                    raise KeyError("this process output does not have a nodata value")
            elif param.annotation == OutputPath:
                try:
                    parameters_at_zoom[name] = output_params["path"]
                except KeyError:  # pragma: no cover
                    raise KeyError("this process output does not have a path")
            elif param.annotation == TileBuffer:
                parameters_at_zoom[name] = (
                    process_tile.pixel_x_size * process_tile.pixelbuffer
                )

        return self.__call__(
            **parameters_at_zoom,
            **inputs,
        )

    def _load_func(self):
        """Import and return process function."""
        logger.debug(f"get process function from {self.name}")
        process_module = self._load_module()
        try:
            if hasattr(process_module, "execute"):
                return process_module.execute
            else:
                raise ImportError("No execute() function found in %s" % self._src)
        except ImportError as e:
            raise MapcheteProcessImportError(e)

    def _load_module(self) -> ModuleType:
        # path to python file or python module path
        if self.path:
            return self._import_module_from_path(self.path)
        # source code as list of strings
        else:
            with NamedTemporaryFile(suffix=".py") as tmpfile:
                logger.debug(f"writing process code to temporary file {tmpfile.name}")
                with open(tmpfile.name, "w") as dst:
                    for line in self._src:
                        dst.write(line + "\n")
                return self._import_module_from_path(
                    MPath.from_inp(tmpfile.name),
                )

    def _import_module_from_path(self, path: Union[MPath, str]) -> ModuleType:
        if path.endswith(".py"):
            module_path = absolute_path(path=path, base_dir=self._root_dir)
            if not module_path.exists():
                raise MapcheteConfigError(f"{module_path} is not available")
            try:
                if self._run_compile:
                    try:
                        py_compile.compile(str(module_path), doraise=True)
                    except FileExistsError:  # pragma: no cover
                        pass
                module_name = module_path.stem
                # load module
                spec = spec_from_file_location(module_name, str(module_path))
                if spec is None or spec.loader is None:  # pragma: no cover
                    raise ImportError(
                        f"cannot import module spec from {str(module_path)}"
                    )
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                # required to make imported module available using multiprocessing
                sys.modules[module_name] = module
                # configure process file logger
                add_module_logger(module.__name__)
            except py_compile.PyCompileError as e:
                raise MapcheteProcessSyntaxError(e)
            except ImportError as e:
                raise MapcheteProcessImportError(e)
        else:
            try:
                module = import_module(str(path))
            except ImportError as e:
                raise MapcheteProcessImportError(e)

        logger.debug(f"return process func: {module}")

        return module
