# Deploy Magma Orchestrator

Create an Ubuntu VM, take reference from [multipass](docs/multipass.md) docs.

Quick Install:
```bash
sudo bash -c "$(curl -sL https://github.com/jblakley/magma-galaxy/raw/master/deploy-orc8r.sh)"
```

Switch to `magma` user after deployment has finsished:
```bash
sudo su - magma
```

Once all pods are ready, setup NMS login:
```bash
cd ~/magma-galaxy
ansible-playbook config-orc8r.yml
```

You can get your `rootCA.pem` file from the following location:
```bash
cat ~/magma-galaxy/secrets/rootCA.pem
```
The latest working version of this is derived from commit `996d59798cff24781030fd5427c8e0082e25b8e5`
