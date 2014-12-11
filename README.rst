Introduction
============

A python plugin for integrating collectd and transmission. With this
installed, collectd will be querying transmission for the following:

Per session and cumulative:

* downloadedBytes
* uploadedBytes
* filesAdded
* secondsActive

General:

* activeTorrentCount
* blocklist\_size
* downloadSpeed
* uploadSpeed
* pausedTorrentCount
* torrentCount

and creating the relevant RRD files (or pushing to graphite or whatever
you have collectd doing)

Some of these metrics are per session, some session cumulative, some are
session independent. Their type 'current', 'cumulative', 'general' is set
in the name of the metric

Compatibility
=============
Developed and tested on Debian Wheezy system.

That means:

* collectd 5.1
* transmissionrpc 0.8

But testing has also been conducted on Debian Jessie systems. Which means:

* collectd 5.4
* transmissionrpc 0.11

It is expected Debian Jessie will be the main playground soon

Feel free to submit PRs for other systems support

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

Configure
=========

Insert the following in your collectd.conf::

    <Plugin python>
        ModulePath "/path/to/module/dir" # Not needed if installed via pip or package
        LogTraces false
        Interactive false
        Import "collectd_transmission"
        <Module collectd_transmission>
            username "myuser" # Required
            password "mypass" # Required
            address "http://localhost:9091/transmission/rpc" # Optional, defaults to "http://localhost:9091/transmission/rpc"
            timeout "5" # Optional, defaults to 5
        </Module>
    </Plugin>

modified accordingly to your needs. Restart collectd and you are done.

.. code-block:: bash

    sudo service collectd restart

There should be rrds for transmission under collectd's data directory.
Most probably that is /var/lib/collectd/rrd/<hostname>/transmission/

How to display your data
========================

Well if you got collectd, you probably already have a way of displaying
your data anyway. If you don't there are various frontends available at:

https://collectd.org/wiki/index.php/List\_of\_front-ends

