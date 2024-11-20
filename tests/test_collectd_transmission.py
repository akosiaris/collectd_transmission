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

    def setUp(self) -> None:
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

    def tearDown(self) -> None:
        del self.config  # The rest will be handled by GC

    def test_config(self) -> None:
        '''
        Test the configuration
        '''

        collectd_transmission.configuration(self.config)

    @mock.patch(
        'collectd_transmission.Client',
        spec=True)
    def test_initialize(self, mock_client: mock.MagicMock) -> None:
        '''
        Test the initialization
        '''

        collectd_transmission.configuration(self.config)
        collectd_transmission.initialize()
        mock_client.assert_called_with(
            host='localhost',
            path='/transmission/rpc',
            port=9091,
            username='myusername',
            password='mypassword',
            timeout=5)

    @mock.patch(
        'collectd_transmission.Client',
        spec=True,
        side_effect=TransmissionError)
    def test_initialize_fail(self, mock_client: mock.MagicMock) -> None:
        '''
        Test a failed init
        '''

        collectd_transmission.configuration(self.config)
        collectd_transmission.initialize()
        mock_client.assert_called_with(
            host='localhost',
            path='/transmission/rpc',
            port=9091,
            username='myusername',
            password='mypassword',
            timeout=5)

    def test_shutdown(self) -> None:
        '''
        Test the shutdown
        '''

        collectd_transmission.shutdown()

    @mock.patch('collectd_transmission.Client', spec=True)
    def test_get_stats(self, mock_client: mock.MagicMock) -> None:
        '''
        Test getting stats
        '''

        collectd_transmission.data['client'] = mock_client
        collectd_transmission.get_stats()
        mock_client.session_stats.assert_called_with()

    @mock.patch('collectd_transmission.Client', spec=True)
    def test_get_stats_exception(self, mock_client: mock.MagicMock) -> None:
        '''
        Test getting stats with an exception
        '''

        mock_client.session_stats = mock.MagicMock(
            side_effect=TransmissionError('foo'))
        collectd_transmission.data['client'] = mock_client
        collectd_transmission.get_stats()
        mock_client.session_stats.assert_called_with()

    @mock.patch('collectd_transmission.Client', spec=True)
    def test_get_stats_none_client(self, _: mock.MagicMock) -> None:
        '''
        Test getting stats if we don't have a client object
        '''

        collectd_transmission.data['client'] = None
        collectd_transmission.get_stats()


class LiveTestCase(unittest.TestCase):
    '''
    Live testing against a running server
    '''

    def setUp(self) -> None:
        # Mock our configuration to avoid having to construct them properly
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

    def tearDown(self) -> None:
        del self.config  # The rest will be handled by GC

    def test_proper_client(self) -> None:
        '''
        Test using a non mocked Client, talking to running transmission-daemon
        on port http://localhost:9091/transmission/rpc, with
        myusername/mypassword auth creds
        '''

        collectd_transmission.configuration(self.config)
        collectd_transmission.initialize()
        collectd_transmission.get_stats()


if __name__ == '__main__':
    unittest.main()
