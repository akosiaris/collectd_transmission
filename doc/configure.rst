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
            host "localhost" # Optional
            port "9091" # Optional
            path "/transmission/rpc" # Optional
            timeout "5" # Optional
        </Module>
    </Plugin>

modified accordingly to your needs. Everything marked as optional, can be
skipped. The default value is given for your convenience

Restart collectd and you are done.

.. code-block:: bash

    sudo service collectd restart

There should be RRDs for transmission under collectd's data directory.
Most probably that is /var/lib/collectd/rrd/<hostname>/transmission/
