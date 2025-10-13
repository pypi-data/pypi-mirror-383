#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
The Lawwenda CLI.
"""
import argparse
import code
import datetime
import getpass
import os
import pathlib
import readline
import rlcompleter
import subprocess
import sys
import typing as t

try:  # weird, but useful in some cases ;)
    if "__main__" == __name__:
        import lawwenda.asset
except ModuleNotFoundError:
    sys.path.append(os.path.abspath(os.path.realpath(__file__)+"/../.."))

import lawwenda.asset


def main():
    arg_parser = parser(only_documentation=False)
    args = arg_parser.parse_args().__dict__
    command_name = (args.pop("command") or "console").replace("-", "_")
    command = getattr(Commands(**args), command_name)
    print(command(**args) or "")


def parser(*, only_documentation: bool = True) -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(
        description=None if only_documentation
        else f"Welcome to Lawwenda {lawwenda.asset.project_info.version}! For more information, read"
             f" {"file://"+str(lawwenda.asset.data.readme_pdf("en"))!r} and visit"
             f" {lawwenda.asset.project_info.homepage_url!r}.")
    arg_parser.add_argument("--config", help="the path of your Lawwenda configuration directory", required=False)
    p_cmd = arg_parser.add_subparsers(help="the action to execute", required=False, dest="command", metavar="[command]")
    p_cmd.add_parser("list_shares", help="lists all shares")
    p_cmd_describe_share = p_cmd.add_parser("describe_share", help="prints details about a share")
    p_cmd_describe_share.add_argument("name", help="the share name")
    p_cmd_add_share = p_cmd.add_parser("add_share", help="adds a new share")
    p_cmd_add_share.add_argument("name", help="the share name")
    p_cmd_add_share.add_argument("path", help="the directory to share")
    p_cmd_add_share.add_argument("--title", help="the share title text")
    p_cmd_add_share.add_argument("--active-until", help="the expiration date/time (in iso format)")
    p_cmd_add_share.add_argument("--hide-by-pattern", help="a regex pattern of paths to hide at first", action="append")
    p_cmd_add_share.add_argument("--hide-by-tag", help="a tag to hide at first", action="append")
    p_cmd_add_share.add_argument("--include-by-pattern", help="a regex pattern of paths to include", action="append")
    p_cmd_add_share.add_argument("--include-by-tag", help="a tag to include", action="append")
    p_cmd_add_share.add_argument("--exclude-by-pattern", help="a regex pattern of paths to exclude entirely",
                                 action="append")
    p_cmd_add_share.add_argument("--exclude-by-tag", help="a tag to exclude entirely", action="append")
    p_cmd_add_share.add_argument("--exclude-hidden", help="exclude each item that is hidden", action="store_true")
    p_cmd_add_share.add_argument("--readwrite", help="allow write access", action="store_false", dest="readonly")
    p_cmd_remove_share = p_cmd.add_parser("remove_share", help="removes a share")
    p_cmd_remove_share.add_argument("name", help="the share name")
    p_cmd.add_parser("console", help="opens the Console (this is the default for no arguments)")
    p_cmd.add_parser("run_tiny_server", help="runs a tiny web server for testing or development")
    p_cmd.add_parser("generate_wsgi", help="generates wsgi application code")
    return arg_parser


class Commands:

    def __init__(self, config, **_):
        self._configuration = lawwenda.Configuration(config)

    def console(self, **_) -> None:
        def _readme():
            freadme = lawwenda.asset.data.find_data_file("README.pdf")
            if not freadme:
                raise EnvironmentError("Your installation does not include documentation.")
            try:
                subprocess.check_output(["xdg-open", freadme])
            except (subprocess.CalledProcessError, IOError):
                print(f"Please open {str(freadme)!r}.")
        consolevars = {**lawwenda.__dict__, "config": self._configuration,
                       "quickstart": lambda: print(self.__quickstart(self._configuration.config_dir)),
                       "readme": _readme}
        print(f"Welcome to Lawwenda Console!\n{self.__quickstart(self._configuration.config_dir)}")
        readline.set_completer(rlcompleter.Completer(consolevars).complete)
        readline.parse_and_bind("tab: complete")
        code.InteractiveConsole(consolevars).interact(banner="", exitmsg="Bye.")

    def run_tiny_server(self, **_) -> None:
        self._configuration.start_tiny_server().wait_stopped()

    def list_shares(self, **_) -> str:
        return "\n".join([share.name for share in self._configuration.all_shares()])

    def describe_share(self, name: str, **_) -> str:
        return str(self._configuration.share_by_name(name) or "")

    def add_share(self, name: str, path: str, title: str, active_until: str,
                  hide_by_pattern: t.Sequence[str]|None, hide_by_tag: t.Sequence[str]|None,
                  include_by_pattern: t.Sequence[str]|None, include_by_tag: t.Sequence[str]|None,
                  exclude_by_pattern: t.Sequence[str]|None, exclude_by_tag: t.Sequence[str]|None,
                  exclude_hidden: bool, readonly: bool, **_) -> None:
        password = getpass.getpass("Please choose a share password: ")
        if getpass.getpass("Please confirm the share password: ") != password:
            raise Exception("The passwords did not match.")

        self._configuration.add_share(
            path, name=name, password=password, title=title, readonly=readonly,
            hide_by_patterns=hide_by_pattern or (), hide_by_tags=hide_by_tag or (),
            include_by_patterns=include_by_pattern, include_by_tags=include_by_tag,
            exclude_by_patterns=exclude_by_pattern or (), exclude_by_tags=exclude_by_tag or (),
            exclude_hidden=exclude_hidden,
            active_until=datetime.datetime.fromisoformat(active_until) if active_until else None)

    def remove_share(self, name: str, **_) -> None:
        self._configuration.remove_share(name)

    def generate_wsgi(self, **_) -> str:
        return self._configuration.generate_wsgi()

    def __quickstart(self, config_path: pathlib.Path) -> str:
        format_command = self.__quickstart__format_command
        return f"""
Quick start guide
-----------------
Whenever you got lost, calling '{format_command("quickstart()")}' shows this text again and 
'{format_command("readme()")}' opens the Lawwenda documentation. Any Python code is allowed.

At first you need a Configuration object. If you are fine with
 {config_path}
as configuration path, just take 'config'. Otherwise, call:
{format_command('config = Configuration("/path/to/my/lawwenda/config/dir")')}
(replace paths with something that fits your needs!)

Then you can create a new share by calling:
{format_command('config.add_share("/path/that/i/want/to/share", name="myshare", password="foo")')}

Call '{format_command('help(config)')}' in order to find out what other methods exist, and 
'{format_command('help(config.add_share)')}' for more parameters of 'add_share', and for other things
when needed. Calls like '{format_command('print(config)')}' print details about an object.

If your web server provides your Lawwenda installation at 
'https://example.com/shares/', you can access your new 'myshare' share at
'https://example.com/shares/myshare/'. For playing around (only!) you can call 
'{format_command('config.start_tiny_server()')}' in order to start a little toy server."""

    def __quickstart__format_command(self, txt: str) -> str:
        return f"\033[1;36m{txt}\033[0m"


if __name__ == "__main__":
    main()
