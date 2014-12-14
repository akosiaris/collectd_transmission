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
