Compatibility
=============

As long as you can install collectd 5.x with the python plugin and
transmission-rpc less than 3.0 it should work out of the box.

transmission-rpc
================

This project started off using transmissionrpc, a project that hasn't
apparently been updated since 2014. While a number of forks do exist,
the most promising one, in 2023, is transmission-rpc. It forked in 2018
apparently and is still seeing updates. It has switched to SemVer,
allowing us to more easily test against the major releases and decide on
how to proceed. There are a number of identified notes here:

* Versions 3.0+ broke the Client() class signature and for now we can't
  use them
* Versions 0.0.x and 0.1.0 used the python 2/3 compatibility layer named
  six. Given that we don't even want to support python 2.x anymore, we
  'll be skipping those releases to avoid installing a redundant
  compatibility layer in users's machines. This is further justified by the
  fact that upstream deprecated python 2 in 1.0.0
