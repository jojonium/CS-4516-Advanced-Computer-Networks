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

We should install OpenSSH, to make it easier to work on the virtual machine.

`tce-load -wi openssh`

Create a configuration file for SSH:

`sudo cp /usr/local/etc/ssh/sshd_config.orig /usr/local/etc/ssh/sshd_config`

Set a password for user tc (the script uses `cs4516` as the password)

`sudo passwd tc`

TinyCore uses a RAM-based filesystem, so you need to store the changes you make
or they will be lost on reboot.

Backup ssh configuration and shadow file:

`sudo printf '/usr/local/etc/ssh' >> /opt/.filetool.lst`
`sudo printf '/etc/shadow' >> /opt/.filetool.lst`
