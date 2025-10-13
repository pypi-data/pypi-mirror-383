# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only

"""
Preview functionality.

Used by different parts of the Lawwenda user interface.
"""

import abc
import dataclasses
import io
import typing as t

import PIL.Image

if t.TYPE_CHECKING:
    import lawwenda.fs


class Previewer(abc.ABC):  # TODO isolate previewers better? chroot alike?
    """
    Base class for previewers.

    Subclasses implement thumbnail and preview functionality for particular file formats.
    """

    thumbsize = thumbwidth, thumbheight = 300, 300

    @abc.abstractmethod
    def is_thumbnailable(self, iar: "IsAbleRequest") -> bool:
        """
        Return if this previewer is able to generate a thumbnail for a file.

        Note that this decision has to be made with very few information, e.g. without knowing the file content, for
        performance reasons.

        See also :py:meth:`thumbnail`.

        :param iar: An object that describes the file.
        """

    @abc.abstractmethod
    def thumbnail(self, node: "lawwenda.fs.node.Node") -> bytes:
        """
        Return a thumbnail for a file in PNG format.

        See also :py:meth:`is_thumbnailable`.

        :param node: The file to generate a thumbnail for.
        """

    @abc.abstractmethod
    def is_previewable(self, iar: "IsAbleRequest") -> bool:
        """
        Return if this previewer is able to generate an html preview snippet for a file.

        Note that this decision has to be made with very few information, e.g. without knowing the file content, for
        performance reasons.

        See also :py:meth:`preview_html`.

        :param iar: An object that describes the file.
        """

    @abc.abstractmethod
    def preview_html(self, node: "lawwenda.fs.node.Node") -> str:
        """
        Return an html snippet that shows a preview of a file.

        This is larger and richer in terms of flexibility than thumbnails, and is typically used by the file details
        panel.

        See also :py:meth:`is_previewable`.

        :param node: The file to preview.
        """

    def _image_scale_to_thumbnail_size(self, imgdata: t.BinaryIO) -> io.BytesIO:
        img = PIL.Image.open(imgdata)
        img.thumbnail(self.thumbsize, PIL.Image.Resampling.LANCZOS)
        resultimg = PIL.Image.new("RGBA", self.thumbsize, (0, 0, 0, 0))
        resultimg.paste(img, (int((self.thumbwidth - img.width) / 2), int((self.thumbheight - img.height) / 2)))
        bimg = io.BytesIO()
        resultimg.save(bimg, format="png")
        return bimg


@dataclasses.dataclass
class IsAbleRequest:
    """
    Information about a particular file, used for asking a :py:class:`Previewer` if it can provide some functionality
    for that file.

    Instances of this class are used as an argument to some :py:class:`Previewer` methods.

    The available infos are not very rich for performance reasons.
    """
    name: str
    mimetype: str
