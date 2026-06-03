# Compatibility shim for markitdown package

from .__about__ import __version__

import importlib
import sys
from pathlib import Path

# Ensure top-level src directory (parent of this package) is on sys.path
# so we can import the top-level modules (_markitdown, _base_converter, etc.)
_src_root = Path(__file__).parent.parent
_src_root_str = str(_src_root)
if _src_root_str not in sys.path:
    sys.path.insert(0, _src_root_str)

# Load core implementation from top-level modules
_mm = importlib.import_module('_markitdown')
# Make markitdown._markitdown available for callers expecting that module path
sys.modules[__name__ + '._markitdown'] = _mm

MarkItDown = _mm.MarkItDown
PRIORITY_SPECIFIC_FILE_FORMAT = _mm.PRIORITY_SPECIFIC_FILE_FORMAT
PRIORITY_GENERIC_FILE_FORMAT = _mm.PRIORITY_GENERIC_FILE_FORMAT

_base = importlib.import_module('_base_converter')
sys.modules[__name__ + '._base_converter'] = _base
DocumentConverter = _base.DocumentConverter
DocumentConverterResult = _base.DocumentConverterResult

_stream = importlib.import_module('_stream_info')
sys.modules[__name__ + '._stream_info'] = _stream
StreamInfo = _stream.StreamInfo

_uri = importlib.import_module('_uri_utils')
sys.modules[__name__ + '._uri_utils'] = _uri

_exc = importlib.import_module('_exceptions')
sys.modules[__name__ + '._exceptions'] = _exc
MarkItDownException = _exc.MarkItDownException
MissingDependencyException = _exc.MissingDependencyException
FailedConversionAttempt = _exc.FailedConversionAttempt
FileConversionException = _exc.FileConversionException
UnsupportedFormatException = _exc.UnsupportedFormatException

# Expose converters and converter_utils as submodules under markitdown package name
_conv = importlib.import_module('converters')
sys.modules[__name__ + '.converters'] = _conv
converters = _conv

_conv_utils = importlib.import_module('converter_utils')
sys.modules[__name__ + '.converter_utils'] = _conv_utils
converter_utils = _conv_utils

__all__ = [
    '__version__', 'MarkItDown', 'DocumentConverter', 'DocumentConverterResult',
    'MarkItDownException','MissingDependencyException','FailedConversionAttempt',
    'FileConversionException','UnsupportedFormatException','StreamInfo',
    'PRIORITY_SPECIFIC_FILE_FORMAT', 'PRIORITY_GENERIC_FILE_FORMAT',
    'converters','converter_utils'
]
