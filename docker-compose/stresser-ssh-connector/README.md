# Stress-ng Worksuite for Model Validation
A package used to ssh into a user's virtual machine where vm kepler, vm model server, and vm estimator are running and run a series of stress-ng commands to stress the the virtual machine. Used to test the model predicted energy metrics under different cpu conditions.

## How to use
_After installing the package use following import:_ <br>

**from stresser-ssh-connector import ssh_vm_instance**

_The stresser works as follows:_

**start_time, end_time, duration = ssh_vm_instance(vm_ip_address=" your qemu vm ip address ", username=" your virtual machine username ", script_path= " your vm filepath to stress-ng test suite ", vm_port= " your exposed virtual machine port default is 22", password=" your password or None if you login via ssh key ", private_ssh_key=" your ssh key or None if you use RSA or password ")<br>**
