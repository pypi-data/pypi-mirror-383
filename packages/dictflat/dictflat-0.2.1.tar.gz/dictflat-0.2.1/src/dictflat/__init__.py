from typing import Final, List

from .dictflat import (
    ALL,
    CHANGE_ROOT,
    CONTEXT_DEPTH,
    CONTEXT_ELEMENT,
    CONTEXT_PATH,
    CONTEXT_ROOT_REF,
    DictFlat,
)
from .dicttools import extract_list, get_dict, get_nested_value, simple_flat

__author__: Final[str] = 'Arnaud Valmary'
__email__: Final[str] = 'github@valmary.eu'
__version_parts__: Final[List[str]] = ['0', '2', '1']
__version__: Final[str] = '.'.join(__version_parts__)
