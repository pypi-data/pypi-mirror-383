# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
WebDAV properties.
"""
import typing as t
import xml.etree.ElementTree as ET

import werkzeug.http

import lawwenda.fs


all_props = []


def register_prop(prop: type["DavProp"]) -> type["DavProp"]:
    """
    Register a DavProp implementation.

    Returns the same type afterward, so it can be used as class decorator.

    :param prop: A subclass of DavProp.
    """
    all_props.append(prop())
    return prop


def get_prop_by_davname(davname: str) -> t.Optional["DavProp"]:
    """
    Return a DavProp by name or `None` if no such ones exist.

    :param davname: The name to find, as used in WebDAV.
    """
    for prop in all_props:
        if prop.davname == davname:
            return prop
    return None


class DavProp:
    """
    Base class for WebDAV properties.

    Each subclass implements one particular property as used in e.g. `PROPFIND` requests.

    Must be registered with :py:func:`register_prop`.
    """

    def __init__(self, davname: str, *, is_writable: bool):
        self.__davname = davname
        self.__is_writable = is_writable

    @property
    def davname(self) -> str:
        """
        The name of this property.
        """
        return self.__davname

    @property
    def is_writable(self) -> bool:
        """
        Whether this property can also be modified (in contrast to read-only properties like the file size).
        """
        return self.__is_writable

    def get_for_node(self, node: lawwenda.fs.node.Node) -> str|None:
        """
        Return the property value for a node.

        :param node: The node to inquire.
        """


@register_prop
class ResourceTypeDavProp(DavProp):
    """
    The WebDAV `resourcetype` property.
    """

    def __init__(self):
        super().__init__("{DAV:}resourcetype", is_writable=False)

    def get_for_node(self, node):
        return ET.Element("{DAV:}collection") if node.is_dir else ""


@register_prop
class SizeDavProp(DavProp):
    """
    The WebDAV `getcontentlength` property.
    """

    def __init__(self):
        super().__init__("{DAV:}getcontentlength", is_writable=False)

    def get_for_node(self, node):
        return node.size


@register_prop
class MtimeDavProp(DavProp):
    """
    The WebDAV `getlastmodified` property.
    """

    def __init__(self):
        super().__init__("{DAV:}getlastmodified", is_writable=False)

    def get_for_node(self, node):
        return werkzeug.http.http_date(node.mtime_ts)


@register_prop
class CommentDavProp(DavProp):  # TODO noh implement write access
    """
    Custom WebDAV property `{DAV:xattr}xdg.comment` that mirrors :py:attr:`lawwenda.fs.node.Node.comment`.
    """

    def __init__(self):
        super().__init__("{DAV:xattr}xdg.comment", is_writable=True)

    def get_for_node(self, node):
        return node.comment


@register_prop
class TagsDavProp(DavProp):
    """
    Custom WebDAV property `{DAV:xattr}xdg.tags` that mirrors :py:attr:`lawwenda.fs.node.Node.tagstring`.
    """

    def __init__(self):
        super().__init__("{DAV:xattr}xdg.tags", is_writable=True)

    def get_for_node(self, node):
        return node.tagstring


@register_prop
class RatingDavProp(DavProp):
    """
    Custom WebDAV property `{DAV:xattr}baloo.rating` that mirrors :py:attr:`lawwenda.fs.node.Node.rating`.
    """

    def __init__(self):
        super().__init__("{DAV:xattr}baloo.rating", is_writable=True)

    def get_for_node(self, node):
        return node.rating


@register_prop
class GeoDavProp(DavProp):
    """
    Custom WebDAV property `{DAV:xattr}pino.geo` that mirrors :py:attr:`lawwenda.fs.node.Node.geo`.
    """

    def __init__(self):
        super().__init__("{DAV:xattr}pino.geo", is_writable=True)

    def get_for_node(self, node):
        return node.geo
