class Dog(object):    
    def __init__(self):
        self.food = 10

    def print_dog_food(self):
        print(self.food)


class Cat(object):    
    def __init__(self):
        self.food = 5

    def print_cat_food(self):
        print(self.food)


class AllAnimals(Cat, Dog):
    def __init__(self):
        Cat.__init__(self)
        Dog.__init__(self)

# Wrong result.
AllAnimals().print_cat_food()  # prints 10
AllAnimals().print_dog_food()  # prints 10