.. Copyright (C) 2019, Nokia

.. image:: https://travis-ci.org/nokia/crl-threadverify.svg?branch=master
    :target: https://travis-ci.org/nokia/crl-threadverify

Threadverify - verifying clean thread management
================================================

The Robot Framework test library *crl.threadverify* is for verifying that the
threads are used in the correct ways. For example it checks that no threads
are not left hanging after the test case execution. The library will help in
debugging the problems by showing the thread creation stack and traces from the
creation time of the new threads.

Documentation
-------------

Documentation for ``crl.threadverify`` can be found from `Read The Docs`_.

.. _Read The Docs: http://crl-threadverify.readthedocs.io/

Installation
------------

``crl.threadverify`` library can be installed with pip::

   pip install crl.threadverify

Contributing
------------

Please see contributing_ for development and contribution practices.

The code_ and the issues_ are hosted on GitHub.

The project is licensed under BSD-3-Clause_.

.. _contributing: https://github.com/nokia/crl-threadverify/blob/master/CONTRIBUTING.rst
.. _code: https://github.com/nokia/crl-threadverify
.. _issues: https://github.com/nokia/crl-threadverify/issues
.. _BSD-3-Clause:  https://github.com/nokia/crl-threadverify/blob/master/LICENSE
