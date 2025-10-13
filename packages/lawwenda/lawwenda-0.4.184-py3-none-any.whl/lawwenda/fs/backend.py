# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Lawwenda filesystem backend foundation.
"""
import datetime
import logging
import mimetypes
import os
import pathlib
import traceback
import typing as t

import lawwenda.fs.data
import lawwenda.fs.node
import lawwenda.fs.previewer


# pylint: disable=no-self-use,too-many-public-methods
class Backend:
    """
    Base class for filesystem implementations.

    Subclasses implement different kinds of filesystems, e.g. :py:class:`lawwenda.builtin.fs_backends.local.Backend`.

    DO NOT USE! The interface of this class is relevant for implementing custom filesystems only!
    See :py:class:`lawwenda.fs.node.Node` instead. Otherwise, things will break, even in security related ways!
    """

    class ReadHandle:
        """
        Read and write handles are just a stupid container that hold one :py:class:`lawwenda.fs.node.Node`.

        This looks stupid at first, because you could just use this node directly instead. The added value of handles
        are a central mechanism for access control, which would be a bit less obvious and more scattered in code without
        this indirection.

        Of course, it cannot avoid a way around it in code. An attacker that can change the code has won anyway. It just
        simplifies writing correct code that hopefully does not provide ways around it for the client.

        See :py:meth:`Backend.read_handle` and :py:meth:`Backend.write_handle`.
        """

        def __init__(self, node: "lawwenda.fs.node.Node"):
            self.readable_node = node

    class WriteHandle(ReadHandle):
        """
        See :py:class:`Backend.ReadHandle`.
        """

        def __init__(self, node: "lawwenda.fs.node.Node"):
            super().__init__(node)
            self.writable_node = node

    def __init__(self):
        """
        Do not use. See :py:func:`lawwenda.fs.factory.filesystem`.
        """
        import lawwenda.builtin.previewers.common_images as common_images
        import lawwenda.builtin.previewers.common_videos as common_videos
        self.__previewers = [common_images.Previewer(), common_videos.Previewer()]
        # TODO text, pdf, libreoffice, audio (without thumbnails though), ... ?!

    @staticmethod
    def sanitize_path(path: str) -> str:
        """
        Sanitize slashes in a path and returns a path in the form `/foo/bar`. See :py:attr:`lawwenda.fs.node.Node.path`.

        :param path: The input path.
        """
        path = os.path.abspath(f"/{path}")
        while "//" in path:
            path = path.replace("//", "/")
        while path[1:].endswith("/"):
            path = path[:-1]
        return path

    @property
    def root_node(self) -> "lawwenda.fs.node.Node":
        """
        The root node of this filesystem.
        """
        return self.node_by_path("")

    def node_by_path(self, path: str) -> "lawwenda.fs.node.Node":
        """
        Return a node by a given path.

        It will not fail, even if there is no such file or access would be denied.

        :param path: The path of the node to return, relative to the filesystem's root node.
        """
        return lawwenda.fs.node.Node(path, filesystem=self)

    def read_handle(self, node: "lawwenda.fs.node.Node") -> ReadHandle:
        """
        Return a read handle for a node.

        Such handles are needed for executing read actions on that node. See also :py:class:`Backend.ReadHandle`.

        :param node: The node to read from later.
        """
        return self.ReadHandle(node)

    def write_handle(self, node: "lawwenda.fs.node.Node") -> WriteHandle:
        """
        Return a write handle for a node.

        Such handles are needed for executing write actions on that node. See also :py:class:`Backend.WriteHandle`.

        :param node: The node to write from later.
        """
        return self.WriteHandle(node)

    def system_path(self, handle: ReadHandle|WriteHandle, *, writable: bool) -> pathlib.Path|None:
        """
        Try to return an absolute path in the local filesystem for a node (in a handle).

        This is optional and the default implementation returns `None`!

        :param handle: The read or write handle to a node.
        :param writable: Whether you might do any write accesses to the result path.
        """
        # pylint: disable=unused-argument
        return None

    def child_nodes(self, handle: ReadHandle) -> t.Iterable["lawwenda.fs.node.Node"]:
        """
        Return all child nodes for a node (in a handle).

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def is_hidden(self, handle: ReadHandle) -> bool:
        """
        Return whether a node (in a handle) is hidden.

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def is_dir(self, handle: ReadHandle) -> bool:
        """
        Return whether a node (in a handle) is a directory.

        This is also `True` for link nodes (see :py:meth:`is_link`) that point to a directory!

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def is_file(self, handle: ReadHandle) -> bool:
        """
        Return whether a node (in a handle) is a regular file.

        This is also `True` for link nodes (see :py:meth:`is_link`) that point to a file!

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def is_link(self, handle: ReadHandle) -> bool:
        """
        Return whether a node (in a handle) is a link. If this is a resolvable link, some of the other `is_` flags are
        `True` as well.

        Resolving links is always done internally by the filesystem implementation. It is usually not required to know
        the link target in order to use the node.

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def exists(self, handle: ReadHandle) -> bool:  # TODO noh review complete module
        """
        Return whether a node (in a handle) points to something that actually exists.

        This can e.g. be `False` for nodes coming from :py:meth:`node_by_path`.

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def size(self, handle: ReadHandle) -> int:
        """
        Return the size of a node (in a handle) in bytes.

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def mimetype(self, handle: ReadHandle) -> str:
        """
        Return the mimetype of a node (in a handle).

        :param handle: The read handle to a node.
        """
        return mimetypes.guess_type(handle.readable_node.name, strict=False)[0] or ""

    def mtime(self, handle: ReadHandle) -> datetime.datetime:
        """
        Return the 'last modified' time of a node (in a handle).

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def has_thumbnail(self, handle: ReadHandle) -> bool:
        """
        Return whether there could be a thumbnail available for a node (in a handle).

        See also :py:meth:`thumbnail`.

        There might be cases when it returns `True` but the thumbnail generation will fail.

        :param handle: The read handle to a node.
        """
        if not handle.readable_node.is_file:
            return False
        iar = lawwenda.fs.previewer.IsAbleRequest(handle.readable_node.name, handle.readable_node.mimetype)
        for previewer in self.__previewers:
            try:
                if previewer.is_thumbnailable(iar):
                    return True
            except Exception:  # pylint: disable=broad-except
                logging.error(traceback.format_exc())
        return False

    def has_preview(self, handle: ReadHandle) -> bool:
        """
        Return whether there could be a html preview snippet available for a node (in a handle).

        See also :py:meth:`preview_html`.

        There might be cases when it returns `True` but the preview generation will fail.

        :param handle: The read handle to a node.
        """
        if not handle.readable_node.is_file:
            return False
        iar = lawwenda.fs.previewer.IsAbleRequest(handle.readable_node.name, handle.readable_node.mimetype)
        for previewer in self.__previewers:
            try:
                if previewer.is_previewable(iar):
                    return True
            except Exception:  # pylint: disable=broad-except
                logging.error(traceback.format_exc())
        return False

    def preview_html(self, handle: ReadHandle) -> str:
        """
        Return an HTML snippet that shows a preview of a node (in a handle).

        This is larger and richer in terms of flexibility than thumbnails, and is typically used by the file details
        panel.

        See also :py:meth:`has_preview`.

        :param handle: The read handle to a node.
        """
        iar = lawwenda.fs.previewer.IsAbleRequest(handle.readable_node.name, handle.readable_node.mimetype)
        for previewer in self.__previewers:
            try:
                if previewer.is_previewable(iar):
                    return previewer.preview_html(handle.readable_node)
            except Exception:  # pylint: disable=broad-except
                logging.error(traceback.format_exc())
        return ""

    def thumbnail(self, handle: ReadHandle) -> bytes:
        """
        Return a thumbnail for a node (in a handle) in PNG format.

        See also :py:meth:`has_thumbnail`.

        :param handle: The read handle to a node.
        """
        iar = lawwenda.fs.previewer.IsAbleRequest(handle.readable_node.name, handle.readable_node.mimetype)
        for previewer in self.__previewers:
            try:
                if previewer.is_thumbnailable(iar):
                    return previewer.thumbnail(handle.readable_node)
            except Exception:  # pylint: disable=broad-except
                logging.error(traceback.format_exc())
        return b""

    def comment(self, handle: ReadHandle) -> str:
        """
        Return the comment assigned to a node (in a handle).

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def rating(self, handle: ReadHandle) -> int:
        """
        Return the rating assigned to a node (in a handle).

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def tags(self, handle: ReadHandle) -> t.Iterable[str]:
        """
        Return the tags that are assigned to a node (in a handle).

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def geo(self, handle: ReadHandle) -> "lawwenda.fs.data.GeoLocation|t.Dict[str, t.Any]":
        """
        Return the geographic location associated to a node (in a handle).

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def delete(self, handle: WriteHandle) -> None:
        """
        Delete a node (in a handle).

        :param handle: The write handle to a node.
        """
        raise NotImplementedError()

    def mkdir(self, handle: WriteHandle) -> None:
        """
        Make a node (in a handle) an existing directory.

        :param handle: The write handle to a node.
        """
        raise NotImplementedError()

    def copy_to(self, source: ReadHandle, destination: WriteHandle) -> None:
        """
        Copy a node (in a handle) to another node (in a handle).

        After copying, the destination node has similar characteristics as the source node, i.e. either is a file
        with the same content, or is a directory with the same subitems as the source.

        :param source: The read handle to the source node.
        :param destination: The write handle to the destination node.
        """
        raise NotImplementedError()

    def move_to(self, source: WriteHandle, destination: WriteHandle) -> None:
        """
        Move a node (in a handle) to another node (in a handle).

        This is similar to :py:meth:`copy_to`; see there for more details.

        :param source: The write handle to the source node.
        :param destination: The write handle to the destination node.
        """
        raise NotImplementedError()

    def set_comment(self, handle: WriteHandle, comment: str) -> None:
        """
        Set the comment for a node (in a handle).

        :param handle: The write handle to a node.
        :param comment: The new comment.
        """
        raise NotImplementedError()

    def set_geo(self, handle: WriteHandle, geo: str) -> None:
        """
        Set the geographic location for a node (in a handle).

        :param handle: The write handle to a node.
        :param geo: The new geographic location (as encoded string).
        """
        raise NotImplementedError()

    def set_rating(self, handle: WriteHandle, rating: int) -> None:
        """
        Set the rating for a node (in a handle).

        :param handle: The write handle to a node.
        :param rating: The new rating.
        """
        raise NotImplementedError()

    def add_tag(self, handle: WriteHandle, tag: str) -> None:
        """
        Add a tag to a node (in a handle).

        :param handle: The write handle to a node.
        :param tag: The tag to add.
        """
        raise NotImplementedError()

    def remove_tag(self, handle: WriteHandle, tag: str) -> None:
        """
        Remove a tag from a node (in a handle).

        :param handle: The write handle to a node.
        :param tag: The tag to remove.
        """
        raise NotImplementedError()

    def read_file(self, handle: ReadHandle) -> t.BinaryIO:
        """
        Return a file-like object for reading content of a node (in a handle).

        The caller must ensure that it gets closed after usage, usually by means of the Python `with` keyword.

        :param handle: The read handle to a node.
        """
        raise NotImplementedError()

    def write_file(self, handle: WriteHandle, content: bytes|t.BinaryIO) -> None:
        """
        Write content to a node (in a handle).

        This will overwrite its original content.

        :param handle: The write handle to a node.
        :param content: The binary content to write to the node.
        """
        raise NotImplementedError()

    def known_tags(self) -> t.Iterable[str]:
        """
        TODO
        """
        raise NotImplementedError()
