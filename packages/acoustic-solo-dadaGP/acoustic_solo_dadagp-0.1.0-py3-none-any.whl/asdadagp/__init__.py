from logging import getLogger

from ._version import __version__
from .const import PKG_NAME

_LOGGER = getLogger(PKG_NAME)

# Constants
from .decoder import asdadagp_decode, tokens2guitarpro

# Main functions
from .encoder import asdadagp_encode, guitarpro2tokens
from .processor import (
    get_string_tunings,
    measures_playing_order,
    pre_decoding_processing,
    tokens_to_measures,
    tracks_check,
)

__all__ = [
    # Version and logging
    "__version__",
    "_LOGGER",
    "PKG_NAME",
    # Main functions
    "asdadagp_encode",
    "guitarpro2tokens",
    "asdadagp_decode",
    "tokens2guitarpro",
    # Processor functions
    "tracks_check",
    "get_string_tunings",
    "tokens_to_measures",
    "measures_playing_order",
    "pre_decoding_processing",
]
