import re
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
    columns: list[str] = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self._extract_columns()

    def _extract_columns(self):
        # match column definitions in both CREATE TABLE and ALTER TABLE statements
        pattern_create = r"^\s*(\w+)\s+(?:[\w\(\)]+).*?(?:,|$)"
        pattern_alter = r"ADD COLUMN\s+(\w+)\s+[\w\(\)]+"

        columns = []
        in_table_definition = False

        for line in self.create.splitlines():
            if "CREATE TABLE" in line.upper():
                in_table_definition = True
                continue

            if in_table_definition:
                parts = line.split(',')
                for part in parts:
                    match = re.match(pattern_create, part.strip())
                    if match:
                        columns.append(match.group(1))

        if self.alter:
            for line in self.alter.splitlines():
                match = re.search(pattern_alter, line.strip(), re.IGNORECASE)
                if match:
                    columns.append(match.group(1))

        object.__setattr__(self, 'columns', columns)

    def full_sql(self, exists=False) -> str:
        sql_parts = super().full_sql().split("\n\n")

        if exists:
            sql_parts[0] = sql_parts[0].replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")

        if self.alter:
            sql_parts.append(self.alter.strip())

        return "\n\n".join(sql_parts)

