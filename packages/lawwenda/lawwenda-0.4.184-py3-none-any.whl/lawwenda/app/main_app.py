# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Lawwenda main wsgi application.
"""
import typing as t

import werkzeug.exceptions
import werkzeug.serving
import werkzeug.wsgi

import lawwenda.app.fm_app
import lawwenda.config.share
import lawwenda.fs


class MainApp:
    """
    Lawwenda main wsgi application.
    """

    class _ShareAppInst:
        """
        Container for one :py:class:`lawwenda.app.fm_app.FmApp` and its associated
        :py:class:`lawwenda.config.share.Share`.
        """

        def __init__(self, share: "lawwenda.config.share.Share"):
            self.__share = share
            self.__app = lawwenda.app.fm_app.FmApp(share)

        @property
        def app(self) -> "lawwenda.app.fm_app.FmApp":
            """
            The application.
            """
            return self.__app

        @property
        def is_active(self) -> bool:
            """
            Whether this share is still active (not yet removed).
            """
            return self.__share.is_active

    def __init__(self, configuration: "lawwenda.Configuration"):
        """
        :param configuration: The Lawwenda configuration.
        """
        self.__configuration = configuration
        self.__share_apps = {}

    def __get_app_for_share(self, share_name: str):
        share_app_inst = self.__share_apps.get(share_name)

        if share_app_inst and not share_app_inst.is_active:
            share_app_inst = self.__share_apps[share_name] = None

        if not share_app_inst:
            share = self.__configuration.share_by_name(share_name)
            if share:
                share_app_inst = self.__share_apps[share_name] = self._ShareAppInst(share)

        return share_app_inst.app if share_app_inst else None

    def __call__(self, environ, start_response):
        request = werkzeug.wrappers.Request(environ)
        share_name = lawwenda.app.pop_path_info(request.environ)
        return (self.__get_app_for_share(share_name) or werkzeug.exceptions.NotFound())(environ, start_response)
