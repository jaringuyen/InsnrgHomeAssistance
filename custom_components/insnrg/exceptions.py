class InsnrgPoolError(Exception):
    """Raised when Insnrg Pool request ended in error.

    Attributes:
        status_code - error code returned by the Insnrg Pool api
        status - more detailed description
        """
    def __init__(self, status_code, status):
        self.status_code = status_code
        self.status = status
