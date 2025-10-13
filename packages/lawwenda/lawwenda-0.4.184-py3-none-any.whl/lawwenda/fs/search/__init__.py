# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
File search functionality.

Used by the Lawwenda user interface's 'Search' feature.
"""
import logging
import re
import subprocess
import typing as t
import urllib.parse

import lawwenda.asset.PiMetadataInterpreter.pimetadatainterpreter as pimetadatainterpreter

if t.TYPE_CHECKING:
    import lawwenda.fs


def _query_by_tree_traversal(
        node: "lawwenda.fs.node.Node",
        decide_func: t.Callable[["lawwenda.fs.node.Node"], bool]) -> "t.Iterable[lawwenda.fs.node.Node]":
    for node_, _ in node.traverse_dir(raise_on_circle=False):
        if decide_func(node_):
            yield node_


def _termstring_to_termlist(term: str) -> t.List[str]:
    return [ss for ss in [s.strip() for s in term.split(" ")] if ss]


class Search:
    """
    Base class for different search behaviors.
    """

    def query(self, node: "lawwenda.fs.node.Node") -> "t.Sequence[lawwenda.fs.node.Node]":
        """
        Return a list of nodes that match the criteria of this search, starting from a given root node.

        :param node: The root node. Query result nodes are usually inside that subtree.
        """
        raise NotImplementedError()


class DeeplySearch(Search):
    """
    Deep searches look for search terms in some places, like file names or comments, but also in fulltext indexes or -
    as a fallback - directly in the content of each file.

    This is a rather versatile search behavior, but is not precisely defined, and can be impractically slow if not
    fulltext index is available.
    """

    def __init__(self, term: str):
        self.__term = term
        self.__terms = _termstring_to_termlist(term.lower())

    def query(self, node):
        if not self.__terms:
            return []
        idxdata = self.__try_get_index(node)
        return self.__query_indexed(node, idxdata) if idxdata else self.__query_unindexed(node)

    def __try_get_index(self, node: "lawwenda.fs.node.Node") -> object:
        nodefullpath = node.system_path(writable=False)
        if not nodefullpath:
            return None
        try:
            recollans = subprocess.check_output(["recollq", "-m", "-a", "-c", "/data/daemondata/recoll", self.__term],
                                                stderr=subprocess.DEVNULL)
            return recollans, nodefullpath
        except OSError:
            return None

    @staticmethod
    def __query_indexed(node: "lawwenda.fs.node.Node", idxdata: object) -> "t.Iterable[lawwenda.fs.node.Node]":
        recollans, nodefullpath = idxdata
        nodefullpathlen = len(nodefullpath)
        if not nodefullpath.endswith("/"):
            nodefullpath += "/"
        for line in recollans.split(b"\n"):
            if line.startswith(b"url ="):
                url = line[5:].decode().strip()
                fullpath = urllib.parse.urlparse(url).path
                if fullpath.startswith(nodefullpath):
                    linepath = fullpath[nodefullpathlen:]
                    linenode = node.child_by_path(linepath)
                    if linenode.exists:
                        yield linenode

    def __query_unindexed(self, node: "lawwenda.fs.node.Node") -> "t.Iterable[lawwenda.fs.node.Node]":
        logging.debug("Searching deeply without recoll index.")
        return _query_by_tree_traversal(node, self.__decide_unindexed)

    def __decide_unindexed(self, node: "lawwenda.fs.node.Node") -> bool:
        return self.__decide_unindexed_by_metadata(node) or self.__decide_unindexed_by_content(node)

    def __decide_unindexed_by_metadata(self, node: "lawwenda.fs.node.Node") -> bool:
        for term in self.__terms:
            if term not in node.name.lower():
                break
        else:
            return True
        for term in self.__terms:
            if term not in node.comment.lower():
                break
        else:
            return True
        for term in self.__terms:
            for tag in node.tags:
                if term in tag.lower():
                    break
            else:
                break
        else:
            return True
        return False

    def __decide_unindexed_by_content(self, node: "lawwenda.fs.node.Node") -> bool:
        if node.is_file:
            try:
                with node.read_file() as f:
                    fcontenthead = f.read(10 * 1024 ** 2)
                for term in self.__terms:
                    for bterm in [term.encode(), term.encode("utf-16")]:
                        if re.search(re.escape(bterm), fcontenthead, re.IGNORECASE):
                            break
                    else:
                        break
                else:
                    return True
            except IOError as ex:
                logging.warning(ex)
        return False


class ByNameSearch(Search):
    """
    Searches for search terms in file names.

    See also :py:attr:`lawwenda.fs.node.Node.name`.
    """

    def __init__(self, term: str):
        self.__terms = _termstring_to_termlist(term.lower())

    def query(self, node):
        if not self.__terms:
            return []
        return _query_by_tree_traversal(node, self.__decide)

    def __decide(self, node: "lawwenda.fs.node.Node") -> bool:
        for term in self.__terms:
            if term not in node.name.lower():
                return False
        return True


class ByTagSearch(Search):
    """
    Searches for files that have particular tags.

    See also :py:attr:`lawwenda.fs.node.Node.tags`.
    """

    def __init__(self, term: str):
        self.__tags = _termstring_to_termlist(term)

    def query(self, node):
        if not self.__tags:
            return []
        return _query_by_tree_traversal(node, self.__decide)

    def __decide(self, node: "lawwenda.fs.node.Node") -> bool:
        for tag in self.__tags:
            if tag not in node.tags:
                return False
        return True


class ByGeoSearch(Search):
    """
    Searches for files that are associated with a particular geographic region.

    See also :py:attr:`lawwenda.fs.node.Node.geo`.
    """

    def __init__(self, position: str, *, radius: t.Union[str, float]):
        if position:
            self.__position = pimetadatainterpreter.GeoLocation.from_geostring(position)
            self.__position.set_accuracy_meters(float(radius or 0))
        else:
            self.__position = None

    def query(self, node):
        if not self.__position:
            return []
        return _query_by_tree_traversal(node, self.__decide)

    def __decide(self, node: "lawwenda.fs.node.Node") -> bool:
        if not node.geo_obj:
            return False
        return self.__position.distance_meters_interval(node.geo_obj)[0] <= 0


def create_search(mode: str, **kwargs) -> Search:
    """
    Return a Search object with a particular configuration.

    :param mode: The search mode string.
    :param kwargs: Additional search arguments, specific to the chosen `mode`.
    """
    if mode == "deeply":
        return DeeplySearch(**kwargs)
    if mode == "byname":
        return ByNameSearch(**kwargs)
    if mode == "bytag":
        return ByTagSearch(**kwargs)
    if mode == "bygeo":
        return ByGeoSearch(**kwargs)
    raise ValueError(f"Invalid mode: {mode}")
