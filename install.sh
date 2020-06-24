#!/bin/bash
clear
echo "------ CmWb Installer v1.0 ------"
echo ""
echo "Install python3 pip3 and other packages."

read -p "Are you sure? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    clear
    exit 1
fi

clear
sudo apt install python3 python3-pip
sudo pip3 install cefpython3 tk

clear
echo "------ All Done Installing ------"
echo ""
echo "Install all done!"
echo "Start browser using ./start.sh"

read -p "Are you sure? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    clear
    exit 1
fi

clear

chmod +x installdata/cmwb
chmod +x *
sudo mkdir /etc/cmwb
sudo cp -r * /etc/cmwb
sudo cp installdata/cmwb /bin/cmwb
sudo cp installdata/cmwb.desktop /usr/share/applications/cmwb.desktop
sudo chmod +x /usr/share/applications/cmwb.desktop
sudo cp installdata/cmwb.desktop ~/Desktop/CmWb.desktop
sudo chown $(whoami) /etc/cmwb/config/*

clear
echo "------ All Done Making Shortcuts ------"
echo ""
echo "Install all done!"
echo "Start browser using ./start.sh in this directory, or using cmwb from anywhere"
echo "Press Enter to Continue"
read
clear

