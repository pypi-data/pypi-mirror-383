#!/usr/bin/python3

# SPDX-FileCopyrightText: © 2018 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only

import argparse
import functools
import json
import math
import os
import re
import sys
import threading
import urllib.parse


class PiMetadataInterpreterError(Exception):
    """
    Exception subclass for any errors raised by us.
    """

    def __call__(self, *args):
        return self.__class__(*(self.args + args))


class TagDuplicateError(PiMetadataInterpreterError):
    """
    Exception for tag duplicates occurred.
    """

    def __init__(self, newtagstring, existingtagstring):
        super().__init__(f"new tag '{newtagstring}' would be a duplicate of '{existingtagstring}'")
        self.newtagstring = newtagstring
        self.existingtagstring = existingtagstring


class MetadataFormatError(PiMetadataInterpreterError):
    pass


class TagAssignment:
    """
    The assignment of one tag to one file (or directory).
    """

    def __init__(self, tagname, filepath=None):
        """
        :param tagname: The tag name.
        :param filepath: The path this assignment is associated with.
        """
        self._filepath = None
        self._tagname = tagname
        self.set_filepath(filepath)

    def __repr__(self):
        return f"TagAssignment({repr(self.tagname())}, filepath={repr(self.filepath())})"

    def set_filepath(self, filepath):
        """
        Sets the path this assignment is associated with. Typically used internally.
        """
        self._filepath = None if (filepath is None) else os.path.abspath(filepath)

    def filepath(self):
        """
        Returns the path this assignment is associated with.
        """
        return self._filepath

    def tagname(self):
        """
        Returns the tag name.
        """
        return self._tagname

    def to_tagstring(self):
        """
        Returns a string representation.
        See TagAssignment.from_tagstring.
        """
        return urllib.parse.quote(self._tagname)

    @staticmethod
    def from_tagstring(tagstring, filepath=None):
        """
        Creates a TagAssignment from a tagstring (like `"baz"`).
        See TagAssignment.to_tagstring and TagAssignments.from_tagsstring.

        :param tagstring: A tagstring.
        :param filepath: The file this assignment are associated with.
        """
        return TagAssignment(urllib.parse.unquote_plus(tagstring), filepath)


class TagAssignments:
    """
    This class provides storage and management for the tag assignments of a file.
    Typically you should not need to create instances directly. See methods for tag handling in MetadataInterpreter.
    """

    def __init__(self, filepath):
        self._filepath = os.path.abspath(filepath)
        self._assignments = []
        self._assignments_sorted = True

    def filepath(self):
        """
        Returns the file path this assignments are associated with.
        Note: Individual assignments may have own filepaths.
        """
        return self._filepath

    def assignments(self, *, exclude_outlying=False):
        """
        Returns all tag assignments as list of TagAssignment.

        :param exclude_outlying: If to exclude assignments, which came from parent directories.
        """
        if not self._assignments_sorted:
            self._assignments.sort(key=lambda a: a.tagname())
            self._assignments_sorted = True
        return list([x for x in self._assignments if (not exclude_outlying) or (not self.is_outlying_assignment(x))])

    def add_assignment(self, a, filepath=None):
        """
        Adds a tag assignment.

        :param a: The TagAssignment to add.
        :param filepath: The filepath to associate this assignment with.
        """
        if isinstance(a, str):
            a = TagAssignment.from_tagstring(a)
        for taa in self.assignments(exclude_outlying=True):
            if taa.tagname() == a.tagname():
                raise TagDuplicateError(a.to_tagstring(), taa.to_tagstring())
        if filepath is None:
            filepath = self.filepath()
        a.set_filepath(filepath)
        self._assignments.append(a)
        self._assignments_sorted = False
        return a

    def find_assignments_by_tagname(self, tagname, *, exclude_outlying=False):
        """
        Returns any assignments matching a given tag name.

        :param tagname: A tag name.
        :param exclude_outlying: If to exclude assignments, which came from parent directories.
        """
        res = []  # in some situation (e.g. after some usages of add_assignment, there can be more than one)
        for ta in self.assignments(exclude_outlying=exclude_outlying):
            if ta.tagname() == tagname:
                res.append(ta)
        return res

    def remove_assignments_by_tagname(self, tagname, *, _exclude_outlying_INTERNAL=True):
        """
        Removes any assignments matching a given tag name.

        :param tagname: A tag name.
        """
        la = self.find_assignments_by_tagname(tagname, exclude_outlying=_exclude_outlying_INTERNAL)
        for ta in la:
            self._assignments.remove(ta)
        return len(la)

    def remove_assignments_by_tagstring(self, tagstring, *, _exclude_outlying_INTERNAL=True):
        """
        Removes any assignments matching a given tagstring.

        :param tagstring: A tagstring.
        """
        n = 0
        ts1 = TagAssignment.from_tagstring(tagstring).to_tagstring()
        for ta in self.assignments(exclude_outlying=_exclude_outlying_INTERNAL):
            if ts1 == ta.to_tagstring():
                self._assignments.remove(ta)
                n += 1
        return n

    @staticmethod
    def check_is_outlying_assignment(bfilepath, a):
        """
        Like TagAssignments.is_outlying_assignment when no instance is available.

        :param bfilepath: The path to assume as the original one.
        :param a: The TagAssignment to check.
        """
        return a.filepath() != bfilepath

    def is_outlying_assignment(self, a):
        """
        Checks if an assignment is outlying (i.e. not directly assigned to this file, but to a parent directory).

        :param a: The TagAssignment to check.
        """
        return TagAssignments.check_is_outlying_assignment(self.filepath(), a)

    def merge_assignments(self, srcas):
        """
        Merges all relevant assignments from another instance into this one.

        :param srcas: The other TagAssignments.
        """
        for srca in srcas.assignments():
            fp = f"{self.filepath()}/"
            afp = f"{srca.filepath()}/"
            do_add = not self.is_outlying_assignment(srca)
            do_add = do_add or fp.startswith(afp)
            if do_add:
                for taa in self.assignments():
                    if taa.tagname() == srca.tagname():
                        tafp = f"{taa.filepath()}/"
                        if afp.startswith(tafp):
                            # what we try to add is at least as deep as the existing one -> drop it
                            do_add = False
                        else:
                            # what we try to add is higher -> we prefer the new one
                            self.remove_assignments_by_tagname(srca.tagname(), _exclude_outlying_INTERNAL=False)
            if do_add:
                self.add_assignment(srca.to_tagstring(), srca.filepath())

    def to_tagsstring(self, *, exclude_outlying=True):
        """
        Returns a string representation.
        See TagAssignments.from_tagsstring.

        :param exclude_outlying: If to exclude assignments, which came from parent directories.
        """
        return self.tags_to_tagstring([x.to_tagstring() for x in self.assignments(exclude_outlying=exclude_outlying)])

    @staticmethod
    def tags_to_tagstring(tags):
        return ",".join(tags)

    @staticmethod
    def from_tagsstring(s, filepath):
        """
        Creates a TagAssignments from a tagsstring (like `"bar baz?deep ... foo"`).
        See TagAssignments.to_tagsstring.
        - A 'tagsstring' is the raw content of the user.xdg.tags xattr for a particular file/dir.
         - In some contexts it may also be a list of strings. This is equal to joining them together using ","
           as separator. The following text mostly ignores this representation.
        - A tagsstring describes a ","-joint list of tagstrings (note: singular), like this:
          "tagstring1,tagstring2,...,tagstringN"
        - A tagstring fully describes one tag assignment to the particular file/dir. It includes the tag name.


        :param s: A tagsstring.
        :param filepath: The file this assignments are associated with.
        """
        if not isinstance(s, str):
            s = TagAssignments.tags_to_tagstring(s)  # ... assuming it is list-like then
        res = TagAssignments(filepath)
        for tagstring in [ss.strip() for ss in s.split(",")]:
            if tagstring:
                res.add_assignment(TagAssignment.from_tagstring(tagstring))
        return res


