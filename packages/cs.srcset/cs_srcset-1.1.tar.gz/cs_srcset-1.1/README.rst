.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/codesyntax/cs.srcset/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/codesyntax/cs.srcset/actions/workflows/plone-package.yml

.. image:: https://img.shields.io/pypi/v/cs.srcset.svg
    :target: https://pypi.python.org/pypi/cs.srcset/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/cs.srcset.svg
    :target: https://pypi.python.org/pypi/cs.srcset
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/cs.srcset.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/cs.srcset.svg
    :target: https://pypi.python.org/pypi/cs.srcset/
    :alt: License


=========
cs.srcset
=========

Backport of the `srcset` method added to the `@@images` view in plone.namedfile 7.1.0 to be able to use it in older Plone versions

Features
--------

It adds a view called `@@images-srcset` that has a single method called `srcset` to be able to create an `img` tag with the `srcset` and `sizes`
attributes to render responsive images.

Read more about responsive images and its use in the `MDN documentation`_


Documentation
-------------

You should use this view like this ::

    <img tal:define="images context/@@images-srcset;"
     tal:replace="structure python:images.srcset(
                                 fieldname='image',
                                 scale_in_src='huge',
                                 sizes='(min-width: 570px) 550px,90vw',
                                 css_class='mini w-100 h-100 responsive-3-2',
                                 alt=context.Title(),
                                 title=context.Title(),
                                 loading='lazy')"
    />

The meaning of each parameter is the following:

- fieldname: name of the field where the image is stored
- scale_in_src: name of the scale that will be used to render the src attribute
- sizes: the value of the sizes attribute in the output tag
- css_class: CSS classes added to the img tag
- additional attributes: any aditional attribute that will be rendered in the img tag, useful to add the title, alt, loading, fetchpriority, id, and other attributes.





Installation
------------

Install cs.srcset by adding it to your buildout::

    [buildout]

    ...

    eggs =
        cs.srcset


and then running ``bin/buildout``

**NOTE**: You do not need to install the product in the Plone add-ons controlpanel, there is nothing to be installed.



Contribute
----------

- Issue Tracker: https://github.com/codesyntax/cs.srcset/issues
- Source Code: https://github.com/codesyntax/cs.srcset


Support
-------

If you are having issues, please let us know.


License
-------

The project is licensed under the GPLv2.

.. _`MDN documentation`: https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images
