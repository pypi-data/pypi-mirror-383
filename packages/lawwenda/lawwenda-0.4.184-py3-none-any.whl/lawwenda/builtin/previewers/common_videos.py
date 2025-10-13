# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Preview functionality for common video formats.
"""
import html
import io
import subprocess
import typing as t

import lawwenda.fs.previewer


class Previewer(lawwenda.fs.previewer.Previewer):
    """
    Preview functionality for common video formats.
    """

    def is_thumbnailable(self, iar):
        return iar.mimetype.startswith("video/")

    @staticmethod
    def __ffmpeg_thumb(inputpath: str, stdin: t.Any = subprocess.DEVNULL) -> bytes:
        return subprocess.check_output(["ffmpeg", "-ss", "00:00:05.000", "-i", inputpath, "-vframes", "1",
                                        "-c:v", "png", "-f", "image2pipe", "-"], stdin=stdin)

    def thumbnail(self, node):
        fullpath = node.system_path(writable=False)
        if fullpath:
            bthimg = self.__ffmpeg_thumb(fullpath)
        else:
            with node.read_file() as f:
                bthimg = self.__ffmpeg_thumb("pipe:0", f)
        return self._image_scale_to_thumbnail_size(io.BytesIO(bthimg)).getvalue()

    def is_previewable(self, iar):
        return self.is_thumbnailable(iar)

    def preview_html(self, node):
        return f'<video class="previewerpiece" src="{html.escape(node.name)}" controls/>'