class GeoLocation:
    """
    A location on earth.
    """

    GEOATTKEY_LAT = "lat"
    GEOATTKEY_LON = "lon"
    GEOATTKEY_ACCURACY = "acc"

    def __init__(self, *, lat, lon, accuracy_meters=None, **kwargs):
        """
        :param lat: The latitude in degrees.
        :param lon: The longitude in degrees.
        :param accuracy_meters: The accuracy in meters.
        :param kwargs: Additional attributes.
        """
        self._geoatts = dict(kwargs)
        self.set_lat(lat)
        self.set_lon(lon)
        if accuracy_meters is not None:
            accm = accuracy_meters
        else:
            accm = self.get_geoatt(GeoLocation.GEOATTKEY_ACCURACY, defaultval=0)
        self.set_accuracy_meters(accm)

    def __repr__(self):
        return "GeoLocation({})".format(", ".join([xk+"="+repr(xv) for xk, xv in self._geoatts.items()]))

    def distance_meters(self, theo):
        """
        Returns the point distance (respecting accuracy) between this location and another one in meters.

        :param theo: The other GeoLocation.
        """
        r = 6371000
        slat = self.lat()
        tlat = theo.lat()
        phi1 = math.radians(slat)
        phi2 = math.radians(tlat)
        dphi = math.radians(tlat - slat)
        dl = math.radians(theo.lon() - self.lon())
        xa = math.sin(dphi / 2) * math.sin(dphi / 2) + math.cos(phi1) * math.cos(phi2) * \
                                                       math.sin(dl / 2) * math.sin(dl / 2)
        c = 2 * math.atan2(math.sqrt(xa), math.sqrt(1 - xa))
        return r * c

    def distance_meters_interval(self, theo):
        """
        Returns the minimum and maximum distance (respecting accuracy) between this location and another one in meters.

        :param theo: The other GeoLocation.
        """
        dm = self.distance_meters(theo)
        delta = (self.accuracy_meters() + theo.accuracy_meters())
        return max(0, dm-delta), dm+delta

    def lat(self):
        """
        Returns the latitude of this location in degrees.
        """
        return float(self.get_geoatt(GeoLocation.GEOATTKEY_LAT, 0))

    def lon(self):
        """
        Returns the longitude of this location in degrees.
        """
        return float(self.get_geoatt(GeoLocation.GEOATTKEY_LON, 0))

    def accuracy_meters(self):
        """
        Returns the accuracy of this location in meters.
        """
        return float(self.get_geoatt(GeoLocation.GEOATTKEY_ACCURACY, 0))

    def set_lat(self, v):
        """
        Sets the latitude of this location in degrees.
        """
        v = float(v)
        while v < -180:
            v += 360
        while v > 180:
            v -= 360
        self.set_geoatt(GeoLocation.GEOATTKEY_LAT, v)

    def set_lon(self, v):
        """
        Sets the longitude of this location in degrees.
        """
        v = float(v)
        while v < -180:
            v += 360
        while v > 180:
            v -= 360
        self.set_geoatt(GeoLocation.GEOATTKEY_LON, v)

    def set_accuracy_meters(self, v):
        """
        Sets the accuracy of this location in meters.
        """
        self.set_geoatt(GeoLocation.GEOATTKEY_ACCURACY, float(v or 0))

    def set_geoatt(self, key, value):
        """
        Sets an attribute value for a key.
        """
        self._geoatts[key] = value

    def get_geoatt(self, key, defaultval=None):
        """
        Returns the attribute value stored for a given key. 
        """
        return self._geoatts.get(key, defaultval)

    def unset_geoatt(self, key):
        """
        Unsets a key in the attributes.
        """
        self._geoatts.pop(key, None)

    def geoattkeys(self):
        """
        Returns a list of all attribute keys stored for this location.
        """
        return list(sorted(self._geoatts.keys()))

    def to_geostring(self):
        """
        Returns a string representation.
        See GeoLocation.from_geostring.
        """
        def sortkeyfct(gx):
            k = gx[0]
            iislat = 0 if (k == GeoLocation.GEOATTKEY_LAT) else 1
            iislon = 0 if (k == GeoLocation.GEOATTKEY_LON) else 1
            return iislat, iislon, k
        lparams = list(sorted([(k, v) for k, v in self._geoatts.items()], key=sortkeyfct))
        for xx in lparams:
            if (xx[0] == GeoLocation.GEOATTKEY_ACCURACY) and (not xx[1]):
                lparams.remove(xx)
        return urllib.parse.urlencode(lparams)

    @staticmethod
    def from_geostring(s):
        """
        Creates a GeoLocation from a geostring (like `"lat=1&lon=2"`).
        See GeoLocation.to_geostring.

        :param s: A geostring.
        """
        kwgeoatts = {k: v[0] for k, v in urllib.parse.parse_qs(s).items()}
        lat = float(kwgeoatts.pop(GeoLocation.GEOATTKEY_LAT))
        lon = float(kwgeoatts.pop(GeoLocation.GEOATTKEY_LON))
        return GeoLocation(lat=lat, lon=lon, **kwgeoatts)


class XattrEngine:
    """
    The engine for handling extended attributes. For a custom xattr backend, subclass it and see get_interpreter.
    """

    def __init__(self, path):
        self.path = path

    def list_xattrs(self):
        """
        Returns a list of available extended attribute keys. Used internally. Without cache handling.
        You might add an own implementation of this (and some others) in a custom subclass for a custom xattr backend.
        """
        import xattr
        try:
            res = [z[13:] for z in
                   [y for y in [x.decode("utf-8") for x in xattr.list(self.path)] if y.startswith("user.")]]
        except Exception:
            res = []
        return res

    def get_xattr(self, key):
        """
        Gets an extended attribute; if key doesn't exist, it returns ''. Used internally. Without cache handling.
        You might add an own implementation of this (and some others) in a custom subclass for a custom xattr backend.
        """
        import xattr
        try:
            res = xattr.get(self.path, f"user.{key}").decode("utf-8")
        except Exception:
            res = ""
        return res

    def set_xattr(self, key, val):
        """
        Sets an extended attribute. Used internally. Without cache handling.
        You might add an own implementation of this (and some others) in a custom subclass for a custom xattr backend.
        """
        import xattr
        xattr.set(self.path, f"user.{key}", val.encode("utf-8"))

    def unset_xattr(self, key):
        """
        Unsets an extended attribute. Used internally. Without cache handling.
        You might add an own implementation of this (and some others) in a custom subclass for a custom xattr backend.
        """
        import xattr
        try:
            xattr.remove(self.path, f"user.{key}")
        except OSError as e:
            if e.errno != 61:  # 61: no data available; doesn't exist
                raise


