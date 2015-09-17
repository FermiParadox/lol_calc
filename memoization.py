import functools


class MemoizeFirstCall(object):
    """
    To be used only for objects that are created once and never change.

    WARNING: Ignores completely differences in args and kwargs after initial memoization.
    """

    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)
        self.storage_used = False
        self.stored_value = None

    def __call__(self, *args, **kwargs):
        if not self.storage_used:
            self.storage_used = True
            self.stored_value = self.func(*args, **kwargs)

        return self.stored_value


if __name__ == '__main__':

    import time

    if 1:
        @MemoizeFirstCall
        def f(x, y):
            delay = 2
            print('\nCalling {}.. delay {} seconds'.format(f.__name__, delay))
            print('(First call should be delayed. Following calls should be instant.)')
            time.sleep(delay)

            return 'x was {}, y was {}'.format(x, y)

        print(f(x=1, y=2))
        print(f(1, 5))
        print(f())
