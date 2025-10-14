import unittest
from doctest import _ellipsis_match

from cs.srcset.testing import CS_SRCSET_INTEGRATION_TESTING
from cs.srcset.view import SrcSetView
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from plone.namedfile.field import NamedImage as NamedImageField
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.tests import MockNamedImage, getFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.annotation import IAttributeAnnotatable
from zope.component import adapter, getSiteManager
from zope.interface import implementer


class IHasImage(IImageScaleTraversable):
    image = NamedImageField()


@implementer(IAttributeAnnotatable, IHasImage)
class DummyContent(SimpleItem):
    image = None
    modified = DateTime
    id = __name__ = "item"
    title = "foo"

    def Title(self):
        return self.title

    def UID(self):
        return "dummy_uuid"


@implementer(IPrimaryFieldInfo)
@adapter(DummyContent)
class PrimaryFieldInfo:
    def __init__(self, context):
        self.context = context
        self.fieldname = "image"
        self.field = self.context.image

    @property
    def value(self):
        return self.field


class TestView(unittest.TestCase):

    layer = CS_SRCSET_INTEGRATION_TESTING

    def setUp(self):
        sm = getSiteManager()
        sm.registerAdapter(PrimaryFieldInfo)

        data = getFile("image.png")
        item = DummyContent()
        item.image = MockNamedImage(data, "image/png", "image.png")
        self.layer["app"]._setOb("item", item)
        self.item = self.layer["app"].item
        self._orig_sizes = SrcSetView._sizes
        self.scaling = SrcSetView(self.item, None)

    def tearDown(self):
        SrcSetView._sizes = self._orig_sizes
        sm = getSiteManager()
        sm.unregisterAdapter(PrimaryFieldInfo)

    def testImgSrcSet(self):
        """test rendered srcset values"""
        self.scaling.available_sizes = {
            "huge": (1600, 65536),
            "great": (1200, 65536),
            "larger": (1000, 65536),
            "large": (800, 65536),
            "teaser": (600, 65536),
            "preview": (400, 65536),
            "mini": (200, 65536),
            "thumb": (128, 128),
            "tile": (64, 64),
            "icon": (32, 32),
            "listing": (16, 16),
        }
        tag = self.scaling.srcset("image", sizes="50vw")
        base = self.item.absolute_url()
        expected = f"""<img title="foo" alt="foo" sizes="50vw" srcset="{base}/@@images/image-200-....png 200w, {base}/@@images/image-128-....png 128w, {base}/@@images/image-64-....png 64w, {base}/@@images/image-32-....png 32w, {base}/@@images/image-16-....png 16w" src="{base}/@@images/image-1600-....png" width="..." height="...".../>"""
        self.assertTrue(_ellipsis_match(expected, tag.strip()))

    def testImgSrcSetCustomSrc(self):
        """test that we can select a custom scale in the src attribute"""
        self.scaling.available_sizes = {
            "huge": (1600, 65536),
            "great": (1200, 65536),
            "larger": (1000, 65536),
            "large": (800, 65536),
            "teaser": (600, 65536),
            "preview": (400, 65536),
            "mini": (200, 65536),
            "thumb": (128, 128),
            "tile": (64, 64),
            "icon": (32, 32),
            "listing": (16, 16),
        }
        tag = self.scaling.srcset("image", sizes="50vw", scale_in_src="mini")
        base = self.item.absolute_url()
        expected = f"""<img title="foo" alt="foo" sizes="50vw" srcset="{base}/@@images/image-200-....png 200w, {base}/@@images/image-128-....png 128w, {base}/@@images/image-64-....png 64w, {base}/@@images/image-32-....png 32w, {base}/@@images/image-16-....png 16w" src="{base}/@@images/image-200-....png" width="200" height="...".../>"""
        self.assertTrue(_ellipsis_match(expected, tag.strip()))

    def testImgSrcSetInexistentScale(self):
        """test that when requesting an inexistent scale for the src attribute
        we provide the biggest scale we can produce
        """
        self.scaling.available_sizes = {
            "huge": (1600, 65536),
            "great": (1200, 65536),
            "larger": (1000, 65536),
            "large": (800, 65536),
            "teaser": (600, 65536),
            "preview": (400, 65536),
            "mini": (200, 65536),
            "thumb": (128, 128),
            "tile": (64, 64),
            "icon": (32, 32),
            "listing": (16, 16),
        }
        tag = self.scaling.srcset(
            "image", sizes="50vw", scale_in_src="inexistent-scale-name"
        )
        base = self.item.absolute_url()
        expected = f"""<img title="foo" alt="foo" sizes="50vw" srcset="{base}/@@images/image-200-....png 200w, {base}/@@images/image-128-....png 128w, {base}/@@images/image-64-....png 64w, {base}/@@images/image-32-....png 32w, {base}/@@images/image-16-....png 16w" src="{base}/@@images/image-200-....png" width="..." height="...".../>"""
        self.assertTrue(_ellipsis_match(expected, tag.strip()))

    def testImgSrcSetCustomTitle(self):
        """test passing a custom title to the srcset method"""
        self.scaling.available_sizes = {
            "huge": (1600, 65536),
            "great": (1200, 65536),
            "larger": (1000, 65536),
            "large": (800, 65536),
            "teaser": (600, 65536),
            "preview": (400, 65536),
            "mini": (200, 65536),
            "thumb": (128, 128),
            "tile": (64, 64),
            "icon": (32, 32),
            "listing": (16, 16),
        }
        tag = self.scaling.srcset("image", sizes="50vw", title="My Custom Title")
        base = self.item.absolute_url()
        expected = f"""<img title="My Custom Title" alt="foo" sizes="50vw" srcset="{base}/@@images/image-200-....png 200w, {base}/@@images/image-128-....png 128w, {base}/@@images/image-64-....png 64w, {base}/@@images/image-32-....png 32w, {base}/@@images/image-16-....png 16w" src="{base}/@@images/image-1600-....png" width="..." height="...".../>"""
        self.assertTrue(_ellipsis_match(expected, tag.strip()))

    def testImgSrcSetAdditionalAttributes(self):
        """test that additional parameters are output as is, like alt, loading, ..."""
        self.scaling.available_sizes = {
            "huge": (1600, 65536),
            "great": (1200, 65536),
            "larger": (1000, 65536),
            "large": (800, 65536),
            "teaser": (600, 65536),
            "preview": (400, 65536),
            "mini": (200, 65536),
            "thumb": (128, 128),
            "tile": (64, 64),
            "icon": (32, 32),
            "listing": (16, 16),
        }
        tag = self.scaling.srcset(
            "image",
            sizes="50vw",
            alt="This image shows nothing",
            css_class="my-personal-class",
            title="My Custom Title",
            loading="lazy",
        )
        base = self.item.absolute_url()

        expected = f"""<img title="My Custom Title" alt="This image shows nothing" class="my-personal-class" loading="lazy" sizes="50vw" srcset="{base}/@@images/image-200-....png 200w, {base}/@@images/image-128-....png 128w, {base}/@@images/image-64-....png 64w, {base}/@@images/image-32-....png 32w, {base}/@@images/image-16-....png 16w" src="{base}/@@images/image-1600-....png" width="..." height="...".../>"""
        self.assertTrue(_ellipsis_match(expected, tag.strip()))
