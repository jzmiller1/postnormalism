import os
from dataclasses import dataclass, field
from ..core import create_items, create_extensions
from . import DatabaseItem, PostnormalismMigrations, Schema


class SchemaProxy:
    def __init__(self, schema: Schema):
        self._schema = schema
        self._items = {}

    def add_item(self, item: DatabaseItem):
        item_name = getattr(item, 'name', None).lower()
        self._items[item_name] = item
        setattr(self, item_name, item)

    def __getattr__(self, name: str):
        if name in self._items:
            return self._items[name]
        raise AttributeError(f"Schema proxy object has no attribute '{name}'")

    def __repr__(self):
        return f"<SchemaProxy for {self._schema.name}>"


@dataclass
class Database:
    migrations_folder: str = field(default=None)
    load_order: list[DatabaseItem | list[DatabaseItem]] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    verbose: bool = field(default=False)
    _schema_contents: dict[str, dict[str, DatabaseItem]] = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.items_by_type = {}
        schema_loaded = {"public"}
        if self.migrations_folder:
            if not os.path.isdir(self.migrations_folder):
                print("Invalid migrations folder.")
        for entry in self.load_order:
            if isinstance(entry, list):
                self.add_items(*entry, schema_loaded=schema_loaded)
            else:
                self.add_items(entry, schema_loaded=schema_loaded)

    def add_items(self, *items: DatabaseItem, schema_loaded: set) -> None:
        for item in items:
            item_type = type(item).__name__

            if isinstance(item, Schema):
                schema_name = item.name.lower()
                schema_loaded.add(schema_name)
                object.__setattr__(self, schema_name, item)
                self._schema_contents[schema_name] = {}
                if self.verbose:
                    print(f"Schema '{schema_name}' registered.")
            else:
                schema_name = getattr(item, 'schema', 'public').lower()
                item_name = getattr(item, 'name', None).lower()

                if self.verbose:
                    print(f"Processing item: {item_name}, Type: {item_type}, Schema: {schema_name}")

                if schema_name not in schema_loaded:
                    raise ValueError(f"Schema '{schema_name}' must be loaded before items in that schema.")

                if schema_name == 'public':
                    object.__setattr__(self, item_name, item)
                else:
                    schema_object = getattr(self, schema_name, None)
                    if schema_object:
                        schema_object.add_item(item_name, item)
                    else:
                        raise AttributeError(f"Schema '{schema_name}' not found in the database object.")

            if self.verbose:
                print(f"Registered schemas: {self._schema_contents.keys()}")

            item_type = item_type.lower()
            if item_type not in self.items_by_type:
                self.items_by_type[item_type] = []
            self.items_by_type[item_type].append(item)

    def get_items_by_type(self, item_type: str) -> list:
        allowed_database_items = ["table", "function", "schema", "view", "trigger"]
        item_type = item_type.lower()
        if item_type not in allowed_database_items:
            raise ValueError(f"Invalid item_type: {item_type}")
        return self.items_by_type.get(item_type, [])

    def __getattr__(self, name: str):
        if '_schemas' in self.__dict__ and name in self.__dict__['_schemas']:
            return self.__dict__['_schemas'][name]

        if name in self.__dict__:
            return self.__dict__[name]

        raise AttributeError(f"Database object has no attribute '{name}'")

    def _create_schema_proxy(self, schema_name: str):
        class SchemaProxy:
            def __init__(self, items):
                self._items = items

            def __getattr__(self, item_name: str):
                try:
                    return self._items[item_name]
                except KeyError:
                    raise AttributeError(f"Schema '{schema_name}' has no attribute '{item_name}'")

        return SchemaProxy(self._schema_contents[schema_name])


    def create(self, cursor, exists=False):
        if self.migrations_folder:
            # Check if the migrations table exists in the database and create it if needed
            if not self.check_table_exists(cursor, PostnormalismMigrations.name):
                cursor.execute(str(PostnormalismMigrations.create))
            self.apply_migrations(cursor)  # Apply pending migrations

        create_extensions(self.extensions, cursor)
        create_items(self.load_order, cursor, exists=exists)

    @staticmethod
    def check_table_exists(cursor, table_name):
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
            (table_name,)
        )
        return cursor.fetchone()[0]

    def apply_migrations(self, cursor):
        # Retrieve the applied migrations from the database table
        applied_migrations = self.get_applied_migrations(cursor)

        # Get the list of migration files in the migrations folder
        migration_files = self.get_migration_files()

        # Filter out the migrations that haven't been applied yet
        pending_migrations = [
            migration_file for migration_file in migration_files
            if migration_file.split('_')[0] not in applied_migrations
        ]

        # Apply the pending migrations
        for migration_file in pending_migrations:
            migration_script = self.read_migration_script(migration_file)
            cursor.execute(migration_script)

            # Update the database table to mark the migration as applied
            self.mark_migration_as_applied(cursor, migration_file)

    @staticmethod
    def get_applied_migrations(cursor):
        # Retrieve the list of applied migrations from the database table
        # Execute a SQL query to fetch the applied migrations
        cursor.execute("""SELECT migration_id FROM postnormalism_migrations""")
        result = cursor.fetchall()
        applied_migrations = [row[0] for row in result]
        return applied_migrations

    def get_migration_files(self):
        # Return a list of migration file names
        migration_files = []
        if self.migrations_folder:
            for file_name in os.listdir(self.migrations_folder):
                if file_name.endswith('.sql'):
                    migration_files.append(file_name)
        return sorted(migration_files)

    def read_migration_script(self, migration_file):
        migration_path = os.path.join(self.migrations_folder, migration_file)
        with open(migration_path, 'r', encoding='utf-8') as file:
            migration_script = file.read()
        return migration_script

    @staticmethod
    def mark_migration_as_applied(cursor, migration_file):
        # Update the database table to mark the migration as applied
        migration_id = migration_file.split('_')[0]  # Extract the migration ID from the file name
        cursor.execute(
            "INSERT INTO postnormalism_migrations (migration_id) VALUES (%s)",
            (migration_id,)
        )
