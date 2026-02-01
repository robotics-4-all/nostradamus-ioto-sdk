"""Enums for the Nostradamus IoTO SDK."""

from enum import Enum


class KeyType(str, Enum):
    """Type of API key for project access control.

    - READ: Read-only access to data
    - WRITE: Write access to send data
    - MASTER: Full access to manage project
    """

    READ = "read"
    WRITE = "write"
    MASTER = "master"


class StatOperation(str, Enum):
    """Statistical operations for data aggregation.

    - AVG: Average value
    - MAX: Maximum value
    - MIN: Minimum value
    - SUM: Sum of values
    - COUNT: Count of records
    - DISTINCT: Count of distinct values
    """

    AVG = "avg"
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    COUNT = "count"
    DISTINCT = "distinct"
