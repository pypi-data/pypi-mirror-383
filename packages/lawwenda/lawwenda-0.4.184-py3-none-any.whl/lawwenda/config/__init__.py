# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
User-side API for reading and modifying Lawwenda configurations, creating shares, and more.

For most cases, instantiate :py:class:`Configuration` and use some if its methods.
"""
import base64
import datetime
import hashlib
import json
import os
import pathlib
import time
import typing as t

import lawwenda.asset
import lawwenda.config.share
import lawwenda.utils.tiny_server


class Configuration:
    """
    Holds a Lawwenda configuration.
    A configuration typically holds some shares.
    Each running Lawwenda instance relates to a configuration, providing access to these shares as configured.
    """

    def __init__(self, config_dir: pathlib.Path|str|None = None):
        """
        :param config_dir: The path of the configuration directory. Will be created on demand if it does not exist.
                           Defaults to a location that is usual for your operating system.
        """
        self.__config_dir = pathlib.Path(config_dir or "/etc/lawwenda")
        self.__shares_config_dir = self.__config_dir / "shares"

    @property
    def config_dir(self) -> pathlib.Path:
        """
        The configuration directory.
        """
        return self.__config_dir

    def __str__(self):
        return f"Configuration in {self.config_dir!r}"

    def peek_share_cache_tag(self, name: str) -> object|None:
        """
        TODO.

        :param name: The share name.
        """
        try:
            return (self.__shares_config_dir / name).stat().st_mtime
        except OSError:
            return None

    def all_shares(self) -> t.Sequence["lawwenda.config.share.Share"]:
        """
        Return all shares that are currently part of this configuration.
        """
        if not self.__shares_config_dir.is_dir():
            return []
        result = None
        tnow = time.time()
        itries = 0
        while result is None:
            itries += 1
            try:
                result_ = []
                for share_config_file in self.__shares_config_dir.iterdir():
                    cache_tag = self.peek_share_cache_tag(share_config_file.name)
                    if not cache_tag:
                        raise OSError("No cache_tag.")

                    sharedict = json.loads(share_config_file.read_text())
                    if cache_tag != self.peek_share_cache_tag(share_config_file.name):
                        raise OSError("cache_tag changed.")
                    share = lawwenda.config.share.Share(**sharedict, configuration=self, cache_tag=cache_tag)
                    if share.is_expired:
                        self.remove_share(share.name)
                    elif share.is_active:
                        result_.append(share)
                    else:
                        raise OSError("Inactive share.")
                result = result_
            except IOError:
                if (time.time() - tnow > 10) and (itries > 100):
                    raise
        return result

    def share_by_name(self, name: str) -> "lawwenda.config.share.Share|None":
        """
        Return the share by a name (or `None` if it does not exist).
        """
        for share in self.all_shares():
            if share.name == name:
                return share
        return None

    def add_share(self, path: str, *, name: str, password: str|None,
                  title: str|None = None, readonly: bool = True,
                  hide_by_patterns: t.Iterable[str] = (), hide_by_tags: t.Iterable[str] = (),
                  include_by_patterns: t.Optional[t.Iterable[str]] = None,
                  include_by_tags: t.Optional[t.Iterable[str]] = None,
                  exclude_by_patterns: t.Iterable[str] = (), exclude_by_tags: t.Iterable[str] = (),
                  exclude_hidden: bool = False,
                  active_until: t.Optional[datetime.datetime] = None) -> "lawwenda.config.share.Share":
        """
        Add a new share.

        :param path: The directory to share. See :py:attr:`lawwenda.config.share.Share.path`.
        :param name: The unique name of the new share. See :py:attr:`lawwenda.config.share.Share.name`.
        :param password: The password to protect the share with.
        :param title: The share title. See :py:attr:`lawwenda.config.share.Share.title`.
        :param readonly: If to share in a read-only way. See :py:attr:`lawwenda.config.share.Share.readonly`.
        :param hide_by_patterns: See :py:attr:`lawwenda.config.share.Share.hide_by_patterns`.
        :param hide_by_tags: See :py:attr:`lawwenda.config.share.Share.hide_by_tags`.
        :param include_by_patterns: See :py:attr:`lawwenda.config.share.Share.include_by_patterns`.
        :param include_by_tags: See :py:attr:`lawwenda.config.share.Share.include_by_tags`.
        :param exclude_by_patterns: See :py:attr:`lawwenda.config.share.Share.exclude_by_patterns`.
        :param exclude_by_tags: See :py:attr:`lawwenda.config.share.Share.exclude_by_tags`.
        :param exclude_hidden: See :py:attr:`lawwenda.config.share.Share.exclude_hidden`.
        :param active_until: The optional expiration time of the share. See
                             :py:attr:`lawwenda.config.share.Share.active_until`.
        """
        self.__verify_valid_name(name)
        if self.share_by_name(name):
            raise ValueError(f"The name '{name}' is already in use.")

        if password:
            pwsalt = os.urandom(16)
            pwscrypt = hashlib.scrypt(password.encode(), salt=pwsalt, n=2**14, r=8, p=1)
            password_scrypt = base64.b64encode(pwscrypt).decode()
            password_salt = base64.b64encode(pwsalt).decode()
        else:
            password_scrypt = password_salt = None

        self.__shares_config_dir.mkdir(parents=True, exist_ok=True)
        (self.__shares_config_dir / name).write_text(json.dumps(lawwenda.config.share.Share(
            path, configuration=self, name=name, title=title or name, readonly=readonly,
            hide_by_patterns=hide_by_patterns, hide_by_tags=hide_by_tags,
            include_by_patterns=include_by_patterns, include_by_tags=include_by_tags,
            exclude_by_patterns=exclude_by_patterns, exclude_by_tags=exclude_by_tags,
            exclude_hidden=exclude_hidden, password_scrypt=password_scrypt, password_salt=password_salt,
            active_until_timestamp=active_until.timestamp() if active_until else None, cache_tag=None)._to_dict()))

        return self.share_by_name(name)

    def remove_share(self, name: str) -> None:
        """
        Remove a share.

        :param name: The name of the share to remove.
        """
        self.__verify_valid_name(name)
        (self.__shares_config_dir / name).unlink(missing_ok=True)

    def start_tiny_server(self) -> "lawwenda.utils.tiny_server._DevServerInfo":
        """
        Start a tiny local server for this configuration.

        Such a server can be used for trying, development, testing, and so on, but is not recommended for real usage.

        It will automatically find a free port and will return a control object that contains the full url, and more.
        """
        server = lawwenda.utils.tiny_server.start_tiny_server(self)  # TODO noh better text in readme (not blocking)
        print(f"Please browse to the the following base address, appended by a share name:\n"
              f" {server.url}")
        return server

    def generate_wsgi(self) -> str:
        """
        Generates a wsgi script for hosting Lawwenda in a web server.

        Read the 'Installation' section of the documentation for more details about what to do with it.
        """
        lawwenda_wsgi_file = lawwenda.asset.data.find_data_file("lawwenda.wsgi")
        if not lawwenda_wsgi_file:
            raise EnvironmentError("Your installation is not able to generate wsgi.")
        return lawwenda_wsgi_file.read_text().format(lawwenda_dir=repr(str(lawwenda.asset.data.lawwenda_package_dir)),
                                                     config_dir=repr(str(self.config_dir)))

    @staticmethod
    def __verify_valid_name(name: str) -> None:
        if (not name) or name != os.path.basename(name):
            raise ValueError(f"Invalid share name {name!r}")
