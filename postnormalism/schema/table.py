from dataclasses import dataclass, field

from .schema_item import SchemaItem


@dataclass(frozen=True)
class Table(SchemaItem):
    """
    A data class for tables.
    """
    alter: str = field(default=None)

    def full_sql(self) -> str:
        sql_parts = super().full_sql().split("\n\n")

        if self.alter:
            sql_parts.append(self.alter.strip())

        return "\n\n".join(sql_parts)
