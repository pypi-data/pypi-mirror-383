from enum import Enum, auto


class Inequality(Enum):
    NOT_GREATER_THAN = auto()
    MUCH_GREATER_THAN = auto()
    GREATER_THAN = auto()
    GREATER_THAN_OR_EQUAL = auto()
    NOT_EQUAL = auto()
    EQUAL = auto()
    LESS_THAN_OR_EQUAL = auto()
    LESS_THAN = auto()
    MUCH_LESS_THAN = auto()
    NOT_LESS_THAN = auto()


INEQUALITY_FROM_SIGNED_INT: dict[int, Inequality] = {-1: Inequality.LESS_THAN,
                                                     0: Inequality.EQUAL,
                                                     1: Inequality.GREATER_THAN}
