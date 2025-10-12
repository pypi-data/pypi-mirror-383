"""Screen capture exception - ported from Qontinui framework.

Exception thrown when screen capture operations fail.
"""

from .qontinui_runtime_exception import QontinuiRuntimeException


class ScreenCaptureException(QontinuiRuntimeException):
    """Exception thrown when screen capture operations fail.

    Port of ScreenCaptureException from Qontinui framework.
    """

    def __init__(
        self,
        message: str = "Screen capture failed",
        cause: Exception | None = None,
        monitor: int | None = None,
    ):
        """Initialize screen capture exception.

        Args:
            message: Error message
            cause: Underlying exception that caused this error
            monitor: Monitor number that failed (if applicable)
        """
        super().__init__(message, cause)
        self.monitor = monitor
