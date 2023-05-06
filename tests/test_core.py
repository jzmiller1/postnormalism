import unittest
from unittest.mock import MagicMock
from postnormalism import schema
from postnormalism.core import create_schema


def create_example_schema_items():
    create_table = """
    CREATE TABLE example (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    """

    create_function = """
    CREATE FUNCTION example_function() RETURNS INTEGER AS $$
    BEGIN
        RETURN 42;
    END;
    $$ LANGUAGE plpgsql;
    """

    table = schema.Table(create=create_table)
    function = schema.Function(create=create_function)

    return [table, function]


class TestCore(unittest.TestCase):
    def test_create_schema(self):
        """Test if create_schema executes the correct SQL statements."""
        load_order = create_example_schema_items()

        # Create a mock cursor object
        mock_cursor = MagicMock()

        # Call create_schema with the mock cursor
        create_schema(load_order, mock_cursor)

        # Assert the correct SQL statements were executed
        for item in load_order:
            mock_cursor.execute.assert_any_call(item.full_sql())

    def test_empty_load_order(self):
        """Test if create_schema handles an empty load_order without raising exceptions."""
        load_order = []

        # Mock a cursor object
        cursor = MagicMock()

        # Call create_schema with an empty load_order and assert that no exceptions are raised
        try:
            create_schema(load_order, cursor)
        except Exception as e:
            self.fail(f"Unexpected exception raised: {e}")

        # Assert that cursor.execute was not called
        cursor.execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()
