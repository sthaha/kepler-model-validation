import paramiko
import time
from typing import Tuple
from datetime import datetime

stressor_command_path = './Documents/kepler-model-validation/docker-compose/vm/stressor.sh'

def ssh_vm_instance(output, vm_ip_address, username, script_path, vm_port=22, password=None, private_ssh_key=None) -> Tuple[datetime, datetime, float]:
    output("connecting to virtual machine via ssh")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=vm_ip_address, port=vm_port, username=username, password=password, pkey=private_ssh_key)
    output(f"successfully connected to: {username}. running stress test")

    start_time = time.time()

    _, stdout, stderr = ssh_client.exec_command(script_path)
    exit_status = stdout.channel.recv_exit_status()

    end_time = time.time()

    ssh_client.close()

    if exit_status == 0:
        output("script execution successful")
    else:
        output("script execution failed")
        
    output("logs for stress test:")
    for line in stdout:
        output(line.strip())
    output("stderr output:")
    for line in stderr:
        output(line.strip())

    duration = end_time - start_time
    start_time_datetime = datetime.fromtimestamp(start_time)
    end_time_datetime = datetime.fromtimestamp(end_time)
    return start_time_datetime, end_time_datetime, duration


if __name__ == "__main__":
    # SSH credentials
    ssh_host_address_to_vm = '192.168.122.51'
    ssh_port = 22
    ssh_username = 'whisper'
    # employ ssh keys to avoid password usage
    #ssh_password = ''
    start_time, end_time, duration = ssh_vm_instance(vm_ip_address=ssh_host_address_to_vm, script_path=stressor_command_path, vm_port=ssh_port, username=ssh_username)
    print(start_time, end_time, duration)

