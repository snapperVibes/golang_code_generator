from dataclasses import dataclass


@dataclass
class X:
    a: int
    b: int

    def __iter__(self):
        for attr in (self.a, self.b):
            yield attr
