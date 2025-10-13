import struct
from typing import Type
import pymem  # type: ignore

from .interface import CStructTypeVar


class WindowsMemoryManager:
    pid: int

    def __init__(self, pid: int):
        self.pid = pid
        self._initialize_process()

    def _initialize_process(self):
        """Initialize the process handle using pymem."""
        try:
            self._process = pymem.Pymem(self.pid)
        except pymem.exception.ProcessNotFound:
            raise IOError(f"Process with PID {self.pid} not found")
        except Exception as e:
            raise IOError(f"Failed to open process memory: {e}")

    def read_bytes(self, address: int, size: int) -> bytes:
        """Read a sequence of bytes from the given address."""
        try:
            data = self._process.read_bytes(address, size)
            if len(data) < size:
                raise IOError(
                    f"Could only read {len(data)} bytes out of {size} at address {address}"
                )
            return data
        except Exception as e:
            raise IOError(f"Failed to read memory at address {address}: {e}")

    def read_short(self, address: int) -> int:
        """Read a signed 2 bytes integer from the given address."""
        data = self.read_bytes(address, 2)
        return struct.unpack("<h", data)[0]

    def read_uint(self, address: int) -> int:
        """Read an unsigned 4 bytes integer from the given address."""
        data = self.read_bytes(address, 4)
        return struct.unpack("<I", data)[0]

    def read_float(self, address: int) -> float:
        """Read a 4 bytes float from the given address."""
        data = self.read_bytes(address, 4)
        return struct.unpack("<f", data)[0]

    def read_ulonglong(self, address: int) -> int:
        """Read an unsigned 8 bytes integer from the given address."""
        data = self.read_bytes(address, 8)
        return struct.unpack("<Q", data)[0]

    def read_string(self, address: int, length: int) -> str:
        """Read a string from the given address with the specified length."""
        data = self.read_bytes(address, length)
        # Find null terminator if present
        null_pos = data.find(b"\0")
        if null_pos != -1:
            data = data[:null_pos]
        return data.decode("utf-8", errors="replace")

    def read_ctype_dataclass(self, address: int, dataclass: Type[CStructTypeVar]) -> CStructTypeVar:
        """Read a C-typed structure dataclass from the given address."""
        length = dataclass.byte_size()
        data = self.read_bytes(address, length)
        return dataclass.from_bytes(data)

    def write_ulonglong(self, address: int, value: int) -> None:
        """Write an unsigned 8-byte integer to the given address."""
        try:
            self._process.write_ulonglong(address, value)
        except Exception as e:
            raise IOError(f"Failed to write memory at address {address}: {e}")

    def __del__(self):
        """Clean up resources when the object is garbage collected."""
        if self._process is not None:
            try:
                self._process.close_process()
            except Exception:
                pass  # Ignore errors during cleanup
