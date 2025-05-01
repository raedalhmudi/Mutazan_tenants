from .middleware import get_current_schema

class CompanySchemaRouter:
    def db_for_read(self, model, **hints):
        return get_current_schema()

    def db_for_write(self, model, **hints):
        return get_current_schema()
    