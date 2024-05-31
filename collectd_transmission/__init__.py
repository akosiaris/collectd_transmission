#!/usr/bin/python3
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

'''
..  moduleauthor:: Alexandros Kosiaris
'''

import collectd  # pylint: disable=import-error
import transmission_rpc  # pylint: disable=import-error


PLUGIN_NAME = 'transmission'

data = {}
metrics = {
    # General metrics
    'general': {
        'active_torrent_count': {'type': 'gauge'},
        'torrent_count': {'type': 'gauge'},
        'download_speed': {'type': 'gauge'},
        'upload_speed': {'type': 'gauge'},
        'paused_torrent_count': {'type': 'gauge'},
    },
    # All time metrics
    'cumulative': {
        'uploaded_bytes': {'type': 'counter'},
        'downloaded_bytes': {'type': 'counter'},
        'files_added': {'type': 'counter'},
        'session_count': {'type': 'counter'},
        'seconds_active': {'type': 'counter'},
    },
    # Per session (restart) metrics
    'current': {
        'uploaded_bytes': {'type': 'counter'},
        'downloaded_bytes': {'type': 'counter'},
        'files_added': {'type': 'counter'},
        'session_count': {'type': 'counter'},
        'seconds_active': {'type': 'counter'},
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
    host = data.get('host', 'localhost')
    port = data.get('port', 9091)
    path = data.get('path', '/transmission/rpc')
    timeout = int(data.get('timeout', '5'))
    try:
        client = transmission_rpc.Client(
            host=host,
            path=path,
            port=port,
            username=username,
            password=password,
            timeout=timeout)
    except transmission_rpc.error.TransmissionError:
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
    if category == 'cumulative':
        return getattr(stats.cumulative_stats, key)
    if category == 'current':
        return getattr(stats.current_stats, key)
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
    except transmission_rpc.error.TransmissionError:
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
