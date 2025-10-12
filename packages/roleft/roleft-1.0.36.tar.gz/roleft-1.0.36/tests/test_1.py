def collect_type_hints(cls):
    cls.__annotations__ = {
        name: type(getattr(cls(), name)).__name__
        for name in cls.__dict__
        if not name.startswith("__") and not callable(getattr(cls(), name))
    }
    return cls

@collect_type_hints
class Address:
    def __init__(self, id: int, comment: str) -> None:
        self.id = id
        self.comment = comment

addr = Address(23, 'jack')
print(dir(addr))

def printProperties(cls: type):
    for prop_name, prop_type in cls.__annotations__.items():
        print(f"Property: {prop_name}, Type: {prop_type}")

printProperties(Address)