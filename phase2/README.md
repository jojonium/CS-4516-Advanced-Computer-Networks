CS4516: Advanced Computer Networks, Phase 2
===========================================

Joseph Petitti and Cole Granof

For this phase, we wrote a Python script called `logFlows` that captures packets
from the Android VM and separates them into bursts and flows. A flow is defined
as a sequence of packets with the same source IP, source port, destination IP,
and destination port. A burst is a group of flows separated by gaps of greater
than one second of silence. After each burst, the program prints a report on
which each flow in that burst, in the following format:

```
<timestamp> <src addr> <dst addr> <src port> <dst port> <proto> <#packets sent> <#packets rcvd> <#bytes send> <#bytes rcvd>
```

Timestamps are measured in seconds since the program was started, and represent
the time of arrival of the last pack in the flow.

`logFlows` uses Python 2 and requires the Python package scapy, which can be
easily installed with pip. Note that it must be run as root on TinyCore.
