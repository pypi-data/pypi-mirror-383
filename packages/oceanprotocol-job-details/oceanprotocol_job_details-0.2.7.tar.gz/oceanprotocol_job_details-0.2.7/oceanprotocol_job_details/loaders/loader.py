from typing import Protocol, TypeVar

T = TypeVar("T", covariant=True)


class Loader(Protocol[T]):

    def load(self) -> T:
        """Load an instance of the given type"""
        ...


del T
