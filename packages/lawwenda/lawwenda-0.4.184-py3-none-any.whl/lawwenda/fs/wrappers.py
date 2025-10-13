# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Filesystem wrappers.

Used for filtering nodes from existing filesystems, influence access control or other things.
"""
import typing as t

import lawwenda.fs.backend


FilesystemNodePredicate = t.Callable[[lawwenda.fs.node.Node], bool]


class AbstractWrappedFilesystem(lawwenda.fs.backend.Backend):  # pylint: disable=abstract-method
    """
    TODO.
    """
    # TODO child_nodes broken (e.g. wrong "filesystem")?

    def __init__(self, inner: lawwenda.fs.backend.Backend):
        super().__init__()
        self._inner = inner

    def _eval_predicate(self, predicate: FilesystemNodePredicate, node: lawwenda.fs.node.Node) -> bool:
        return predicate(self._inner.node_by_path(node.path))

    def child_nodes(self, handle):
        return [handle.readable_node.child_by_name(n.name) for n
                in self._inner.child_nodes(self._inner.read_handle(self._inner.node_by_path(
                handle.readable_node.path)))]

    def __getattribute__(self, item):
        if ((item not in ["node_by_path", "root_node"]) and (not item.startswith("_"))
                and (not type(self).__dict__.get(item)) and hasattr(self._inner, item)):
            return getattr(self._inner, item)
        return super().__getattribute__(item)


class HidingNodesWrappedFilesystem(AbstractWrappedFilesystem):  # pylint: disable=abstract-method
    """
    Wrapper for filesystems that marks some nodes as hidden by a predicate (on top of the nodes that are already hidden
    by the filesystem implementation itself, e.g. file names that start with a dot).

    Note: See user can see and access hidden files if he decides so. For access control purposes, just might want to
    exclude them instead!
    """

    def __init__(self, inner: lawwenda.fs.backend.Backend, predicate: FilesystemNodePredicate):
        """
        :param inner: The inner filesystem.
        :param predicate: The predicate that defines what nodes to hide.
        """
        super().__init__(inner)
        self.__predicate = predicate

    def is_hidden(self, handle):
        return self._eval_predicate(self.__predicate, handle.readable_node) or self._inner.is_hidden(handle)


class ExcludingNodesWrappedFilesystem(AbstractWrappedFilesystem):  # pylint: disable=abstract-method
    """
    Wrapper for filesystems that forcefully excludes some nodes.
    """
    # TODO check if all parent dirs are also not excluded?!

    def __init__(self, inner: lawwenda.fs.backend.Backend, predicate: FilesystemNodePredicate):
        """
        :param inner: The inner filesystem.
        :param predicate: The predicate that defines what nodes to exclude.
        """
        super().__init__(inner)
        self.__predicate = predicate

    def child_nodes(self, handle):  # TODO noh dedup
        return [handle.readable_node.child_by_name(n.name)
                for n in self._inner.child_nodes(self._inner.read_handle(
                    self._inner.node_by_path(handle.readable_node.path)))
                if not self._eval_predicate(self.__predicate, n)]

    def read_handle(self, node):
        if self._eval_predicate(self.__predicate, node):
            raise PermissionError(f"no read access for {node.path}")
        return self._inner.read_handle(node)  # TODO noh dangerous trap: must not use super() here (better api?!)

    def write_handle(self, node):
        if self._eval_predicate(self.__predicate, node):
            raise PermissionError(f"no write access for {node.path}")
        return self._inner.write_handle(node)


class ReadOnlyWrappedFilesystem(AbstractWrappedFilesystem):  # pylint: disable=abstract-method
    """
    Wrapper for filesystems that blocks all write accesses, making it a readonly filesystem.
    """

    def write_handle(self, node):
        raise PermissionError(f"no write access for {node.path}")
