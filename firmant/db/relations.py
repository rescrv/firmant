import os.path

class Relation(object):
    '''
    This is a loose wrapper around the database layer that allows easy
    conversion from SQL results to objects without losing the flexibility
    associated with raw SQL.
    '''

    # The attributes of the relation.  Corresponds to columns in a table.
    attributes = None

    def __init__(self):
        '''
        Ensure that the Relation class is not instantiated without attributes of
        a relation.
        '''
        if self.__class__.attributes == None:
            raise NotImplementedError(
                    'You must declare attributes of the relation.')

    def _select(self, cursor, fields):
        '''
        This function accepts a cursor, and a list of names of the various
        tables returned.  it will then populate the Relation object by setting
        the attributes to the values returned by fields.  In the event that
        multple rows are returned, a list of relation objects will be returned.

        Example:
        The Message relation is a subclass of Relation.  The attributes of a
        message are 'message' and 'dest'.  The user defines a function that
        runs the query "SELECT * from messages;".  The following would be
        returned by psql:
         message | dest 
        ---------+------
         hello   | John
         goodbye | Jack
        The cursor is ready to return these results using the standard fetch.

        fields = ['message', 'dest']
        attributes = ['message', 'dest']

        If a function invoked _select with the above scenario it would generate
        two Message objects with the attributes 'message' and 'dest' set on the
        object.

        It does check to make sure fields is a subset of attributes.
        '''
        # Verify the arguments.
        # fields intersect attributes should equal fields.
        f = set(fields)
        a = set(self.__class__.attributes)
        if f & a != f:
            raise AttributeError("fields must be a subset of attributes")

        # Create the appropriate instances
        results = []
        row = cursor.fetchone()
        while row != None:
            if len(row) != len(fields):
                cursor.close()
                raise ValueError("Query tables not equivalent to fields")
            r = self.__class__()
            for key, value in zip(fields, row):
                setattr(r, key, value)
            results.append(r)
            row = cursor.fetchone()
        return results

def schema(schema_name):
    '''
    This function takes a string argument such as 'atom' and loads the
    corresponding file firmant/db/schemas/<name>.sql and returns the file as
    text.
    '''
    mod = __import__('firmant.db.schemas', {}, {}, ['schemas'])
    schema = os.path.join(os.path.dirname(mod.__file__), schema_name + '.sql')
    del mod
    f = open(schema)
    schema = f.read()
    f.close()
    del f
    return schema