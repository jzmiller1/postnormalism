from dataclasses import dataclass, field
import re

from .database_item import DatabaseItem


@dataclass(frozen=True)
class Domain(DatabaseItem):
    """
    A data class for PostgreSQL domains.
    """
    _item_type: str = 'domain'
    _name_pattern: str = field(default=r'CREATE\s+DOMAIN\s+(?:(\w+)\.)?(".*?"|\w+)')
    _schema_pattern: str = field(default=r'CREATE\s+DOMAIN\s+(\w+)\.')

    def __post_init__(self):
        create_statement = self.create.strip()

        # Schema parsing
        schema_match = re.search(self._schema_pattern, create_statement, re.IGNORECASE)
        schema = schema_match.group(1) if schema_match else 'public'
        object.__setattr__(self, '_schema', schema)

        # Name parsing
        name_match = re.search(self._name_pattern, create_statement, re.IGNORECASE)
        if name_match:
            name = name_match.group(2).strip('"')
            object.__setattr__(self, '_name', name)
        else:
            raise ValueError("Could not parse the name from the create statement")

    def full_sql(self, exists=False) -> str:
        sql_parts = [self.create.strip()]

        if exists:
            sql_parts[0] = sql_parts[0].replace("CREATE DOMAIN", "CREATE DOMAIN IF NOT EXISTS", 1)

        if self.comment:
            sql_parts.append(self.comment.strip())

        return "\n\n".join(sql_parts)
