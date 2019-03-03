#!/bin/bash
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update && sudo apt-get -y dist-upgrade
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && \
sudo apt-get update && sudo apt-get -y install docker-ce && sudo usermod -a -G docker $USER
sudo apt-get install -y python-pip
sudo pip install docker-compose
