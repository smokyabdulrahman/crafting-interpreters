from typing import final


@final
class Environment:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        print(name, value)
        self.values[name] = value

    def assign(self, name: str, value: object) -> None:
        self.get(name)
        self.values[name] = value

    def get(self, name: str) -> object:
        try:
            return self.values[name]
        except KeyError:
            raise RuntimeError(f'Variable {name} doesnt exist')
