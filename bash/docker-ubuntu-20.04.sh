#!/bin/bash

#	RUN bash ~/git/SysSetup/apps/docker/docker-ubuntu-20.04.sh

DUSER=$USER

# Docker.io
sudo apt-get -y install \
	    apt-transport-https \
	    ca-certificates \
	    curl \
	    software-properties-common 
	
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable" 

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - 
sudo apt-key fingerprint 0EBFCD88 
sudo apt-get -y update 
	
#	apt -y install docker-ce
# or maybe
sudo apt -y install docker.io 
pip install --upgrade docker-compose


# Set up a non-root user
egrep "^docker" /etc/group || sudo groupadd docker
if [ -n "$DUSER" ]
then
	sudo usermod -aG docker $DUSER
	sudo newgrp docker
fi
# may need to logout and log back in to 

	
# verify
docker run hello-world && docker info

# Setup deldockerdead
test -d ~/bin || mkdir ~/bin
cp deldockerdead ~/bin/

