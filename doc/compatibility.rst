Compatibility
=============

As long as you can install collectd 5.x with the python plugin and
transmissionrpc 0.11 it should work out of the box

Development
===========
Developed initially on a Debian Wheezy system.

That used to mean:

* collectd 5.1
* transmissionrpc 0.8

Since then few things have changed (we no longer support tranmissionrpc 0.8)
and python < 3.4. Still supporting python 2.7

Development now continues on a Debian Stretch system. Which means:

* collectd 5.7
* transmissionrpc 0.11

There is extra testing via automated means but there only so much it can do

Feel free to submit PRs for other systems support
