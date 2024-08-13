import unittest
from postnormalism.schema import Database, Table, Function, Schema, View


class TestDatabase(unittest.TestCase):
    def setUp(self):
        create_table = """
        CREATE TABLE example_table (
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

        create_schema = """
        CREATE SCHEMA example_schema;
        """

        create_view = """
        CREATE VIEW example_view AS SELECT * FROM example_table;
        """

        create_view_in_schema = """
        CREATE VIEW example_schema.example_view_in_schema AS SELECT * FROM example_table;
        """

        self.db = Database(
            load_order=[
                Schema(create=create_schema),
                Table(create=create_table),
                Function(create=create_function),
                View(create=create_view),
                View(create=create_view_in_schema)
            ]
        )

    def test_get_items_by_type(self):
        item_types = ["table", "function", "schema", "view"]
        expected_outputs = [
            ["example_table"],
            ["example_function"],
            ["example_schema"],
            ["example_view", "example_view_in_schema"],
        ]

        for item_type, expected_output in zip(item_types, expected_outputs):
            with self.subTest(item_type=item_type):
                self.assertEqual(
                    [item.name for item in self.db.get_items_by_type(item_type)],
                    expected_output
                )

    def test_dot_notation_access(self):
        self.assertEqual(self.db.example_table.name, "example_table")
        self.assertEqual(self.db.example_view.name, "example_view")
        self.assertEqual(self.db.example_function.name, "example_function")
        self.assertEqual(self.db.example_schema.name, "example_schema")
        self.assertEqual(self.db.example_schema.example_view_in_schema.name, "example_view_in_schema")

    def test_schema_dot_notation_access(self):
        with self.assertRaises(AttributeError):
            _ = self.db.example_schema.example_table

    def test_invalid_dot_notation_access(self):
        with self.assertRaises(AttributeError):
            _ = self.db.non_existent_table

        with self.assertRaises(AttributeError):
            _ = self.db.example_schema.non_existent_view


if __name__ == '__main__':
    unittest.main()