class MetadataInterpreter:
    """
    Instances of this class allow to execute all kinds of operations on the metadata of files (and directories). They 
    are always bound to a particular file path.
    Don't construct instances directly, but use get_interpreter.
    """

    _cache_lock = threading.Lock()
    _cache_refcnt = 0
    _cache_xattrs = None

    XATTR_KEY_COMMENT = "xdg.comment"
    XATTR_KEY_GEO = "pino.geo"
    XATTR_KEY_RATING = "baloo.rating"
    XATTR_KEY_TAGS = "xdg.tags"

    @staticmethod
    def _clear_cache():
        """
        Used internally for clearing the cache.
        """
        with MetadataInterpreter._cache_lock:
            if MetadataInterpreter._cache_xattrs is not None:
                MetadataInterpreter._cache_xattrs.clear()

    class Cache:
        """
        Use this together with `with` for bundling some operations together for faster operations.
        """

        def __enter__(self):
            with MetadataInterpreter._cache_lock:
                if MetadataInterpreter._cache_refcnt == 0:
                    MetadataInterpreter._cache_xattrs = {}
                MetadataInterpreter._cache_refcnt += 1
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            with MetadataInterpreter._cache_lock:
                MetadataInterpreter._cache_refcnt -= 1
                if MetadataInterpreter._cache_refcnt == 0:
                    MetadataInterpreter._cache_xattrs = None

    def __init__(self, path, xattrengine):
        self._filepath = path
        self._xattrengine = xattrengine

    def filepath(self):
        """
        Returns the path to the file or directory this interpreter operates on.
        """
        return self._filepath

    def _list_xattrs(self):
        """
        Returns a list of available extended attribute keys. Used internally. Includes cache handling.
        """
        return self._xattrengine.list_xattrs()

    def _get_xattr(self, key):
        """
        Gets an extended attribute; if key doesn't exist, it returns ''. Used internally. Includes cache handling.
        """
        res = self
        fkey = (self._filepath, key)
        with MetadataInterpreter._cache_lock:
            if MetadataInterpreter._cache_xattrs is not None:
                res = MetadataInterpreter._cache_xattrs.get(fkey, self)
            if res == self:
                res = self._xattrengine.get_xattr(key)
                if MetadataInterpreter._cache_xattrs is not None:
                    MetadataInterpreter._cache_xattrs[fkey] = res
        return res

    def _set_xattr(self, key, val):
        """
        Sets an extended attribute. Used internally. Includes cache handling.
        """
        MetadataInterpreter._clear_cache()
        return self._xattrengine.set_xattr(key, val)

    def _unset_xattr(self, key):
        """
        Unsets an extended attribute. Used internally. Includes cache handling.
        """
        MetadataInterpreter._clear_cache()
        return self._xattrengine.unset_xattr(key)

    def get_tagassignments_flat(self):
        """
        Returns the assigned tags as TagAssignments instance. 
        It will contain only tags assigned directly to this file; see MetadataInterpreter.get_tagassignments.
        """
        return TagAssignments.from_tagsstring(self._get_xattr(self.XATTR_KEY_TAGS), self._filepath)

    def get_tagassignments(self):
        """
        Returns the assigned tags as TagAssignments instance. 
        It may also contain deep tags assigned to parent directories; see MetadataInterpreter.get_tagassignments_flat.
        """
        lfilepath = None
        filepath = self._filepath
        res = TagAssignments(self._filepath)
        while filepath != lfilepath:
            lfilepath = filepath
            res.merge_assignments(get_interpreter(filepath,
                                                  engineclass=type(self._xattrengine)).get_tagassignments_flat())
            filepath = os.path.dirname(filepath)
        return res

    def store_tagassignments(self, tas):
        """
        Sets assigned tags by a TagAssignments instance, potentially overwriting the existing ones.
        Beforehand you can get an instance with MetadataInterpreter.get_tagassignments_flat and edit it.

        :param tag: The new TagAssignments.
        """
        if self._filepath != tas.filepath():
            raise PiMetadataInterpreterError(f"this tag assignments are associated"
                                             f" with '{tas.filepath()}' instead of '{self._filepath}'")
        tasss = tas.to_tagsstring()
        if tasss:
            self._set_xattr(self.XATTR_KEY_TAGS, tasss)
        else:
            self._unset_xattr(self.XATTR_KEY_TAGS)

    def tags(self, *, full=True):
        """
        Returns all tags assigned as list of TagAssignment.

        :param full: If also parent directories shall be scanned (i.e. for 'deep' tags).
        """
        if full:
            res = self.get_tagassignments()
        else:
            res = self.get_tagassignments_flat()
        return res.assignments()

    def add_tag(self, *, tagname=None, tagstring=None):
        """
        Adds a new tag. Specify either 'tagname' or 'tagstring'!

        :param tagname: The tagname for the new tag.
        :param tagstring: The tagstring for the new tag.
        """
        if len([x for x in [tagname, tagstring] if x]) != 1:
            raise PiMetadataInterpreterError("either tagname or tagstring must be specified")
        if tagname:
            res = TagAssignment(tagname)
        elif tagstring:
            res = TagAssignment.from_tagstring(tagstring)
        tas = self.get_tagassignments_flat()
        tas.add_assignment(res)
        self.store_tagassignments(tas)
        return res

    def remove_tag(self, tagname):
        """
        Removes a tag by name. Returns True if anything was removed.
        """
        tas = self.get_tagassignments_flat()
        res = tas.remove_assignments_by_tagname(tagname)
        self.store_tagassignments(tas)
        return res > 0

    def comment(self):
        """
        Returns the comment text (as string).
        """
        return self._get_xattr(self.XATTR_KEY_COMMENT)

    def set_comment(self, txt):
        """
        Sets the comment text (overwriting the old one).

        :param txt: The new text.
        """
        if txt:
            self._set_xattr(self.XATTR_KEY_COMMENT, txt)
        else:
            self._unset_xattr(self.XATTR_KEY_COMMENT)

    def add_comment(self, txt):
        """
        Appends a comment text.

        :param txt: The text to append.
        """
        txt = txt.strip()
        octxt = self.comment()
        nctxt = octxt.strip() + "\n"
        txtismultiline = "\n" in txt
        if octxt.endswith("\n") or txtismultiline:
            nctxt += "\n"
        nctxt += txt
        if txtismultiline:
            nctxt += "\n"
        self.set_comment(nctxt.lstrip())

    RATING_MIN_VALUE = 1
    RATING_MAX_VALUE = 10
    RATING_DEFAULT_VALUE = 0

    @staticmethod
    def _rating_sanitize_value(v):
        try:
            return max(MetadataInterpreter.RATING_MIN_VALUE, min(MetadataInterpreter.RATING_MAX_VALUE, int(v)))
        except (ValueError, TypeError):
            return MetadataInterpreter.RATING_DEFAULT_VALUE

    def rating(self):
        """
        Returns the rating. See MetadataInterpreter.RATING_MIN_VALUE and other constants.
        """
        return MetadataInterpreter._rating_sanitize_value(self._get_xattr(self.XATTR_KEY_RATING))

    def set_rating(self, v):
        """
        Sets the rating.

        :param v: The new value. See MetadataInterpreter.RATING_MIN_VALUE and other constants.
        """
        if v is None or (v == MetadataInterpreter.RATING_DEFAULT_VALUE):
            self._unset_xattr(self.XATTR_KEY_RATING)
        else:
            self._set_xattr(self.XATTR_KEY_RATING, str(MetadataInterpreter._rating_sanitize_value(v)))

    def reset_rating(self):
        """
        Resets the rating back to default.
        """
        self.set_rating(None)

    def geo(self):
        """
        Returns the geo location as GeoLocation (or None).
        """
        gs = self._get_xattr(self.XATTR_KEY_GEO)
        if gs:
            return GeoLocation.from_geostring(gs)
        else:
            return None

    def set_geo(self, v):
        """
        Sets a new geo location by string or GeoLocation.

        :param v: The new location (may be None).
        """
        if v:
            if isinstance(v, str):
                v = GeoLocation.from_geostring(v)
            self._set_xattr(self.XATTR_KEY_GEO, v.to_geostring())
        else:
            self._unset_xattr(self.XATTR_KEY_GEO)

    def set_geolocation(self, *, lat, lon, accuracy_meters=None, **geoatts):
        """
        Sets a new geo location by separate values.

        :param lat: The latitude in degrees.
        :param lon: The longitude in degrees.
        :param accuracy_meters: The accuracy of this location in meters.
        :param geoatts: Additional geo attributes.
        """
        self.set_geo(GeoLocation(lat=lat, lon=lon, accuracy_meters=accuracy_meters, **geoatts))

    class CompleteMetadataStruct:
        """
        A convenience structure which aggregates all known metadata about one object. It provides some dump functions.
        
        Don't construct instances directly. See MetadataInterpreter.get_complete_metadata.
        """

        def _geo_to_raw(self, geo):
            if geo:
                res = dict(geo._geoatts)
                res["geostring"] = geo.to_geostring()
                return res

        def _tags_to_raw(self, tags):
            res = []
            for ta in tags:
                tres = {"tagname": ta.tagname(),
                        "filepath": ta.filepath(),
                        "is_outlying": TagAssignments.check_is_outlying_assignment(self._mi.filepath(), ta),
                        "tagstring": ta.to_tagstring()}
                res.append(tres)
            return res

        def __init__(self, mi):
            self._mi = mi
            self.comment = mi.comment()
            self.geo = mi.geo()
            self.rating = mi.rating()
            self.tags = mi.tags()
            self.tags_tagsstring_flat = mi.get_tagassignments_flat().to_tagsstring()
            self.tags_tagsstring_full = mi.get_tagassignments().to_tagsstring(exclude_outlying=False)

        def to_dict(self):
            """
            Returns a representation based on Python dicts and 'no objects'.
            """
            res = dict(self.__dict__)
            res.pop("_mi")
            res["geo"] = self._geo_to_raw(res["geo"])
            res["tags"] = self._tags_to_raw(res["tags"])
            return res

        def to_json(self):
            """
            Returns the json representation of this structure as string.
            """
            return json.dumps(self.to_dict())

    def get_complete_metadata(self):
        """
        Returns the complete known metadata (as MetadataInterpreter.CompleteMetadataStruct). Use this e.g. for
        dumping python-dict or json representations.
        """
        return MetadataInterpreter.CompleteMetadataStruct(self)


def get_interpreter(path, engineclass=XattrEngine):
    """
    Returns an interpreter (i.e. an instance of MetadataInterpreter) for a path. Use this object for working with
    metadata for this path.

    :param path: The path to operate on with this instance.
    :param engineclass: For some cases it might be convenient to subclass XattrEngine and use this subclass
                        here (e.g. a custom xattr backend). 
    """
    # we don't allow parameters here, because we have to construct new instances for recursive operations
    eng = engineclass(path)
    res = MetadataInterpreter(path, eng)
    return res


## searches

class SearchResultItem:
    """
    One file or directory as part of a search result.
    """

    def __init__(self, path, summary):
        """
        Used internally. See SearchEngine.search. 
        """
        self.path = path
        self.summary = summary

    def __repr__(self):
        return "SearchResultItem({}, summary={})".format(repr(self.path), repr(self.summary))


