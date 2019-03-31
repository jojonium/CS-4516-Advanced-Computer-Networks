# CS 4516: Advanced Computer Networks

Coursework and projects for WPI class CS 4516: Advanced Computer Networks

## Phase 1

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

### SSH

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

### Static IP

Next, we need to configure the eth1 interface of TinyCore with the static IP
address 192.168.12.1, netmask 255.255.255.0. This is the interface it will use
to connect to the Internet, and we have to persist the change so it deploys the
configuration every time the machine boots up. We can do this with a command:

`ifconfig eth1 192.168.12.1 netmask 255.255.255.0 broadcast 192.168.12.255 up`

But we want the change to be persistent, so that it deploys the new
configuration every time the machine boots up. We'll put it in a startup script,
`/opt/eth1.sh` soon, but we have some other stuff to do first.


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
