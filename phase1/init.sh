#! /bin/sh

# install openssh
tce-load -wi openssh;

# create ssh configuration file
sudo cp /usr/local/etc/ssh/sshd_config.orig /usr/local/etc/ssh/sshd_config;

# set password for user tc to `cs4516'
printf "cs4516\ncs4516" | sudo passwd tc

# make sure ssh starts at boot                                                     
sudo sh -c 'echo "sudo /usr/local/etc/init.d/openssh start" >> /opt/bootlocal.sh'

# add ssh configuration and shadow file to backup list
echo '/usr/local/etc/ssh' >> /opt/.filetool.lst;
echo '/etc/shadow' >> /opt/.filetool.lst;

# backup changes
filetool.sh -b