class SearchCriterion:
    """
    Abstract base class for the implementation of search criteria (those with program code deciding if a file matches
    a certain query). Also includes business logic for (de)serialization of querystrings.
    """

    SERIALIZE_FORMAT_JSON = 1  # allows to serialize arbitrary objects to json.
    SERIALIZE_FORMAT_SUBCRITERION = 2  # allows to serialize a SearchCriterion to a compactly embedded querystring.
    SERIALIZE_FORMAT_URLENCODEDSTRING = 3  # allows to serialize a string to an (reducedly) urlencoded format.

    @staticmethod
    def define_serialize_param(*, objname, to, expanded=False, ctor_arglist=False,
                               serialize_format=SERIALIZE_FORMAT_JSON):
        """
        Used for decorating SearchCriterion subclasses for specifying which arguments to (de)serialize and how.

        :param objname: The argument name as it is stored inside the instance (and as the constructor expects it).
        :param to: The serialization destination. Either an integer, then it's an index of a positional argument within
                   the resulting querystring. Or a string, then it's the key of a keyword argument.
        :param expanded: If the parameter is expected to be a list, which is to be expanded within the querystring.
        :param ctor_arglist: If the constructor expects this argument as positional one.
        :param serialize_format: The serialization format. One of SearchCriterion.SERIALIZE_FORMAT_*.
        """

        def dcrtr(clss):
            sinf = clss._serializationinfo = getattr(clss, "_serializationinfo", [])
            sinf.insert(0, (objname, to, expanded, serialize_format, ctor_arglist))
            return clss
        return dcrtr

    @staticmethod
    def _encode_part(s):
        """
        Encodes a value string in some reduces variant of urlencoding, avoiding conflicts with the control characters
        used in a querystring. Used internally.
        """
        s = s.replace("%", "%25")
        for wsm in reversed(list(re.finditer("\\s", s))):
            wsi = wsm.span()[0]
            s = s[:wsi] + urllib.parse.quote(s[wsi]) + s[wsi + 1:]
        s = s.replace("{", "%7B").replace("}", "%7D").replace("&", "%26").replace("?", "%3F").replace("=", "%3D")
        return s

    def __str__(self):
        return self.to_querystring()

    @staticmethod
    def _serialize_value(v, serialize_format):
        """
        Serializes an arbitrary value to some serialization format. Used internally.

        :param v: The value as string, or arbitrary object, or whatever 'serialize_format' allows.
        :param serialize_format: The serialization format. One of SearchCriterion.SERIALIZE_FORMAT_*.
        """
        # some characters must not be used, since they are used as control characters
        if serialize_format == SearchCriterion.SERIALIZE_FORMAT_JSON:
            return SearchCriterion._encode_part(json.dumps(v)) if (v is not None) else ""
        elif serialize_format == SearchCriterion.SERIALIZE_FORMAT_SUBCRITERION:
            # this is the only one which may use { and }!
            return "{" + v.to_querystring() + "}"
        elif serialize_format == SearchCriterion.SERIALIZE_FORMAT_URLENCODEDSTRING:
            return SearchCriterion._encode_part(str(v))
        else:
            raise MetadataFormatError(f"bad serialization format: {serialize_format}")

    @staticmethod
    def _deserialize_value(s, serialize_format):
        """
        Deserializes back what SearchCriterion._serialize_value returns. Used internally.
        """
        if serialize_format == SearchCriterion.SERIALIZE_FORMAT_JSON:
            if s == "":
                return None
            return json.loads(urllib.parse.unquote(s))
        elif serialize_format == SearchCriterion.SERIALIZE_FORMAT_SUBCRITERION:
            return SearchCriterion.from_querystring(s[1:-1])
        elif serialize_format == SearchCriterion.SERIALIZE_FORMAT_URLENCODEDSTRING:
            return urllib.parse.unquote(s)
        else:
            raise MetadataFormatError(f"bad serialization format: {serialize_format}")

    @staticmethod
    def from_querystring(s):
        """
        Returns a SearchCriterion by interpreting a querystring. See also SearchCriterion.to_querystring.

        :param s: A querystring specifying the search criterion.
        """
        iqm = s.find("?")
        if iqm > -1:  # there are some arguments
            critname = s[:iqm]
            # raw split
            tokens = []
            strrs = s[iqm+1:]
            while strrs:
                if strrs.startswith("{"):
                    parsebracesegment = 1
                else:
                    ieqlb = strrs.find("={")
                    if ieqlb > -1:
                        parsebracesegment = ieqlb + 2
                    else:
                        parsebracesegment = False
                if parsebracesegment is not False:  # parse until a {...} block ends
                    i = parsebracesegment
                    openbraces = 1
                    while openbraces:
                        ilb = strrs.find("{", i)
                        irb = strrs.find("}", i)
                        if ((ilb < irb) or (irb == -1)) and (ilb != -1):
                            i = ilb + 1
                            openbraces += 1
                        elif ((irb < ilb) or (ilb == -1)) and (irb != -1):
                            i = irb + 1
                            openbraces -= 1
                        else:
                            raise MetadataFormatError(f"bad query string format: {s}")
                    tokens.append(strrs[:i])
                    strrs = strrs[i+1:]
                else:  # parse regularly
                    iaa = strrs.find("&")
                    if iaa > -1:
                        tokens.append(strrs[:iaa])
                        strrs = strrs[iaa+1:]
                    else:
                        tokens.append(strrs)
                        strrs = ""
            if not tokens:
                # there is a "?" but no token so far (while logically there should be an empty one then)
                tokens.append("")
        else:
            critname = s
            tokens = []
        if not critname:
            raise MetadataFormatError(f"no criteria name given: {s}")
        clss = globals()[f"SearchCriterion{critname}"]
        # raw extraction
        la = []
        lb = []
        k = None
        for token in tokens:
            ieq = token.find("=")
            ilb = token.find("{")
            if (ieq == -1) or ((ilb != -1) and (ilb < ieq)):  # positional argument (if no keyword argument came before)
                if k is not None:
                    lb.append((k, token))
                else:
                    la.append(token)
            else:  # keyword argument
                k = token[:ieq]
                v = token[ieq+1:]
                lb.append((k, v))
        # assign to actual positions/keys
        a = []
        b = {}
        for psi in getattr(clss, "_serializationinfo", []):
            objname = psi[0]
            to = psi[1]
            expanded = psi[2]
            serialize_format = psi[3]
            ctor_arglist = psi[4]
            if isinstance(to, int):  # positional argument
                if expanded:
                    val = [SearchCriterion._deserialize_value(xx, serialize_format) for xx in la[to:]]
                else:
                    val = SearchCriterion._deserialize_value(la[to], serialize_format)
            else:  # keyword argument
                slb = [xv for (xk, xv) in lb if xk == to]
                if expanded:
                    val = [SearchCriterion._deserialize_value(xx, serialize_format) for xx in slb]
                else:
                    val = SearchCriterion._deserialize_value(slb[0], serialize_format) if slb else None
            if ctor_arglist:
                a += val if expanded else [val,]
            else:
                b[objname] = val
        return clss(*a, **b)

    def to_querystring(self):
        """
        Returns a querystring representation for this search criterion. See also SearchCriterion.from_querystring.
        """
        clss = type(self)
        n = clss.__name__[15:]
        a = {}  # note: we actually use a dict for positional arguments and a list for keyword ones ;)
        b = []
        for psi in getattr(clss, "_serializationinfo", []):
            val = getattr(self, psi[0])
            to = psi[1]
            expanded = psi[2]
            serialize_format = psi[3]
            if isinstance(to, int):  # positional argument > add to 'a'
                if expanded:  # assume a list and add the items to 'a'
                    for vv in val:
                        a[to] = self._serialize_value(vv, serialize_format)
                        to += 1
                else:  # assume a value to be added directly to 'a'
                    a[to] = self._serialize_value(val, serialize_format)
            else:  # keyword argument > add to 'b'
                if expanded:  # assume a list and add the items to 'b'
                    b.append((to, "&".join([self._serialize_value(vv, serialize_format) for vv in val])))
                else:  # assume a value to be added directly to 'b'
                    if val is not None:
                        b.append((to, self._serialize_value(val, serialize_format)))
        res = n
        jsonnone = json.dumps(None)
        stra = "&".join([a.get(i, jsonnone) for i in range(max(-1, -1, *a.keys())+1)])
        strb = "&".join([bk+"="+bv for bk, bv in b])
        strab = "&".join([x for x in [stra, strb] if x])
        if strab:
            res += "?" + strab
        return res

    def is_matching(self, intp):
        """
        Checks if a file (or dir) is matching the search criterion. Used internally.
        Implement this in a subclass with own decision logic.

        :param intp: A MetadataInterpreter pointing to the file to check. Get its path by `intp.filepath()`.
        """
        raise NotImplementedError()


@SearchCriterion.define_serialize_param(objname="innercriterion", to=0,
                                        serialize_format=SearchCriterion.SERIALIZE_FORMAT_SUBCRITERION)
class SearchCriterionNot(SearchCriterion):
    """
    A search criterion which inverts an inner one.
    Example querystring: `Not?{SomeOther?...}`.
    """

    def __init__(self, innercriterion):
        """
        :param innercriterion: The criterion to invert (as SearchCriterion or querystring).
        """
        self.innercriterion = SearchCriterion.from_querystring(innercriterion) \
                                if isinstance(innercriterion, str) else innercriterion

    def is_matching(self, intp):
        return not self.innercriterion.is_matching(intp)


@SearchCriterion.define_serialize_param(objname="innercriteria", to=0, expanded=True, ctor_arglist=True,
                                        serialize_format=SearchCriterion.SERIALIZE_FORMAT_SUBCRITERION)
class SearchCriterionOr(SearchCriterion):
    """
    A search criterion which matches, iff at least one of its inner ones matches.
    Example querystring: `Or?{SomeOther?...}&{YetAnother?...}&...`.
    """

    def __init__(self, *innercriteria):
        """
        :param innercriteria: The criteria to combine (as list of SearchCriterion or querystrings).
        """
        self.innercriteria = [(SearchCriterion.from_querystring(c) if isinstance(c, str) else c) for c in innercriteria]

    def is_matching(self, intp):
        for icr in self.innercriteria:
            ires = icr.is_matching(intp)
            if not ((ires is False) or (ires is None)):
                return ires


@SearchCriterion.define_serialize_param(objname="innercriteria", to=0, expanded=True, ctor_arglist=True,
                                        serialize_format=SearchCriterion.SERIALIZE_FORMAT_SUBCRITERION)
class SearchCriterionAnd(SearchCriterion):
    """
    A search criterion which matches, iff all its inner ones match.
    Example querystring: `And?{SomeOther?...}&{YetAnother?...}&...`.
    """

    def __init__(self, *innercriteria):
        """
        :param innercriteria: The criteria to combine (as list of SearchCriterion or querystrings).
        """
        self.innercriteria = [(SearchCriterion.from_querystring(c) if isinstance(c, str) else c) for c in innercriteria]

    def is_matching(self, intp):
        cmt = []
        ismatching = True
        for icr in self.innercriteria:
            ires = icr.is_matching(intp)
            if ires:
                if isinstance(ires, str):
                    cmt.append(ires)
                elif isinstance(ires, list):
                    cmt += ires
            elif (ires is False) or (ires is None):
                ismatching = False
                break
        if ismatching:
            return cmt


@SearchCriterion.define_serialize_param(objname="tagname", to=0,
                                        serialize_format=SearchCriterion.SERIALIZE_FORMAT_URLENCODEDSTRING)
@SearchCriterion.define_serialize_param(objname="tagname_is_regexp", to="is_re")
class SearchCriterionTags(SearchCriterion):
    """
    A search criterion which matches, iff an item has a certain tag assigned.
    Example querystring: `Tags?sometag&is_re=false`.
    """

    def __init__(self, tagname, tagname_is_regexp=None):
        """
        :param tagname: The tag name to search for.
        :param tagname_is_regexp: If tagname is to be interpreted as regular expression (default: no).
        """
        self.tagname = tagname
        self.tagname_is_regexp = tagname_is_regexp
        self.re_tagname = re.compile(tagname) if tagname_is_regexp else None

    def is_matching(self, intp):
        for ta in intp.tags():
            tam = None
            if self.re_tagname:
                if self.re_tagname.fullmatch(ta.tagname()):
                    tam = ta
            else:
                if self.tagname == ta.tagname():
                    tam = ta
            if tam:
                if TagAssignments.check_is_outlying_assignment(intp.filepath(), tam):
                    comment = f"from {tam.filepath()}: "
                else:
                    comment = ""
                comment += f"tag '{tam.tagname()}'"
                return comment


@SearchCriterion.define_serialize_param(objname="comment", to=0,
                                        serialize_format=SearchCriterion.SERIALIZE_FORMAT_URLENCODEDSTRING)
@SearchCriterion.define_serialize_param(objname="comment_is_regexp", to="is_re")
class SearchCriterionComment(SearchCriterion):
    """
    A search criterion which matches, iff an item has a certain comment.
    Example querystring: `Comment?foo.*&is_re=true`.
    """

    def __init__(self, comment, comment_is_regexp=None):
        """
        :param comment: The comment substring to search for (as a regular expression it applies to the entire comment).
        :param comment_is_regexp: If comment is to be interpreted as regular expression (default: no).
        """
        self.comment = comment
        self.comment_is_regexp = comment_is_regexp
        self.re_comment = re.compile(comment) if comment_is_regexp else None

    def is_matching(self, intp):
        tam = False
        comment = intp.comment()
        if self.re_comment:
            if self.re_comment.fullmatch(comment):
                tam = True
        else:
            if self.comment in comment:
                tam = True
        if tam:
            return f"comment '{comment}'"


