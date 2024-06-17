#!/usr/bin/python3
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

'''
..  moduleauthor:: Alexandros Kosiaris
'''

import collectd  # pylint: disable=import-error
from transmission_rpc import Client, Session  # pylint: disable=import-error
from transmission_rpc.error import TransmissionError  # pylint: disable=import-error
try:
    # This will only succeed past version 4.0.0
    # The name key in the following dicts exists to avoid metric names breaking
    # when upgrading from transmission-rpc < 4.0.0
    from transmission_rpc.session import SessionStats
    metrics= {
        # General metrics
        'general': {
            'active_torrent_count': {'type': 'gauge', 'name': 'activeTorrentCount'},
            'torrent_count': {'type': 'gauge', 'name': 'torrentCount'},
            'download_speed': {'type': 'gauge', 'name': 'downloadSpeed'},
            'upload_speed': {'type': 'gauge', 'name': 'uploadSpeed'},
            'paused_torrent_count': {'type': 'gauge', 'name': 'pausedTorrentCount'},
            # The following used to exist, but it is not a property of a
            # Session instance anymore
            # 'blocklist_size': {'type': 'gauge', 'name': 'blocklist_size'},
        },
        # All time metrics
        'cumulative': {
            'downloaded_bytes': {'type': 'counter', 'name': 'downloadedBytes'},
            'files_added': {'type': 'counter', 'name': 'filesAdded'},
            'uploaded_bytes': {'type': 'counter', 'name': 'uploadedBytes'},
            'seconds_active': {'type': 'gauge', 'name': 'secondsActive'},
            'session_count': {'type': 'gauge', 'name': 'sessionCount'},
        },
        # Per session (restart) metrics
        'current': {
            'downloaded_bytes': {'type': 'counter', 'name': 'downloadedBytes'},
            'files_added': {'type': 'counter', 'name': 'filesAdded'},
            'uploaded_bytes': {'type': 'counter', 'name': 'uploadedBytes'},
            'seconds_active': {'type': 'gauge', 'name': 'secondsActive'},
            'session_count': {'type': 'gauge', 'name': 'sessionCount'},
        }
    }
except ImportError:
    # SessionStats import failed, assume we are using transmission-rpc < 4.0.0
    metrics= {
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

PLUGIN_NAME = 'transmission'

data = {}

def configuration(config):
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
    username = data['username']
    password = data['password']
    host = data.get('host', 'localhost')
    port = int(data.get('port', '9091'))
    path = data.get('path', '/transmission/rpc')
    timeout = int(data.get('timeout', '5'))
    try:
        client = Client(
            host=host,
            path=path,
            port=port,
            username=username,
            password=password,
            timeout=timeout)
    except TransmissionError:
        client = None
    data['client'] = client


def shutdown():
    '''
    Collectd shutdown routine
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
    if category == 'cumulative':
        return stats.cumulative_stats.get(key)
    if category == 'current':
        return stats.current_stats.get(key)
    # We are in "general"
    try:
        return stats.get(key)
    except AttributeError:
        return getattr(stats, key)


def get_stats():
    '''
    Collectd routine to actually get and dispatch the statistics
    '''
    # If we are not correctly initialized, initialize us once more.
    # Something happened after the first init and we have lost state
    if 'client' not in data or data['client'] is None:
        shutdown()
        initialize()
    # And let's fetch our data
    try:
        stats = data['client'].session_stats()
    except TransmissionError:
        shutdown()
        initialize()
        return  # On this run, just fail to return anything
    # Let's get our data
    for category, catmetrics in metrics.items():
        for metric, attrs in catmetrics.items():
            metric_name = attrs.get('name', metric)
            values = collectd.Values(
                type=attrs['type'],
                plugin=PLUGIN_NAME,
                type_instance=f'{category}-{metric_name}')
            values.dispatch(values=[field_getter(stats, metric_name, category)])


# Register our functions
collectd.register_config(configuration)
collectd.register_init(initialize)
collectd.register_read(get_stats)
collectd.register_shutdown(shutdown)
