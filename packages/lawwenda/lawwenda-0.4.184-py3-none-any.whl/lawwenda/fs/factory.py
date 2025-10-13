# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Creating Lawwenda filesystems.
"""
import re
import typing as t

import lawwenda.builtin.fs_backends.local
import lawwenda.config.share
import lawwenda.fs.backend
import lawwenda.fs.wrappers


def filesystem(root_path: str, *, readonly: bool = False,
               hide_by_patterns: t.Iterable[str] = (), hide_by_tags: t.Iterable[str] = (),
               include_by_patterns: t.Iterable[str]|None = None,
               include_by_tags: t.Iterable[str]|None = None,
               exclude_by_patterns: t.Iterable[str] = (), exclude_by_tags: t.Iterable[str] = (),
               exclude_hidden: bool = False) -> lawwenda.fs.node.Node:
    """
    Create a filesystem resembling a particular subtree of your real local filesystem, with some configuration for
    access control and more, and return its root node.

    :param root_path: The path from your real local filesystem to consider as the root directory.
    :param readonly: See :py:attr:`lawwenda.config.share.Share.readonly`.
    :param hide_by_patterns: See :py:attr:`lawwenda.config.share.Share.hide_by_patterns`.
    :param hide_by_tags: See :py:attr:`lawwenda.config.share.Share.hide_by_tags`.
    :param include_by_patterns: See :py:attr:`lawwenda.config.share.Share.include_by_patterns`.
    :param include_by_tags: See :py:attr:`lawwenda.config.share.Share.include_by_tags`.
    :param exclude_by_patterns: See :py:attr:`lawwenda.config.share.Share.exclude_by_patterns`.
    :param exclude_by_tags: See :py:attr:`lawwenda.config.share.Share.exclude_by_tags`.
    :param exclude_hidden: See :py:attr:`lawwenda.config.share.Share.exclude_hidden`.
    """
    # TODO refactor and test all this scariness
    return _configured_filesystem(lawwenda.builtin.fs_backends.local.Backend(root_path), readonly=readonly,
                                  hide_by_patterns=hide_by_patterns, hide_by_tags=hide_by_tags,
                                  include_by_patterns=include_by_patterns, include_by_tags=include_by_tags,
                                  exclude_by_patterns=exclude_by_patterns, exclude_by_tags=exclude_by_tags,
                                  exclude_hidden=exclude_hidden).root_node


def _configured_filesystem(filesystem: lawwenda.fs.backend.Backend, *, readonly: bool = False,
                           hide_by_patterns: t.Iterable[str] = (), hide_by_tags: t.Iterable[str] = (),
                           include_by_patterns: t.Iterable[str]|None = None,
                           include_by_tags: t.Iterable[str]|None = None,
                           exclude_by_patterns: t.Iterable[str] = (), exclude_by_tags: t.Iterable[str] = (),
                           exclude_hidden: bool = False) -> lawwenda.fs.backend.Backend:
    """
    Decorates a filesystem with some access control and more.

    :param filesystem: The filesystem to decorate.
    :param readonly: See :py:attr:`lawwenda.config.share.Share.readonly`.
    :param hide_by_patterns: See :py:attr:`lawwenda.config.share.Share.hide_by_patterns`.
    :param hide_by_tags: See :py:attr:`lawwenda.config.share.Share.hide_by_tags`.
    :param include_by_patterns: See :py:attr:`lawwenda.config.share.Share.include_by_patterns`.
    :param include_by_tags: See :py:attr:`lawwenda.config.share.Share.include_by_tags`.
    :param exclude_by_patterns: See :py:attr:`lawwenda.config.share.Share.exclude_by_patterns`.
    :param exclude_by_tags: See :py:attr:`lawwenda.config.share.Share.exclude_by_tags`.
    :param exclude_hidden: See :py:attr:`lawwenda.config.share.Share.exclude_hidden`.
    """
    # pylint: disable=too-many-locals
    if readonly:
        filesystem = lawwenda.fs.wrappers.ReadOnlyWrappedFilesystem(filesystem)

    hide_predicates = []
    for hide_by_pattern in hide_by_patterns:
        hide_predicates.append(_path_matches_regexp(hide_by_pattern))
    for hide_by_tag in hide_by_tags:
        hide_predicates.append(_has_tag(hide_by_tag))
    if hide_predicates:
        filesystem = lawwenda.fs.wrappers.HidingNodesWrappedFilesystem(filesystem, _any(hide_predicates))

    exclude_predicates = []
    for exclude_by_pattern in exclude_by_patterns:
        exclude_predicates.append(_path_matches_regexp(exclude_by_pattern))
    for exclude_by_tag in exclude_by_tags:
        exclude_predicates.append(_has_tag(exclude_by_tag))
    if exclude_hidden:
        exclude_predicates.append(lambda node: node.is_hidden)

    if (include_by_patterns is not None) or (include_by_tags is not None):
        include_predicates = []
        for include_by_pattern in include_by_patterns or []:
            include_predicates.append(_path_matches_regexp(include_by_pattern))
        for include_by_tag in include_by_tags or []:
            include_predicates.append(_has_tag(include_by_tag))
        exclude_predicates.append(_not(_descending(_any(include_predicates))))

    if exclude_predicates:
        filesystem = lawwenda.fs.wrappers.ExcludingNodesWrappedFilesystem(filesystem, _any(exclude_predicates))

    return filesystem


def _any(predicates: t.Iterable["lawwenda.fs.wrappers.FilesystemNodePredicate"]
         ) -> "lawwenda.fs.wrappers.FilesystemNodePredicate":
    """
    Return a predicate that returns `True` iff at least one of the input predicates return `True`.

    :param predicates: The input predicates.
    """
    def predicate_(node):
        return any(predicate(node) for predicate in predicates)
    return predicate_


def _not(predicate: "lawwenda.fs.wrappers.FilesystemNodePredicate") -> "lawwenda.fs.wrappers.FilesystemNodePredicate":
    """
    Return a predicate that inverts the input predicate.

    :param predicate: The input predicate.
    """
    def predicate_(node):
        return not predicate(node)
    return predicate_


def _descending(predicate: "lawwenda.fs.wrappers.FilesystemNodePredicate"
                ) -> "lawwenda.fs.wrappers.FilesystemNodePredicate":
    """
    Return a predicate that returns `True` iff the input predicate returns `True` for the input node and/or some
    nodes in its subtree (if it is a directory).

    :param predicate: The input predicate.
    """
    def predicate_(node):  # TODO cache
        return any(predicate(node_) for node_, _ in node.traverse_dir(raise_on_circle=False))
    return predicate_


def _path_matches_regexp(regexp: str) -> "lawwenda.fs.wrappers.FilesystemNodePredicate":
    """
    Return a predicate that returns `True` for input nodes whose :py:attr:`node.Node.path` fully matches the given
    regular expression.

    :param regexp: The regular expression string.
    """
    re_pattern = re.compile(regexp)
    def predicate_(node):
        return bool(re_pattern.fullmatch(node.path))
    return predicate_


def _has_tag(tag: str) -> "lawwenda.fs.wrappers.FilesystemNodePredicate":
    """
    Return a predicate that returns `True` for input nodes whose :py:attr:`node.Node.tags` contain the given
    tag.

    :param tag: The tag to look for.
    """
    def predicate_(node):
        return tag in node.tags
    return predicate_
