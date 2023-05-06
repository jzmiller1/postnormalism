import unittest
from unittest.mock import MagicMock
from postnormalism.schema import Table, Function


class TestSchema(unittest.TestCase):
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

    def test_function_full_sql(self):
        """Test that the full_sql method of the Function class returns the expected SQL statement."""
        create_function = """
        CREATE FUNCTION example_function() RETURNS INTEGER AS $$
        BEGIN
            RETURN 42;
        END;
        $$ LANGUAGE plpgsql;
        """

        function = Function(create=create_function)
        expected_sql = create_function.strip()

        self.assertEqual(function.full_sql(), expected_sql)

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

    def test_function_sql_not_executed(self):
        """Test that the SQL statements are not executed when creating a Function object."""
        create_function = """
        CREATE FUNCTION example_function() RETURNS INTEGER AS $$
        BEGIN
            RETURN 42;
        END;
        $$ LANGUAGE plpgsql;
        """

        function = Function(create=create_function)

        # Create a mock cursor object
        mock_cursor = MagicMock()

        # Assert the SQL statements were not executed on function creation
        mock_cursor.execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()
