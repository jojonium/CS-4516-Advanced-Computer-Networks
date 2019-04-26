# CS 4516: Advanced Computer Networks

Coursework and projects for WPI class CS 4516: Advanced Computer Networks

### Table of Contents

* [Phase 1](#phase-1)
* [Phase 2](#phase-2)
* [Phase 3](#phase-3)
* [Phase 4](#phase-4)

Phase 1
=======

Cole Granof and Joseph Petitti

In this phase, we configure the TinyCore VM to act as a gateway.

First, configure the VirtualBox NAT interface (Adapter 1) so that it
port-forwards from port 12345 of the host to port 22 of the guest VM:

* Open the VM network settings, select Adapter #1, click port-forwarding.
* Add a port forwarding rule from port 12345 of the host to port 22 of the
  guest.

Then, install Android x86 in another virtual machine, and configure it to use
the gateway VM to reach the internet:

![](https://raw.githubusercontent.com/jojonium/CS-4516-Advanced-Computer-Networks/master/phase1/virtualbox-config.png)

__Note:__ Everything below this point can be done by the `phase1/init.sh`
script, or you can follow along and do it manually.

SSH
---

We should install OpenSSH, to make it easier to work on the virtual machine.

`tce-load -wi openssh`

Create a configuration file for SSH:

`sudo cp /usr/local/etc/ssh/sshd_config.orig /usr/local/etc/ssh/sshd_config`

Set a password for user tc (the script uses `cs4516` as the password)

`sudo passwd tc`

Make sure SSH starts at boot

`sudo sh -c 'echo "sudo /usr/local/etc/init.d/openssh start" >> /opt/bootlocal.sh'`

TinyCore uses a RAM-based filesystem, so you need to store the changes you make
or they will be lost on reboot.

Backup ssh configuration and shadow file:

```
echo '/usr/local/etc/ssh' >> /opt/.filetool.lst
echo '/etc/shadow' >> /opt/.filetool.lst
```

Backup changes:

`filetool.sh -b`

__Note:__ You should be able to reboot and SSH into the TinyCore gateway now
with `ssh -p 12345 tc@localhost` on the host machine.

Static IP
---------

Next, we need to configure the eth1 interface of TinyCore with the static IP
address 192.168.12.1, netmask 255.255.255.0. This is the interface it will use
to connect to the Internet, and we have to persist the change so it deploys the
configuration every time the machine boots up. We can do this with a command:

`ifconfig eth1 192.168.12.1 netmask 255.255.255.0 broadcast 192.168.12.255 up`

But we want the change to be persistent, so that it deploys the new
configuration every time the machine boots up. We'll put it in a startup script,
`/opt/eth1.sh` soon, but we have some other stuff to do first.

IP Gateway
----------

For this step we need to configure TinyCore to actually forward IP packets. For
this we'll need to packages, so install them now:

```
tce-load -wi iptables
tce-load -wi ipv6-KERNEL
```

Next we need to turn on IP forwarding, and configure it to do this at startup:

`sudo sh -c 'echo "sudo sysctl -w net.ipv4.ip_forward=1" >> /opt/bootlocal.sh'`

And use the newly installed iptables package to route packets from eth0 (the
interface connected to the Android VM).

`sudo sh -c 'echo "sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE" >> /opt/bootlocal.sh'`
 
DHCP Server
-----------

We also want TinyCore to act as a DHCP server for its subnet. We'll create a
configuration file for the program udhcpd that outlines how we want it to work:

```
start 192.168.12.100
end 192.168.12.200
interface eth1
option subnet 255.255.255.0
option router 192.168.12.1
option lease 43200
option dns 10.0.2.3       # the address of VirtualBox's virtual DNS server
option domain network2
```

Put this file in `/etc/eth1_udhcpd.conf`.

Startup Script
--------------

We're almost done setting up the IP gateway, we just need a script to 
`/opt/eth1.sh`, to do this for us every time the virtual machine boots up. This
script kills the udhcpc process if it's already running, uses the command from
earlier to set up eth1, and then starts the udhcpc server process. Put this file
in `/opt/eth1.sh`.

```
#! /bin/sh

# kill dhcp client for eth1
if [ -f /var/run/udhcpc.eth1.pid ]; then
	kill `cat /var/run/udhcpc.eth1.pid`
	sleep 0.1
fi

# configure interface eth1
ifconfig eth1 192.168.12.1 netmask 255.255.255.0 broadcast 192.168.12.255 up

# start the DHCP server process in the background once the interface is ready
sudo udhcpd /etc/eth1_udhcpd.conf &
```

Now we just have to make sure `/opt/eth1.sh` is run at startup, so include it in
`/opt/bootlocal.sh`:

`sudo sh -c 'echo "/opt/eth1.sh &" >> /opt/bootlocal.sh'`

And that's it! Make sure to run `filetool.sh -b` to backup everything, then
reboot and it should work. If the Android VM can't connect to the internet
something went wrong.

Phase 2
=======

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

Phase 3
=======

Cole Granof and Joseph Petitti

To run this program, run `./classifyFlows filename.pcap`, where `filename.pcap`
is a PCAP packet capture trace. It will identify all flows in this trace and
attempt to identify which application they are from. At the end it will print
summary statistics including the percentage identified as each app.

Python Packages
---------------

We used Python 3 for this phase. Required packages:

* scipy
* kamene
* scikit-learn
* numpy
* pickle

Classification Vectors
----------------------

Our classification model is a random forest classifier generated by creating
feature vectors from test flows with the following information:

* Byte ratio (bytes sent / bytes received, or reciprocal)
* Packet ratio (packets sent / packets received, or reciprocal)
* Mean packet length
* Standard deviation of packet lengths (zero if n <= 2)
* Packet length kurtosis
* Packet length skew
* Mean time gap between each packet (zero if n <= 1)
* Time gap kurtosis
* Time gap skew
* Min packet length
* Max packet length
* Min time gap
* Max time gap
* Protocol (1 for TCP, 0 for UDP)

File Breakdown
--------------

`pcapper.py` runs on TinyCore, captures packets from eth1 and writes them as
PCAP files. `trainer.py` builds the classification model based on feature
vectors that we collected. It takes in two or more pickled python objects
representing the feature vectors and uses them to build the model. It will
continue to train an existing `model.pkl` file if one exists, or will create one
otherwise. `classifyFlows` requires `model.pkl` to be in the same directory. It
takes in a PCAP file as an argument and classifies each of the flows in it based
on the `model.pkl`. It then makes a prediction about what application the flow
came from and prints it in the following format:

```
<timestamp> <src addr> <dst addr> <src port> <dst port> <proto>\
<#packets sent> <#packets rcvd> <#bytes send> <#bytes rcvd> <label>
```

A modified version of `classifyFlows` was also used to build vectors out of PCAP
files to feed to `trainer.py`.

We didn't include the PCAP and feature vector files we used for testing and
training to conserve space and fit within Canvas's upload limit.

Results
-------

The following table shows the results of our test. The second column shows the
percentage of flows that were correctly identified, excluding flows identified
as unknown.

| Application Name | % Correct  | % Unknown  |
| ---------------- | ---------- | ---------- |
| YouTube          | 79.94%     | 11.39%     |
| Browser          | 20.53%     | 34.48%     |
| Google News      | 36.13%     | 24.44%     |
| Fruit Ninja      | 53.33%     | 11.76%     |
| Weather Channel  | 55.84%     | 20.10%     |
| __Average__      | __55.84%__ | __20.10%__ |

For each application, our model was more accurate than simply guessing (20%).
Overall, it is correct more often that not.

Limitations and Shortcomings
----------------------------

For some reason our model really likes misidentifying flows as being from the
Weather Channel app. We hypothesize that the Weather Channel's app performs a
variety of network applications including video, advertisements, and
asynchronous data requests, which makes it easy to confuse with other apps. Our
machine learning model is also probably not ideal because neither of us have
taken a machine learning class.
