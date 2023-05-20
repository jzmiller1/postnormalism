from dataclasses import dataclass, field
from ..core import create_schema, create_extensions
from . import DatabaseItem, Table, Function


@dataclass
class Database:
    items: dict[str, DatabaseItem] = field(default_factory=dict)
    load_order: list[DatabaseItem | list[DatabaseItem]] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)

    def __post_init__(self):
        for entry in self.load_order:
            if isinstance(entry, list):
                self.add_items(*entry)
            else:
                self.add_items(entry)

    def add_items(self, *items: DatabaseItem) -> None:
        for item in items:
            self.items[item.name] = item

    def get_items_by_type(self, item_type: str):
        type_mapping = {
            "table": Table,
            "function": Function,
        }

        if item_type not in type_mapping:
            raise ValueError(f"Invalid item_type: {item_type}")

        lookup_type = type_mapping[item_type]
        return [
            name for name, item in self.items.items()
            if isinstance(item, lookup_type)
        ]

    def __getattr__(self, name: str):
        if name in self.items:
            return self.items[name]
        raise AttributeError(f"Schema object has no attribute '{name}'")

    def create(self, cursor, exists=False):
        create_extensions(self.extensions, cursor)
        create_schema(self.load_order, cursor, exists=exists)
