from dataclasses import dataclass, field
import re
import warnings


@dataclass(frozen=True)
class DatabaseItem:
    """
    A base data class for schema items like tables, functions, etc.
    """
    create: str
    comment: str = field(default=None)
    _item_type: str = field(default=None)
    _name_pattern: str = field(default=None)
    _name: str = field(init=False, default=None)
    _schema_pattern: str = field(default=None)
    _schema: str = field(init=False, default=None)
    _database: object = field(default=None, init=False, repr=False)  # Internal use only

    def __post_init__(self):
        create = self.create.upper()

        schema_match = re.search(self._schema_pattern, create) if self._schema_pattern else None
        object.__setattr__(
            self,
            '_schema',
            schema_match.group(1).lower() if schema_match else 'public'
        )

        name_match = re.search(self._name_pattern, create) if self._name_pattern else None
        if name_match:
            object.__setattr__(self, '_name', name_match.group(1).lower())
        else:
            raise ValueError("Could not parse the name from the create statement")

    def full_sql(self, exists=False) -> str:
        """
        Returns the full SQL string, including the create statement and optional comment.
        """
        sql_parts = [self.create.strip()]

        if self.comment:
            sql_parts.append(self.comment.strip())

        return "\n\n".join(sql_parts)

    @property
    def name(self) -> str:
        return self._name

    @property
    def schema(self) -> str:
        return self._schema

    @property
    def itype(self) -> str:
        return self._item_type

    @property
    def database(self):
        """Get the database reference."""
        return self._database

    @database.setter
    def database(self, db):
        """Set the database reference for this item."""
        object.__setattr__(self, '_database', db)

    def warn_if_no_database(self):
        """Warn if the database is not set and required for operations."""
        if not self.database:
            warnings.warn(
                f"Database reference is not set for '{self.name}'. Certain operations may not work correctly."
            )
