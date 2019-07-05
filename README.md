# Collectd Opa error counters Python Plugin 

## Overview

This project contains a Python script `ora_error.py` that collects all Opa
error counters on all OPA ports on infiniband fabric. 

This script is designed to be used as a collectd Python plugin and directly
from CLI (mostly for testing purpose).

This Python script relies on opaextracterror which is a bash script which call opaerror
command.

## Usage

### CLI

Once the script is deployed on one node with Intel OPA CLI commands,
just run the Python script:

```
python opa_error.py
```

### Collectd plugin

Deploy the script on one of your Slurm cluster node (eg. batch controller) in
the directory of your choice (eg. `/usr/share/python/collectd/plugins/`). Then add the module to
your `collectd.conf`:

```
    LoadPlugin python

    <Plugin python>
       ModulePath "/usr/share/python/collectd/plugins"
       Import "opa_error"
    </Plugin>
```

Make sure to adjust the `ModulePath` value.

## Description

See bellow description of thresolds collected by this plugin:

Errors: Signal Integrity
    Link Qual Indicator                      LinkQualityIndicator
    Uncorrectable Errors                     UncorrectableErrors
    Link Downed                              LinkDowned
    Rcv Errors                               RcvErrors
    Exc. Buffer Overrun                      ExcessiveBufferOverruns
    FM Config Errors                         FMConfigErrors
    Local Link Integ Err                     LocalLinkIntegrityErrors
    Link Error Recovery                      LinkErrorRecovery
    Rcv Rmt Phys Err                         RcvRemotePhysicalErrors
Errors: Security
    Xmit Constraint                          XmitConstraintErrors
    Rcv Constraint                           RcvConstraintErrors
Errors: Routing and Other Errors
    Rcv Sw Relay Err                         RcvSwitchRelayErrors
    Xmit Discards                            XmitDiscards

## Licensing

This script is distributed under the terms of the GNU General Public License
version 3, or any later version.
