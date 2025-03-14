from abc import ABC, abstractmethod
from typing import Any, Generator

class DerivationTree(ABC):
    """
    Abstract base class for all derivation tree implementations.
    """

    @abstractmethod
    def traverse(self) -> Generator[Any, None, None]:
        """
        Abstract method for traversing the derivation tree.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def structural_hash(self) -> int:
        """
        Abstract method to compute a unique hash of the tree structure.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        """
        Returns a string representation of the derivation tree.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def parse(cls, grammar: Any, input_string: str) -> "DerivationTree":
        """
        Abstract factory method to create a derivation tree from a string using a grammar.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

#
# class TreeAdapter:
#     def __init__(self, tree, node_getter, children_getter):
#         """
#         Wraps an arbitrary tree structure to support `node, children = tree`.
#
#         :param tree: The original tree instance.
#         :param node_getter: A function that extracts the node value.
#         :param children_getter: A function that extracts the children list.
#         """
#         self._tree = tree
#         self._node_getter = node_getter
#         self._children_getter = children_getter
#
#     def __iter__(self):
#         """Unpacking support: node, children = tree"""
#         node = self._node_getter(self._tree)
#         children = [
#             TreeAdapter(child, self._node_getter, self._children_getter)  # Recursively wrap
#             for child in self._children_getter(self._tree)
#         ]
#         yield node
#         yield children
#
#     def __repr__(self):
#         node, children = self
#         return f"TreeAdapter({node!r}, {children!r})"
#
#
#
# if __name__ == "__main__":
#     class ListBasedTree:
#         def __init__(self, node, children=None):
#             self.node = node
#             self.children = children or []
#
#     list_tree = ListBasedTree("Root", [
#         ListBasedTree("Child1", [
#             ListBasedTree("Grandchild1"),
#             ListBasedTree("Grandchild2", [
#                 ListBasedTree("GreatGrandchild1")
#             ]),
#         ]),
#         ListBasedTree("Child2")
#     ])
#
#     wrapped_list_tree = TreeAdapter(
#         list_tree,
#         node_getter=lambda t: t.node,
#         children_getter=lambda t: t.children
#     )
#
#     # Unpacking at root level
#     node, children = wrapped_list_tree
#     print("Root Node:", node)
#     print("Children:", children)
#
#     # Unpacking at second level
#     node, children = children[0]  # "Child1"
#     print("Node:", node)
#     print("Children:", children)
#
#     # Unpacking at third level
#     node, children = children[1]  # "Grandchild2"
#     print("Node:", node)
#     print("Children:", children)
#
#     # Unpacking at fourth level
#     node, children = children[0]  # "GreatGrandchild1"
#     print("Node:", node)
#     print("Children:", children)  # Should be an empty list []
