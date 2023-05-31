Introduction
============

.. image:: https://img.shields.io/pypi/v/collectd_transmission.svg
   :target: https://pypi.python.org/pypi/collectd_transmission
   :alt: PyPi version

.. image:: https://readthedocs.org/projects/collectd-transmission/badge/?version=latest
   :target: https://readthedocs.org/projects/collectd-transmission/
   :alt: Documentation Status

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

Quick Installation
==================

Debian/Ubuntu assumed. Prereqs installation

.. code-block:: bash

    apt-get install collectd transmission-daemon python-transmissionrpc python-pip


And then the actually software

.. code-block:: bash

    pip install collectd_transmission

Configure
=========

Insert the following in your collectd.conf::

    <Plugin python>
        LogTraces false
        Interactive false
        Import "collectd_transmission"
        <Module collectd_transmission>
            username "myuser" # Required
            password "mypass" # Required
        </Module>
    </Plugin>

modified accordingly to your needs. Restart collectd and you are done.

There should be rrds for transmission under collectd's data directory.
Most probably that is `/var/lib/collectd/rrd/<hostname>/transmission/`

Documentation
=============

If you want some actually documentation and more detailed installation
and/or configuration instructions head over to:

https://pythonhosted.org/collectd_transmission/
