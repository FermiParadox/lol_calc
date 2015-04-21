def my_decorator(func):

    def wrapped(*args, **kwargs):

        return func(*args, **kwargs)

    return wrapped


@my_decorator
def f():
    return 1



print(f())