from time import time_ns
from typing import TYPE_CHECKING, final

from src.interperter_lib.interfaces import LoxCallable

if TYPE_CHECKING:
    from src.interperter_lib.interpreter import Interpreter


@final
class ClockFunc(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: 'Interpreter', args: list[object]) -> object:
        return time_ns()

    def __str__(self) -> str:
        return '<native|fun time>'
