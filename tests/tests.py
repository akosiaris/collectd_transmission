#!/usr/bin/env python

import unittest
import mock
import sys

# Monkey patching the collectd module to facilitate testing
mock_collectd = mock.MagicMock()
sys.modules['collectd'] = mock_collectd

# This is a hack to force tests to use the in-repo version of the module and not
# the one installed by tox
sys.path.insert(0, '.')
import collectd_transmission


class MethodTestCase(unittest.TestCase):
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
        collectd_transmission.config(self.config)

    @mock.patch('collectd_transmission.transmissionrpc.Client')
    def test_initialize(self, mock_Client):
        collectd_transmission.config(self.config)
        collectd_transmission.initialize()
        mock_Client.assert_called_with(
            address='http://localhost:9091/transmission/rpc',
            user='myusername',
            password='mypassword',
            timeout=5)

    def test_shutdown(self):
        collectd_transmission.shutdown()

    @mock.patch('collectd_transmission.transmissionrpc.Client')
    def test_get_stats(self, mock_Client):
        collectd_transmission.collectd = mock.MagicMock()
        collectd_transmission.config(self.config)
        collectd_transmission.initialize()
        collectd_transmission.data['client'] = mock_Client
        collectd_transmission.get_stats()
        mock_Client.session_stats.assert_called_with()

if __name__ == '__main__':
    unittest.main()
