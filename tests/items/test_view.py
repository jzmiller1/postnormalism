import unittest
from postnormalism.schema import View


class TestView(unittest.TestCase):

    def test_view_with_schema(self):
        create_statement = """
        CREATE VIEW api.materials AS
        SELECT * FROM materials;
        """
        view = View(create=create_statement)
        self.assertEqual(view.schema, 'api')
        self.assertEqual(view.name, 'materials')

    def test_view_without_schema(self):
        create_statement = """
        CREATE VIEW materials AS
        SELECT * FROM materials;
        """
        view = View(create=create_statement)
        self.assertEqual(view.schema, 'public')
        self.assertEqual(view.name, 'materials')


if __name__ == '__main__':
    unittest.main()
