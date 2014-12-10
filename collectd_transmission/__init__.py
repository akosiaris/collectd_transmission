#!/usr/bin/env python
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

import collectd
import transmissionrpc
from distutils.version import StrictVersion

PLUGIN_NAME = 'transmission'

data = {}
metrics = {
    'general': {
    # General metrics
        'activeTorrentCount': { 'type': 'gauge'},
        'torrentCount': { 'type': 'gauge'},
        'downloadSpeed': { 'type': 'gauge'},
        'uploadSpeed': { 'type': 'gauge'},
        'pausedTorrentCount': { 'type': 'gauge'},
        'blocklist_size': { 'type': 'gauge'},
    },
    # All time metrics
    'cumulative': {
        'downloadedBytes': { 'type': 'counter'},
        'filesAdded': { 'type': 'counter'},
        'uploadedBytes': { 'type': 'counter'},
        'secondsActive': { 'type': 'gauge'},
        'sessionCount': { 'type': 'gauge'},
    },
    # Per session (restart) metrics
    'current': {
        'downloadedBytes': { 'type': 'counter'},
        'filesAdded': { 'type': 'counter'},
        'uploadedBytes': { 'type': 'counter'},
        'secondsActive': { 'type': 'gauge'},
        'sessionCount': { 'type': 'gauge'},
    }
}

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

def field_getter(stats, key, category):
    # 0.9 and onwards have statistics in a different field
    if StrictVersion(data['client_version']) >= StrictVersion('0.9') :
        if category == 'cumulative':
            return stats.cumulative_stats[key]
        elif category == 'current':
            return stats.current_stats[key]
        elif category == 'general':
            return stats.key
        else:
            return 0
    else:
        if category == 'cumulative':
            return stats.fields['cumulative_stats'][key]
        elif category == 'current':
            return stats.fields['current_stats'][key]
        elif category == 'general':
            return stats.fields[key]
        else:
            return 0

def get_stats():
    stats=data['client'].session_stats()
    # And let's fetch our data
    for category, catmetrics in metrics.items():
        for metric, attrs in catmetrics.items():
            vl = collectd.Values(type=attrs['type'],
                                 plugin=PLUGIN_NAME,
                                 type_instance='%s-%s' % (category, metric))
            vl.dispatch(values=[field_getter(stats, metric, category)])

collectd.register_config(config)
collectd.register_init(initialize)
collectd.register_read(get_stats)
collectd.register_shutdown(shutdown)
