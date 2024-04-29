import pytest
import yaml
import os

class RemoteParams:
    def __init__(self, ip_addr, user, port, pkey=None, password=None):
        self.ip_addr = ip_addr
        self.user = user
        self.port = port
        self.pkey = pkey
        self.password = password


class PromConnectorParams:
    def __init__(self, endpoint):
        self.endpoint = endpoint


def import_validator():
    # Import validator.yaml
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    config_file = os.path.join(parent_dir, "validator.yaml")
    config = None
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

@pytest.fixture
def remote_params():
    config = import_validator()
    if config:
        remote = config.remote
        ip_addr = remote.get("host", "192.168.122.51")
        user = remote.get("username", "whisper")
        pkey = remote.get("pkey", None)
        port = remote.get("port", 22)
        password = remote.get("password", None)
        return RemoteParams(ip_addr=ip_addr, user=user, pkey=pkey, port=port, password=password)
    else:
        raise FileNotFoundError("failed to open config file for remote params")
    
@pytest.fixture
def prom_params():
    config = import_validator()
    if config:
        prom = config.prometheus
        endpoint = prom.get("url", "http://localhost:9090")
        return PromConnectorParams(endpoint)
    else:
        raise FileNotFoundError("failed to open config file for prom params")
