from . import schema


def create_schema_items_in_transaction(schema_items: list[schema.DatabaseItem], exists=False) -> str:
    """
    Create schema items within a single transaction.
    """
    sql_parts = ["BEGIN;"]

    # First, create all schema items and add comments
    for item in schema_items:
        # Get the SQL parts of each item
        full_sql_parts = item.full_sql(exists=exists).split("\n\n")
        # Append only the CREATE TABLE statements (and comments if any)
        sql_parts.append(full_sql_parts[0])
        if item.comment:
            sql_parts.append(full_sql_parts[1])

    # Then, add the ALTER TABLE statements for tables
    for item in schema_items:
        if isinstance(item, schema.Table) and item.alter:
            # Get the SQL parts of each item
            full_sql_parts = item.full_sql(exists=exists).split("\n\n")
            # Append only the ALTER TABLE statements
            if len(full_sql_parts) > 2:
                sql_parts.append(full_sql_parts[2])

    sql_parts.append("COMMIT;")

    return "\n\n".join(sql_parts)


def create_items(load_order: list[schema.DatabaseItem | list[schema.DatabaseItem]], cursor, exists=False):
    """
    Create database items in a specified load order.
    """
    for item_or_group in load_order:
        if isinstance(item_or_group, list):
            # For related tables or functions, create them within a single transaction
            transaction_sql = create_schema_items_in_transaction(item_or_group, exists=exists)
            cursor.execute(transaction_sql)
        elif isinstance(item_or_group, schema.DatabaseItem):
            # For tables and functions, execute the full_sql
            cursor.execute(item_or_group.full_sql(exists=exists))
        else:
            raise ValueError(f"Unsupported type in load_order: {type(item_or_group)}")


def create_extensions(extensions: list[str], cursor):
    """
    Create extensions in a specified load order.
    """
    for extension in extensions:
        cursor.execute(f'CREATE EXTENSION IF NOT EXISTS "{extension}";')
