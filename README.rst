vcrpy-facebook
==============

|Build Status| |Coverage Report| |PyPI| |Gitter|

This package provides filters for eliding sensitive data in HTTP transactions
with Facebook recorded with `VCR.py`_.

Installation
------------

Install from PyPI_:

.. code:: sh

   pip install vcrpy-facebook

Usage
-----

Instantiate VCR with kwargs provided by ``vcrpy-facebook``:

.. code:: python

    import vcr
    import vcr_facebook

    kwargs = vcr_facebook.get_vcr_kwargs()
    my_vcr = vcr.VCR(**kwargs)


If you already have kwargs, then you can pass them in the call to
``get_vcr_kwargs`` and they'll be preserved:

.. code:: python

    kwargs = dict(
        filter_headers=['authorization'],
        match_on=['method', 'uri', 'headers', 'raw_body'],
    )
    kwargs = vcr_facebook.get_vcr_kwargs(kwargs)
    my_vcr = vcr.VCR(**kwargs)

vcrpy-unittest
~~~~~~~~~~~~~~

If you're using `vcrpy-unittest`_ then it works like this:

.. code:: python

    import vcr_unittest
    import vcr_facebook

    class MyTestCase(vcr_unittest.VCRTestCase):

        def _get_vcr_kwargs(self):
            kwargs = super(MyTestCase, self)._get_vcr_kwargs()
            kwargs = vcr_facebook.get_vcr_kwargs(kwargs)
            return kwargs

Customization
-------------

You can pass some extra kwargs to ``get_vcr_kwargs`` to customize the behavior
of ``vcrpy-facebook``.

elide_access_token
~~~~~~~~~~~~~~~~~~

By default ``vcrpy-facebook`` replaces tokens with a string like
``ELIDED-d41d8cd98f00b204e9800998ecf8427e`` where the right side is the md5 hex
digest of the elided token.

Pass a callable as ``elide_access_token`` to customize how Facebook access
tokens are elided, for example to look up a username from `django-allauth`_:

.. code:: python

    def elide_access_token(token):
        try:
            user = User.objects.get(socialaccount__socialtoken__token=token)
        except User.DoesNotExist:
            pass
        else:
            return 'USER-{}'.format(user.username)

elide_appsecret_proof
~~~~~~~~~~~~~~~~~~~~~

By default ``vcrpy-facebook`` replaces appsecret_proof with a string like
``ELIDED-d41d8cd98f00b204e9800998ecf8427e`` where the right side is the md5 hex
digest of the elided proof.

Pass a callable as ``elide_appsecret_proof`` to customize how the proof is
elided. The callable should take two positional parameters: ``proof`` and
``token`` (since the proof is a signature based on the token used for the
transaction).

This is only really useful for an application with multiple Facebook apps, and
wanting to make sure the proofs are generated with an app that corresponds to
the token.

Compatibility
-------------

``vcrpy-facebook`` supports the same Python versions supported by VCR.py.

License
-------

This library uses the MIT license, which is the same as VCR.py. See `LICENSE.txt
<https://github.com/agriffis/vcrpy-facebook/blob/master/LICENSE.txt>`__ for more
details.

.. _PyPI: https://pypi.python.org/pypi/vcrpy-facebook
.. _VCR.py: https://github.com/kevin1024/vcrpy
.. _vcrpy-unittest: https://github.com/agriffis/vcrpy-unittest
.. _django-allauth: http://www.intenct.nl/projects/django-allauth/

.. |Build Status| image:: https://travis-ci.org/agriffis/vcrpy-facebook.svg?branch=master
   :target: https://travis-ci.org/agriffis/vcrpy-facebook?branch=master
.. |Coverage Report| image:: https://img.shields.io/coveralls/agriffis/vcrpy-facebook/master.svg
   :target: https://coveralls.io/github/agriffis/vcrpy-facebook?branch=master
.. |PyPI| image:: https://img.shields.io/pypi/v/vcrpy-facebook.svg?style=plastic
   :target: PyPI_
.. |Gitter| image:: https://img.shields.io/badge/gitter-join%20chat%20%E2%86%92-green.svg?style=plastic
   :target: https://gitter.im/kevin1024/vcrpy
