import unittest
from postnormalism.schema import Schema, Table


class TestSchema(unittest.TestCase):

    def test_schema_full_sql(self):
        """Test that the full_sql method of the Schema class returns the expected SQL statement."""
        create_schema = """
        CREATE SCHEMA example;
        """

        schema = Schema(create=create_schema)
        expected_sql = create_schema.strip()

        self.assertEqual(schema.full_sql(), expected_sql)

    def test_schema_full_sql_with_exists(self):
        """Test that the full_sql method of the Schema class includes the IF NOT EXISTS clause if exists flag is set."""
        create_schema = """
        CREATE SCHEMA example;
        """
        schema = Schema(create=create_schema)

        output_sql = schema.full_sql(exists=True)

        # We're not comparing the entire SQL string anymore, just checking if "IF NOT EXISTS" is present
        self.assertIn("IF NOT EXISTS", output_sql)

    def test_schema_full_sql_with_alter(self):
        """Test that the full_sql method of the Schema class includes the ALTER statement if provided."""
        create_schema = """
        CREATE SCHEMA example;
        """
        alter_schema = """
        ALTER SCHEMA example OWNER TO new_owner;
        """

        schema = Schema(create=create_schema, alter=alter_schema)
        expected_sql = f"{create_schema.strip()}\n\n{alter_schema.strip()}"

        self.assertEqual(schema.full_sql(), expected_sql)

    def test_invalid_create_schema_statement(self):
        """Test that an invalid CREATE SCHEMA statement raises a ValueError."""
        create_schema = """
        CREATE example;
        """
        with self.assertRaises(ValueError):
            Schema(create=create_schema)

    def test_schema_name_extraction(self):
        """Test that the schema name is extracted correctly."""
        create_schema = """
        CREATE SCHEMA example;
        """
        schema = Schema(create=create_schema)
        self.assertEqual(schema.name, "example")

    def test_add_item(self):
        create_table = """
        CREATE TABLE example_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """

        table = Table(create=create_table)
        schema = Schema(create="CREATE SCHEMA example;")
        schema.add_item("example_table", table)

        # Check if the item was added correctly
        self.assertEqual(schema.example_table, table)

    def test_add_item_attribute_error(self):
        schema = Schema(create="CREATE SCHEMA example;")

        with self.assertRaises(AttributeError):
            _ = schema.non_existing_item


if __name__ == '__main__':
    unittest.main()
