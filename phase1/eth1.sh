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
