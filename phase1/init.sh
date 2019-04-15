#! /bin/sh

# install openssh
tce-load -wi openssh;

# create ssh configuration file
sudo cp /usr/local/etc/ssh/sshd_config.orig /usr/local/etc/ssh/sshd_config;

# set password for user tc to `cs4516'
printf "cs4516\ncs4516" | sudo passwd tc;

# make sure ssh starts at boot                                                     
sudo sh -c 'echo "sudo /usr/local/etc/init.d/openssh start" >> /opt/bootlocal.sh';

# add ssh configuration and shadow file to backup list
echo '/usr/local/etc/ssh' >> /opt/.filetool.lst;
echo '/etc/shadow' >> /opt/.filetool.lst;

# install IP forwarding packages
tce-load -wi iptables;
tce-load -wi ipv6-KERNEL;

# turn on IP forwarding at startup
sudo sh -c 'echo "sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE" >> /opt/bootlocal.sh';

# copy DHCP configuration to the /etc
sudo cp eth1_udhcpd.conf /etc/eth1_udhcpd.conf;

# copy eth1 configuration to /opt
sudo cp eth1.sh /opt/eth1.sh;

# run eth1.sh at startup

sudo sh -c 'echo "/opt/eth1.sh &" >> /opt/bootlocal.sh';

# backup changes
filetool.sh -b;

# reboot
sudo reboot;
