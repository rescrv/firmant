class Relation(object):
    '''
    This is a loose wrapper around the database layer that allows easy
    conversion from SQL results to objects without losing the flexibility
    associated with raw SQL.
    '''

    # The attributes of the relation.  Corresponds to columns in a table.
    attributes = None

    # The function to call to return a new connection instance.
    connection = None

    def __init__(self):
        '''
        Ensure that the Relation class is not instantiated without attributes of
        a relation or the ability to create a connection.
        '''
        if self.__class__.attributes == None:
            raise NotImplementedError(
                    'You must declare attributes of the relation.')
        if self.__class__.connection == None:
            raise NotImplementedError(
                    'You must declare a connection factory.')

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
        connection = MessageConnectionFactory

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
