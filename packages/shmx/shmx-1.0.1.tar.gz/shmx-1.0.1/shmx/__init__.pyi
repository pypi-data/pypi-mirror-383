"""Type stubs for shmx"""

from typing import Dict, List, Optional, Any, Tuple

__version__: str
VERSION_MAJOR: int
VERSION_MINOR: int

# Data type constants
DT_BOOL: int
DT_I8: int
DT_U8: int
DT_I16: int
DT_U16: int
DT_I32: int
DT_U32: int
DT_I64: int
DT_U64: int
DT_F16: int
DT_BF16: int
DT_F32: int
DT_F64: int

# Layout constants
LAYOUT_SOA_SCALAR: int
LAYOUT_AOS_VECTOR: int

# TLV type constants
TLV_STATIC_DIR: int
TLV_FRAME_STREAM: int
TLV_CONTROL_USER: int

class Client:
    """Shared memory client for consuming frames"""

    def __init__(self) -> None: ...

    def open(self, name: str) -> bool:
        """Open shared memory region by name"""
        ...

    def close(self) -> None:
        """Close the connection and release resources"""
        ...

    def is_open(self) -> bool:
        """Check if connection is open"""
        ...

    def get_header_info(self) -> Dict[str, Any]:
        """Get header information as dict"""
        ...

    def get_streams_info(self) -> List[Dict[str, Any]]:
        """
        Get list of available streams with metadata.

        Returns:
            List of dicts with keys: 'id', 'name', 'dtype', 'dtype_code',
            'components', 'layout', 'bytes_per_elem', optional 'extra'
        """
        ...

    def get_latest_frame(self) -> Optional[Dict[str, Any]]:
        """
        Get latest frame as dict with stream data as memoryview objects.

        Returns:
            None if no frame available or validation failed.
            Dict with '__metadata__' key and stream names as keys.
            Each stream value is a dict with:
                - 'data': memoryview (zero-copy buffer)
                - 'elem_count': int
                - 'bytes': int
        """
        ...

    def refresh_static(self) -> bool:
        """Refresh static stream metadata"""
        ...

    def send_control(self, type: int, data: bytes) -> bool:
        """Send control message to server"""
        ...

    def send_control_empty(self, type: int) -> bool:
        """Send control message without data"""
        ...


class Server:
    """Shared memory server for publishing frames"""

    def __init__(self) -> None: ...

    def create(
        self,
        name: str,
        slots: int = 3,
        reader_slots: int = 16,
        static_bytes_cap: int = 4096,
        frame_bytes_cap: int = 65536,
        control_per_reader: int = 4096,
        streams: List[Dict[str, Any]] = []
    ) -> bool:
        """
        Create shared memory region with given configuration.

        Args:
            name: Shared memory region name
            slots: Number of frame slots
            reader_slots: Maximum number of concurrent readers
            static_bytes_cap: Capacity for static metadata
            frame_bytes_cap: Maximum bytes per frame
            control_per_reader: Control ring buffer size per reader
            streams: List of stream specifications (dicts with keys:
                     'id', 'name', 'dtype_code', 'components', 'bytes_per_elem',
                     optional 'layout_code', 'extra')
        """
        ...

    def destroy(self) -> None:
        """Destroy and release shared memory"""
        ...

    def get_header_info(self) -> Dict[str, Any]:
        """Get header information as dict"""
        ...

    def begin_frame(self) -> Any:
        """Begin a new frame, returns opaque frame handle"""
        ...

    def append_stream(
        self,
        frame_handle: Any,
        stream_id: int,
        data: bytes,
        elem_count: int
    ) -> bool:
        """Append stream data to frame"""
        ...

    def publish_frame(self, frame_handle: Any, sim_time: float) -> bool:
        """Publish frame to shared memory"""
        ...

    def poll_control(self, max_messages: int = 256) -> List[Dict[str, Any]]:
        """
        Poll control messages from clients.

        Returns:
            List of dicts with keys: 'reader_id', 'type', 'data' (bytes)
        """
        ...

    def snapshot_readers(self) -> List[Dict[str, Any]]:
        """
        Get snapshot of connected readers.

        Returns:
            List of dicts with keys: 'reader_id', 'heartbeat',
            'last_frame_seen', 'in_use'
        """
        ...

    def reap_stale_readers(self, now_ticks: int, timeout_ticks: int) -> int:
        """Remove stale readers, returns count of reaped readers"""
        ...


class Inspector:
    """Read-only inspector for shared memory state"""

    def __init__(self) -> None: ...

    def open(self, name: str) -> bool:
        """Open shared memory region by name (read-only)"""
        ...

    def close(self) -> None:
        """Close the connection"""
        ...

    def get_header_info(self) -> Dict[str, Any]:
        """Get header information as dict"""
        ...

    def get_streams_info(self) -> List[Dict[str, Any]]:
        """Get list of available streams"""
        ...

    def get_readers_info(self) -> List[Dict[str, Any]]:
        """Get list of connected readers"""
        ...

    def inspect(self) -> Dict[str, Any]:
        """
        Get full inspection report.

        Returns:
            Dict with keys: 'session_id', 'static_gen', 'frame_seq',
            'readers_connected', 'streams', 'readers'
        """
        ...


def dtype_to_string(dtype_code: int) -> str:
    """Convert dtype code to string"""
    ...

def layout_to_string(layout_code: int) -> str:
    """Convert layout code to string"""
    ...

def frame_to_numpy(
    frame_dict: Dict[str, Any],
    dtype_map: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convert frame dict to numpy arrays (optional helper).
    Requires numpy to be installed.
    """
    ...

def create_stream_spec(
    stream_id: int,
    name: str,
    dtype_code: int,
    components: int,
    bytes_per_elem: int,
    layout_code: Optional[int] = None,
    extra: Optional[bytes] = None
) -> Dict[str, Any]:
    """Helper to create stream specification dict for Server.create()"""
    ...

