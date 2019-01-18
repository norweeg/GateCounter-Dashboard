#!/bin/bash

sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update && sudo apt-get -y dist-upgrade
sudo apt-get install apt-transport-https ca-certificates curl gnupg2 software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
   "deb [arch=armhf] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
sudo apt-get update && sudo apt-get -y install docker-ce
sudo apt-get install -y python-pip
sudo pip install docker-compose
