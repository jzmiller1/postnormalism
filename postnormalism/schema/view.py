from dataclasses import dataclass, field

from .database_item import DatabaseItem


@dataclass(frozen=True)
class View(DatabaseItem):
    """
    A data class for database views.
    """
    _item_type: str = 'view'
    _name_pattern: str = field(default=r'CREATE\s+VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\w+\.)?(\w+)')
    _schema_pattern: str = field(default=r'CREATE\s+VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\.')

    def full_sql(self, exists=False) -> str:
        sql_parts = super().full_sql().split("\n\n")

        if exists:
            sql_parts[0] = sql_parts[0].replace("CREATE VIEW", "CREATE OR REPLACE VIEW")

        return "\n\n".join(sql_parts)
