# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Local filesystem backend.
"""
import datetime
import os
import pathlib
import shutil
import stat

import lawwenda.asset.PiMetadataInterpreter.pimetadatainterpreter as pimetadatainterpreter

import lawwenda.fs.backend


# pylint: disable=too-many-public-methods
class Backend(lawwenda.fs.backend.Backend):
    """
    A filesystem backend that resembles a particular subtree of your real local filesystem.
    """

    def __init__(self, root_path: pathlib.Path|str):
        super().__init__()
        self.__root_path = pathlib.Path(root_path)

    def __path_to_system_path(self, path: pathlib.Path|str) -> pathlib.Path:
        result = pathlib.Path(Backend.sanitize_path(f"{self.__root_path}/{path}"))
        if not result.is_relative_to(self.__root_path):
            raise PermissionError(f"path '{path}' is outside of the specified filesystem.")
        return result

    def system_path(self, handle, *, writable):
        return self.__path_to_system_path(handle.writable_node.path if writable else handle.readable_node.path)

    def child_nodes(self, handle):
        result = []
        hpath = handle.readable_node.path
        for cname in os.listdir(self.__path_to_system_path(hpath)):
            result.append(self.node_by_path(f"{hpath}/{cname}"))
        return result

    def is_hidden(self, handle):
        return handle.readable_node.name.startswith(".")

    def is_dir(self, handle):
        return os.path.isdir(self.__path_to_system_path(handle.readable_node.path))

    def is_file(self, handle):
        return os.path.isfile(self.__path_to_system_path(handle.readable_node.path))

    def is_link(self, handle):
        return self.exists(handle) and stat.S_ISLNK(self.__path_to_system_path(handle.readable_node.path).lstat().st_mode)

    def exists(self, handle):
        return os.path.lexists(self.__path_to_system_path(handle.readable_node.path))

    def size(self, handle):
        return os.path.getsize(self.__path_to_system_path(handle.readable_node.path))

    def mtime(self, handle):
        nmtime = os.path.getmtime(self.__path_to_system_path(handle.readable_node.path))
        return datetime.datetime.fromtimestamp(nmtime)

    def comment(self, handle):
        return pimetadatainterpreter.get_interpreter(self.__path_to_system_path(handle.readable_node.path)).comment()

    def rating(self, handle):
        return pimetadatainterpreter.get_interpreter(self.__path_to_system_path(handle.readable_node.path)).rating()

    def tags(self, handle):
        return [tg.tagname() for tg in pimetadatainterpreter.get_interpreter(self.__path_to_system_path(
            handle.readable_node.path)).tags()]

    def geo(self, handle):
        return pimetadatainterpreter.get_interpreter(self.__path_to_system_path(handle.readable_node.path)).geo()

    def delete(self, handle):
        hfullpath = self.__path_to_system_path(handle.writable_node.path)
        if handle.writable_node.is_link:
            os.unlink(hfullpath)
        elif handle.writable_node.is_dir:
            shutil.rmtree(hfullpath)
        else:
            os.unlink(hfullpath)

    def mkdir(self, handle):
        os.makedirs(self.__path_to_system_path(handle.writable_node.path), exist_ok=True)

    def copy_to(self, source, destination):
        # TODO xx metadata, xattr, ... (also for dirs!)
        # TODO what with links
        srcreadnode = source.readable_node
        destwritenode = destination.writable_node
        if srcreadnode.is_dir:
            destwritenode.mkdir()
            for child in srcreadnode.child_nodes:
                self.copy_to(self.read_handle(child), self.write_handle(destwritenode.child_by_name(child.name)))
        else:
            shutil.copyfile(self.__path_to_system_path(srcreadnode.path),
                            self.__path_to_system_path(destwritenode.path))

    def move_to(self, source, destination):
        os.rename(self.__path_to_system_path(source.writable_node.path),
                  self.__path_to_system_path(destination.writable_node.path))

    def set_comment(self, handle, comment):
        pimetadatainterpreter.get_interpreter(self.__path_to_system_path(handle.writable_node.path)).set_comment(comment)

    def set_geo(self, handle, geo):
        pimetadatainterpreter.get_interpreter(self.__path_to_system_path(handle.writable_node.path)).set_geo(geo)

    def set_rating(self, handle, rating):
        pimetadatainterpreter.get_interpreter(self.__path_to_system_path(handle.writable_node.path)).set_rating(rating)

    def add_tag(self, handle, tag):
        pimetadatainterpreter.get_interpreter(self.__path_to_system_path(handle.writable_node.path)).add_tag(tagname=tag)

    def remove_tag(self, handle, tag):
        pimetadatainterpreter.get_interpreter(self.__path_to_system_path(handle.writable_node.path)).remove_tag(tag)

    def read_file(self, handle):
        return open(self.__path_to_system_path(handle.readable_node.path), "rb")

    def write_file(self, handle, content):
        handle.writable_node.parent_node.mkdir()
        with open(self.__path_to_system_path(handle.writable_node.path), "wb") as f:
            if isinstance(content, bytes):
                f.write(content)
            else:
                while True:
                    buf = content.read(8096)
                    if len(buf) == 0:
                        break
                    f.write(buf)

    def known_tags(self):
        return ["foo", "bar", "baz"]
