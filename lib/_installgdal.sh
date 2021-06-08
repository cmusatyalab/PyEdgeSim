#!/bin/bash
sudo add-apt-repository -y ppa:ubuntugis/ppa && \
sudo apt-get update && \
sudo apt-get install -y gdal-bin && \
sudo apt-get install libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
OGRINFO=$(ogrinfo --version)
OGRVER=$(ogrinfo --version|awk '{print $2}'|sed 's/,//')
pip install GDAL==${OGRVER}