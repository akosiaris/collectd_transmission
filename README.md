# Introduction #

A python plugin for integrating collectd and transmission. With this
installed, collectd will be querying transmission for the following:

* downloadedBytes
* uploadedBytes
* filesAdded
* secondsActive
* activeTorrentCount
* blocklist\_size
* downloadSpeed
* uploadSpeed
* pausedTorrentCount
* torrentCount

and creating the relevant RRD files (or pushing to graphite or you have
collectd doing)

# How to use #
I assume a Debian system here, amend accordingly for your system

If you have not already installed transmision, install it:

    apt-get install transmission-daemon

The above install the daemon cause a headless box is assumed. It should
probably work with a non headless box as well and a normal transmission
installation but this has not been tested.

Install the python transmission binding

    apt-get install python-transmissionrpc

Install collectd.

    apt-get install collectd

Clone the repo, copy the .py, do whatever you want so that the .py file
ends up somewhere in your fileystem

Insert the following in your collectd.conf

    <Plugin python>
        ModulePath "/path/to/module/dir"
        LogTraces false
        Interactive false
        Import "transmission_stats"
        <Module transmission_stats>
            username "myuser" # Required
            password "mypass" # Required
            hostname "http://localhost:9091/transmission/rpc" # Optional, default to what we got here
            timeout "5" # Optional, defaults to 5
        </Module>
    </Plugin>

modified accordingly to your needs. Restart collectd and you are done.

    sudo service collectd restart

There should be rrds for transmission under collectd's data directory.
Most probably that is /var/lib/collectd/rrd/_hostname_/transmission/

## How to display your data ##

Well if you got collectd, you probably already have a way of displaying
your data anyway. If you don't there are various frontends available at:

[https://collectd.org/wiki/index.php/List\_of\_front-ends](https://collectd.org/wiki/index.php/List\_of\_front-ends)

# Compatibility #

Developed and tested on Debian Wheezy system. Feel free to submit PRs for other systems support
