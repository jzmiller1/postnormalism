import unittest
from postnormalism.schema import Domain


class TestDomain(unittest.TestCase):
    def test_domain_full_sql(self):
        """Test that the full_sql method of the Domain class returns the expected SQL statement."""
        create_domain = """
        CREATE DOMAIN "text/html" AS TEXT;
        """

        domain = Domain(create=create_domain)
        expected_sql = create_domain.strip()

        self.assertEqual(domain.full_sql(), expected_sql)

    def test_domain_full_sql_with_exists(self):
        """Test that the full_sql method of the Domain class includes the IF NOT EXISTS clause if exists flag is set."""
        create_domain = """
        CREATE DOMAIN "text/html" AS TEXT;
        """
        domain = Domain(create=create_domain)

        output_sql = domain.full_sql(exists=True)

        self.assertIn("IF NOT EXISTS", output_sql)

    def test_invalid_create_domain_statement(self):
        """Test that an invalid CREATE DOMAIN statement raises a ValueError."""
        invalid_create_domain = """
        CREATE "text/html" AS TEXT;
        """
        with self.assertRaises(ValueError):
            Domain(create=invalid_create_domain)

    def test_domain_in_non_public_schema(self):
        """Test that a domain is correctly created inside a non-public schema."""
        create_domain = """
        CREATE DOMAIN custom_schema."text/html" AS TEXT;
        """

        domain = Domain(create=create_domain)
        expected_sql = create_domain.strip()
        self.assertEqual(domain.full_sql(), expected_sql)
        self.assertEqual(domain.schema, "custom_schema")
        self.assertEqual(domain.name, "text/html")

    def test_domain_in_non_public_schema_with_exists(self):
        """Test that a domain in a non-public schema includes IF NOT EXISTS when exists=True."""
        create_domain = """
        CREATE DOMAIN custom_schema."text/html" AS TEXT;
        """

        domain = Domain(create=create_domain)
        output_sql = domain.full_sql(exists=True)
        self.assertIn("IF NOT EXISTS", output_sql)
        self.assertEqual(domain.schema, "custom_schema")
        self.assertEqual(domain.name, "text/html")


if __name__ == '__main__':
    unittest.main()
