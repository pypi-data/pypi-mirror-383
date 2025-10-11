import typeguard
from consts_everywhere import Const
import consts_everywhere


x = Const(45)


class A:
    a = Const(10)


class B:
    def __add__(self, other):
        return B()


def test1():
    global b
    print("here")
    b = c = d = Const(10)
    print(b)
    print(type(b))

def test2():
    a = A()
    a.a = Const(5)
    print(a.a)
    del a.a
    print(a.a)

def test3():
    a = Const(B())
    print(a)

@typeguard.typechecked
def test4(a: Const[list[int]]):
    pass
    
def main():
    print(x)
    test1()
    print()
    test2()
    print()
    test3()
    test4(Const([1,2,3]))

if consts_everywhere.patch_and_reload_module():
    main()
