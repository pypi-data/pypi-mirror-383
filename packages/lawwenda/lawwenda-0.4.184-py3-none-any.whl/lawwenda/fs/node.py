# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Lawwenda filesystem nodes.
"""
import datetime
import os
import pathlib
import typing as t

import lawwenda.asset.PiMetadataInterpreter.pimetadatainterpreter as pimetadatainterpreter
import lawwenda.fs.data


class Node:
    """
    A filesystem node. It represents a particular filesystem item (a file, directory, link, ...) in a particular
    filesystem, by some path. This may be an item that does not even exist (but maybe e.g. is going to be created).

    This interface provides all filesystem operations. All parts of code in Lawwenda and its plugins must use this
    interface.
    """

    def __init__(self, path: str, *, filesystem: "lawwenda.fs.backend.Backend"):
        """
        Do not use.

        In order to get a filesystem node, start with a root node (see :py:func:`lawwenda.fs.factory.filesystem`). Then
        use attributes and methods like :py:attr:`child_nodes` or :py:meth:`child_by_name`.
        """
        self.__path = lawwenda.fs.backend.Backend.sanitize_path(path)
        self.__filesystem = filesystem

    def __eq__(self, other):
        return isinstance(other, Node) and self.__path == other.__path and self.__filesystem == other.__filesystem

    def __hash__(self):
        return hash((self.__path, self.__filesystem))

    @property
    def path(self) -> str:
        """
        The path of this node (like :code:`"/foo/bar"`).

        This is similar to a Unix filesystem path, i.e. path segments are separated by `"/"`.

        This path will always be considered as relative to the root node of the :py:attr:`_filesystem` it is part
        of. It is not relative to '`/`' of your real filesystem (unless you have actually set up a
        :py:class:`Filesystem` that resembles your entire real filesystem).

        In detail, a path has the following pattern:

        - with a slash in the beginning
        - without a slash at the end (exception: root path)
        - without double slashes
        - with `..` and `.` resolved
        - root path: `/`
        """
        return self.__path

    @property
    def _filesystem(self) -> "lawwenda.fs.backend.Backend":
        return self.__filesystem

    @property
    def name(self) -> str:
        """
        The file name of the node.

        This is the last segment of :py:attr:`path`.
        """
        return os.path.basename(self.__path)

    @property
    def dirpath(self) -> str:
        """
        The directory path of the node.

        This is all but the last segment of :py:attr:`path`. Same as :py:attr:`path` of :py:attr:`parent_node`.
        """
        return os.path.dirname(self.__path)

    @property
    def is_writable(self) -> bool:
        """
        Whether the node is writable.
        """
        try:
            self.__filesystem.write_handle(self)
            return True
        except Exception:  # pylint: disable=broad-except
            return False

    @property
    def is_hidden(self) -> bool:
        """
        Whether the node is hidden.
        """
        return self.__filesystem.is_hidden(self.__filesystem.read_handle(self))

    @property
    def is_dir(self) -> bool:
        """
        Whether the node is a directory.

        This is also `True` for link nodes (see :py:meth:`is_link`) that point to a directory!
        """
        return self.__filesystem.is_dir(self.__filesystem.read_handle(self))

    @property
    def is_file(self) -> bool:
        """
        Whether the node is a regular file.

        This is also `True` for link nodes (see :py:meth:`is_link`) that point to a directory!
        """
        return self.__filesystem.is_file(self.__filesystem.read_handle(self))

    @property
    def is_link(self) -> bool:
        """
        Whether the node is a link. If this is a resolvable link, some of the other `is_` flags are `True` as well.

        Resolving links is always done internally by the filesystem implementation. It is usually not required to
        know the link target in order to use the node.
        """
        return self.__filesystem.is_link(self.__filesystem.read_handle(self))

    @property
    def exists(self) -> bool:
        """
        Whether a node points to something that actually exists.

        This can e.g. be `False` for nodes coming e.g. from :py:meth:`child_by_name`.
        """
        return self.__filesystem.exists(self.__filesystem.read_handle(self))

    @property
    def size(self) -> int:
        """
        The size of this node in bytes.
        """
        return self.__filesystem.size(self.__filesystem.read_handle(self))

    @property
    def mimetype(self) -> str:
        """
        The mimetype of this node.
        """
        return self.__filesystem.mimetype(self.__filesystem.read_handle(self)) or "application/octet-stream"

    @property
    def mtime(self) -> datetime.datetime:
        """
        The 'last modified' time of this node.
        """
        return self.__filesystem.mtime(self.__filesystem.read_handle(self))

    @property
    def mtime_ts(self) -> float:
        """
        Same as :py:attr:`mtime`, but as Unix timestamp.
        """
        return self.mtime.timestamp()

    @property
    def icon_name(self) -> str|None:
        """
        The recommended icon name for this node.
        """
        if self.has_thumbnail:
            return None
        if self.is_dir:
            return "dir"
        return "file"

    @property
    def has_thumbnail(self) -> bool:
        """
        Whether there could be a thumbnail available for this node.

        See also :py:meth:`thumbnail`.

        There might be cases when it returns `True` but the thumbnail generation will fail.
        """
        return self.__filesystem.has_thumbnail(self.__filesystem.read_handle(self))

    @property
    def has_preview(self) -> bool:
        """
        Whether there could be a html preview snippet available for this node.

        See also :py:attr:`preview_html`.

        There might be cases when it returns `True` but the preview generation will fail.
        """
        return self.__filesystem.has_preview(self.__filesystem.read_handle(self))

    @property
    def comment(self) -> str:
        """
        The node comment text.
        """
        return self.__filesystem.comment(self.__filesystem.read_handle(self))

    @property
    def rating(self) -> int:
        """
        The node rating.
        """
        return self.__filesystem.rating(self.__filesystem.read_handle(self))

    @property
    def tags(self) -> t.Sequence[str]:
        """
        The tags assigned to this node.
        """
        return tuple(self.__filesystem.tags(self.__filesystem.read_handle(self)))

    @property
    def tagstring(self) -> str:
        """
        The tags assigned to this node, encoded in one string.
        """
        return pimetadatainterpreter.TagAssignments.tags_to_tagstring(self.tags)

    @property
    def geo(self) -> str:
        """
        The geographic location associated to this node, encoded in a string.
        """
        geoobj = self.geo_obj
        return geoobj.to_geostring() if geoobj else ""

    @property
    def geo_obj(self) -> "lawwenda.fs.data.GeoLocation":
        """
        The geographic location associated to this node.
        """
        return self.__filesystem.geo(self.__filesystem.read_handle(self))

    @property
    def basics_as_dict(self):
        """
        Basic node data as dict.

        This is solely used internally for serialization.
        """
        return {k: getattr(self, k) for k in ["name", "dirpath", "is_dir", "is_file", "is_link", "size", "mtime_ts",
                                              "icon_name"]}

    @property
    def full_as_dict(self):
        """
        Complete node data as dict.

        This is solely used internally for serialization.
        """
        return {**{k: getattr(self, k) for k in ["comment", "rating", "tags", "geo", "preview_html"]},
                **self.basics_as_dict}

    @property
    def preview_html(self) -> str:
        """
        An HTML snippet that shows a preview of this node.

        This is larger and richer in terms of flexibility than thumbnails, and is typically used by the file details
        panel.

        See also :py:attr:`has_preview`.
        """
        return self.__filesystem.preview_html(self.__filesystem.read_handle(self))

    @property
    def child_nodes(self) -> t.Sequence["Node"]:
        """
        The list of child nodes, i.e. nodes for all files and subdirectories inside this node.

        This only makes sense on directory nodes and will be empty otherwise.
        """
        if not self.is_dir:
            return ()
        return tuple(self.__filesystem.child_nodes(self.__filesystem.read_handle(self)))

    @property
    def parent_node(self) -> "Node":
        """
        The parent node.

        This is `None` for the root node.
        """
        return None if self.path == "/" else self.child_by_path("..")

    def traverse_dir(self, *, raise_on_circle: bool,
                     param_path: str = "") -> t.Iterable[t.Tuple["Node", str]]:
        """
        Return paths from this node and all descendants (i.e. the subtree).

        :param raise_on_circle: If to raise an exception when there is a circle (due to links), instead of silently
                                skipping and continuing.
        :param param_path: Prefix for all output paths.
        """
        nodes = [(self, lawwenda.fs.backend.Backend.sanitize_path(param_path))]
        seen = set()
        while nodes:
            node, nparampath = nodes.pop()
            seenkey = node.path, node._filesystem  # pylint: disable=protected-access
            if seenkey in seen:
                if raise_on_circle:
                    raise lawwenda.fs.CircularTraversalError()
                continue
            seen.add(seenkey)
            yield node, nparampath
            for cnode in node.child_nodes:
                nodes.append((cnode, lawwenda.fs.backend.Backend.sanitize_path(f"{nparampath}/{cnode.name}")))

    def system_path(self, *, writable: bool) -> pathlib.Path|None:
        """
        Try to return an absolute path in the local filesystem for this node.

        You should usually not need this method, you should avoid to use it as good as you can, and when you use it,
        you must be very careful! This is due to the following reasons:

        - It allows you to get a path from a filesystem that is shared in a read-only way, but then accidentally
          make write accesses to it. Such a bug would obviously lead to a disastrous security hole. Avoid that by
          taking care of the `writable` argument!
        - Some :py:class`Filesystem`s might not support that at all and return `None`.
        - The method signature could change in later versions due to new access control features.

        :param writable: Whether you might do any write accesses to the result path. Never set to `False` without
                         understanding the security implications mentioned above.
        """
        handle = self.__filesystem.write_handle(self) if writable else self.__filesystem.read_handle(self)
        return self.__filesystem.system_path(handle, writable=writable)

    def child_by_name(self, name: str) -> "Node":
        """
        Return a child node by name.

        This will not fail for names that do not exist yet, but return a node that could be used for creating it.

        :param name: The file name of the child.
        """
        if name in (".", "..", "") or "/" in name:
            raise ValueError(f"invalid child name: {name}")
        return self.child_by_path(name)

    def child_by_path(self, path: str) -> "Node":
        """
        Return a child node by path.

        This will not fail for names that do not exist yet, but return a node that could be used for creating it.

        :param path: The relative file path of the child.
        """
        return self.__filesystem.node_by_path(f"{self.path}/{path}")

    def read_file(self) -> t.BinaryIO:
        """
        Return a file-like object for reading content of this node.

        The caller must ensure that it gets closed after usage, usually by means of the Python `with` keyword.
        """
        return self.__filesystem.read_file(self.__filesystem.read_handle(self))

    def thumbnail(self) -> bytes:
        """
        The thumbnail for this node in PNG format.

        See also :py:attr:`has_thumbnail`.
        """
        return self.__filesystem.thumbnail(self.__filesystem.read_handle(self))

    def delete(self) -> None:
        """
        Delete this node.
        """
        self.__filesystem.delete(self.__filesystem.write_handle(self))

    def mkdir(self) -> None:
        """
        Make this node an existing directory.
        """
        self.__filesystem.mkdir(self.__filesystem.write_handle(self))

    def copy_to(self, newpath: str) -> None:
        """
        Copy this node to a destination path.

        After copying, the destination has similar characteristics as this node, i.e. either is a file with the same
        content, or is a directory with the same subitems.

        :param newpath: The destination path.
        """
        self.__filesystem.copy_to(self.__filesystem.read_handle(self),
                                  self.__filesystem.write_handle(self.__filesystem.node_by_path(newpath)))

    def move_to(self, newpath: str) -> None:
        """
        Move this node to a destination path.

        After moving, the destination has similar characteristics as this node had, i.e. either is a file with the
        same content, or is a directory with the same subitems.

        :param newpath: The destination path.
        """
        self.__filesystem.move_to(self.__filesystem.write_handle(self),
                                  self.__filesystem.write_handle(self.__filesystem.node_by_path(newpath)))

    def set_comment(self, comment: str) -> None:
        """
        Set the comment for this node.

        :param comment: The new comment.
        """
        self.__filesystem.set_comment(self.__filesystem.write_handle(self), comment)

    def set_geo(self, geo: str) -> None:
        """
        Set the geographic location for this node.

        :param geo: The new geographic location (as encoded string).
        """
        self.__filesystem.set_geo(self.__filesystem.write_handle(self), geo)

    def set_rating(self, rating: int) -> None:
        """
        Set the rating for this node.

        :param rating: The new rating.
        """
        self.__filesystem.set_rating(self.__filesystem.write_handle(self), rating)

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to this node.

        :param tag: The tag to add.
        """
        self.__filesystem.add_tag(self.__filesystem.write_handle(self), tag)

    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from this node.

        :param tag: The tag to remove.
        """
        self.__filesystem.remove_tag(self.__filesystem.write_handle(self), tag)

    def write_file(self, content: t.Union[bytes, t.BinaryIO]) -> None:
        """
        Write content to this node.

        This will overwrite its original content.

        :param content: The binary content to write to the node.
        """
        self.__filesystem.write_file(self.__filesystem.write_handle(self), content)

    def known_tags(self) -> t.Sequence[str]:
        """
        TODO.
        """
        return tuple(self.__filesystem.known_tags())
