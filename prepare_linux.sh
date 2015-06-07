#!/bin/sh

echo "###############################################################"
echo "Start the installation of qt5 and python2"
echo "###############################################################"
sudo apt-get install qt5-default
sudo apt-get install python-dev

echo "###############################################################"
echo "Start the installation of sip,which is an import tool to call "
echo "gcc compile source code of pyqt into binary code"
echo "###############################################################"
cd ~
mkdir temp
cd temp
wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.7/sip-4.16.7.tar.gz
tar -xzf sip-4.16.7.tar.gz
cd sip-4.16.7&&python configure.py --platform linux-g++&&make&&sudo make install
echo "###############################################################"
echo "Start the installation of pyqt "
echo "It will take some time because we need to compile the souece code"
echo "###############################################################"
cd ~/temp
wget http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.4.1/PyQt-gpl-5.4.1.tar.gz
tar -xzf PyQt-gpl-5.4.1.tar.gz
#This step is import or you will recive error on include<python.h>, details can
#be found here
#http://stackoverflow.com/questions/17698877/fatal-error-while-compiling-pyqt5-python-h-does-not-exist
sudo ln -s /usr/include/python2.7 /usr/local/include/python2.7
cd PyQt-gpl-5.4.1 && python configure.py && sudo make && sudo make install
echo "###############################################################"
echo "All the installation has done! please check your installation"
echo "###############################################################"
