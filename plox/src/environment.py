from typing import final


@final
class Environment:
    def __init__(self, enclosing: 'Environment | None' = None) -> None:
        self.values: dict[str, object] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def assign(self, name: str, value: object) -> None:
        try:
            _ = self.values[name]  # check
            self.values[name] = value
            return
        except KeyError:
            if self.enclosing:
                return self.enclosing.assign(name, value)

            raise RuntimeError(f'Variable {name} doesnt exist')

    def get(self, name: str) -> object:
        try:
            return self.values[name]
        except KeyError:
            if self.enclosing:
                return self.enclosing.get(name)

            raise RuntimeError(f'Variable {name} doesnt exist')
