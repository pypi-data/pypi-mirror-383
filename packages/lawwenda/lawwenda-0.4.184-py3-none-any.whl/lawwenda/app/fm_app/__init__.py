# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
A wsgi application that provides a browser based user interface, similar to a desktop file manager.

See :py:class:`FmApp`.
"""
import base64
import hashlib
import html
import io
import json
import mimetypes
import os
import pathlib
import random
import stat
import string
import threading
import time
import typing as t
import zipfile

import werkzeug.datastructures.auth
import werkzeug.exceptions
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi

import lawwenda.app.http_webdav_app
import lawwenda.asset
import lawwenda.config.share
import lawwenda.fs.factory
import lawwenda.fs.search


# pylint: disable=no-self-use,unused-argument
class FmApp:
    """
    A wsgi application that provides a browser based user interface, similar to a desktop file manager, for a particular
    share. It also includes :py:class:`lawwenda.app.http_webdav_app.HttpWebdavApp` for bare http/WebDAV functionality.
    """

    URL_INTERNALS_NAME = ".~__lawwenda__int~"  # TODO security?! we should make sure that such a node is forbidden?!

    def __init__(self, share: "lawwenda.config.share.Share"):
        """
        :param share: The share to provide by this application.
        """
        self.__templates_dir = pathlib.Path(__file__).parent / "-templates"
        self.__share = share
        self.__temp_zips = _TempZips()
        self.__root_node = lawwenda.fs.factory.filesystem(
            share.path, readonly=share.readonly,
            hide_by_patterns=share.hide_by_patterns, hide_by_tags=share.hide_by_tags,
            include_by_patterns=share.include_by_patterns, include_by_tags=share.include_by_tags,
            exclude_by_patterns=share.exclude_by_patterns, exclude_by_tags=share.exclude_by_tags,
            exclude_hidden=share.exclude_hidden)
        self.__http_webdav_app = lawwenda.app.http_webdav_app.HttpWebdavApp(self.__root_node)
        self.__auth_cache = {}
        self.__auth_lock = threading.Lock()
        self.__url_map = werkzeug.routing.Map((
            werkzeug.routing.Rule("/api/copy/", endpoint="api_copy", methods=("POST",)),
            werkzeug.routing.Rule("/api/delete/", endpoint="api_delete", methods=("POST",)),
            werkzeug.routing.Rule("/api/details/", endpoint="api_details", methods=("GET",)),
            werkzeug.routing.Rule("/api/dir/", endpoint="api_dir", methods=("GET",)),
            werkzeug.routing.Rule("/api/known_tags/", endpoint="api_known_tags", methods=("GET",)),
            werkzeug.routing.Rule("/api/mkdir/", endpoint="api_mkdir", methods=("POST",)),
            werkzeug.routing.Rule("/api/move/", endpoint="api_move", methods=("POST",)),
            werkzeug.routing.Rule("/api/rename/", endpoint="api_rename", methods=("POST",)),
            werkzeug.routing.Rule("/api/set_comment/", endpoint="api_set_comment", methods=("POST",)),
            werkzeug.routing.Rule("/api/set_geo/", endpoint="api_set_geo", methods=("POST",)),
            werkzeug.routing.Rule("/api/set_rating/", endpoint="api_set_rating", methods=("POST",)),
            werkzeug.routing.Rule("/api/tag_entries/", endpoint="api_tag_entries", methods=("POST",)),
            werkzeug.routing.Rule("/api/thumbnail/", endpoint="api_thumbnail", methods=("GET",)),
            werkzeug.routing.Rule("/api/untag_entries/", endpoint="api_untag_entries", methods=("POST",)),
            werkzeug.routing.Rule("/api/upload/", endpoint="api_upload", methods=("POST",)),
            werkzeug.routing.Rule("/api/zip/", endpoint="api_zip", methods=("POST",)),
            werkzeug.routing.Rule("/api/zip_content/<zip_id>/stuff.zip", endpoint="api_zip_content", methods=("GET",)),
            werkzeug.routing.Rule("/help", endpoint="help", methods=("GET",)),
            werkzeug.routing.Rule("/static/<path:file_path>", endpoint="static", methods=("GET",))))

    @property
    def root_node(self) -> lawwenda.fs.node.Node:
        """
        The filesystem root node served by this FmApp.
        """
        return self.__root_node

    def _on_api_dir(self, request):
        node = self.__root_node.child_by_path(request.args["path"])
        settings = json.loads(request.args["config"])

        hidden_files_visible = settings.get("hiddenFilesVisible", False)
        sort_column = settings.get("sortColumn")
        if sort_column not in ("name", "size", "mtime"):
            sort_column = "name"
        sort_descending = settings.get("sortDescending", False)
        search_config = settings.get("searchConfig")

        if search_config:
            nodes = list(lawwenda.fs.search.create_search(**json.loads(search_config)).query(node))
        else:
            nodes = list(node.child_nodes)

        if not hidden_files_visible:
            nodes = [_ for _ in nodes if not _.is_hidden]
        nodes.sort(key=lambda _: (getattr(_, sort_column), _.name), reverse=sort_descending)
        nodes.sort(key=lambda _: 0 if _.is_dir else 1)

        return self.__json_response([_.basics_as_dict for _ in nodes])

    def _on_api_details(self, request):
        return self.__json_response(self.__root_node.child_by_path(request.args["path"]).full_as_dict)

    def _on_api_delete(self, request):
        for path in request.json["paths"]:
            self.__root_node.child_by_path(path).delete()

    def _on_api_mkdir(self, request):
        self.__root_node.child_by_path(request.json["path"]).mkdir()

    def _on_api_copy(self, request):
        return self.__on_api_copy_move(request, False)

    def _on_api_move(self, request):
        return self.__on_api_copy_move(request, True)

    def _on_api_rename(self, request):
        node = self.__root_node.child_by_path(request.json["path"])
        node.move_to(node.parent_node.child_by_name(request.json["newname"]).path)

    def _on_api_set_comment(self, request):
        comment = request.json["comment"]
        for path in request.json["paths"]:
            self.__root_node.child_by_path(path).set_comment(comment)

    def _on_api_set_geo(self, request):
        geo = request.json["geo"]
        for path in request.json["paths"]:
            self.__root_node.child_by_path(path).set_geo(geo)

    def _on_api_set_rating(self, request):
        rating = request.json["rating"]
        for path in request.json["paths"]:
            self.__root_node.child_by_path(path).set_rating(rating)

    def _on_api_thumbnail(self, request):
        return werkzeug.wrappers.Response(self.__root_node.child_by_path(request.args["path"]).thumbnail(),
                                          mimetype="image/png")

    def _on_api_upload(self, request):
        destination_dir_node = self.__root_node.child_by_path(request.form["destpath"])
        for upload_file in request.files.getlist("upload"):
            destination_dir_node.child_by_name(upload_file.filename).write_file(upload_file)

    def _on_api_known_tags(self, _):
        return self.__json_response(tuple(self.__root_node.known_tags()))

    def _on_api_tag_entries(self, request):
        tag = request.json["tag"]
        for path in request.json["paths"]:
            self.__root_node.child_by_path(path).add_tag(tag)

    def _on_api_untag_entries(self, request):
        tag = request.json["tag"]
        for path in request.json["paths"]:
            self.__root_node.child_by_path(path).remove_tag(tag)

    def _on_api_zip(self, request):
        zip_id = self.__temp_zips.create_temp_zip([self.__root_node.child_by_path(path)
                                                   for path in request.json["paths"]])
        return self.__json_response({"url": f"{self.URL_INTERNALS_NAME}/api/zip_content/{zip_id}/stuff.zip"})

    def _on_api_zip_content(self, _, zip_id):
        time.sleep(0.1)  # security; so guessing zip_ids is harder
        zip_content = self.__temp_zips.temp_zip_content(zip_id)
        if zip_content is None:
            return werkzeug.exceptions.NotFound()
        return werkzeug.wrappers.Response(zip_content, mimetype="application/zip")

    def __on_api_copy_move(self, request, move: bool):
        destination_dir = request.json["destpath"]
        for source_path in request.json["srcpaths"]:
            source_node = self.__root_node.child_by_path(source_path)
            (source_node.move_to if move else source_node.copy_to)(f"{destination_dir}/{source_node.name}")

    def _on_static(self, _, file_path):
        full_path = (lawwenda.asset.data.data_dir / f"web/{file_path}").resolve()

        if not (full_path.is_relative_to(lawwenda.asset.data.data_dir) and full_path.is_file()):
            return werkzeug.exceptions.NotFound()

        return werkzeug.wrappers.Response(full_path.read_bytes(), mimetype=mimetypes.guess_type(file_path)[0],
                                          headers={"Cache-Control": "public, max-age=600"})

    def _on_help(self, _):
        ui_pdf = lawwenda.asset.data.find_data_file("ui.pdf")
        if not ui_pdf:
            return werkzeug.routing.RequestRedirect(
                "https://pseudopolis.eu/wiki/pino/projs/lawwenda/FULLREADME/UI.html")
        return werkzeug.wrappers.Response(ui_pdf.read_bytes(), mimetype="application/pdf",
                                          headers={"Cache-Control": "public, max-age=600"})

    def __json_response(self, data: t.Any) -> werkzeug.wrappers.Response:
        return werkzeug.wrappers.Response(json.dumps(data), mimetype="application/json")

    def __render_template(self, template: str, *, html_head_inner: str = "", path: str = "", head_only: bool = False,
                          url_internals_name: str = URL_INTERNALS_NAME, **kwargs) -> werkzeug.wrappers.Response:
        csrf_token = base64.b64encode(os.urandom(64)).decode()
        response_content = "" if head_only else self.__render_template_text(
            template, **kwargs, html_head_inner=html_head_inner, url_internals_name=url_internals_name, path=path,
            rootname=self.__share.title, accessmode="readwrite" if self.__root_node.is_writable else "read",
            csrf_token=csrf_token)
        response = werkzeug.wrappers.Response(response_content, mimetype=mimetypes.guess_type(template)[0],
                                              headers={"Cache-Control": "public, max-age=600"})
        response.set_cookie("csrf_token", csrf_token)
        return response

    def __render_template_text(self, template: str, *, csrf_token: str, html_head_inner: str, **kwargs) -> str:
        html_body_inner = self.__render_template_text_raw(template, **kwargs)
        return self.__render_template_text_raw("base.html", **kwargs, html_head_inner=html_head_inner,
                                               html_body_inner=html_body_inner, csrf_token=csrf_token)

    def __render_template_text_raw(self, template: str, **kwargs) -> str:
        with open(f"{self.__templates_dir}/{template}", "r") as f:
            return f.read().format(**{k: _RenderTemplateValue(v) for k, v in kwargs.items()})

    def __auth(self, username: str, password: str) -> bool:
        if not self.__share.password_scrypt:
            return True
        if len(username) > 100 or len(password) > 100:
            return False

        with self.__auth_lock:
            result = self.__auth_cache.get((username, password))
            if result is None:
                salt = base64.b64decode(self.__share.password_salt)
                share_scrypt = base64.b64decode(self.__share.password_scrypt)
                password_scrypt = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1)
                result = password_scrypt == share_scrypt

                if len(self.__auth_cache) > 30:
                    self.__auth_cache.pop(random.choice(list(self.__auth_cache.keys())))
                self.__auth_cache[(username, password)] = result

        return result

    def __dispatch_request(self, request):
        try:
            self.__ensure_authed(request)
        except werkzeug.exceptions.HTTPException as ex:
            return ex

        if f"/{self.URL_INTERNALS_NAME}/" in request.environ["PATH_INFO"]:
            return self.__dispatch_request_internals(request)
        return self.__dispatch_request_normal(request)

    def __ensure_authed(self, request):
        if not self.__share.password_scrypt:
            return

        credentials = request.authorization
        if credentials:
            if not (credentials.password and self.__auth(credentials.username, credentials.password)):
                raise werkzeug.exceptions.Forbidden()
        else:
            raise werkzeug.exceptions.Unauthorized(www_authenticate=werkzeug.datastructures.auth.WWWAuthenticate(
                "basic", {"realm": f"file share: {self.__share.name}"}))

    def __dispatch_request_internals(self, request):
        if request.method not in ("GET", "HEAD"):
            csrf_token_1 = request.cookies.get("csrf_token")
            csrf_token_2 = request.headers.get("X-CSRFToken")
            if (not csrf_token_1) or (csrf_token_1 != csrf_token_2):
                return werkzeug.exceptions.Forbidden("csrf tokens do not match (cookies disables?)")

        path_segment = None
        while path_segment != self.URL_INTERNALS_NAME:
            path_segment = lawwenda.app.pop_path_info(request.environ)

        endpoint, values = self.__url_map.bind_to_environ(request.environ).match()
        try:
            return getattr(self, f"_on_{endpoint}")(request, **values) or self.__json_response(None)
        except werkzeug.exceptions.HTTPException as ex:
            return ex

    def __dispatch_request_normal(self, request):
        node = self.__root_node.child_by_path(request.path)

        if request.method in ("GET", "HEAD") and node.is_dir:
            if not request.environ["PATH_INFO"].endswith("/"):
                url = request.url
                if not url.endswith("/"):
                    url = f"{url}/"
                return werkzeug.routing.RequestRedirect(url)

            return self.__render_template("index.html", path=request.path, html_head_inner=f"""
            <script type="module" src="{self.URL_INTERNALS_NAME}/static/pageresources/index.js"></script>
            <link rel="stylesheet" href="{self.URL_INTERNALS_NAME}/static/pageresources/index.css" type="text/css"/>""")

        return None  # otherwise we leave it to the HttpWebdavApp

    def __call__(self, environ, start_response):
        request = werkzeug.wrappers.Request(environ)
        response = self.__dispatch_request(request)
        return (response or self.__http_webdav_app)(environ, start_response)


class _TempZips:
    """
    Handler for temporary zip files.

    Allows to create zip files containing some nodes and automatically cleans them up after some time.

    This is a static class, potentially used by many applications in parallel.
    """

    def __init__(self):
        self.__zips = {}
        self.__cleanup_thread = None
        self.__lock = threading.Lock()

    def create_temp_zip(self, nodes: t.List["lawwenda.fs.node.Node"]) -> str:
        """
        Create a temporary zip archive from some nodes in memory and return an identifier.

        See also :py:meth:`temp_zip_content`.

        :param nodes: The nodes to include in the zip archive.
        """
        retention_time_secs = 60 * 10
        with self.__lock:
            if not self.__cleanup_thread:
                self.__cleanup_thread = threading.Thread(target=self.__cleanup_loop, daemon=True)
                self.__cleanup_thread.start()
            temp_zip = self._TempZip(nodes)
            self.__zips[temp_zip.zip_id] = (temp_zip, time.monotonic() + retention_time_secs)
            return temp_zip.zip_id

    def temp_zip_content(self, zip_id: str) -> t.Optional[bytes]:
        """
        Return the binary content of a zip archive that was created before by :py:meth:`create_temp_zip`.

        :param zip_id: The identifier returned by `create_temp_zip`.
        """
        with self.__lock:
            temp_zip, _ = self.__zips.get(zip_id) or (None, None)
            return temp_zip.bytes if temp_zip else None

    def __cleanup_loop(self):
        while True:
            now = time.monotonic()
            with self.__lock:
                for key, (_, keep_until) in list(self.__zips.items()):
                    if keep_until < now:
                        self.__zips.pop(key)
            time.sleep(60)

    class _TempZip:
        """
        A temporary zip file.
        """

        def __init__(self, nodes: t.List["lawwenda.fs.node.Node"]):
            self.zip_id = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(512))
            zip_stream = io.BytesIO()
            with zipfile.ZipFile(zip_stream, "w", zipfile.ZIP_DEFLATED) as zip_file_obj:
                for node in nodes:
                    self.__put_node(node, zip_file_obj)
            self.__bytes = zip_stream.getvalue()

        @property
        def bytes(self):
            """
            The binary representation of this temporary zip archive.
            """
            return self.__bytes

        def __put_node(self, node: "lawwenda.fs.node.Node", zip_file_obj: zipfile.ZipFile) -> None:
            for child_node, child_relative_path in node.traverse_dir(param_path=node.name, raise_on_circle=False):
                child_in_archive_path = child_relative_path[1:]
                child_content = b""
                if child_node.is_dir:
                    child_in_archive_path = f"{child_in_archive_path}/"
                    child_zip_item_attr = 0o755 << 16
                    child_zip_item_attr |= 1 << 14 << 16  # unix directory flag
                    child_zip_item_attr |= 0x10  # MS-DOS directory flag
                else:
                    with child_node.read_file() as f:
                        child_content = f.read()
                    child_zip_item_attr = 0o644 << 16
                    child_zip_item_attr |= 1 << 15 << 16  # unix file flag
                    if self.__is_executable(child_node):
                        child_zip_item_attr |= 0o111 << 16
                zipinfo = zipfile.ZipInfo(child_in_archive_path, child_node.mtime.timetuple()[:6])
                zipinfo.external_attr = child_zip_item_attr
                zip_file_obj.writestr(zipinfo, child_content)

        @staticmethod
        def __is_executable(node: "lawwenda.fs.node.Node") -> bool:
            system_path = node.system_path(writable=False)
            return system_path and (system_path.stat().st_mode & stat.S_IXUSR) == stat.S_IXUSR


class _RenderTemplateValue:
    """
    String representation for usage in template rendering.

    Usually an HTML escaped variant of the input string, but with an option to also get the unescaped string.
    """

    def __init__(self, s):
        self.__s = str(s)
        self.__html_escaped_s = html.escape(self.__s)

    def __str__(self):
        return self.__html_escaped_s

    @property
    def unescaped(self):
        """
        The unescaped string.
        """
        return self.__s
