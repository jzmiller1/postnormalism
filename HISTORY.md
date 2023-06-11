## v0.0.4 (2023-06-11)

* add ability to create Schema
* cleaning up more naming and references related to the SchemaItem -> DatabaseItem change in v0.0.2
* use _name_pattern attribute to avoid defining a __post_init__ on all DatabaseItems
* add additional tests
* add GitHub action to run tests
* add GitHub action to release to PyPI


## v0.0.3 (2023-05-26)

* Migrations: specify a migrations_folder and write SQL migrations that are loaded in Database.create

## v0.0.2 (2023-05-19)

* SchemaItem -> DatabaseItem: the term schema has some meaning in a PostgreSQL database.  Starting to change SchemaItems into DatabaseItems in order to create a way to manage real PostgreSQL schemas
* DatabaseItem dataclass allows Tables and Functions to extract the table name from the CREATE and makes it accessible via the name property
* Adding the Database dataclass: Database is a class for managing a PostgreSQL database such as the load_order of DatabaseItems and the extensions to install
* There's now an 'exists' option on Tables that allows them to load with IF NOT EXISTS inserted into the CREATEs.  The exists option is a boolean parameter on the Database create method

## v0.0.1 (2023-05-06)

Initial release
