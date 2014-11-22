#!/usr/bin/env python
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

import collectd
from transmissionrpc import Client

data={}

def config(config):
    for child in config.children:
        data[child.key] = child.values[0]

def initialize():
    USERNAME = data['username']
    PASSWORD = data['password']
    HOST = data.get('hostname', 'http://localhost:9091/transmission/rpc')
    TIMEOUT = int(data.get('timeout', '5'))
    c = Client(address=HOST, user=USERNAME, password=PASSWORD, timeout=TIMEOUT)
    data['client'] = c

def shutdown():
    # Not really any resource to close, just clear the object
    data['client'] = None

def get_stats():
    stats=data['client'].session_stats()
    gauges = ['activeTorrentCount', 'torrentCount', 'downloadSpeed', 'uploadSpeed', 'pausedTorrentCount', 'blocklist_size' ]
    for gauge in gauges:
        vl = collectd.Values(type='gauge',
                             plugin='transmission',
                             type_instance=gauge)
        vl.dispatch(values=[stats.fields[gauge]])
    counters = [ 'downloadedBytes', 'filesAdded', 'uploadedBytes', 'secondsActive', ]
    for counter in counters:
        vl = collectd.Values(type='counter',
                             plugin='transmission',
                             type_instance=counter)
        vl.dispatch(values=[stats.fields['cumulative_stats'][counter]])

collectd.register_config(config)
collectd.register_init(initialize)
collectd.register_read(get_stats)
collectd.register_shutdown(shutdown)
