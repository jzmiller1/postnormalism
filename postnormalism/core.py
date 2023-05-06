from . import schema


def create_schema_items_in_transaction(schema_items: list[schema.SchemaItem]) -> str:
    """
    Create schema items within a single transaction.
    """
    sql_parts = ["BEGIN;"]

    # First, create all schema items and add comments
    for item in schema_items:
        sql_parts.append(item.create.strip())
        if item.comment:
            sql_parts.append(item.comment.strip())

    # Then, add the ALTER TABLE statements for tables
    for item in schema_items:
        if isinstance(item, schema.Table) and item.alter:
            sql_parts.append(item.alter.strip())

    sql_parts.append("COMMIT;")

    return "\n\n".join(sql_parts)


def create_schema(load_order: list[schema.SchemaItem | list[schema.SchemaItem]], cursor):
    """
    Create schema items in a specified load order.
    """
    for item_or_group in load_order:
        if isinstance(item_or_group, list):
            # For related tables or functions, create them within a single transaction
            transaction_sql = create_schema_items_in_transaction(item_or_group)
            cursor.execute(transaction_sql)
        elif isinstance(item_or_group, (schema.Table, schema.Function)):
            # For tables and functions, execute the full_sql
            cursor.execute(item_or_group.full_sql())
        else:
            raise ValueError(f"Unsupported type in load_order: {type(item_or_group)}")
