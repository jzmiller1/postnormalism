from dataclasses import dataclass, field

from .database_item import DatabaseItem


@dataclass(frozen=True)
class Table(DatabaseItem):
    """
    A data class for tables.
    """
    _item_type: str = 'table'
    _name_pattern: str = field(default=r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\s+)?(?:TABLE)\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\w+\.)?(\w+)')
    _schema_pattern: str = field(default=r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\.\w+')
    alter: str = field(default=None)

    def full_sql(self, exists=False) -> str:
        sql_parts = super().full_sql().split("\n\n")

        if exists:
            sql_parts[0] = sql_parts[0].replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")

        if self.alter:
            sql_parts.append(self.alter.strip())

        return "\n\n".join(sql_parts)
