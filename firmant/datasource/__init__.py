class Storage(object):
    '''An object that abstracts the task of providing a common interface to
    storage.  There is simply the save and delete methods.  A save will save
    unless there is a unique violation.  A delete will forget the object unless
    it does not exist.  Any errors other than these two should be wrapped in a
    StorageError.'''

    class DoesNotExistError(Exception): pass
    class StorageError(Exception): pass
    class UniqueViolationError(Exception): pass

    def save(self, obj):
        try:
            self._save(obj)
        except Storage.UniqueViolationError:
            raise
        except Exception, e:
            raise Storage.StorageError('%s %s' % (type(e), str(e)))

    def delete(self, obj):
        try:
            self._delete(obj)
        except Storage.DoesNotExistError:
            raise
        except Exception, e:
            raise Storage.StorageError('%s %s' % (type(e), str(e)))
