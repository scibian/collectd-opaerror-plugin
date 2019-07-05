#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 EDF SA
#
# Authors: CCN - HPC <dsp-cspit-ccn-hpc@edf.fr>
#
# This file is part of collectd-sdiag-plugin
#
# collectd-sdiag-plugin is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# collectd-sdiag-plugin is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with collectd-sdiag-plugin.  If not, see
# <http://www.gnu.org/licenses/>.


import subprocess
import re
import logging

DEBUG = 0

def initialize_logger(debug):
# setup logger
    if debug >= 3:
        level = logging.DEBUG
    elif debug >=1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logger = logging.basicConfig(level=level)

def run(cmd, exit_on_error=True):
    """Run a command and check its return code.

       Arguments:
       * cmd: list of command arguments
       * exit_on_error: boolean to control behaviour on command error (ie.
           return code != 0). If true (default) exits, otherwise the
           function raises an RuntimeError exception.
     """

    logging.debug("acceptance/run: {0}".format(cmd))

    try:
        popen = subprocess.Popen(cmd, shell = True, stdin = None, 
            stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        output, error = popen.communicate()
        return popen.returncode, output.rstrip(), error
    except OSError, e:
        return 1, "", e.errno

def opaextracterror():

    metric = {}
    cmd = '/usr/sbin/opareport -o comps -s -x -d 10 -M | /usr/sbin/opaxmlextract -d \; -e NodeDesc -e SystemImageGUID -e PortNum -e LinkSpeedActive -e LinkWidthDnGradeTxActive -e LinkWidthDnGradeRxActive -e LinkQualityIndicator -e RcvSwitchRelayErrors -e LocalLinkIntegrityErrors -e RcvErrors -e ExcessiveBufferOverruns -e FMConfigErrors -e LinkErrorRecovery -e LinkDowned -e UncorrectableErrors -e RcvConstraintErrors -e XmitConstraintErrors -e XmitDiscards -e RcvRemotePhysicalErrors -s Neighbor -s SMs'
    retcode, output, error = run(cmd)

    output = output.split('\n')
    for index in range(len(output)):
        if index:
            line = re.split(';',output[index])
            NodeDesc = re.sub(' ','_',line[0])
            SystemImageGUID = line[1]
            PortNum = line[2]
            row = '{0}_{1}'.format(NodeDesc,PortNum)
    	    for col in range(4,len(line)):
				if line[col] == 'None' or line[col] == '':
					metric[header[col]][row] = 'None'
				else:
					metric[header[col]][row] =  int(line[col])
        else:
            header = re.split(';',output[index])
    	    for col in range(4,len(header)):
                metric[header[col]] = {}

    return metric

def print_metrics(debug):
    initialize_logger(debug)
    # Read value
    output = opaextracterror()

    for instance in output:
        row = output[instance]
        for key in row:
            if row[key] == 'None':
                msg = 'no counter {0} for {1}'.format(instance,key)
                logging.debug(msg)
            else:
                print '{0}_{1} {2}'.format(instance,key,row[key])

def config(config):
	for kv in config.children:
		if kv.key == 'Interval':
			global INTERVAL
			INTERVAL = int(kv.values[0])
			collectd.info('plugin opa_error: get Interval value --> {0}'.format(INTERVAL))
		elif kv.key == 'Debug':
			global DEBUG
			DEBUG = int(kv.values[0])
			collectd.info('plugin opa_error: get Debug value --> {0}'.format(DEBUG))

def read():
    # Read value
    output = opaextracterror()

    # Dispatch value to collectd
    for instance in output:
        row = output[instance]
        for key in row:
            if row[key] == 'None':
                collectd.warning('no opa counter for {0}_{1}'.format(instance,key))
            else:
                metric = collectd.Values()
                metric.type = 'gauge'
                metric.type_instance = '{0}_{1}'.format(instance,key)
                metric.plugin = 'opa_error'
                metric.values = [row[key]]
                msg = 'plugin opa_error: counter {0} is {1} for {2}'.format(instance,row[key],key)
                if DEBUG: collectd.info(msg)
                metric.dispatch()


if __name__ == '__main__':
    # outside plugin just print metric
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        DEBUG = 3
    print_metrics(DEBUG)
else:
    # when running inside plugin register each callback
    import collectd
    # default interval
    INTERVAL = 300
    collectd.register_config(config)
    collectd.register_read(read, INTERVAL)
