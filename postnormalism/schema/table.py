import re
from dataclasses import dataclass, field

from .database_item import DatabaseItem


@dataclass(frozen=True)
class Table(DatabaseItem):
    """
    A data class for tables.
    """
    _item_type: str = 'table'
    _name_pattern: str = field(
        default=r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMP\s+)?(?:TABLE)\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\w+\.)?(\w+)')
    _schema_pattern: str = field(default=r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\.\w+')
    _pattern_create: str = field(default=r"^\s*(\w+)\s+(?:[\w\(\)]+).*?(?:,|$)")
    _pattern_alter: str = field(default=r"ADD COLUMN\s+(\w+)\s+[\w\(\)]+")
    _pattern_inherits: str = field(default=r"INHERITS\s*\((\w+)\)")

    alter: str = field(default=None)
    inherits: bool = field(default=False, init=False)
    _columns: list[str] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        inherit_match = re.search(self._pattern_inherits, self.create, re.IGNORECASE)
        if inherit_match:
            object.__setattr__(self, 'inherits', True)
        self._initialize_columns()

    @property
    def columns(self):
        if self._columns is None:
            self._initialize_columns()
        return self._columns

    def _initialize_columns(self):
        self._extract_columns()
        if self.inherits:
            self._extract_inherited_columns()

    def _extract_columns(self):
        columns = []
        in_table_definition = False

        for line in self.create.splitlines():
            if "CREATE TABLE" in line.upper():
                in_table_definition = True
                continue

            if in_table_definition:
                parts = line.split(',')
                for part in parts:
                    match = re.match(self._pattern_create, part.strip())
                    if match:
                        columns.append(match.group(1))

        if self.alter:
            for line in self.alter.splitlines():
                match = re.search(self._pattern_alter, line.strip(), re.IGNORECASE)
                if match:
                    columns.append(match.group(1))
        object.__setattr__(self, '_columns', columns)

    def _extract_inherited_columns(self):
        inherit_match = re.search(self._pattern_inherits, self.create, re.IGNORECASE)
        if inherit_match and self.database:
            parent_table_name = inherit_match.group(1).lower()
            parent_table = self._get_parent_table(parent_table_name)
            if parent_table:
                parent_columns = parent_table.columns if parent_table else []
                columns = parent_columns + (self._columns or [])
                object.__setattr__(self, '_columns', columns)
        else:
            # Fallback to setting columns to an empty list if no parent found
            object.__setattr__(self, '_columns', [])

    def _get_parent_table(self, parent_table_name):
        if not self.database:
            raise ValueError("Database reference not set in Table instance.")
        return getattr(self.database, parent_table_name)

    def full_sql(self, exists=False) -> str:
        sql_parts = [self.create.strip()]

        if exists:
            sql_parts[0] = sql_parts[0].replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")

        if self.comment:
            sql_parts.append(self.comment.strip())

        if self.alter:
            sql_parts.append(self.alter.strip())

        return "\n\n".join(sql_parts)
