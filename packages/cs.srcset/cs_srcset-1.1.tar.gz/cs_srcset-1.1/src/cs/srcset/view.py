from AccessControl.ZopeGuards import guarded_getattr
from Acquisition import aq_base
from DateTime import DateTime
from plone.namedfile.interfaces import IAvailableSizes
from plone.namedfile.scaling import ImageScale
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.scale.storage import IImageScaleStorage
from Products.Five.browser import BrowserView
from xml.sax.saxutils import quoteattr
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.component import queryUtility

import functools
import logging


logger = logging.getLogger(__name__)
_marker = object()


def _image_tag_from_values(*values):
    """Turn list of tuples into an img tag.

    Naturally, this should at least contain ("src", "some url").
    """
    parts = ["<img"]
    for k, v in values:
        if v is None:
            continue
        if isinstance(v, int):
            v = str(v)
        elif isinstance(v, bytes):
            v = str(v, "utf8")
        parts.append(f"{k}={quoteattr(v)}")
    parts.append("/>")

    return " ".join(parts)


class SrcSetView(BrowserView):

    _sizes = None
    _scale_view_class = ImageScale

    def guarded_orig_image(self, fieldname):
        # Note: you must not call this from publishTraverse.
        # No authentication has taken place there yet, so everyone is still anonymous.
        return guarded_getattr(self.context, fieldname, None)

    def getImageSize(self, fieldname=None):
        if fieldname is not None:
            try:
                value = self.guarded_orig_image(fieldname)
            except Unauthorized:
                # This is a corner case that can be seen in some tests,
                # at least plone.app.caching and plone.formwidget.namedfile.
                # When it is *really* unauthorized to get this image,
                # it will go wrong somewhere else.
                value = None
            if value is None:
                return (0, 0)
            return value.getImageSize()
        value = IPrimaryFieldInfo(self.context).value
        return value.getImageSize()

    @property
    def available_sizes(self):
        # fieldname is ignored by default
        if self._sizes is None:
            sizes_util = queryUtility(IAvailableSizes)
            if sizes_util is None:
                self._sizes = {}
            else:
                self._sizes = sizes_util() or {}
        return self._sizes

    @available_sizes.setter
    def available_sizes(self, value):
        self._sizes = value

    def modified(self, fieldname=None):
        """Provide a callable to return the modification time of content
        items, so stored image scales can be invalidated.
        """
        context = aq_base(self.context)
        if fieldname is not None:
            field = getattr(context, fieldname, None)
            modified = getattr(field, "modified", None)
            date = DateTime(modified or context._p_mtime)
        else:
            date = DateTime(context._p_mtime)
        return date.millis()

    def scale(
        self,
        fieldname=None,
        scale=None,
        height=None,
        width=None,
        mode="scale",
        pre=False,
        include_srcset=None,
        **parameters,
    ):
        if fieldname is None:
            try:
                primary = IPrimaryFieldInfo(self.context, None)
            except TypeError:
                return
            if primary is None:
                return  # 404
            fieldname = primary.fieldname
        if scale is not None:
            if width is not None or height is not None:
                logger.warning(
                    "A scale name and width/height are given. Those are "
                    "mutually exclusive: solved by ignoring width/height and "
                    "taking name",
                )
            available = self.available_sizes
            if scale not in available:
                return None  # 404
            width, height = available[scale]
        storage = getMultiAdapter(
            (self.context, functools.partial(self.modified, fieldname)),
            IImageScaleStorage,
        )
        scale_method = storage.scale
        info = scale_method(
            fieldname=fieldname,
            height=height,
            width=width,
            mode=mode,
            scale=scale,
            **parameters,
        )
        if info is None:
            return  # 404

        # Do we want to include srcset info for HiDPI?
        # If there is no explicit True/False given, we look at the value of 'pre'.
        # When 'pre' is False, the visitor is requesting a scale via a url,
        # so we only want a single image and not any fancy extras.
        if include_srcset is None and pre:
            include_srcset = True
        if include_srcset:
            if "srcset" not in info:
                info["srcset"] = self.calculate_srcset(
                    fieldname=fieldname,
                    height=height,
                    width=width,
                    mode=mode,
                    scale=scale,
                    storage=storage,
                    **parameters,
                )
        if "fieldname" not in info:
            info["fieldname"] = fieldname
        scale_view = self._scale_view_class(self.context, self.request, **info)
        return scale_view

    def srcset(
        self,
        fieldname=None,
        scale_in_src="huge",
        sizes="",
        alt=_marker,
        css_class=None,
        title=_marker,
        **kwargs,
    ):
        if fieldname is None:
            try:
                primary = IPrimaryFieldInfo(self.context, None)
            except TypeError:
                return
            if primary is None:
                return  # 404
            fieldname = primary.fieldname

        original_width, original_height = self.getImageSize(fieldname)

        storage = getMultiAdapter(
            (self.context, functools.partial(self.modified, fieldname)),
            IImageScaleStorage,
        )

        srcset_urls = []
        for width, height in self.available_sizes.values():
            if width <= original_width:
                scale = storage.scale(
                    fieldname=fieldname, width=width, height=height, mode="scale"
                )
                extension = scale["mimetype"].split("/")[-1].lower()
                srcset_urls.append(
                    f'{self.context.absolute_url()}/@@images/{scale["uid"]}.{extension} {scale["width"]}w'
                )
        attributes = {}
        if title is _marker:
            attributes["title"] = self.context.Title()
        elif title:
            attributes["title"] = title
        if alt is _marker:
            attributes["alt"] = self.context.Title()
        else:
            attributes["alt"] = alt

        if css_class is not None:
            attributes["class"] = css_class

        attributes.update(**kwargs)

        attributes["sizes"] = sizes

        srcset_string = ", ".join(srcset_urls)
        attributes["srcset"] = srcset_string

        if scale_in_src not in self.available_sizes:
            for key, (width, height) in self.available_sizes.items():
                if width <= original_width:
                    scale_in_src = key
                    break

        scale = self.scale(fieldname=fieldname, scale=scale_in_src)
        attributes["src"] = scale.url
        if "width" not in attributes:
            attributes["width"] = scale.width
        if "height" not in attributes:
            attributes["height"] = scale.height

        return _image_tag_from_values(*attributes.items())
