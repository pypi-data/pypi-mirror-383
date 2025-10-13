# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Preview functionality for common image formats.
"""
import html

import lawwenda.fs.previewer


class Previewer(lawwenda.fs.previewer.Previewer):
    """
    Preview functionality for common image formats.
    """

    def is_thumbnailable(self, iar):
        return iar.mimetype.startswith("image/")

    def thumbnail(self, node):
        with node.read_file() as f:
            return self._image_scale_to_thumbnail_size(f).getvalue()

    def is_previewable(self, iar):
        return self.is_thumbnailable(iar)

    def preview_html(self, node):
        return f'<img class="previewerpiece" src="{html.escape(node.name)}"/>'
