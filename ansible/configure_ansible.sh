#!/bin/bash
# Add repos for installing yq and ansible
sudo add-apt-repository --yes ppa:rmescandon/yq
sudo add-apt-repository --yes ppa:ansible/ansible

# Install yq and ansible
sudo apt install yq ansible -y
