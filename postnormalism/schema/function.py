from dataclasses import dataclass, field

from .database_item import DatabaseItem


@dataclass(frozen=True)
class Function(DatabaseItem):
    """
    A data class for functions.
    """

    _item_type: str = 'function'
    _name_pattern: str = field(default=r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\s+)?FUNCTION\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\w+\.)?(\w+)')
    _schema_pattern: str = field(default=r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\s+)?FUNCTION\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\.')

    def full_sql(self, exists=False) -> str:
        sql_parts = super().full_sql().split("\n\n")

        if exists:
            sql_parts[0] = sql_parts[0].replace("CREATE FUNCTION", "CREATE OR REPLACE FUNCTION")

        return "\n\n".join(sql_parts)
