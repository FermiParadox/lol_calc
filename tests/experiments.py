def some_decorator(func):
    def wrapped(*args, **kwargs):
        func(*args, **kwargs)
    return wrapped


def food(b):
    return b


def eat():
    return food()

print(eat())