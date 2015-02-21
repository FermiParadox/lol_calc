import matplotlib.pyplot as plt
import numpy

def single_num():
    num = None
    while True:
        loc = 200
        scale = 50
        num = numpy.random.normal(loc=loc,scale=scale)

        # Removed the filter below
        if True:
            break

    return num

lst_of_nums = [single_num() for _ in range(1000000)]

plt.hist(lst_of_nums, bins=200)
plt.xlabel("value")
plt.ylabel("frequency")
plt.show()