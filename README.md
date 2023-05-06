# postnormalism: PostgreSQL Schema Management  
  
postnormalism is Not an Object Relational Mapper (NORM) it is a lightweight and simple-to-use Python library for managing PostgreSQL database schemas. It provides an easy way to define tables and functions, organize schema items, and create them in a database with a specified load order.  
  
## Features  
  
- Define tables and functions using Python dataclasses  
- Create schema items (Tables, Functions) with comments
- Load schema items in a specified load order  
- Group related schema items and create them within a single transaction  
  
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
  
### Defining Schema Items  
  
To define a table or a function, use the `Table` and `Function` dataclasses from the `postnormalism` module:  
  
```python  
from postnormalism import Table, Function  
```
  
### Define a Table
```python
create_table_sql = """  
CREATE TABLE material (  
id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),  
name varchar(120) NOT NULL,  
description varchar(240)  
);  
"""  
  
Material = Table(create=create_table_sql)  
```
  
### Define a Postgresql Function  
```python
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
  
### Creating Schema Items in a Database  
  
To create schema items in a PostgreSQL database, use the `create_schema` function from the `postnormalism` module:  
  
```python  
import psycopg  
from postnormalism import create_schema  
from your_example_file import Material, get_material_for_variant

db_connection_string = "dbname=test user=postgres password=secret host=localhost port=5432"  

connection = psycopg.connect(db_connection_string)  
cursor = connection.cursor()  

create_schema([Material, get_material_for_variant], cursor)  

connection.commit()  
connection.close()  
```  

  
## Contributing  
  
Please submit a pull request or create an issue if you have any suggestions or improvements.  
  
## License  
  
postnormalism is released under the MIT License. See the `LICENSE` file for more information.
