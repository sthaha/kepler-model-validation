import paramiko
import time
from typing import Tuple
from datetime import datetime


class ScriptResult:
    def __init__(self, start_time, end_time, duration):
        self.start_time = start_time
        self.end_time = end_time
        self.output = end_time


class Remote: 
    def __init__(self, ip, script_path, key, user, port, password):
        self.ip = ip
        self.key = key
        self.user = user
        self.port = port
        self.password = password
        self.ssh_client = paramiko.SSHClient()



    def __repr__(self):
        return f"<Remote {self.user}@{self.ip}>"
    
    def run_script(self, script_path):
        pass


def run_script(host, username, script_path, port=22, password=None, pkey_path=None) -> Tuple[datetime, datetime]:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"ssh -> {username}@{host}")
    if pkey_path is not None:
        pkey = paramiko.RSAKey.from_private_key_file(pkey_path)
        ssh_client.connect(hostname=host, port=port, username=username, pkey=pkey)
    else:
        ssh_client.connect(hostname=host, port=port, username=username, password=password)

    print(f"successfully connected to: {username}@{host}. Running stress test ...")

    start_time = time.time()

    _, stdout, stderr = ssh_client.exec_command(script_path)
    exit_status = stdout.channel.recv_exit_status()

    end_time = time.time()

    ssh_client.close()

    if exit_status == 0:
        print("script execution successful")
    else:
        print("script execution failed")
        
    print("logs for stress test:")
    for line in stdout:
        print(line.strip())
    print("stderr output:")
    for line in stderr:
        print(line.strip())

    start_time_datetime = datetime.fromtimestamp(start_time)
    end_time_datetime = datetime.fromtimestamp(end_time)
    return start_time_datetime, end_time_datetime

