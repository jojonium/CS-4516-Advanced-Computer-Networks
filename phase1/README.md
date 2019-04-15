CS 4516: Advanced Computer Networks, Phase 1
============================================

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
