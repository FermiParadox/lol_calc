def repeat_cluster(func):
    """
    Wrapper used for repeating cluster of suggestions.
    """

    def wrapped(*args, **kwargs):

        while True:
            func(*args, **kwargs)

            if input('halo'):
                break

    return wrapped

@repeat_cluster
def f():
    print('hi')

f()