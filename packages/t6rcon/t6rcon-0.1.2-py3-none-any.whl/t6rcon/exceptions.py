class PlutoRCONError(Exception): 
    """Base Exception"""

class AuthenticationError(PlutoRCONError):
    """Raised when authentication with RCON server fails"""
    def __init__(self, error: str = "Invalid RCON password or authentication failed") -> None:
        super().__init__(error)

class TimeoutError(PlutoRCONError):
    """Raised when the RCON server does not respond in time"""
    def __init__(self, error: str = "RCON server timed out") -> None:
        super().__init__(error)

class InvalidResponseError(PlutoRCONError):
    def __init__(self, *, command: str, response: str = "") -> None:
        error = f"Invalid response for {command}: {response}"
        super().__init__(error)