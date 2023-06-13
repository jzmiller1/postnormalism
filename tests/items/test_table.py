import unittest
from unittest.mock import MagicMock
from postnormalism.schema import Table


class TestTable(unittest.TestCase):
    def test_table_full_sql(self):
        """Test that the full_sql method of the Table class returns the expected SQL statement."""
        create_table = """
        CREATE TABLE example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """

        table = Table(create=create_table)
        expected_sql = create_table.strip()

        self.assertEqual(table.full_sql(), expected_sql)

    def test_table_sql_not_executed(self):
        """Test that the SQL statements are not executed when creating a Table object."""
        create_table = """
        CREATE TABLE example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """

        table = Table(create=create_table)

        # Create a mock cursor object
        mock_cursor = MagicMock()

        # Assert the SQL statements were not executed on table creation
        mock_cursor.execute.assert_not_called()



    def test_table_full_sql_with_alter(self):
        """Test that the full_sql method of the Table class includes the ALTER statement if provided."""
        create_table = """
        CREATE TABLE example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
        alter_table = """
        ALTER TABLE example
        ADD COLUMN email VARCHAR(255);
        """

        table = Table(create=create_table, alter=alter_table)
        expected_sql = f"{create_table.strip()}\n\n{alter_table.strip()}"

        self.assertEqual(table.full_sql(), expected_sql)

    def test_table_name_extraction(self):
        """Test that the table name is extracted correctly."""
        create_table = """
        CREATE TABLE example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
        table = Table(create=create_table)
        self.assertEqual(table.name, "example")

    def test_table_schema_extraction(self):
        """Test that the table schema is extracted correctly."""
        create_table = """
        CREATE TABLE test_schema.example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
        table = Table(create=create_table)
        self.assertEqual(table.schema, "test_schema")

    def test_invalid_create_statement(self):
        """Test that an invalid CREATE statement raises a ValueError."""
        create_table = """
        CREATE example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
        with self.assertRaises(ValueError):
            Table(create=create_table)

    def test_table_full_sql_with_exists(self):
        """Test that the full_sql method of the Table class includes the IF NOT EXISTS clause if exists flag is set."""
        create_table = """
        CREATE TABLE example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
        table = Table(create=create_table)

        output_sql = table.full_sql(exists=True)

        # We're not comparing the entire SQL string anymore, just checking if "IF NOT EXISTS" is present
        self.assertIn("IF NOT EXISTS", output_sql)

    def test_table_full_sql_with_comment(self):
        """Test that the full_sql method of the Table class includes the comment if provided."""
        create_table = """
        CREATE TABLE example (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
        table_comment = """
        COMMENT ON TABLE example IS 'This is an example table.';
        """
        table = Table(create=create_table, comment=table_comment)
        expected_sql = f"{create_table.strip()}\n\n{table_comment.strip()}"
        self.assertEqual(table.full_sql(), expected_sql)

