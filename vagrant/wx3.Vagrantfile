# -*- mode: ruby -*-
# vi: set ft=ruby :

# An environment where wxPython 3.0.0.0 can be tested.

$script = <<SCRIPT
# wxPython dependencies
yum install -y make automake gcc gcc-c++ kernel-devel gtk2-devel gtkglext-devel gstreamer-plugins-base-devel python-devel webkitgtk

# Download wxPython source
yum install -y wget
wget http://downloads.sourceforge.net/wxpython/wxPython-src-3.0.0.0.tar.bz2
tar xvvf wxPython-src-3.0.0.0.tar.bz2

# Build wxPython
cd wxPython-src-3.0.0.0/wxPython/
python build-wxpython.py --build_dir=../build

# Generate startup script
echo '#!/bin/bash'                                                      > /home/vagrant/run_timeline_with_wx3.sh
echo 'PYTHONPATH=/home/vagrant/wxPython-src-3.0.0.0/wxPython \\'       >> /home/vagrant/run_timeline_with_wx3.sh
echo 'LD_LIBRARY_PATH=/home/vagrant/wxPython-src-3.0.0.0/build/lib \\' >> /home/vagrant/run_timeline_with_wx3.sh
echo 'python /vagrant/timeline.py'                                     >> /home/vagrant/run_timeline_with_wx3.sh
chmod +x /home/vagrant/run_timeline_with_wx3.sh

# For X11
yum install -y xorg-x11-xauth

# Some fonts
yum install -y gnu-free-*-fonts
SCRIPT

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "chef/fedora-20"

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--memory", "2048"]
    vb.cpus = 2
  end

  config.vm.provision "shell", inline: $script

  config.ssh.forward_x11 = "true"

end
