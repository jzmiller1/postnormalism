from dataclasses import dataclass, field


@dataclass(frozen=True)
class SchemaItem:
    """
    A base data class for schema items like tables and functions.
    """
    create: str
    comment: str = field(default=None)

    def full_sql(self) -> str:
        sql_parts = [self.create.strip()]

        if self.comment:
            sql_parts.append(self.comment.strip())

        return "\n\n".join(sql_parts)
