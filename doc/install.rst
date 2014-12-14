How to install
==============

Prerequisites
-------------

Those are collectd and transmission

I assume a Debian system here, amend accordingly for your system

If you have not already installed transmision, install it:

.. code-block:: bash

    apt-get install transmission-daemon

The above install the daemon cause a headless box is assumed. It should
probably work with a non headless box as well and a normal transmission
installation but this has not been tested.

Install the python transmission binding

.. code-block:: bash

    apt-get install python-transmissionrpc

Install collectd.

.. code-block:: bash

    apt-get install collectd

Install collectd_transmission
-----------------------------

There are two ways to achieve this for now

Use the python package
++++++++++++++++++++++

.. code-block:: bash

    pip install collectd_transmission

Do it manually
++++++++++++++

Clone the repo, copy the module directory somewhere in your fileystem
