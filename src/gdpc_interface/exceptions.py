"""
Custom exceptions for the GDPC interface layer.
"""

class GDPCInterfaceError(Exception):
    """Base exception for all GDPC interface errors."""
    pass

class ConnectionError(GDPCInterfaceError):
    """Raised when there's an issue connecting to the Minecraft server."""
    pass

class BuildAreaError(GDPCInterfaceError):
    """Raised when an operation attempts to modify blocks outside the build area."""
    pass

class InvalidBlockError(GDPCInterfaceError):
    """Raised when an invalid block ID or format is used."""
    pass

class InvalidOperationError(GDPCInterfaceError):
    """Raised for operations that are not supported or invalid."""
    pass

class PlayerNotFoundError(GDPCInterfaceError):
    """Raised when a specified player cannot be found."""
    pass

class NBTError(GDPCInterfaceError):
    """Raised for errors related to NBT data processing."""
    pass

class CommandError(GDPCInterfaceError):
    """Raised when a Minecraft command executed via the interface fails."""
    pass

class TimeoutError(ConnectionError):
    """Raised when a request to the server times out."""
    pass

class RateLimitError(ConnectionError):
    """Raised when the interface rate limit is exceeded (if applicable)."""
    # Note: GDMC HTTP Interface doesn't explicitly mention rate limits,
    # but this could be useful for future-proofing or custom implementations.
    pass