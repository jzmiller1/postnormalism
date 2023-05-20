from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class DatabaseItem:
    """
    A base data class for schema items like tables and functions.
    """
    create: str
    comment: str = field(default=None)
    _name: str = field(init=False, default=None)

    def __post_init__(self, name_pattern: str = None):
        if name_pattern:
            create = self.create.upper()
            match = re.search(name_pattern, create)

            if match:
                object.__setattr__(self, '_name', match.group(1).lower())
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
