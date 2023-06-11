from dataclasses import dataclass, field

from .database_item import DatabaseItem


@dataclass(frozen=True)
class Function(DatabaseItem):
    """
    A data class for functions.
    """

    _name_pattern: str = field(default=r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\s+)?(?:FUNCTION)\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\w+\.)?(\w+)')
