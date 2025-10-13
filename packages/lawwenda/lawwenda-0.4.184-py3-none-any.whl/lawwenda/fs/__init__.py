# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Lawwenda abstract filesystem.

Lawwenda usually shows a subtree of the local filesystem, but could also work with something completely different. This
module implements the basic infrastructure for that.

See :py:func:`lawwenda.fs.factory.filesystem`.
"""
import lawwenda.fs.node


class CircularTraversalError(IOError):
    """
    Raised when traversing a tree that has a circle (i.e. that is not really a tree), usually by an 'unfortunate' link.
    """


str(""" # TODO
def link_target(self, node: FilesystemNode, *, recursive: bool) -> t.Optional[FilesystemNode]:
    if not node.is_link:        return node
    lnktgt = os.readlink(self._path_to_fullpath(node.path))
    rlnktgt = os.path.relpath(lnktgt if os.path.isabs(lnktgt) else f"{node.dirpath}/{lnktgt}", self.__rootpath)
    result = self.node(rlnktgt)
    if recursive:        result = self.link_target(result, recursive=True)
    return result
""")
# TODO xx umask 007 ?!
# TODO xx occassionally crashes (at least with firefox dev tools open)
# TODO bytes instead of str for paths and filenames ?!
