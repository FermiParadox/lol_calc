import copy

mom = dict(
    a=4,
    b={'b2': 4}
)

kid = dict(
    c=33)
kid.update(mom)

