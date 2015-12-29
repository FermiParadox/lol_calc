class D(dict):
    """
    Allows creation of a dict only with specified keys.
    Keys can be removed or reinserted but only if they are within the allowed.
    """

    MANDATORY_KEYS = {1,'2'}
    OPTIONAL_KEYS = {'3'}
    ALLOWED_KEYS = MANDATORY_KEYS | OPTIONAL_KEYS

    EXTRA_KEY_DETECTED_MSG = 'Extra keys given ({}). Keys are restricted only to "ALLOWED_KEYS".'

    def __init__(self, given_dct):
        given_dct_keys = given_dct.keys()

        # Disallows extra keys.
        extra_keys = given_dct_keys - self.ALLOWED_KEYS
        if extra_keys:
            raise KeyError(self.EXTRA_KEY_DETECTED_MSG.format(extra_keys))

        # Disallows omitting mandatory keys.
        self.mandatory_keys_omitted = self.MANDATORY_KEYS - given_dct_keys
        if self.mandatory_keys_omitted:
            raise KeyError('Mandatory keys omitted: {}'.format(self.mandatory_keys_omitted))

        # Auto inserts optional keys with False-type value.
        full_dct = {i: {} for i in self.OPTIONAL_KEYS}
        full_dct.update(given_dct)
        super().__init__(full_dct)

    def __setitem__(self, key, value):
        if key not in self.ALLOWED_KEYS:
            raise KeyError('Trying to insert new key ({}) in a SafeDict.'.format(key))
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        else:
            return {}

    def delete_keys(self, sequence):
        """
        Deletes all keys in given sequence.

        Used to make deletion of multiple keys less verbose.

        :return: (None)
        """
        for i in sequence:
            del self[i]

    def update(self, *args, **kwargs):
        if (set(kwargs) - self.ALLOWED_KEYS) or (set(*args) - self.ALLOWED_KEYS):
            raise KeyError(self.EXTRA_KEY_DETECTED_MSG)
        dict.update(*args, **kwargs)


d = D({1: 11, '2': 22})

print(d['3'])

