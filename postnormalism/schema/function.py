from dataclasses import dataclass

from .database_item import DatabaseItem


@dataclass(frozen=True)
class Function(DatabaseItem):
    """
    A data class for functions.
    """

    def __post_init__(self):
        function_name_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\s+)?(?:FUNCTION)\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\w+\.)?(\w+)'
        super().__post_init__(function_name_pattern)
