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
        except Storage.StorageError:
            raise
        # This is just a safeguard to ensure the errors raised are limited to
        # just the subset of errors defined in storage.  As such, there should
        # never be a case it is executed (if there is, the underlying plugin
        # should be raising the StorageError itself).  Thus, there is no need to
        # cover it.
        except Exception, e: # pragma: no cover
            raise Storage.StorageError('%s %s' % (type(e), str(e)))

    def delete(self, obj):
        try:
            self._delete(obj)
        except Storage.DoesNotExistError:
            raise
        except Storage.StorageError:
            raise
        # See above.
        except Exception, e: # pragma: no cover
            raise Storage.StorageError('%s %s' % (type(e), str(e)))
