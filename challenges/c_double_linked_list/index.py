from typing import Generic, TypeVar

T = TypeVar("T")


class Node(Generic[T]):
    def __init__(
        self,
        next: "Node[T] | None",
        prev: "Node[T] | None",
        value: T | None,
    ) -> None:
        self.next = next
        self.prev = prev
        self.value = value


class DoubleLinkedList(Generic[T]):
    def __init__(self) -> None:
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None

    def add(self, value: T) -> None:
        if self.head is None:
            self.head = Node[T](
                prev=None,
                next=self.tail,
                value=value,
            )
            return
        if self.tail is None:
            self.tail = Node[T](
                prev=self.head,
                next=None,
                value=value,
            )
            self.head.next = self.tail
            return

        old_tail = self.tail
        new_tail = Node[T](
            prev=old_tail,
            next=None,
            value=value,
        )
        old_tail.next = new_tail
        self.tail = new_tail

    def print(self) -> None:
        current = self.head
        while current is not None:
            print(f"{current.value} -> ")
            current = current.next

    def get(self, index: int) -> Node[T] | None:
        if index < 0:
            return None

        current = self.head
        i = 0
        while current is not None:
            if index == i:
                return current

            i += 1
            current = current.next

        return None

    def remove(self, index: int) -> Node[T]: ...

    def has(self, el: Node[T]) -> bool: ...


a = DoubleLinkedList[int]()
a.add(1)
a.add(2)
a.add(3)
a.add(4)
a.add(5)
a.print()
node = a.get(2)
if node:
    print(f"Node(value={node.value})")
