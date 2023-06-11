from dataclasses import dataclass, field

from .database_item import DatabaseItem


@dataclass(frozen=True)
class Schema(DatabaseItem):
    """
    A data class for schema.
    """
    _name_pattern: str = field(default=r'CREATE\s+SCHEMA\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)')
    alter: str = field(default=None)

    def full_sql(self, exists=False) -> str:
        sql_parts = super().full_sql().split("\n\n")

        if exists:
            sql_parts[0] = sql_parts[0].replace("CREATE SCHEMA", "CREATE SCHEMA IF NOT EXISTS")

        if self.alter:
            sql_parts.append(self.alter.strip())

        return "\n\n".join(sql_parts)
