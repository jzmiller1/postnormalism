from dataclasses import dataclass

from .schema_item import SchemaItem


@dataclass(frozen=True)
class Function(SchemaItem):
    """
    A data class for functions.
    """
    pass
