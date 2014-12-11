#!/bin/sh

set -e

CLEAN=${1:-""}
COLLECTD_DIR=${2:-"/var/lib/collectd/rrd"}
HOSTNAME=`hostname -f`

cd $COLLECTD_DIR/${HOSTNAME}/transmission

for i in \
	counter-downloadedBytes.rrd \
	counter-filesAdded.rrd \
	counter-secondsActive.rrd \
	counter-uploadedBytes.rrd \
	gauge-secondsActive.rrd
do
	TYPE=`echo $i | sed -e 's/\([a-z]*\)-\([a-zA-Z_]*\).rrd/\1/'`
	SECOND_PART=`echo $i | sed -e 's/\([a-z]*\)-\([a-zA-Z_]*\).rrd/\2/'`
	ln $i $TYPE-cumulative-$SECOND_PART.rrd
	if [ -n "$CLEAN" ]; then
		rm $i
	fi
done

for i in \
	gauge-activeTorrentCount.rrd \
	gauge-blocklist_size.rrd \
	gauge-downloadSpeed.rrd \
	gauge-pausedTorrentCount.rrd \
	gauge-torrentCount.rrd \
	gauge-uploadSpeed.rrd
do
	TYPE=`echo $i | sed -e 's/\([a-z]*\)-\([a-zA-Z_]*\).rrd/\1/'`
	SECOND_PART=`echo $i | sed -e 's/\([a-z]*\)-\([a-zA-Z_]*\).rrd/\2/'`
	ln $i $TYPE-general-$SECOND_PART.rrd
	if [ -n "$CLEAN" ]; then
		rm $i
	fi
done
