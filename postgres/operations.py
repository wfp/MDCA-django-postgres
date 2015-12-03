from django.db.migrations.operations.base import Operation

# from .fields.composite_field import composite_type_created


class LoadSQLFromScript(Operation):
    def __init__(self, filename):
        self.filename = filename

    @property
    def reversible(self):
        return False

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(open(self.filename).read().replace('%', '%%'))


class CreateCompositeType(Operation):
    def __init__(self, name=None, fields=None):
        self.name = name
        self.fields = fields

    @property
    def reversible(self):
        return True

    def state_forwards(self, app_label, state):
        state.composite_fields[self.name] = self.fields

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        connection = schema_editor.connection
        schema_editor.execute('CREATE TYPE %s AS (%s)' % (
            self.name, ", ".join(["{} {}".format(name, field.db_type(connection)) for name, field in self.fields])
        ))
        # composite_type_created.send(sender=self.__class__, db_type=self.name)

    def state_backwards(self, app_label, state):
        pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute('DROP TYPE %s' % self.name)
