class MyException(BaseException):
    pass


def exception_handler(func):

    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except BaseException as exc_msg:
            print(exc_msg)
    return wrapped

@exception_handler
def f(x):
    raise MyException('error')

if __name__ == '__main__':

    f(1)