@SearchCriterion.define_serialize_param(objname="min", to="min")
@SearchCriterion.define_serialize_param(objname="max", to="max")
class SearchCriterionRating(SearchCriterion):
    """
    A search criterion which matches, iff an item is in a certain rating range. Note that each item implicitly has some
    default rating, if it never got one assigned explicitly.
    Example querystring: `Rating?min=2&max=3`.
    """

    def __init__(self, min=None, max=None):
        """
        :param min: The minimal rating (default: unlimited).
        :param max: The maximal rating (default: unlimited).
        """
        self.min = min
        self.max = max

    def is_matching(self, intp):
        rating = intp.rating()
        if ((self.min is None) or (rating >= self.min)) and ((self.max is None) or (rating <= self.max)):
            return f"rating {rating}"


@SearchCriterion.define_serialize_param(objname="center_lat", to="lat")
@SearchCriterion.define_serialize_param(objname="center_lon", to="lon")
@SearchCriterion.define_serialize_param(objname="distance_meters", to="dist")
@SearchCriterion.define_serialize_param(objname="distance_tolerance", to="tol")
class SearchCriterionGeo(SearchCriterion):
    """
    A search criterion which matches, iff an item is within a certain distance of a certain geographic range.
    Example querystring: `Geo?lat=12&lon=34&dist=5000`.
    """

    def __init__(self, center=None, center_lat=None, center_lon=None, distance_meters=5000, distance_tolerance=None):
        """
        You must specify either center, or both of center_lat and center_lon!

        :param center: The geographic center location as GeoLocation.
        :param center_lat: The latitude of the geographic center location as number.
        :param center_lon: The longitude of the geographic center location as number.
        :param distance_meters: The maximum distance in meters.
        :param distance_tolerance: How to deal with position inaccuracies. 
                                   None: center-to-center, -1: worst case, 1: best case.   
        """
        if isinstance(center, str):
            center = GeoLocation.from_geostring(center)
        elif isinstance(center, GeoLocation):
            pass
        elif None not in [center_lat, center_lon]:
            center = GeoLocation(lat=center_lat, lon=center_lon)
        else:
            raise PiMetadataInterpreterError("you must either specify 'center' or all of 'center_*'")
        self.center = center
        self.center_lat = center.lat()
        self.center_lon = center.lon()
        self.distance_meters = distance_meters
        self.distance_tolerance = distance_tolerance

    def is_matching(self, intp):
        geo = intp.geo()
        if geo:
            if self.distance_tolerance == 1:
                gdist = geo.distance_meters_interval(self.center)[0]
            elif self.distance_tolerance == -1:
                gdist = geo.distance_meters_interval(self.center)[1]
            else:
                gdist = geo.distance_meters(self.center)
            if gdist <= self.distance_meters:
                return f"geo location 'lat:{geo.lat()} ; lon:{geo.lon()}'"


@SearchCriterion.define_serialize_param(objname="value", to=0,
                                        serialize_format=SearchCriterion.SERIALIZE_FORMAT_URLENCODEDSTRING)
@SearchCriterion.define_serialize_param(objname="key", to="key",
                                        serialize_format=SearchCriterion.SERIALIZE_FORMAT_URLENCODEDSTRING)
@SearchCriterion.define_serialize_param(objname="key_is_regexp", to="key_is_re")
@SearchCriterion.define_serialize_param(objname="value_is_regexp", to="value_is_re")
class SearchCriterionXattrValue(SearchCriterion):
    """
    A search criterion which matches, iff a certain item's xattr has a certain value. You should typically not need it.
    Example querystring: `XattrValue?some%20comment&key=comment`.
    """

    def __init__(self, value, *, key, key_is_regexp=None, value_is_regexp=None):
        """
        :param value: The value to search for (as string).
        :param key: The xattr key to look into (as string; None for all).
        :param key_is_regexp: If key is to be interpreted as regular expression (default: no).
        :param value_is_regexp: If value is to be interpreted as regular expression (default: no).
        """
        self.key = key
        self.value = value
        self.key_is_regexp = key_is_regexp
        self.value_is_regexp = value_is_regexp
        self.re_value = re.compile(value) if value_is_regexp else None
        self.re_key = re.compile(key) if key_is_regexp else None

    def is_matching(self, intp):
        if self.re_key:
            xkeys = [xk for xk in intp._list_xattrs() if self.re_key.fullmatch(xk)]
        else:
            xkeys = [self.key, ] if self.key else intp._list_xattrs()
        for xkey in xkeys:
            v = intp._get_xattr(xkey)
            if self.re_value:
                tam = self.re_value.fullmatch(v)
            else:
                tam = self.value == v
            if tam:
                return f"{xkey} '{v}'"


class SearchEngine:
    """
    This is an abstract subclass for search engines.
    Instances of them allow to execute searches within a directory on the metadata of contained items.
    Don't construct instances directly, but use get_searchengine.
    """

    def _listdir(self, path):
        """
        Lists the content of a directory.
        Used internally.
        Implement this in a custom search engine.
        """
        raise NotImplementedError()

    def _isdir(self, path):
        """
        Checks if a given path points to a directory.
        Used internally.
        Implement this in a custom search engine.
        """
        raise NotImplementedError()

    def init(self, rootpath, engineclass):
        """
        Initializes a search engine. Used internally.
        """
        self.rootpath = os.path.abspath(rootpath)  # absolute path is important here ( ..startswith(rootpath) )!
        self.engineclass = engineclass

    def _getinterpreter(self, path):
        """
        Constructs a MetadataInterpreter for a path. Used internally. 
        """
        return get_interpreter(path, engineclass=self.engineclass)

    def search(self, *criteria):
        """
        Executes a search by some criteria and returns all matching items as list of SearchResultItem.

        :param criteria: One or more search criteria as SearchCriterion or querystrings. Items will match if they
                         match all of the given criteria (but you can logically combine them further inside e.g.
                         using SearchCriterionOr).
        """
        with MetadataInterpreter.Cache():
            res = []
            lsk = [self.rootpath]
            ecriteria = [(SearchCriterion.from_querystring(c) if isinstance(c, str) else c) for c in criteria]
            while lsk:
                l = lsk.pop()
                for c in sorted(self._listdir(l)):
                    fc = f"{l}/{c}"
                    fcpm = self._getinterpreter(fc)
                    ismatching = True
                    lcomment = []
                    for criterion in ecriteria:
                        rim = criterion.is_matching(fcpm)
                        if rim:
                            if isinstance(rim, str):
                                rim = [rim, ]
                            if isinstance(rim, list):
                                lcomment += [llr.replace("\n", " ") for llr in rim]
                        elif (rim is False) or (rim is None):
                            ismatching = False
                            break
                        ismatching = ismatching and rim
                    if ismatching:
                        summary = "\n\n".join(lcomment)
                        res.append(SearchResultItem(fc, summary))
                    if self._isdir(fc):
                        lsk.append(fc)
            return res


class DefaultSearchEngine(SearchEngine):
    """
    The default implementation of SearchEngine using on Parsley metadata xattrs.
    """

    class _NullXattrEngine(XattrEngine):

        def list_xattrs(self):
            return []

        def get_xattr(self, key):
            return ""

        def set_xattr(self, key, val):
            pass

        def unset_xattr(self, key):
            pass

    def __init__(self, *, prefer_shadowmetadata_storage=False):
        """
        :param prefer_shadowmetadata_storage: If to prefer usage of a Parsley metadata shadow storage, if one exists, 
                                              for a few things. You should typically not use it. 
                                              This accelerates searches, but may ignore freshly attributed items. 
                                              It also caches some internal stuff, so you should not reuse your instance!
        """
        SearchEngine.__init__(self)
        self.prefer_shadowmetadata_storage = prefer_shadowmetadata_storage
        self._shadowmds_pcdirs_noparsley = set()
        self._shadowmds_pcdirs_parsleyroots = set()
        self._shadowmds_nomd = set()

    def _get_shadowmetadata_path(self, path):
        # this method does not return the correct result for dirs (doesn't matter for our use can, but speed matters)
        for xr in self._shadowmds_pcdirs_parsleyroots:
            if f"{path}/".startswith(f"{xr}/"):
                return f"{xr}/.parsley.control/content_metadata{path[len(xr):]}"
        pp = path
        opp = None
        pnop = []
        while pp != opp:
            if pp in self._shadowmds_pcdirs_noparsley:
                return
            if os.path.exists(f"{pp}/.parsley.control"):
                self._shadowmds_pcdirs_parsleyroots.add(pp)
                return f"{pp}/.parsley.control/content_metadata{path[len(pp):]}"
            else:
                pnop.append(pp)
            opp = pp
            pp = os.path.dirname(pp)
        self._shadowmds_pcdirs_noparsley.update(pnop)

    @functools.lru_cache(32)
    def _smd_listdir_as_set(self, p):
        try:
            return set(self._listdir(p))
        except FileNotFoundError:
            return set()

    def _smd_pathexist(self, p):
        if p == "/":
            return True
        ils = p.rfind("/")
        return p[ils+1:] in self._smd_listdir_as_set(p[:ils] or "/")

    def _getinterpreter(self, path):
        if self.prefer_shadowmetadata_storage:
            mdpath = self._get_shadowmetadata_path(path)
            if mdpath and not self._smd_pathexist(mdpath):
                return get_interpreter(path, engineclass=DefaultSearchEngine._NullXattrEngine)
        return super()._getinterpreter(path)

    def _listdir(self, path):
        return [x for x in os.listdir(path) if x != ".parsley.control"]

    def _isdir(self, path):
        return os.path.isdir(path) and (not os.path.islink(path))


