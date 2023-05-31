#!/usr/bin/python3
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

'''
..  moduleauthor:: Alexandros Kosiaris
'''

from packaging.version import Version, parse
import collectd  # pylint: disable=import-error
import transmissionrpc  # pylint: disable=import-error


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
    address = data.get('address', 'http://localhost:9091/transmission/rpc')
    timeout = int(data.get('timeout', '5'))
    try:
        client = transmissionrpc.Client(
            address=address,
            user=username,
            password=password,
            timeout=timeout)
    except transmissionrpc.error.TransmissionError:
        client = None
    data['client'] = client


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
    client_version = transmissionrpc.__version__
    if parse(client_version) <= Version('0.9'):
        raise RuntimeError('transmissionrpc version < 0.9 found, not supported')
    if category == 'cumulative':
        return stats.cumulative_stats[key]
    if category == 'current':
        return stats.current_stats[key]
    # We are in "general"
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
    except transmissionrpc.error.TransmissionError:
        shutdown()
        initialize()
        return  # On this run, just fail to return anything
    # Let's get our data
    for category, catmetrics in metrics.items():
        for metric, attrs in catmetrics.items():
            values = collectd.Values(
                type=attrs['type'],
                plugin=PLUGIN_NAME,
                type_instance=f'{category}-{metric}')
            values.dispatch(values=[field_getter(stats, metric, category)])


# Register our functions
collectd.register_config(configuration)
collectd.register_init(initialize)
collectd.register_read(get_stats)
collectd.register_shutdown(shutdown)
