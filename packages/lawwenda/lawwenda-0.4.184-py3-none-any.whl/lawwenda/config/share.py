# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
User-side API for reading and modifying Lawwenda configurations, creating shares, and more.

For most cases, instantiate :py:class:`lawwenda.config.Configuration` and use some if its methods.
"""
import datetime
import os
import pathlib
import time
import typing as t

import lawwenda.config


# pylint: disable=too-many-locals,too-many-instance-attributes
class Share:
    """
    A directory path together with some parameters (e.g. for access control) for sharing via Lawwenda. Read the
    documentation for more about shares.
    """

    def __init__(self, path: pathlib.Path|str, *, configuration: "lawwenda.config.Configuration", name: str,
                 title: str, cache_tag: object, readonly: bool = True,
                 hide_by_patterns: t.Iterable[str] = (), hide_by_tags: t.Iterable[str] = (),
                 include_by_patterns: t.Iterable[str]|None = None,
                 include_by_tags: t.Iterable[str]|None = None,
                 exclude_by_patterns: t.Iterable[str] = (), exclude_by_tags: t.Iterable[str] = (),
                 exclude_hidden: bool = False,
                 password_scrypt: str|None = None, password_salt: str|None = None,
                 active_until_timestamp: float|None = None):
        """
        Do not use. Instantiated by the Lawwenda infrastructure.
        """
        self.__path = os.path.abspath(path)
        self.__configuration = configuration
        self.__name = name
        self.__title = title
        self.__cache_tag = cache_tag
        self.__readonly = readonly
        self.__hide_by_patterns = tuple(hide_by_patterns)
        self.__hide_by_tags = tuple(hide_by_tags)
        self.__include_by_patterns = None if include_by_patterns is None else tuple(include_by_patterns)
        self.__include_by_tags = None if include_by_tags is None else tuple(include_by_tags)
        self.__exclude_by_patterns = tuple(exclude_by_patterns)
        self.__exclude_by_tags = tuple(exclude_by_tags)
        self.__exclude_hidden = exclude_hidden
        self.__password_scrypt = password_scrypt or None
        self.__password_salt = password_salt
        self.__active_until_timestamp = active_until_timestamp

    @property
    def path(self) -> str:
        """
        The path of the share's root directory.
        """
        return self.__path

    @property
    def name(self) -> str:
        """
        The share name.

        This usually makes the last part of the url to this share. Is unique in the containing :py:attr:`configuration`.
        """
        return self.__name

    @property
    def configuration(self) -> "lawwenda.config.Configuration":
        """
        The configuration that contains this share.
        """
        return self.__configuration

    @property
    def title(self) -> str:
        """
        The share title.

        This is an arbitrary text shown in the window title. Should not contain line breaks and should be short.
        """
        return self.__title

    @property
    def readonly(self) -> bool:
        """
        If this share is restricted to only read actions (no removal, copying, uploading, editing, ... of the files and
        directories in :py:attr:`path`).
        """
        return self.__readonly

    @property
    def hide_by_patterns(self) -> t.Sequence[str]:
        """
        A list of regular expressions of paths for hiding.

        A file or directory will be hidden if its path matches at least one of them. Those paths are always relative to
        :py:attr:`path`, always start with a `'/'`, but never end with a one (unless it is the root path).

        Note that hiding is not a security feature unless :py:attr:`exclude_hidden` is set.
        """
        return self.__hide_by_patterns

    @property
    def hide_by_tags(self) -> t.Sequence[str]:
        """
        A list of tags for hiding files and directories.

        A file or directory will be hidden if it is tagged with at least one of them.

        Note that hiding is not a security feature unless :py:attr:`exclude_hidden` is set.
        """
        return self.__hide_by_tags

    @property
    def include_by_patterns(self) -> t.Sequence[str]|None:
        """
        A list of regular expressions of paths for including explicitly.

        Those paths are always relative to :py:attr:`path`, always start with a `'/'`, but never end with a one (unless
        it is the root path).

        If this is specified, the share will switch from blacklist to whitelist. Everything that is not considered as
        included is implicitly considered as excluded.
        """
        return self.__include_by_patterns

    @property
    def include_by_tags(self) -> t.Sequence[str]|None:
        """
        A list of tags for including files and directories.

        If this is specified, the share will switch from blacklist to whitelist. Everything that is not considered as
        included is implicitly considered as excluded.
        """
        return self.__include_by_tags

    @property
    def exclude_by_patterns(self) -> t.Sequence[str]:
        """
        A list of regular expressions of paths for excluding.

        A file or directory will be excluded if its path matches at least one of them. Those paths are always relative
        to :py:attr:`path`, always start with a `'/'`, but never end with a one (unless it is the root path).

        Exclusions are enforced on backend side and not just a presentation aspect. There is no way for a client to work
        around that (unless there is a software bug).
        """
        return self.__exclude_by_patterns

    @property
    def exclude_by_tags(self) -> t.Sequence[str]:
        """
        A list of tags for excluding files and directories.

        Exclusions are enforced on backend side and not just a presentation aspect. There is no way for a client to work
        around that (unless there is a software bug).
        """
        return self.__exclude_by_tags

    @property
    def exclude_hidden(self) -> bool:
        """
        If to consider 'hidden' flags of files or directories as exclusions.

        Exclusions are enforced on backend side and not just a presentation aspect. There is no way for a client to work
        around that (unless there is a software bug).
        """
        return self.__exclude_hidden

    @property
    def password_scrypt(self) -> str|None:
        """
        The scrypt hash of the password for this share.

        Empty or `None` for disabled password protection. See also :py:attr:`password_salt`.
        """
        return self.__password_scrypt

    @property
    def password_salt(self) -> str|None:
        """
        The hash salt of the password for this share, if password protected.

        See also :py:attr:`password_scrypt`.
        """
        return self.__password_salt

    @property
    def active_until(self) -> datetime.datetime|None:
        """
        The expiration time of this share, or `None` for infinite.
        """
        return datetime.datetime.fromtimestamp(self.active_until_timestamp) if self.active_until_timestamp else None

    @property
    def active_until_timestamp(self) -> float|None:
        """
        Same as :py:attr:`active_until`, but as Unix timestamp.
        """
        return self.__active_until_timestamp

    @property
    def is_active(self) -> bool:
        """
        If this share is currently active (e.g. not yet expired; see :py:attr:`active_until`).
        """
        return (not self.is_expired) and self.__cache_tag and (
                self.configuration.peek_share_cache_tag(self.name) == self.__cache_tag)

    @property
    def is_expired(self) -> bool:
        """
        If this share is expired.
        """
        return (self.active_until_timestamp is not None) and (self.active_until_timestamp < time.time())

    def __str__(self):
        return (f"Share {self.name}\n"
                f"- path: {self.path}\n"
                f"- title: {self.title}\n"
                f"- readonly: {self.readonly}\n"
                f"- active until timestamp: {self.active_until_timestamp}\n"
                f"- hide by patterns: {self.hide_by_patterns}\n"
                f"- hide by tags: {self.hide_by_tags}\n"
                f"- include by patterns: {self.include_by_patterns}\n"
                f"- include by tags: {self.include_by_tags}\n"
                f"- exclude by patterns: {self.exclude_by_patterns}\n"
                f"- exclude by tags: {self.exclude_by_tags}\n"
                f"- exclude hidden: {self.exclude_hidden}\n"
                f"- password protected: {bool(self.password_scrypt)}\n")

    def _to_dict(self):
        return {k: getattr(self, k) for k in ["path", "name", "title", "readonly",
                                              "hide_by_patterns", "hide_by_tags", "include_by_patterns",
                                              "include_by_tags", "exclude_by_patterns", "exclude_by_tags",
                                              "exclude_hidden", "password_scrypt", "password_salt",
                                              "active_until_timestamp"]}
