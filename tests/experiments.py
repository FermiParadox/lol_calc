class Dog(object):

    @staticmethod
    def f():
        return 1


class Puppy(Dog):

    def f(self):
        return super().f()
