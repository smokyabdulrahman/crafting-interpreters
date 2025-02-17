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

    def assign_at(self, lvl: int, name: str, value: object) -> None:
        self.ancestor(lvl).values[name] = value

    def get(self, name: str) -> object:
        try:
            return self.values[name]
        except KeyError:
            if self.enclosing:
                return self.enclosing.get(name)

            raise RuntimeError(f'Variable {name} doesnt exist')

    def get_at(self, name: str, lvl: int) -> object:
        return self.ancestor(lvl).values.get(name)

    def ancestor(self, lvl: int) -> 'Environment':
        env = self
        for _ in range(0, lvl):
            assert env.enclosing
            env = env.enclosing

        return env
