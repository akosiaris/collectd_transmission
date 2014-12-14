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