def get_searchengine(rootpath, engineclass=XattrEngine, searchengineclass=DefaultSearchEngine, **sxa):
    """
    Returns a search engine (i.e. an instance of SearchEngine) for a root path. Use this object for searching by
    metadata in this directory.

    :param rootpath: The directory path to search within.
    :param engineclass: For some cases it might be convenient to subclass XattrEngine and use this subclass
                        here (e.g. a custom xattr backend). 
    :param searchengineclass: For some cases it might be convenient to subclass SearchEngine and use this subclass here.
    :param sxa: Additional search engine parameters.
    """
    res = searchengineclass(**sxa)
    res.init(rootpath, engineclass)
    return res


## command line interface

class CommandLineInterface:
    """
    This class allows usage of the most features from command line.
    """

    def comment__get(self, mi):
        print(mi.comment())

    def comment__set(self, mi, newcomment):
        mi.set_comment(newcomment)

    def comment__add(self, mi, newcomment):
        mi.add_comment(newcomment)

    def geo__get(self, mi):
        g = mi.geo()
        if g:
            gad = dict(g._geoatts)
            for kgad in [GeoLocation.GEOATTKEY_LAT, GeoLocation.GEOATTKEY_LON, GeoLocation.GEOATTKEY_ACCURACY]:
                print(f"{kgad}:", self._friendlyquote(gad.pop(kgad, 0)))
            for kgad in list(gad.keys()):
                print(f"{kgad}:", self._friendlyquote(gad.pop(kgad, 0)))

    def geo__getraw(self, mi):
        g = mi.geo()
        if g:
            print(g.to_geostring())

    def geo__modify(self, mi, key, value):
        g = mi.geo() or GeoLocation(lat=0, lon=0)
        g.set_geoatt(key, value)
        mi.set_geo(g)

    def geo__set(self, mi, newgeostring):
        if newgeostring:
            g = GeoLocation.from_geostring(newgeostring)
        else:
            g = None
        mi.set_geo(g)

    def rating__get(self, mi):
        print(mi.rating())

    def rating__set(self, mi, newrating):
        mi.set_rating(newrating)

    def rating__reset(self, mi):
        mi.reset_rating()

    def rating__vminimum(self, mi):
        print(MetadataInterpreter.RATING_MIN_VALUE)

    def rating__vmaximum(self, mi):
        print(MetadataInterpreter.RATING_MAX_VALUE)

    def rating__vdefault(self, mi):
        print(MetadataInterpreter.RATING_DEFAULT_VALUE)

    def tags__get(self, mi):
        for ta in mi.tags():
            print(self._friendlyquote(ta.tagname()))
            print(" " + self._friendlyquote_as_fileurl(ta.filepath()))
            print()

    def tags__addtag(self, mi, bytagname=None, bytagstring=None):
        mi.add_tag(tagname=bytagname, tagstring=bytagstring)

    def tags__droptag(self, mi, tagname):
        mi.remove_tag(tagname)

    def tags__edittag(self, mi, tagname, kind, key, value=None):
        if kind == "removeatt":
            mi.modify_tag(tagname, remove_tagatts=[key])
        else:
            raise Exception("unknown kind")

    def misc__getcomplete_json(self, mi):
        print(mi.get_complete_metadata().to_json())

    def misc__measure_geolocations_distance(self, mi, geostring1, geostring2):
        g1 = GeoLocation.from_geostring(geostring1)
        g2 = GeoLocation.from_geostring(geostring2)
        mm = g1.distance_meters_interval(g2)
        a = g1.distance_meters(g2)
        print("minimum:", mm[0])
        print("average:", a)
        print("maximum:", mm[1])

    def misc__search(self, mi, querystring):
        se = get_searchengine(mi.filepath())
        for sr in se.search(querystring):
            print(self._friendlyquote_as_fileurl(sr.path))
            print(" " + self._friendlyquote(sr.summary))

    @staticmethod
    def _friendlyquote(s, encode_whitespaces=False):
        s = str(s)
        if encode_whitespaces:
            for wsm in reversed(list(re.finditer(r"\s", s))):
                wsi = wsm.span()[0]
                s = s[:wsi] + urllib.parse.quote(s[wsi]) + s[wsi+1:]
        return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")

    @staticmethod
    def _friendlyquote_as_fileurl(s):
        return "file://" + CommandLineInterface._friendlyquote(os.path.abspath(str(s)), encode_whitespaces=True)

    def _execargs(self, args):
        k = args.__dict__
        mi = get_interpreter(k.pop("filepath"))
        fct = getattr(self, k.pop("metadata_key")+"__"+k.pop("command"), None)
        fct(mi, **k)

    def main(self):
        parser = argparse.ArgumentParser(description="Parsley Metadata Interpreter.")
        parser.add_argument("filepath", help="The file or dir to operate on.")
        sbcommand = parser.add_subparsers(help="The metadata to operate on.",
                                          metavar="metadata_key", dest="metadata_key")
        sbcommand.required = True
        sprco = sbcommand.add_parser("comment", help="Comment.")
        subsprco = sprco.add_subparsers(help="The command to execute.",
                                        metavar="command", dest="command")
        subsprco.required = True
        sprcoget = subsprco.add_parser("get", help="Returns the comment.")
        sprcoset = subsprco.add_parser("set", help="Sets (and overwrites) the comment.")
        sprcoset.add_argument("newcomment", help="The new comment.")
        sprcoadd = subsprco.add_parser("add", help="Adds a new comment.")
        sprcoadd.add_argument("newcomment", help="The new comment.")
        sprge = sbcommand.add_parser("geo", help="Geographic location.")
        subsprge = sprge.add_subparsers(help="The command to execute.",
                                        metavar="command", dest="command")
        subsprge.required = True
        sprgeget = subsprge.add_parser("get", help="Returns the geographic location.")
        sprgegetraw = subsprge.add_parser("getraw", help="Returns the geographic location as raw geostring.")
        sprgemodify = subsprge.add_parser("modify", help="Modifies one part of the geographic location.")
        sprgemodify.add_argument("key", help='The key to modify (e.g. "{}", "{}" or "{}").'.format(
            GeoLocation.GEOATTKEY_LAT, GeoLocation.GEOATTKEY_LON, GeoLocation.GEOATTKEY_ACCURACY))
        sprgemodify.add_argument("value", help="The new value.")
        sprgeset = subsprge.add_parser("set", help="Sets the geographic location as raw geostring.")
        sprgeset.add_argument("newgeostring", help="The new geostring.")
        sprra = sbcommand.add_parser("rating", help="Rating.")
        subsprra = sprra.add_subparsers(help="The command to execute.",
                                        metavar="command", dest="command")
        subsprra.required = True
        sprraget = subsprra.add_parser("get", help="Returns the rating.")
        sprraset = subsprra.add_parser("set", help="Sets the rating.")
        sprraset.add_argument("newrating", help="The new rating value.")
        sprrareset = subsprra.add_parser("reset", help="Resets the rating to default.")
        sprravalueminimum = subsprra.add_parser("vminimum", help="Returns the rating minimum value.")
        sprravaluemaximum = subsprra.add_parser("vmaximum", help="Returns the rating maximum value.")
        sprravaluedefault = subsprra.add_parser("vdefault", help="Returns the rating default value.")
        sprta = sbcommand.add_parser("tags", help="Tags.")
        subsprta = sprta.add_subparsers(help="The command to execute.",
                                        metavar="command", dest="command")
        subsprta.required = True
        sprtaget = subsprta.add_parser("get", help="Returns all tags.")
        sprtaaddtag = subsprta.add_parser("addtag", help="Adds a new tag.")
        sprtaaddtag.add_argument("--bytagname", help="The new tag's tagname (without any attributes).",
                                 metavar="tagname")
        sprtaaddtag.add_argument("--bytagstring", help="The new tag's tagstring (also encodes attributes).",
                                 metavar="tagstring")
        sprtadroptag = subsprta.add_parser("droptag", help="Removes a tag (by tagname).")
        sprtadroptag.add_argument("tagname", help="The tagname of the tag you want to remove.")
        sprtaedittag = subsprta.add_parser("edittag", help="Modifies an existing tag's tag attributes.")
        sprtaedittag.add_argument("tagname", help="The tagname of the tag you want to edit.")
        spsprtaedittagkind = sprtaedittag.add_subparsers(help="The kind of change to apply to the chosen tag.",
                                                         metavar="kind", dest="kind")
        spsprtaedittagkind.required = True
        sedittagkindremove = spsprtaedittagkind.add_parser("removeatt", help="Unsets a tag attribute.")
        sedittagkindremove.add_argument("key", help="The key of the tagatt to remove.")
        sprmi = sbcommand.add_parser("misc", help="Miscellaneous, independent stuff.")
        subsprmi = sprmi.add_subparsers(help="The command to execute.",
                                        metavar="command", dest="command")
        subsprmi.required = True
        sprmigetcompletejson = subsprmi.add_parser("getcomplete_json",
                                                   help="Returns a json containing the complete metadata.")
        sprmimeasuregpdist = subsprmi.add_parser("measure_geolocations_distance",
                                                 help="Returns the distance in meters between two geostrings. "
                                                      "The specified 'filepath' doesn't matter with this command.")
        sprmimeasuregpdist.add_argument("geostring1", help="A geostring encoding the 1st point.")
        sprmimeasuregpdist.add_argument("geostring2", help="A geostring encoding the 2nd point.")
        sprmisearch = subsprmi.add_parser("search", help="Search for children files/dirs by some metadata criteria.")
        sprmisearch.add_argument("querystring", help="A querystring encoding the search criteria.")
        args = parser.parse_args()
        self._execargs(args)


if __name__ == "__main__":
    try:
        CommandLineInterface().main()
    except PiMetadataInterpreterError as e:
        print("Fatal error:", e)
        sys.exit(1)


# tests

