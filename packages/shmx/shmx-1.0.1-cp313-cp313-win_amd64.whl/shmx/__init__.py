"""
SHMX: High-performance shared-memory IPC for frame streaming

Zero dependencies - returns native Python types (memoryview, bytes, dict).
Compatible with numpy but doesn't require it.
"""

from .shmx_core import (
    # Classes
    Client,
    Server,
    Inspector,
    # Constants - Data types
    DT_BOOL, DT_I8, DT_U8, DT_I16, DT_U16,
    DT_I32, DT_U32, DT_I64, DT_U64,
    DT_F16, DT_BF16, DT_F32, DT_F64,
    # Constants - Layouts
    LAYOUT_SOA_SCALAR,
    LAYOUT_AOS_VECTOR,
    # Constants - TLV types
    TLV_STATIC_DIR,
    TLV_FRAME_STREAM,
    TLV_CONTROL_USER,
    # Utility functions
    dtype_to_string,
    layout_to_string,
    # Version
    __version__,
    VERSION_MAJOR,
    VERSION_MINOR,
)

__all__ = [
    # Classes
    'Client',
    'Server',
    'Inspector',
    # Constants
    'DT_BOOL', 'DT_I8', 'DT_U8', 'DT_I16', 'DT_U16',
    'DT_I32', 'DT_U32', 'DT_I64', 'DT_U64',
    'DT_F16', 'DT_BF16', 'DT_F32', 'DT_F64',
    'LAYOUT_SOA_SCALAR',
    'LAYOUT_AOS_VECTOR',
    'TLV_STATIC_DIR',
    'TLV_FRAME_STREAM',
    'TLV_CONTROL_USER',
    # Functions
    'dtype_to_string',
    'layout_to_string',
    # Version
    '__version__',
]

def create_stream_spec(stream_id, name, dtype_code, components, bytes_per_elem,
                       layout_code=None, extra=None):
    """
    Helper to create stream specification dict for Server.create()

    Args:
        stream_id: Unique stream identifier
        name: Human-readable stream name
        dtype_code: Data type constant (e.g., DT_F32)
        components: Number of components per element
        bytes_per_elem: Total bytes per element
        layout_code: Optional layout (default: LAYOUT_SOA_SCALAR)
        extra: Optional extra metadata as bytes

    Returns:
        Dict suitable for Server.create() streams parameter
    """
    spec = {
        'id': stream_id,
        'name': name,
        'dtype_code': dtype_code,
        'components': components,
        'bytes_per_elem': bytes_per_elem,
    }

    if layout_code is not None:
        spec['layout_code'] = layout_code

    if extra is not None:
        spec['extra'] = extra if isinstance(extra, bytes) else bytes(extra)

    return spec

