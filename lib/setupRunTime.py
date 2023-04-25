#!/usr/bin/env python
# https://github.com/InterDigitalInc/AdvantEDGE/wiki/runtime-environment
import sys
import os
import pprint
import json
import shutil

from pyutils import *

from simlogging import mconsole
 
def setupDockerDaemon(cnf):
    if oscmd('diff {}/daemon.json /etc/docker/daemon.json'.format(cnf['QSFILES'])) == 0:
        mconsole("/etc/docker/daemon.json already current")
        return 0
    entry = input("Configure /etc/docker/daemon.json? [y/N] ") or "n"
    if entry in ['Y','y']:  
        oscmd("sudo swapoff -a")
        oscmd("sudo sed -i '/ swap / s/^/#/' /etc/fstab")
        oscmd('sudo cp {}/daemon.json /etc/docker'.format(cnf['QSFILES']))
        oscmd('sudo mkdir -p /etc/systemd/system/docker.service.d')
        return -1
    ''' REBOOT '''
    return 0
    # ## Install Kubernetes
def setupKubernetes(cnf):
    if 'KUBERNETESTYPE' in cnf and cnf['KUBERNETESTYPE'] == "k3s":
        return setupK3s(cnf)
    entry = input("Set up kubernetes (k8s)? [y/N] ") or "n"
    if entry in ['Y','y']:

        oscmd("sudo swapoff -a") # Turn this off in /etc/fstab as well
        oscmd("sudo     apt-get update && sudo apt-get install -y apt-transport-https curl")
        oscmd('curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -')
        fn = "/etc/apt/sources.list.d/kubernetes.list"
        if not os.path.isfile(fn):
            oscmd('sudo cp {}/kubernetes.list {}'.format(cnf['QSFILES'],fn))
        
        # Install latest supported k8s version
        if oscmd("sudo apt-get update") != 0: return -1
        oscmd("sudo apt-get install -y kubelet=1.19.1-00 kubeadm=1.19.1-00 kubectl=1.19.1-00 kubernetes-cni=0.8.7-00")
        # Lock current version
        oscmd("sudo apt-mark hold kubelet kubeadm kubectl")
        oscmd("sudo systemctl enable docker.service")
        # May need to turn off firewall
        # May need to add to /etc/docker/daemon.json --> "exec-opts": ["native.cgroupdriver=systemd"],
        oscmd("sudo kubeadm init --ignore-preflight-errors=all")
        
        oscmd("mkdir -p $HOME/.kube")
        
        oscmd("sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config")
        oscmd("sudo chown $(id -u):$(id -g) $HOME/.kube/config")
         
        oscmd("kubectl taint nodes --all node-role.kubernetes.io/master-")
        
        oscmd("sudo sysctl net.bridge.bridge-nf-call-iptables=1")
        # oscmd("kubectl apply -f \"https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')&env.WEAVE_MTU=1500\"")
        oscmd("kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s-1.11.yaml")
        
        gstr = "source <(kubectl completion bash)"
        if oscmd('grep "{}" ~/.bashrc'.format(gstr)) != 0:
            oscmd('echo "{}" >> ~/.bashrc'.format(gstr))
        
        IP = cmd0("kubectl get nodes -o json|jq -r '.items[].status.addresses[] | select( .type | test(\"InternalIP\")) | .address'")
        
        if oscmd("grep meep-docker-registry /etc/hosts") != 0: 
            oscmd("sudo sh -c 'echo \"{}    meep-docker-registry\" >> /etc/hosts'".format("127.0.0.1"))
         
        # Add K8s CA to list of trusted CAs
        fn="/usr/local/share/ca-certificates/kubernetes-ca.crt"
        if not os.path.isfile(fn):
            oscmd("sudo cp /etc/kubernetes/pki/ca.crt {}".format(fn))
            oscmd("sudo chmod 644 {}".format(fn))
            oscmd("sudo update-ca-certificates")
        # # Add the network add-on    
        # oscmd("kubectl apply -f https://docs.projectcalico.org/v3.14/manifests/calico.yaml")
        # Restart docker daemon
        setupK8sGPU()
        
        oscmd("sudo systemctl restart docker")  

    return 0

