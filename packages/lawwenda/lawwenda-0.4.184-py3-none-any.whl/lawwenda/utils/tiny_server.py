# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Tiny local server for trying, development, testing.
"""
import threading
import typing as t

import werkzeug.serving

import lawwenda.app.main_app

if t.TYPE_CHECKING:
    import lawwenda


def start_tiny_server(configuration: "lawwenda.Configuration") -> "_DevServerInfo":
    """
    Start a tiny local server for a given configuration.

    Such a server can be used for trying, development, testing, and so on, but is not recommended for real usage.

    It will automatically find a free port and will return a control object that contains the full url, and more.

    :param configuration: The configuration to run with.
    """
    return _start_tiny_server_for_app(lawwenda.app.main_app.MainApp(configuration))


def running_tiny_servers() -> t.Sequence["_DevServerInfo"]:
    """
    Return the servers started by :py:func:`start_tiny_server` that are currently running.
    """
    with _running_tiny_servers_lock:
        return tuple(_running_tiny_servers.values())


def _start_tiny_server_for_app(app: t.Callable) -> "_DevServerInfo":
    """
    Start a tiny local server for a given wsgi application.

    :param app: The wsgi application to run.
    """
    wsgi_server = werkzeug.serving.ThreadedWSGIServer("localhost", 0, app)
    server_thread = _DevServerThread(wsgi_server)
    server_info = _DevServerInfo(wsgi_server, server_thread)
    with _running_tiny_servers_lock:
        _running_tiny_servers[wsgi_server] = server_info
    server_thread.start()
    return server_info


_running_tiny_servers = {}
_running_tiny_servers_lock = threading.Lock()


class _DevServerThread(threading.Thread):

    def __init__(self, wsgi_server):
        super().__init__(daemon=True)
        self.__wsgi_server = wsgi_server

    def run(self):
        try:
            self.__wsgi_server.serve_forever()
        finally:
            with _running_tiny_servers_lock:
                _running_tiny_servers.pop(self.__wsgi_server)


class _DevServerInfo:

    def __init__(self, wsgi_server, server_thread):
        self.__wsgi_server = wsgi_server
        self.__server_thread = server_thread

    @property
    def url(self) -> str:
        """
        The url of this running server.
        """
        return f"http://{self.__wsgi_server.host}:{self.__wsgi_server.port}/"

    def shutdown(self) -> None:
        """
        Stop this server.
        """
        self.__wsgi_server.shutdown()
        self.wait_stopped()

    def wait_stopped(self) -> None:
        """
        Wait until this server stopped.
        """
        self.__server_thread.join()
