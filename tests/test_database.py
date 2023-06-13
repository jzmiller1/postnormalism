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
        CREATE VIEW example_view AS SELECT * FROM example;
        """

        self.db = Database(
            items={
                "example_table": Table(create=create_table),
                "example_function": Function(create=create_function),
                "example_schema": Schema(create=create_schema),
                "example_view": View(create=create_view)
            }
        )

    def test_get_items_by_type(self):
        item_types = ["table", "function", "schema", "view"]
        expected_outputs = [
            ["example_table"],
            ["example_function"],
            ["example_schema"],
            ["example_view"],
        ]

        for item_type, expected_output in zip(item_types, expected_outputs):
            with self.subTest(item_type=item_type):
                self.assertEqual([item.name for item in self.db.get_items_by_type(item_type)], expected_output)


if __name__ == '__main__':
    unittest.main()
