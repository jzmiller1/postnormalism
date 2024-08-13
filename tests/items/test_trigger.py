import unittest
from postnormalism.schema import Trigger


class TestTrigger(unittest.TestCase):

    def test_trigger_with_schema(self):
        create_statement = """
        CREATE TRIGGER trigger_name
        AFTER INSERT ON api.table_name
        FOR EACH ROW
        EXECUTE FUNCTION trigger_function();
        """
        trigger = Trigger(create=create_statement)
        self.assertEqual(trigger.schema, 'api')
        self.assertEqual(trigger.name, 'trigger_name')

    def test_trigger_without_schema(self):
        create_statement = """
        CREATE TRIGGER trigger_name
        AFTER INSERT ON table_name
        FOR EACH ROW
        EXECUTE FUNCTION trigger_function();
        """
        trigger = Trigger(create=create_statement)
        self.assertEqual(trigger.schema, 'public')
        self.assertEqual(trigger.name, 'trigger_name')


if __name__ == '__main__':
    unittest.main()
