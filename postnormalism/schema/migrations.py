from postnormalism.schema import Table

create = """
CREATE TABLE postnormalism_migrations (
    id SERIAL PRIMARY KEY,
    migration_id VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT NOW()
);
"""

comment = """
COMMENT ON TABLE postnormalism_migrations IS
  $$ Maintains list of migrations and time applied $$;
"""

PostnormalismMigrations = Table(create=create, comment=comment)
