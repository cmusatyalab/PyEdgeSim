''' K9s '''
#!/usr/bin/env python
import sys
import os
from platform import machine,system
from urllib.request import urlopen
import tarfile

ARCH = "arm64" if machine() == "aarch64" else "x86_64"
SYS = "Windows" if system() == "Windows" else "Linux"
EXECUTABLE = "k9s.exe" if system() == "Windows" else "k9s"
VER = "k9s_{}_{}.tar.gz".format(SYS,ARCH)
URL = "https://github.com/derailed/k9s/releases/download/v0.25.18/{}".format(VER)
with urlopen(URL) as file:
    content = file.read()
with open(VER, 'wb') as download:
    download.write(content)
file = tarfile.open(VER)
for member in file.getmembers():
    if member.name == EXECUTABLE:
        HOME = os.environ['HOME'] if SYS == 'Linux' else os.environ['USERPROFILE']
        BIN = os.path.join(HOME,"bin")
        if not os.path.isdir(BIN): os.makedirs(BIN)
        file.extract(member,BIN)
        print("k9s installed in {}".format(BIN))
        break
file.close()
os.remove(VER)

