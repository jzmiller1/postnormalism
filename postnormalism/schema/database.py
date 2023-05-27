import os
from dataclasses import dataclass, field
from ..core import create_schema, create_extensions
from . import DatabaseItem, Table, Function, PostnormalismMigrations


@dataclass
class Database:
    migrations_folder: str = field(default=None)
    items: dict[str, DatabaseItem] = field(default_factory=dict)
    load_order: list[DatabaseItem | list[DatabaseItem]] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.migrations_folder:
            if not os.path.isdir(self.migrations_folder):
                print("Invalid migrations folder.")
        for entry in self.load_order:
            if isinstance(entry, list):
                self.add_items(*entry)
            else:
                self.add_items(entry)

    def add_items(self, *items: DatabaseItem) -> None:
        for item in items:
            self.items[item.name] = item

    def get_items_by_type(self, item_type: str):
        type_mapping = {
            "table": Table,
            "function": Function,
        }

        if item_type not in type_mapping:
            raise ValueError(f"Invalid item_type: {item_type}")

        lookup_type = type_mapping[item_type]
        return [
            name for name, item in self.items.items()
            if isinstance(item, lookup_type)
        ]

    def __getattr__(self, name: str):
        if name in self.items:
            return self.items[name]
        raise AttributeError(f"Schema object has no attribute '{name}'")

    def create(self, cursor, exists=False):
        if self.migrations_folder:
            # Check if the migrations table exists in the database and create it if needed
            if not self.check_table_exists(cursor, PostnormalismMigrations.name):
                cursor.execute(str(PostnormalismMigrations.create))
            self.apply_migrations(cursor)  # Apply pending migrations

        create_extensions(self.extensions, cursor)
        create_schema(self.load_order, cursor, exists=exists)

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
