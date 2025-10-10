class RemoteExecutionError(Exception):
    """Raised when a remote function execution fails on the Globus Compute endpoint.

    Attributes:
        message: Human-readable error description
        stderr: Standard error output from the remote execution
        returncode: Exit code from the remote process
    """

    def __init__(self, message: str, stderr: str, returncode: int):
        # Remove trailing WARNING lines that aren't part of the traceback
        lines = stderr.strip().split("\n")
        while lines and lines[-1].startswith("WARNING:"):
            lines.pop()

        self.stderr = "\n".join(lines)
        self.returncode = returncode
        super().__init__(message + f"\n[stderr]:\n{self.stderr}")


class PayloadTooLargeError(Exception):
    """Raised when a serialized payload exceeds Globus Compute's 10MB size limit.

    Attributes:
        size_mb: The size of the payload in megabytes
    """

    def __init__(self, size_mb: float):
        self.size_mb = size_mb
        super().__init__(
            f"Payload size ({size_mb:.2f} MB) exceeds Globus Compute's 10 MB limit. "
            "See also: https://globus-compute.readthedocs.io/en/latest/limits.html#data-limits"
        )
