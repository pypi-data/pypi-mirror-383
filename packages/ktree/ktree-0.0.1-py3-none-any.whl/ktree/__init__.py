import abc
import collections
import dataclasses
import math
import typing

T = typing.TypeVar("T", int, float)


def check_axis_intersect(that: typing.Tuple[T, T], z: T):
    x, y = that
    return y >= z >= x


def is_collision(that: typing.List[typing.Tuple[T, T]], other: typing.List[T]) -> bool:
    if len(that) != len(other):
        raise ValueError("Invalid arguments, different length of values")

    return all([check_axis_intersect(t, z) for t, z in zip(that, other)])


def calc_distance(x: T, y: T):
    return math.fabs(y - x) / 2


@dataclasses.dataclass
class VectorNode(typing.Generic[T]):
    data: typing.List[T]
    value: T

    def __gt__(self, other):
        return self.value > other.value

    def __str__(self):
        return f"{self.data}, {self.value}"

    def __iter__(self):
        return iter([*self.data, self.value])

    def __len__(self):
        return len(self.data)


@dataclasses.dataclass
class Node(typing.Generic[T]):
    vertex: typing.List[typing.Tuple[T, T]]
    nodes: list

    def append(self, node: typing.List[T]):
        self.nodes.append(node)

    def is_collide(self, node: typing.List[T]):
        return is_collision(self.vertex, node)

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    def __hash__(self):
        _hash = hash(tuple(self.vertex))

        return _hash


@dataclasses.dataclass
class NodeValue(typing.Generic[T]):
    vertex: typing.List[typing.Tuple[T, T]]
    node: VectorNode

    def __gt__(self, other: VectorNode):
        return self.value > other.value

    @property
    def value(self):
        return self.node.value


class KTreeContainerInterface(abc.ABC):
    @property
    @abc.abstractmethod
    def axis(self) -> typing.List[typing.Tuple[T, T]]: ...

    @property
    @abc.abstractmethod
    def children(self): ...

    @property
    @abc.abstractmethod
    def node(self) -> Node: ...

    @property
    @abc.abstractmethod
    def is_parent(self) -> bool: ...

    @abc.abstractmethod
    def insert(self, verx: typing.List[T]): ...

    @abc.abstractmethod
    def sort(self): ...

    @abc.abstractmethod
    def __iter__(self): ...


class KTree(typing.Generic[T]):
    def __init__(self, axis: typing.List[typing.Tuple[T, T]], limit_divisions: int = 1):
        """
        KTree is the main container for sorting elements.

        :param axis: Establishes the main axes where the elements will be ordered.
        :param limit_divisions: Maximum number of divisions.
        """
        if limit_divisions < -1:
            raise ValueError("Limit divisions cannot be less than one.")

        self.__children: typing.Dict[int, KTree[T]] = {}
        self.__node: Node[T] = Node(vertex=axis, nodes=[])
        self.__axis: typing.List[typing.Tuple[T, T]] = axis
        self.__limit_divisions: int = limit_divisions

    def __hash__(self):
        return hash(self.__node)

    @property
    def axis(self):
        return [*self.__axis]

    @property
    def children(self):
        return self.__children

    @property
    def node(self) -> Node:
        return self.__node

    @property
    def is_parent(self):
        return len(self.children) != 0

    def insert(self, verx: typing.List[T]):
        return self._insert_recursive(verx)

    def sort(self) -> typing.List[typing.Tuple[typing.Tuple[T, ...], typing.List[typing.List[T]]]]:
        """
        This method returns the elements already sorted from sorted.
        :return:
        """
        return self.__iter_child_recursive()

    def __iter__(self):
        """
        Iterate the already sorted elements of sorted ones.
        :return:
        """
        return iter(self.__iter_child_recursive())

    def _insert_recursive(self, verx: typing.List[T]):
        def create_vertex(verx):
            root_axis = collections.deque()

            for axis, c in zip(self.axis, verx):
                x, y = axis
                d = calc_distance(x, y)

                if x <= c <= (x + d):
                    root_axis.append((x, x + d))
                else:
                    root_axis.append((x + d, y))

            axis = list(root_axis)

            return axis

        tree = KTree(create_vertex(verx), self.__limit_divisions - 1)
        tree_key = hash(tree)

        if tree_key in self.__children:
            tree = self.__children[tree_key]
        else:
            self.__children[tree_key] = tree

        if self.__limit_divisions > 0:
            return tree.insert(verx)
        else:
            if not tree.node.is_collide(verx):
                raise ValueError(f"Vertex no collide: {tree.node} {verx}")

            tree.node.append(verx)

        return tree

    def __iter_child_recursive(self):
        def get_iter_child(root, nodes=None):
            if nodes is None:
                nodes = []

            for _, child in root.children.items():
                if child.is_parent:
                    get_iter_child(child, nodes)
                else:
                    if len(child.node) > 0:
                        axis = child.node.vertex

                        nodes.append((axis, list(child.node.nodes)))

            return nodes

        return get_iter_child(self, [])