def setupK3s(cnf):
    calico = True
    entry = input("Set up kubernetes (k3s)? [y/N] ") or "n"
    if entry in ['Y', 'y']:
        kubedn = f"{os.environ['HOME']}/.kube"
        kubefn = kubedn + "/config"
        if not calico:
            oscmd("curl -sfL https://get.k3s.io | sh -s - --docker")
                # NEW FOR K3S with Calico
        else:
            oscmd('curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE="644" INSTALL_K3S_EXEC="--flannel-backend=none --cluster-cidr=192.168.0.0/16 --disable-network-policy --disable=traefik" sh -')
        if not os.path.exists(kubedn): os.mkdir(kubedn)
        # oscmd(f"test -d {kubedn} || mkdir {kubedn}")
        oscmd(f"sudo cp /etc/rancher/k3s/k3s.yaml {kubefn}")
        oscmd(f"sudo chown jblake1 {kubefn};sudo chgrp jblake1 {kubefn};chmod 0600 {kubefn}")
        os.environ['KUBECONFIG'] = kubefn
        oscmd("kubectl get nodes")
        if calico:
            oscmd("kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.25.0/manifests/tigera-operator.yaml")
            oscmd("kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.25.0/manifests/custom-resources.yaml")

        # oscmd("watch kubectl get pods --all-namespaces")
        
        IP = cmd0("kubectl get nodes -o json|jq -r '.items[].status.addresses[] | select( .type | test(\"InternalIP\")) | .address'")
        print(f'Master IP={IP}')

    return 0


def setupK8sGPU():
        entry = input("Enable NVIDIA GPU in Kubernetes? [y/N] ") or "n"
        if entry in ['Y','y']:
            oscmd("kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/1.0.0-beta4/nvidia-device-plugin.yml")
            cmd_all('bash -c "grep default-runtime /etc/docker/daemon.json >/dev/null|| jq \'. += {\\"default-runtime\\":\\"nvidia\\"}\' < /etc/docker/daemon.json >newdaemon.json"')

def setupHelm(cnf):
    entry = input("Set up helm? [y/N] ") or "n"
    if entry in ['Y','y']:
        return oscmd("sudo snap install helm --channel=3.3/stable --classic")
    return 0

def installAdvantEDGE(cnf):
    entry = input("Install AdvantEDGE? [y/N] ") or "n"
    if entry not in ['Y','y']: return 0
    mconsole("Installing AdvantEDGE")
    retcode = 0
    ''' Check configuration '''
    if 'ADVANTEDGEDIR' not in cnf:
        mconsole("ADVANTEDGEDIR not set in configuration",level="ERROR")
        return -1
    ad_dir = cnf['ADVANTEDGEDIR']
    if os.path.isdir(ad_dir):
        mconsole("ADVANTEDGEDIR already exists: {}".format(ad_dir),level="ERROR")
        retcode = -2
        entry = input("Delete and reinstall AdvantEDGE? [y/N] ") or "n"
        if entry in ['Y','y']:
            entry = input("Are you sure? Type yes to confirm: ") or "n"
            if entry in ['Yes','yes']:
                retcode = 0
                mconsole("Removing {}".format(ad_dir))
                shutil.rmtree(ad_dir)
  
    ''' Clone AdvantEDGE '''
    if retcode == 0:
        cmdstr = "git clone {} {}".format(cnf['ADVANTEDGEGIT'],cnf['ADVANTEDGEDIR'])
        if oscmd(cmdstr) != 0:
            mconsole("Could not clone: {}".format(cmdstr),level="ERROR")
            return -3
    else:
        retcode = 0
    return retcode

