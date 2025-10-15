"""Caching of information."""

import json
from json.encoder import JSONEncoder
from pathlib import Path
from typing import Any, Dict, Optional, Type

from pymetadata import log


logger = log.get_logger(__name__)


class DataclassJSONEncoder(JSONEncoder):
    """JSON serialization of dataclasses."""

    def default(self, o: Any) -> Any:
        """Serialize to JSON."""
        return o.__dict__


def read_json_cache(cache_path: Path) -> Dict:
    """Read JSON cache file.

    :param cache_path:
    :return: Dictionary with content or None if cache file does not exist.
    """
    if cache_path.exists():
        with open(cache_path) as fp:
            logger.debug(f"Read cache: {cache_path}")
            return json.load(fp)  # type: ignore

    raise IOError(f"Cache path does not exist: '{cache_path}'")


def write_json_cache(
    data: Dict, cache_path: Path, json_encoder: Optional[Type[JSONEncoder]] = None
) -> None:
    """Write JSON cache file.

    :param data: data to serialize
    :param cache_path: path for the cache file
    :param json_encoder: optional JSON encoder
    :return:
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as fp:
        logger.info(f"Write cache: {cache_path}")
        if json_encoder:
            json.dump(data, fp=fp, indent=2, cls=json_encoder)
        else:
            json.dump(data, fp=fp, indent=2)
