#!/usr/bin/python3
'''
Tests for collectd_transmission
'''

import sys
import unittest
from unittest import mock
from transmission_rpc.error import TransmissionError

# Monkey patching the collectd module to facilitate testing
mock_collectd = mock.MagicMock()
sys.modules['collectd'] = mock_collectd
import collectd_transmission  # pylint: disable=wrong-import-position



class MethodTestCase(unittest.TestCase):
    '''
    Testing methods
    '''

    def setUp(self):
        # Mock our configuration to enable testing
        self.config = mock.Mock()
        self.config.children = []
        child1 = mock.Mock()
        child1.key = 'username'
        child1.values = ['myusername']
        child2 = mock.Mock()
        child2.key = 'password'
        child2.values = ['mypassword']

        self.config.children.append(child1)
        self.config.children.append(child2)

    def tearDown(self):
        del self.config  # The rest will be handled by GC

    def test_config(self):
        '''
        Test the configuration
        '''

        collectd_transmission.configuration(self.config)

    @mock.patch('collectd_transmission.transmission_rpc.Client', spec=True)
    def test_initialize(self, mock_client):
        '''
        Test the initialization
        '''

        collectd_transmission.configuration(self.config)
        collectd_transmission.initialize()
        mock_client.assert_called_with(
            address='http://localhost:9091/transmission/rpc',
            user='myusername',
            password='mypassword',
            timeout=5)

    @mock.patch(
        'collectd_transmission.transmission_rpc.Client',
        spec=True,
        side_effect=TransmissionError)
    def test_initialize_fail(self, mock_client):
        '''
        Test a failed init
        '''

        collectd_transmission.configuration(self.config)
        collectd_transmission.initialize()
        mock_client.assert_called_with(
            address='http://localhost:9091/transmission/rpc',
            user='myusername',
            password='mypassword',
            timeout=5)

    def test_shutdown(self):
        '''
        Test the shutdown
        '''

        collectd_transmission.shutdown()

    @mock.patch('collectd_transmission.transmission_rpc.Client', spec=True)
    def test_get_stats(self, mock_client):
        '''
        Test getting stats
        '''

        collectd_transmission.data['client'] = mock_client
        collectd_transmission.get_stats()
        mock_client.session_stats.assert_called_with()

    @mock.patch('collectd_transmission.transmission_rpc.Client', spec=True)
    def test_get_stats_exception(self, mock_client):
        '''
        Test getting stats with an exception
        '''

        mock_client.session_stats = mock.MagicMock(
            side_effect=TransmissionError('foo'))
        collectd_transmission.data['client'] = mock_client
        collectd_transmission.get_stats()
        mock_client.session_stats.assert_called_with()

    @mock.patch('collectd_transmission.transmission_rpc.Client', spec=True)
    def test_get_stats_none_client(self, _):
        '''
        Test getting stats if we don't have a client object
        '''

        collectd_transmission.data['client'] = None
        collectd_transmission.get_stats()


if __name__ == '__main__':
    unittest.main()
