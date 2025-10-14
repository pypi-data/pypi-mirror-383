"""Mock specific errors."""

from zhinst.comms_schemas.labone.errors import LabOneError


class LabOneMockError(LabOneError):
    """Base class for all LabOne mock errors."""
