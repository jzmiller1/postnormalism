from dataclasses import dataclass, field

from .database_item import DatabaseItem


@dataclass(frozen=True)
class Schema(DatabaseItem):
    """
    A data class for schema.
    """
    _item_type: str = 'schema'
    _name_pattern: str = field(default=r'CREATE\s+SCHEMA\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)')
    alter: str = field(default=None)
    _items: dict[str, DatabaseItem] = field(default_factory=dict, init=False)

    def add_item(self, item_name: str, item: DatabaseItem):
        self._items[item_name] = item

    def __getattr__(self, name: str):
        if name in self._items:
            return self._items[name]
        raise AttributeError(f"Schema object has no attribute '{name}'")

    def full_sql(self, exists=False) -> str:
        sql_parts = [super().full_sql().strip()]

        if exists:
            sql_parts[0] = sql_parts[0].replace("CREATE SCHEMA", "CREATE SCHEMA IF NOT EXISTS")

        if self.alter:
            sql_parts.append(self.alter.strip())

        return "\n\n".join(sql_parts)
