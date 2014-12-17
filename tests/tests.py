#!/usr/bin/env python

import unittest
import sys

sys.path.append('..')

import collectd_transmission

# A Monkey object to make our lives easier. We want to avoid including
# collectd module which is why all the fuss
class MonkeyObject(object):
    pass

class MethodTestCase(unittest.TestCase):
    def setUp(self):
        self.config = MonkeyObject()
        self.config.children = []
        child1 = MonkeyObject()
        child1.key = 'username'
        child1.values = ['myusername']
        child2 = MonkeyObject()
        child2.key = 'password'
        child2.values = ['mypassword']

        self.config.children.append(child1)
        self.config.children.append(child2)

    def tearDown(self):
        del self.config # The rest will be handled by GC

    def test_config(self):
        collectd_transmission.config(self.config)

    def test_initialize(self):
        collectd_transmission.config(self.config)
        collectd_transmission.initialize()

if __name__ == '__main__':
    unittest.main()
