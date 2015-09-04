#!/usr/bin/env python
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

'''
..  moduleauthor:: Alexandros Kosiaris
'''

import collectd
import transmissionrpc
from distutils.version import StrictVersion

PLUGIN_NAME = 'transmission'

data = {}
metrics = {
    # General metrics
    'general': {
        'activeTorrentCount': {'type': 'gauge'},
        'torrentCount': {'type': 'gauge'},
        'downloadSpeed': {'type': 'gauge'},
        'uploadSpeed': {'type': 'gauge'},
        'pausedTorrentCount': {'type': 'gauge'},
        'blocklist_size': {'type': 'gauge'},
    },
    # All time metrics
    'cumulative': {
        'downloadedBytes': {'type': 'counter'},
        'filesAdded': {'type': 'counter'},
        'uploadedBytes': {'type': 'counter'},
        'secondsActive': {'type': 'gauge'},
        'sessionCount': {'type': 'gauge'},
    },
    # Per session (restart) metrics
    'current': {
        'downloadedBytes': {'type': 'counter'},
        'filesAdded': {'type': 'counter'},
        'uploadedBytes': {'type': 'counter'},
        'secondsActive': {'type': 'gauge'},
        'sessionCount': {'type': 'gauge'},
    }
}


def config(config):
    '''
    Read the configuration and store it at a shared variable

    Retrieve the configuration from the config variable passed by collectd to
    the python module

    Args:
        config: The config instance passed by collectd to the module
    Returns:
        Nothing
    '''
    for child in config.children:
        data[child.key] = child.values[0]


def initialize():
    '''
    Collectd initialization routine
    '''
    USERNAME = data['username']
    PASSWORD = data['password']
    ADDRESS = data.get('address', 'http://localhost:9091/transmission/rpc')
    TIMEOUT = int(data.get('timeout', '5'))
    c = transmissionrpc.Client(address=ADDRESS, user=USERNAME, password=PASSWORD, timeout=TIMEOUT)
    data['client'] = c
    data['client_version'] = transmissionrpc.__version__


def shutdown():
    '''
    Collectd shutdown routive
    '''
    # Not really any resource to close, just clear the object
    data['client'] = None


def field_getter(stats, key, category):
    '''
    Get the statistics associated with a key and category

    Args:
        stats (dict): A dictionary containing the statistics
        key (str): A string to denote the name of the metric
        category (str): The category this metric belongs in. Possible values:
        'cumulative', 'current', 'general'

    Returns:
        int. The metric value or 0
    '''
    # 0.9 and onwards have statistics in a different field
    if StrictVersion(data['client_version']) >= StrictVersion('0.9'):
        if category == 'cumulative':
            return stats.cumulative_stats[key]
        elif category == 'current':
            return stats.current_stats[key]
        else:  # We are in "general"
            return getattr(stats, key)
    else:
        if category == 'cumulative':
            return stats.fields['cumulative_stats'][key]
        elif category == 'current':
            return stats.fields['current_stats'][key]
        else:  # We are in "general"
            return stats.fields[key]


def get_stats():
    '''
    Collectd routine to actually get and dispatch the statistics
    '''
    stats = data['client'].session_stats()
    # And let's fetch our data
    for category, catmetrics in metrics.items():
        for metric, attrs in catmetrics.items():
            vl = collectd.Values(type=attrs['type'],
                                 plugin=PLUGIN_NAME,
                                 type_instance='%s-%s' % (category, metric))
            vl.dispatch(values=[field_getter(stats, metric, category)])

# Register our functions
collectd.register_config(config)
collectd.register_init(initialize)
collectd.register_read(get_stats)
collectd.register_shutdown(shutdown)
