# postnormalism: PostgreSQL Schema Management  
  
postnormalism is Not an Object Relational Mapper (NORM) it is a lightweight and simple-to-use Python library for managing PostgreSQL database schemas. It provides an easy way to define tables and functions, organize schema items, and create them in a database with a specified load order.  
  
## Features  
  
- Manage the creation of schemas, domains, tables, views, triggers and functions using Python dataclasses
- Create database items with comments
- Group related database items and create them within a single transaction  
- Create a Database object that allows loading database items in a specified load order and managing database extensions
- Access database objects through the Database class using dot notation, with schema-based grouping (e.g., `db.schema_name.table_name`).
- exists mode for loading database items with IF NOT EXISTS and OR REPLACE 
- SQL Migration Loader

  
## NORM vs. ORM: Features Comparison  
  
postnormalism is a lightweight and simple-to-use Python library for managing PostgreSQL database schemas. It does not possess all the characteristics of a full-fledged ORM, focusing mainly on schema management and organization.  
  
Here is a comparison of postnormalism's features with typical ORM characteristics:  
  
1. **Object-oriented representation**: postnormalism does not map database tables to classes or table rows to instances. Instead, it uses dataclasses to represent schema items, like tables and functions, for organizing and generating schema items.  
  
2. **Abstraction**: postnormalism provides a smidgen of abstraction for creating schema items, but doesn't bother with things like query generation.    
  
3. **Query generation**: postnormalism does not include a query builder or DSL for constructing database queries. It focuses on schema management, not query generation.  You are the query generator.
  
4. **Transactions and concurrency**: postnormalism kindly allows you to group related schema items and create them within a single transaction. However, it knows when to draw the line and leaves transaction management and concurrency handling for other database operations to more heavyweight solutions.  
  
5. **Schema management**: postnormalism excels at schema management by allowing you to excel at schema management. Create schema items and load them in a specified order.  
  
6. **Relationships and associations**: postnormalism doesn't get entangled in relationships or associations between tables or objects. After all, it's just a simple library with simple needs.  You have to understand your schema.
  
7. **Data validation and constraints**: postnormalism doesn't have time for built-in data validation or constraint enforcement. But fear not, you can still define constraints in your schema items.
  
8. **Caching**: postnormalism believes in living in the moment, so caching mechanisms to improve performance are left to others.  
  
Should you require a complete ORM solution for your project, consider using a full-fledged ORM like SQLAlchemy or Django's ORM for Python. postnormalism is for those brave souls who seek a lightweight way to manage PostgreSQL schemas without all the bells and whistles.  
  
## Installation  
  
You can install postnormalism using pip:  
  
```sh  
pip install postnormalism  
```  
  
## Usage  
  
### Defining Database Items  
  
To define a table or a function, use the `Table` and `Function` dataclasses from the `postnormalism` module:  
  
```python  
from postnormalism.schema import Schema, Table, Function, View, Trigger  
```

### Define a Schema
```python
from postnormalism import schema

create = """
CREATE SCHEMA basic_auth;
"""

comment = """
COMMENT ON SCHEMA basic_auth IS
  $$ The basic auth schema $$;
"""

basic_auth = schema.Schema(create=create, comment=comment)
```
  
### Define a Table
```python
from postnormalism.schema import Table

create_table_sql = """  
CREATE TABLE material (  
id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),  
name varchar(120) NOT NULL,  
description varchar(240)  
);  
"""  
  
Material = Table(create=create_table_sql)  

# Access the columns
print(Material.columns)  # Outputs: ['id', 'name', 'description']

# Define a parent table
create_parent_table_sql = """  
CREATE TABLE parent_table (  
id uuid PRIMARY KEY,  
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
);  
"""

# Define a child table that inherits from the parent table
create_child_table_sql = """  
CREATE TABLE child_table (  
name varchar(120)  
) INHERITS (parent_table);  
"""

ParentTable = Table(create=create_parent_table_sql)
ChildTable = Table(create=create_child_table_sql)

# The child table's columns will include those from the parent table
print(ChildTable.columns)  # Outputs: ['id', 'created_at', 'name']
```
  
### Define a Postgresql Function  
```python
from postnormalism.schema import Function

create_function_sql = """  
CREATE FUNCTION get_material_for_variant(variant uuid)  
RETURNS uuid  
AS $$  
material_plan = plpy.prepare("SELECT material FROM material_variant WHERE id = $1",  
["uuid"])  
material = plpy.execute(material_plan, [variant])[0]["material"]  
return material  
$$ LANGUAGE plpython3u;  
"""  
  
comment_function_sql = """  
COMMENT ON FUNCTION get_material_for_variant IS  
$$ An example function $$;  
"""  
  
get_material_for_variant = Function(create=create_function_sql, comment=comment_function_sql)  
```  
  
### Creating Database Items in a Database  
  
To create database items in a PostgreSQL database, use the `Database` class:  
  
```python  
import psycopg  
from postnormalism.schema import Database
from your_example_file import Material, get_material_for_variant, Player, Inventory, basic_auth

universe = Database(
    load_order=[
        basic_auth,
        Material, get_material_for_variant,
        [Player, Inventory],  # example of grouping DatabaseItems into a transaction
    ],
    extensions=['uuid-ossp', 'plpython3u', 'pgcrypto']
)

db_connection_string = "dbname=test user=postgres password=secret host=localhost port=port"  

connection = psycopg.connect(db_connection_string)  
cursor = connection.cursor()  

universe.create(cursor)  

connection.commit()  
connection.close()  
```  

### Using exists Mode
Calling Database.create with exists=True inserts IF NOT EXISTS or OR REPLACE into all of your CREATE statements allowing you to easily add new items.

```python
universe.create(cursor, exists=True)
```

### Accessing Schema Objects via Dot Notation
You can now access tables, views, and other schema objects directly through the `Database` instance using dot notation:

```python
# Assuming you have already defined a schema and table
print(db.schema_name.table_name.name)  # Outputs the table name
print(db.schema_name.table_name.columns)  # Outputs the list of columns in the table
```

### Doing migrations
Update your `DatabaseItem`s and write your SQL migration transaction.  If you create your Database instance with 
a `migrations_folder` they will run during the create call.  Migration files should ideally be prefixed with a 
load order (ex: 0001) and must end with `.sql`.

```python
universe = Database(
    load_order=[
        Material, get_material_for_variant,
        [Player, Inventory],  # example of grouping DatabaseItems into a transaction
    ],
    extensions=['uuid-ossp', 'plpython3u', 'pgcrypto'],
    migrations_folder='/example/folder/path'
)

```


## Contributing  
  
Please submit a start a discussion, create a pull request or create an issue if you have any suggestions or improvements.  

### Primary Authors

- @jzmiller1 (Zac Miller)

### Other Contributors

- @ggopi19
- @malu1112

  
## License  
  
postnormalism is released under the MIT License. See the `LICENSE` file for more information.
