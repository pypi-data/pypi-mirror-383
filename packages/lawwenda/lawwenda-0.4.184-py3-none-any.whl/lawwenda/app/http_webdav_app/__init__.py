# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
A wsgi application that provides an http interface to a filesystem.

See :py:class:`HttpWebdavApp`.
"""
import mimetypes
import typing as t
import xml.etree.ElementTree as ET

import werkzeug.exceptions
import werkzeug.routing
import werkzeug.serving
import werkzeug.wrappers
import werkzeug.wsgi

import lawwenda.app.http_webdav_app.davprop

if t.TYPE_CHECKING:
    import lawwenda.fs


# pylint: disable=no-self-use,unused-argument
class HttpWebdavApp:
    """
    A wsgi application that provides an http interface to a filesystem.

    It provides bare http access, and also WebDAV extensions for a more complete interface. It does not provide an own
    user interface or user authentication.
    """

    # TODO ensure (list, get, put) compatible with nautilus, dolphin, windows
    # TODO prevent csrf in webdav?! (e.g. use another auth realm name somehow?! but how?!)
    # TODO review all
    # TODO If-Range?

    def __init__(self, root_node: "lawwenda.fs.node.Node"):
        self.__root_node = root_node

    @property
    def root_node(self) -> "lawwenda.fs.node.Node":
        """
        The filesystem root node served by this HttpWebdavApp.
        """
        return self.__root_node

    def _method_get(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node", *,
                    is_head_request: bool = False):
        if not node.is_file:
            return werkzeug.exceptions.NotFound()

        ranges_str = request.headers.get("Range") or ""
        headers = {"Accept-Ranges": "bytes"}
        status = 200

        range_end = -1
        range_begin = -1
        if ranges_str.startswith("bytes="):
            range_begin = node.size
            range_end = -1
            for range_str in [r for r in [r.strip() for r in ranges_str[6:].split(",")] if r]:
                range_str_parts = range_str.split("-")
                if len(range_str_parts) == 2:
                    range_begin = min(int(range_str_parts[0]), range_begin)
                    range_end = max(int(range_str_parts[1] or node.size - 1), range_end)
            if range_end != -1:
                headers["Content-Range"] = f"bytes {range_begin}-{range_end}/{node.size}"
                status = 206

        response_content = b""
        if not is_head_request:
            with node.read_file() as f:
                if range_end != -1:
                    f.seek(range_begin)
                response_content = f.read((range_end - range_begin + 1) if (range_end != -1) else -1)

        return werkzeug.wrappers.Response(response_content, mimetype=mimetypes.guess_type(node.path)[0],
                                          headers=headers, status=status)

    def _method_head(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node"):
        return self._method_get(request, node, is_head_request=True)

    def _method_propfind(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node"):#TODO finish
        props = []
        depth = request.headers.get("Depth", "infinity")
        if request.data:
            xreq = ET.fromstring(request.data)
            for cxreq in xreq:
                if cxreq.tag == "{DAV:}prop":
                    for ccxreq in cxreq:
                        props.append(ccxreq.tag)
        else:
            props = [prop.davname for prop in lawwenda.app.http_webdav_app.davprop.all_props]
        def _walker(xresult, walknode, furl, dpt):
            # TODO if not walknode.exists?!
            resp = ET.Element("{DAV:}response")
            resphref = ET.Element("{DAV:}href")
            resphref.text = furl
            resp.append(resphref)
            for prop in props:
                resppropstat = ET.Element("{DAV:}propstat")
                respstatus = ET.Element("{DAV:}status")
                respstatus.text = "HTTP/1.1 200 OK"
                resppropstat.append(respstatus)
                respprop = ET.Element("{DAV:}prop")
                resppropval = ET.Element(prop)
                dprop = lawwenda.app.http_webdav_app.davprop.get_prop_by_davname(prop)
                if dprop:
                    dpropval = dprop.get_for_node(walknode)
                    if isinstance(dpropval, ET.Element):
                        resppropval.append(dpropval)
                    else:
                        resppropval.text = str(dpropval)
                else:
                    respstatus.text = "HTTP/1.1 404 Not Found"
                respprop.append(resppropval)
                resppropstat.append(respprop)
                resp.append(resppropstat)
            xresult.append(resp)
            if (dpt != "0") and walknode.is_dir:
                for cfn in walknode.child_nodes:  # TODO prevent symlink circles
                    cfurl = f"{furl}{cfn.name}/"
                    _walker(xresult, cfn, cfurl, dpt if (dpt == "infinity") else "0")
        result = ET.Element("{DAV:}multistatus")
        _walker(result, node, "./", depth)
        return werkzeug.wrappers.Response(ET.tostring(result), mimetype="text/xml", status=207)

    def _method_proppatch(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node"):#TODO finish
        props = []  # TODO dedup
        xreq = ET.fromstring(request.data)
        for cxreq in xreq:
            if cxreq.tag == "{DAV:}prop":
                for cxreqprop in cxreq:
                    props.append(cxreqprop.tag)
        result = ET.Element("{DAV:}multistatus")
        resp = ET.Element("{DAV:}response")
        resphref = ET.Element("{DAV:}href")
        resphref.text = request.url
        resp.append(resphref)
        resppropstat = ET.Element("{DAV:}propstat")
        respstatus = ET.Element("{DAV:}status")
        respstatus.text = "HTTP/1.1 409 Conflict"
        # TODO complete answer instead (this is an incomplete dummy)
        resppropstat.append(respstatus)
        resp.append(resppropstat)
        result.append(resp)
        return werkzeug.wrappers.Response(ET.tostring(result), mimetype="text/xml", status=207)

    def _method_options(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node"):
        return werkzeug.wrappers.Response(headers={"Allows": ", ".join(self.__allowed_methods), "DAV": "1"})

    def _method_put(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node"):
        if (not node.parent_node.is_dir) or node.is_dir:
            return werkzeug.exceptions.Conflict()
        node.write_file(request.data)  # TODO noh preserve metadata on overwrite?!
        return werkzeug.wrappers.Response(status=201)

    def _method_delete(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node"):
        node.delete()
        return werkzeug.wrappers.Response(status=204)

    def _method_mkcol(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node"):
        node.mkdir()
        return werkzeug.wrappers.Response(status=201)

    def _method_copy(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node"):
        return self.__method_copy_move(request, node, transfer_method="copy_to")

    def _method_move(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node"):
        return self.__method_copy_move(request, node, transfer_method="move_to")

    def __method_copy_move(self, request: werkzeug.wrappers.Request, node: "lawwenda.fs.node.Node", *,
                           transfer_method: str):
        destination_node = self.__root_node.child_by_path(request.headers["Destination"])

        if destination_node.exists:
            if request.headers.get("overwrite") == "F":
                return werkzeug.exceptions.PreconditionFailed()
            else:
                destination_node.delete()

        getattr(node, transfer_method)(destination_node.path)
        return werkzeug.wrappers.Response(status=204)

    @property
    def __allowed_methods(self) -> t.Sequence[str]:
        return tuple(attr_name[8:].upper() for attr_name in dir(self) if attr_name.startswith("_method_"))

    def __call__(self, environ, start_response):
        request = werkzeug.wrappers.Request(environ)
        if method_func := getattr(self, f"_method_{request.method.lower()}"):
            response = method_func(request, self.__root_node.child_by_path(request.path))
        else:
            response = werkzeug.exceptions.MethodNotAllowed(valid_methods=self.__allowed_methods)
        return response(environ, start_response)
