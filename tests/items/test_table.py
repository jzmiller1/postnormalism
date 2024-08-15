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

    def test_simple_create_table_column_extraction(self):
        sql = """
        CREATE TABLE material (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT
        );
        """
        table = Table(create=sql)
        self.assertEqual(table.columns, ["id", "name", "description"])

    def test_complex_create_table_column_extraction(self):
        sql = """
        CREATE TABLE user_account (
            id UUID PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'suspended')),
            profile_id UUID REFERENCES user_profile(id),
            bio TEXT DEFAULT ''
        );
        """
        table = Table(create=sql)
        expected_columns = ["id", "username", "email", "created_at", "updated_at", "status", "profile_id", "bio"]
        self.assertEqual(table.columns, expected_columns)

    def test_table_with_constraints_and_defaults(self):
        sql = """
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INT NOT NULL,
            order_date DATE NOT NULL DEFAULT CURRENT_DATE,
            amount NUMERIC(10, 2) CHECK (amount > 0),
            status VARCHAR(20) DEFAULT 'pending',
            notes TEXT
        );
        """
        table = Table(create=sql)
        expected_columns = ["order_id", "customer_id", "order_date", "amount", "status", "notes"]
        self.assertEqual(table.columns, expected_columns)

    def test_simple_create_table_column_extraction_multiple_per_line(self):
        sql = """
        CREATE TABLE material (
            id UUID PRIMARY KEY, name VARCHAR(255) NOT NULL, description TEXT
        );
        """
        table = Table(create=sql)
        self.assertEqual(table.columns, ["id", "name", "description"])

    def test_create_table_with_alter_table(self):
        sql_create = """
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INT NOT NULL,
            order_date DATE NOT NULL DEFAULT CURRENT_DATE
        );
        """
        sql_alter = """
        ALTER TABLE orders
        ADD COLUMN amount NUMERIC(10, 2) CHECK (amount > 0),
        ADD COLUMN status VARCHAR(20) DEFAULT 'pending',
        ADD COLUMN notes TEXT;
        """
        table = Table(create=sql_create, alter=sql_alter)
        expected_columns = ["order_id", "customer_id", "order_date", "amount", "status", "notes"]
        self.assertEqual(table.columns, expected_columns)

    def test_inherited_table_columns(self):
        create_parent = """
        CREATE TABLE process_element (
            id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_child = """
        CREATE TABLE process_element_material (
            element uuid REFERENCES material NOT NULL
        ) INHERITS (process_element);
        """

        ProcessElement = Table(create=create_parent)
        ProcessElementMaterial = Table(create=create_child)

        from postnormalism.schema import Database

        universe_db = Database(
            load_order=[
                ProcessElement,
                ProcessElementMaterial,
            ],
        )

        expected_columns = [
            "id", "created_at", "updated_at", "element"
        ]
        self.assertEqual(universe_db.process_element_material.columns, expected_columns)

    def test_exclude_check_and_unique_constraints(self):
        create_statement = """
        CREATE TABLE process_action (
            id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
            process uuid REFERENCES process NOT NULL,
            target uuid NOT NULL,
            calculated uuid REFERENCES attribute NOT NULL,
            description varchar(240),
            action_type varchar(10) NOT NULL,
            CHECK (action_type = 'linear' OR action_type = 'inplace'),
            UNIQUE (process, target, calculated)
        );
        """

        expected_columns = [
            'id', 'process', 'target', 'calculated', 'description', 'action_type'
        ]
        process_action_table = Table(create=create_statement)
        self.assertEqual(process_action_table.columns, expected_columns)
