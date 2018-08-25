"""
@file ctor_ex1.py
@brief Construct class instance using typeinfo only.
"""


class SensorBase():
    name = "SensorBase"

    def __init__(self, name=None):
        print("Constructing " + self.name + " ...")
        if name is not None:
            self.name = name

    def print_name(self):
        print("I'm " + self.name)


class BaseA():
    name = "BaseA"

    def __init__(self, name=None):
        print("Constructing " + self.name + " ...")
        if name is not None:
            self.name = name

    def print_name(self):
        print("I'm " + self.name)


class BaseB():
    name = "BaseB"

    def __init__(self, name=None):
        print("Constructing " + self.name + " ...")
        if name is not None:
            self.name = name

    def print_name(self):
        print("I'm " + self.name)


# Types:
type1 = SensorBase
type2 = BaseA
type3 = BaseB


def create_instance(class_type: type) -> object:
    inst = class_type.__call__()
    print("Instance info: " + repr(inst))
    return inst


def print_types():
    global type1
    global type2
    global type3
    #
    print("Class types:")
    print("============")
    print(repr(type1))
    print(repr(type2))
    print(repr(type3))
    print("")


# ************************* TEST ******************************
if __name__ == "__main__":
    #
    print_types()
    #
    o1 = create_instance(type1)
    print(repr(o1))
    o1.print_name()
    #
    o2 = create_instance(type2)
    print(repr(o2))
    o2.print_name()
    #
    o3 = create_instance(type3)
    print(repr(o3))
    o3.print_name()

