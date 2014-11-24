#!/usr/bin/env python
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

import collectd
import transmissionrpc
from distutils.version import StrictVersion

data={}

def config(config):
    for child in config.children:
        data[child.key] = child.values[0]

def initialize():
    USERNAME = data['username']
    PASSWORD = data['password']
    ADDRESS = data.get('address', 'http://localhost:9091/transmission/rpc')
    TIMEOUT = int(data.get('timeout', '5'))
    c = transmissionrpc.Client(address=ADDRESS, user=USERNAME, password=PASSWORD, timeout=TIMEOUT)
    data['client'] = c
    data['client_version'] = transmissionrpc.__version__

def shutdown():
    # Not really any resource to close, just clear the object
    data['client'] = None

def field_getter(stats, key, cumulative=False):
    # 0.9 and onwards have statistics in a different field
    if StrictVersion(data['client_version']) >= StrictVersion('0.9') :
        if cumulative:
            return stats.cumulative_stats[key]
        else:
            return stats.key
    else:
        if cumulative:
            return stats.fields['cumulative_stats'][key]
        else:
            return stats.fields[key]

def get_stats():
    stats=data['client'].session_stats()
    # And let's fetch our data
    gauges = ['activeTorrentCount', 'torrentCount', 'downloadSpeed',
            'uploadSpeed', 'pausedTorrentCount', 'blocklist_size', ]
    for gauge in gauges:
        vl = collectd.Values(type='gauge',
                             plugin='transmission',
                             type_instance=gauge)
        vl.dispatch(values=[field_getter(stats, gauge)])
    counters = [ 'downloadedBytes', 'filesAdded', 'uploadedBytes', 'secondsActive', ]
    for counter in counters:
        vl = collectd.Values(type='counter',
                             plugin='transmission',
                             type_instance=counter)
        vl.dispatch(values=[field_getter(stats, counter, True)])

collectd.register_config(config)
collectd.register_init(initialize)
collectd.register_read(get_stats)
collectd.register_shutdown(shutdown)
