import re
from dataclasses import dataclass, field

from .database_item import DatabaseItem


@dataclass(frozen=True)
class Trigger(DatabaseItem):
    """
    A data class for database triggers.
    """
    _item_type: str = 'trigger'
    _name_pattern: str = field(default=r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:CONSTRAINT\s+)?TRIGGER\s+(\w+)")

    def full_sql(self, exists=False) -> str:
        sql_parts = super().full_sql().split("\n\n")

        if exists:
            sql_parts[0] = sql_parts[0].replace("CREATE TRIGGER", "CREATE OR REPLACE TRIGGER")

        return "\n\n".join(sql_parts)

    @property
    def schema(self) -> str:
        """
        Derive the schema from the associated table/view.
        This assumes that the table/view is correctly referenced in the CREATE TRIGGER statement.
        """
        match = re.search(r'\bON\s+(\w+)\.(\w+)\b', self.create)
        if match:
            return match.group(1).lower()
        return 'public'