try:
    import unittest
    with_tests = True
except ModuleNotFoundError:
    with_tests = False

if with_tests:

    class MyTestCase(unittest.TestCase):

        dummyfname = "/proc///this/dummy/does/not/exist"

        _ustorage = {}

        class MyMetadataEngine(XattrEngine):

            def __init__(self, path):
                XattrEngine.__init__(self, path)
                MyTestCase._ustorage[path] = self._storage = MyTestCase._ustorage.get(path, {})

            def list_xattrs(self):
                return list(self._storage.keys())

            def get_xattr(self, key):
                return self._storage.get(key, "")

            def set_xattr(self, key, val):
                self._storage[key] = val

            def unset_xattr(self, key):
                try:
                    self._storage.pop(key)
                except KeyError:
                    pass

        class MySearchEngine(SearchEngine):

            def _listdir(self, path):
                pl = len(path) + 1
                r = MyTestCase._ustorage.keys()
                r = [x[pl:] for x in r if (f"{x}/").startswith(f"{path}/")]
                r = [(x[:x.find("/")] if ("/" in x) else x) for x in r if x]
                return list(set(r))

            def _isdir(self, path):
                return bool(self._listdir(path))

        @staticmethod
        def get_myinterpreter(path):
            return get_interpreter(path, engineclass=MyTestCase.MyMetadataEngine)

        @staticmethod
        def get_mysearchengine(rootpath):
            return get_searchengine(rootpath, searchengineclass=MyTestCase.MySearchEngine,
                                    engineclass=MyTestCase.MyMetadataEngine)

        def test_parse_and_generate_tagstring_to_from_tagassignments(self):
            for ts in ["mytag1",
                       "mytag2%3Fatt1%3D1",
                       "mytag3%3Fatt2",
                       "mytag4%3Fatt3%26att4%3D%22foo%22",
                       "mytag5%3Fatt5%3Dfalse%26att6%3D0%26att7%26att8%3D0.0"]:
                tas = TagAssignments.from_tagsstring(ts, MyTestCase.dummyfname)
                ts1 = tas.to_tagsstring()
                self.assertEqual(ts1, ts)

        def test_create_tagassignment_s_and_tagassignments_s_from_scratch_and_assign_them(self):
            engine1 = MyTestCase.get_myinterpreter("/test_d/b1")
            engine2 = MyTestCase.get_myinterpreter("/test_d/b1/a2")
            tas = engine1.get_tagassignments_flat()
            tas.add_assignment("t1")
            tas.add_assignment(TagAssignment.from_tagstring("t2"))
            tas.add_assignment(TagAssignment("t3"))
            engine1.store_tagassignments(tas)
            tas = TagAssignments("/test_d/b1/a2")
            tas.add_assignment("t4")
            engine2.store_tagassignments(tas)
            tas = engine2.get_tagassignments()
            ftags = tas.assignments()
            for iftags, (seftags, sefisoutsize) in \
                    enumerate([("t1", True), ("t2", True), ("t3", True), ("t4", False)]):
                ssftags = ftags[iftags].to_tagstring()
                self.assertEqual(ssftags, seftags)
                self.assertEqual(tas.is_outlying_assignment(ftags[iftags]), sefisoutsize)

        def test_tags_non_alphanumeric_characters(self):
            for tname in ["whitespaces in\tnames",
                          "some.other,difficult;characters/are",
                          "more\nline\nbreak"]:
                ta = TagAssignment(tname)
                ts = ta.to_tagstring()
                ta2 = TagAssignment.from_tagstring(ts)
                tname2 = ta2.tagname()
                self.assertEqual(tname, tname2)

        def test_hilvl_tags(self):
            engine = MyTestCase.get_myinterpreter("/test_i/a1")
            self.assertEqual(engine.tags(), [])
            engine.add_tag(tagname="tag?name1")
            engine.add_tag(tagname="tag?name2")
            engine.add_tag(tagstring="tag%3Fname3")
            self.assertEqual(sorted([x.to_tagstring() for x in engine.tags()]),
                             sorted(["tag%3Fname1", "tag%3Fname2", "tag%3Fname3"]))

        def test_hilvl_comment(self):
            engine = MyTestCase.get_myinterpreter("/test_j/a1")
            self.assertEqual(engine.comment(), "")
            engine.set_comment("a\nb")
            engine.add_comment("c")
            engine.add_comment("d\ne")
            engine.add_comment("f\n")
            engine.add_comment("g")
            self.assertEqual(engine.comment(), "a\nb\nc\n\nd\ne\n\nf\ng")
            engine.add_comment("h\ni")
            self.assertEqual(engine.comment(), "a\nb\nc\n\nd\ne\n\nf\ng\n\nh\ni\n")
            engine2 = MyTestCase.get_myinterpreter("/test_j/a1/a2")
            engine2.add_comment("a")
            self.assertEqual(engine2.comment(), "a")
            engine2.add_comment("b")
            self.assertEqual(engine2.comment(), "a\nb")

        def test_hilvl_rating(self):
            engine = MyTestCase.get_myinterpreter("/test_k/a1")
            self.assertEqual(engine.rating(), MetadataInterpreter.RATING_DEFAULT_VALUE)
            engine.set_rating(MetadataInterpreter.RATING_MIN_VALUE - 100)
            self.assertEqual(engine.rating(), MetadataInterpreter.RATING_MIN_VALUE)
            engine.set_rating(MetadataInterpreter.RATING_MAX_VALUE + 100)
            self.assertEqual(engine.rating(), MetadataInterpreter.RATING_MAX_VALUE)
            engine.set_rating(1)
            self.assertEqual(engine.rating(), 1)
            engine.reset_rating()
            self.assertEqual(engine.rating(), MetadataInterpreter.RATING_DEFAULT_VALUE)

        def test_hilvl_geo(self):
            engine = MyTestCase.get_myinterpreter("/test_l/a1")
            self.assertEqual(engine.geo(), None)
            engine.set_geolocation(lat=10, lon=20, accuracy_meters=5.1, foo="bar")
            gg1 = engine.geo()
            self.assertEqual(gg1.lat(), 10.0)
            self.assertEqual(gg1.lon(), 20.0)
            self.assertEqual(gg1.accuracy_meters(), 5.1)
            self.assertEqual(gg1.get_geoatt("foo"), "bar")
            self.assertEqual(gg1.get_geoatt("goo", "noo"), "noo")
            gg1.set_lat(17.5)
            engine.set_geo(gg1)
            gg2 = engine.geo()
            self.assertEqual(gg2.lat(), 17.5)
            self.assertEqual(gg2.lon(), 20.0)
            self.assertEqual(gg2.accuracy_meters(), 5.1)
            self.assertEqual(gg2.get_geoatt("foo"), "bar")
            for ls, elat, elon, eacc, eatts, els in [
                ("lat=1&lon=2", 1, 2, 0, {}, "lat=1.0&lon=2.0"),
                ("lat=11&lon=22&acc=33", 11, 22, 33, {}, "lat=11.0&lon=22.0&acc=33.0"),
                ("lat=1&lon=1&foo=bar&acc=0", 1, 1, 0, {'foo': 'bar'}, "lat=1.0&lon=1.0&foo=bar"),
                ("lat=-361&lon=362", -1, 2, 0, {}, "lat=-1.0&lon=2.0"),
            ]:
                engine.set_geo(GeoLocation.from_geostring(ls))
                gg3 = engine.geo()
                self.assertEqual(gg3.lat(), elat)
                self.assertEqual(gg3.lon(), elon)
                self.assertEqual(gg3.accuracy_meters(), eacc)
                for k, v in eatts.items():
                    self.assertEqual(gg3.get_geoatt(k), v)
                self.assertEqual(gg3.to_geostring(), els)
            gp1 = GeoLocation(lat=50.77473, lon=6.08393, accuracy_meters=1500)
            gp2 = GeoLocation.from_geostring("acc=400&lon=6.11064&lat=50.80439")
            def is_roundabout(i1, i2, thresh=0.1):
                avg = (i1 + i2) / 2
                return math.fabs(thresh * 0.5 * avg) >= math.fabs(i1-avg), "{} vs. {}".format(i1, i2)
            self.assertFalse(*is_roundabout(gp2.distance_meters(gp1), 3000))
            self.assertFalse(*is_roundabout(gp2.distance_meters(gp1), 5000))
            self.assertTrue(*is_roundabout(gp1.distance_meters(gp2), 4000))
            self.assertTrue(*is_roundabout(gp2.distance_meters(gp1), 4000))
            gpint1 = gp1.distance_meters_interval(gp2)
            gpint2 = gp1.distance_meters_interval(gp2)
            self.assertTrue(*is_roundabout(gpint1[0], 2000))
            self.assertTrue(*is_roundabout(gpint2[0], 2000))
            self.assertTrue(*is_roundabout(gpint1[1], 6000))
            self.assertTrue(*is_roundabout(gpint2[1], 6000))

        def test_interpreter_cache_xattr(self):
            class MyS1MetadataEngine(MyTestCase.MyMetadataEngine):
                def __init__(self, path):
                    MyTestCase.MyMetadataEngine.__init__(self, path)
                    self.cnt = 0
                def get_xattr(self, key):
                    self.cnt += 1
                    return super().get_xattr(key)
            engine = get_interpreter("/test_o/a1", engineclass=MyS1MetadataEngine)
            self.assertEqual(engine._xattrengine.cnt, 0)
            engine.tags(full=False)
            self.assertEqual(engine._xattrengine.cnt, 1)
            engine.tags(full=False)
            engine.tags(full=False)
            self.assertEqual(engine._xattrengine.cnt, 3)
            with MetadataInterpreter.Cache():
                engine.tags(full=False)
                self.assertEqual(engine._xattrengine.cnt, 4)
                engine.tags(full=False)
                engine.tags(full=False)
                self.assertEqual(engine._xattrengine.cnt, 4)
            engine.tags(full=False)
            self.assertEqual(engine._xattrengine.cnt, 5)
            engine.tags(full=False)
            engine.tags(full=False)
            self.assertEqual(engine._xattrengine.cnt, 7)

        def test_hilvl_getcompletemetadata(self):
            engine0 = MyTestCase.get_myinterpreter("/test_p")
            engine0.add_tag(tagstring="t0")
            engine = MyTestCase.get_myinterpreter("/test_p/n1")
            engine.set_comment("a")
            engine.set_rating(1)
            engine.set_geo("lat=1&lon=2&acc=3")
            engine.add_tag(tagname="t1")
            engine.add_tag(tagstring="t2")
            rd = json.loads(engine.get_complete_metadata().to_json())
            self.assertEqual(rd["comment"], "a")
            self.assertEqual(rd["geo"]["lat"], 1)
            self.assertEqual(rd["geo"]["lon"], 2)
            self.assertEqual(rd["geo"]["acc"], 3)
            self.assertEqual(rd["geo"]["geostring"], "lat=1.0&lon=2.0&acc=3.0")
            self.assertEqual(rd["rating"], 1)
            self.assertEqual(rd["tags"][0]["tagname"], "t0")
            self.assertEqual(rd["tags"][0]["filepath"], "/test_p")
            self.assertEqual(rd["tags"][0]["is_outlying"], True)
            self.assertEqual(rd["tags"][0]["tagstring"], "t0")
            self.assertEqual(rd["tags"][1]["tagname"], "t1")
            self.assertEqual(rd["tags"][1]["filepath"], "/test_p/n1")
            self.assertEqual(rd["tags"][1]["is_outlying"], False)
            self.assertEqual(rd["tags"][1]["tagstring"], "t1")
            self.assertEqual(rd["tags"][2]["tagname"], "t2")
            self.assertEqual(rd["tags"][2]["filepath"], "/test_p/n1")
            self.assertEqual(rd["tags"][2]["is_outlying"], False)
            self.assertEqual(rd["tags"][2]["tagstring"], "t2")
            self.assertEqual(rd["tags_tagsstring_flat"], "t1,t2")
            self.assertEqual(rd["tags_tagsstring_full"], "t0,t1,t2")

        def test_search_via_querystring_by_tags_comment_rating_geo(self):
            se = MyTestCase.get_mysearchengine("/test_q/a")
            MyTestCase.get_myinterpreter("/test_q").add_tag(tagstring="t")
            MyTestCase.get_myinterpreter("/test_q/a").add_tag(tagstring="ta")
            MyTestCase.get_myinterpreter("/test_q/b").add_tag(tagstring="tb")
            enginew = MyTestCase.get_myinterpreter("/test_q/a/w")
            enginew.set_rating(1)
            enginew.add_tag(tagstring="tx")
            enginex = MyTestCase.get_myinterpreter("/test_q/a/x")
            enginex.set_comment("comment foo")
            enginex.set_rating(2)
            enginex.set_geo(GeoLocation(lat=10.1, lon=20))
            enginex.add_tag(tagstring="tx")
            enginex.add_tag(tagstring="tfoo")
            enginey = MyTestCase.get_myinterpreter("/test_q/a/y")
            enginey.set_comment("comment bar")
            enginey.set_rating(3)
            enginey.set_geo(GeoLocation(lat=10, lon=20.1))
            enginey.add_tag(tagstring="ty")
            enginey.add_tag(tagstring="tbar")
            enginez = MyTestCase.get_myinterpreter("/test_q/a/z")
            enginez.set_comment("comment baz")
            enginez.set_rating(4)
            enginez.set_geo(GeoLocation(lat=20, lon=50))
            enginez.add_tag(tagstring="tz")
            enginez.add_tag(tagstring="tbaz")
            def _strp(sr):
                return sorted([x.path[x.path.rfind("/")+1] for x in sr])
            self.assertEqual(_strp(se.search("Comment?")), ["w", "x", "y", "z"])
            self.assertEqual(_strp(se.search("Comment?comment foo")), ["x"])
            self.assertEqual(_strp(se.search("Comment?comment ba.&is_re=true")), ["y", "z"])
            self.assertEqual(_strp(se.search("Geo?lat=10&lon=20&dist=20000")), ["x", "y"])
            self.assertEqual(_strp(se.search("Rating?min=2")), ["x", "y", "z"])
            self.assertEqual(_strp(se.search("Rating?max=2")), ["w", "x"])
            self.assertEqual(_strp(se.search("Rating?min=2&max=3")), ["x", "y"])
            self.assertEqual(_strp(se.search("Tags?t")), ["w", "x", "y", "z"])
            self.assertEqual(_strp(se.search("Tags?tx")), ["w", "x"])
            self.assertEqual(_strp(se.search("Tags?tba.&is_re=true")), ["y", "z"])

        def test_search_via_searchcriteria_by_combined(self):
            se = MyTestCase.get_mysearchengine("/test_r/a")
            enginew = MyTestCase.get_myinterpreter("/test_r/a/w")
            enginew.set_rating(1)
            enginew.add_tag(tagstring="tw")
            enginex = MyTestCase.get_myinterpreter("/test_r/a/x")
            enginex.set_comment("comment foo")
            enginex.set_rating(2)
            enginex.set_geo(GeoLocation(lat=10.1, lon=20))
            enginex.add_tag(tagstring="tx")
            enginex.add_tag(tagstring="tfoo")
            enginey = MyTestCase.get_myinterpreter("/test_r/a/y")
            enginey.set_comment("comment bar")
            enginey.set_rating(3)
            enginey.set_geo(GeoLocation(lat=10, lon=20.1))
            enginey.add_tag(tagstring="ty")
            enginey.add_tag(tagstring="tbar")
            enginez = MyTestCase.get_myinterpreter("/test_r/a/z")
            enginez.set_comment("comment baz")
            enginez.set_rating(4)
            enginez.set_geo(GeoLocation(lat=20, lon=50))
            enginez.add_tag(tagstring="tz")
            enginez.add_tag(tagstring="tbaz")
            def _strp(sr):
                return sorted([x.path[x.path.rfind("/") + 1] for x in sr])
            self.assertEqual(_strp(se.search(SearchCriterionAnd(
                SearchCriterionComment("comment ba.", comment_is_regexp=True),
                SearchCriterionGeo(center_lat=10, center_lon=20, distance_meters=20000)
            ))), ["y"])
            self.assertEqual(_strp(se.search(SearchCriterionOr(
                SearchCriterionComment("comment ba.", comment_is_regexp=True),
                SearchCriterionTags("tx"),
            ))), ["x", "y", "z"])
            self.assertEqual(_strp(se.search(SearchCriterionAnd(
                SearchCriterionComment("comment ba.", comment_is_regexp=True),
                SearchCriterionNot(SearchCriterionGeo(center_lat=20, center_lon=50, distance_meters=20000))
            ))), ["y"])
            self.assertEqual(_strp(se.search(SearchCriterionOr(
                SearchCriterionTags("ty"),
                SearchCriterionTags("tx"),
            ), SearchCriterionRating(max=2))), ["x"])

        def test_search_convert_querystring_searchcriterion(self):
            for qs in ["Comment?foo", "Tags?foo&is_re=true",
                       "Or?{Tags?foo}&{And?{Geo?lat=1.0&lon=2.0&dist=4000.0}&{Tags?bar}}&{Rating?min=3&max=4}",
                       "XattrValue?foo&key=bar&key_is_re=true&value_is_re=true"]:
                cqs = SearchCriterion.from_querystring(
                    SearchCriterion.from_querystring(qs).to_querystring()).to_querystring()
                self.assertEqual(cqs, qs)
            for sc, qs in [(SearchCriterionRating(max=3, min=1), "Rating?min=1&max=3"),
                           (SearchCriterionGeo(center_lon=2, center_lat=3), "Geo?lat=3.0&lon=2.0&dist=5000"),
                           (SearchCriterionNot(SearchCriterionTags("foo")), "Not?{Tags?foo}")]:
                cqs = sc.to_querystring()
                self.assertEqual(cqs, qs)

        def test_search_by_xattr(self):
            se = MyTestCase.get_mysearchengine("/test_s/a")
            enginex = MyTestCase.get_myinterpreter("/test_s/a/x")
            enginex.set_comment("comment foo")
            enginex.add_tag(tagstring="tx")
            enginex.add_tag(tagstring="tfoo")
            enginey = MyTestCase.get_myinterpreter("/test_s/a/y")
            enginey.set_comment("comment bar")
            enginey.set_rating(3)
            enginey.add_tag(tagstring="ty")
            enginey.add_tag(tagstring="tbar")
            def _strp(sr):
                return sorted([x.path[x.path.rfind("/") + 1] for x in sr])
            self.assertEqual(_strp(se.search("XattrValue?tfoo,tx&key=xdg.tags")), ["x"])
            self.assertEqual(_strp(se.search("XattrValue?c.*t%20ba.&key=xdg.comment&value_is_re=true")), ["y"])
            self.assertEqual(_strp(se.search("XattrValue?c.*t%20ba.&key=.*co.*t&key_is_re=true&value_is_re=true")), ["y"])
            self.assertEqual(_strp(se.search("XattrValue?&key=baloo.rating")), ["x"])

        def test_search_querystring_empty(self):
            se = MyTestCase.get_mysearchengine("/test_t")
            MyTestCase.get_myinterpreter("/test_t/a").set_rating(1)
            with self.assertRaises(MetadataFormatError):
                se.search("")

        def test_search_tags_control_character(self):
            se = MyTestCase.get_mysearchengine("/test_u")
            MyTestCase.get_myinterpreter("/test_u/a").add_tag(tagname="f?o{o")
            self.assertEqual(se.search(SearchCriterionTags("f?o{o"))[0].path, "/test_u/a")
