# Description

A custom, minimal, incomplete implementation of Python's dataclasses. The current features: 

 - Instance attributes can be specified using class attribute syntax.
 - Custom `__init__` and `__str__` methods are auto-generated to handle initialization, and the custom `__init__` allows for a `__post_init__` method to be defined to customize initialization.


# Example

    class NewClass(MyDataclass):
        a: int = 1
        b: int = 2
    
    first = NewClass()
    second = NewClass(8, 9)
    
    print(first, second) 
    # Prints "NewClass(a=1, b=2) NewClass(a=8, b=9)"

I'm largely doing this project to practice unit testing and get a better understanding of metaclasses.