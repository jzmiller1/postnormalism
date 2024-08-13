import unittest
from unittest.mock import MagicMock
from postnormalism.schema import Function


class TestFunction(unittest.TestCase):
    
    def setUp(self) -> None:
        self.create_function = """
        CREATE FUNCTION example_function() RETURNS INTEGER AS $$
        BEGIN
            RETURN 42;
        END;
        $$ LANGUAGE plpgsql;
        """

        self.function_comment = """
        COMMENT ON FUNCTION example_function IS 'This is an example function.';
        """


    def test_function_full_sql(self):
        """Test that the full_sql method of the Function class returns the expected SQL statement."""

        function = Function(create=self.create_function)
        expected_sql = self.create_function.strip()

        self.assertEqual(function.full_sql(), expected_sql)

    def test_function_full_sql(self):
        """Test that the full_sql method of the Function class returns the expected SQL statement."""

        function = Function(create=self.create_function)
        expected_sql = self.create_function.strip()

        self.assertEqual(function.full_sql(), expected_sql)

    def test_function_sql_not_executed(self):
        """Test that the SQL statements are not executed when creating a Function object."""
        function = Function(create=self.create_function)

        # Create a mock cursor object
        mock_cursor = MagicMock()

        # Assert the SQL statements were not executed on function creation
        mock_cursor.execute.assert_not_called()


    def test_function_full_sql_with_exists(self):
        """Test that the full_sql method of the Function class returns the expected SQL statement with "OR REPLACE" when exists=True."""
        function = Function(create=self.create_function)
        expected_sql = self.create_function.strip().replace("CREATE FUNCTION", "CREATE OR REPLACE FUNCTION")

        self.assertEqual(function.full_sql(exists=True), expected_sql)

    def test_function_name(self):
        """Test that the name property of the Function class returns the correct function name."""
        function = Function(create=self.create_function)
        self.assertEqual(function.name, "example_function")

    def test_function_name_extraction(self):
        """Test that the function name is extracted correctly."""
        function = Function(create=self.create_function)
        self.assertEqual(function.name, "example_function")

    def test_invalid_create_function_statement(self):
        """Test that an invalid CREATE FUNCTION statement raises a ValueError."""
        invalid_create_function = """
        CREATE example_function() RETURNS INTEGER AS $$
        BEGIN
            RETURN 42;
        END;
        $$ LANGUAGE plpgsql;
        """
        with self.assertRaises(ValueError):
            Function(create=invalid_create_function)

    def test_function_full_sql_with_comment(self):
        """Test that the full_sql method of the Function class includes the comment if provided."""
        function = Function(create=self.create_function, comment=self.function_comment)
        expected_sql = f"{self.create_function.strip()}\n\n{self.function_comment.strip()}"
        self.assertEqual(function.full_sql(), expected_sql)

    def test_function_with_schema(self):
        create_statement = """
        CREATE FUNCTION api.function_name(param INT)
        RETURNS VOID AS $$
        BEGIN
            -- function body
        END;
        $$ LANGUAGE plpgsql;
        """
        function = Function(create=create_statement)
        self.assertEqual(function.schema, 'api')
        self.assertEqual(function.name, 'function_name')

    def test_function_without_schema(self):
        create_statement = """
        CREATE FUNCTION function_name(param INT)
        RETURNS VOID AS $$
        BEGIN
            -- function body
        END;
        $$ LANGUAGE plpgsql;
        """
        function = Function(create=create_statement)
        self.assertEqual(function.schema, 'public')
        self.assertEqual(function.name, 'function_name')
