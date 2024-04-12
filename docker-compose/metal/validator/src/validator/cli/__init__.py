# SPDX-FileCopyrightText: 2024-present Sunil Thaha <sthaha@redhat.com>
#
# SPDX-License-Identifier: APACHE-2.0
import click
from validator.__about__ import __version__

from validator.stresser.stresser import ssh_vm_instance
from validator.prom_query_validator.prom_query_validator import (
    PromMetricsValidator, deltas_func, percentage_err
)


import statistics

PROM_QUERIES = {
    "vm_process_joules_total": "kepler_process_package_joules_total{pid='{}', job='metal'}",
    "platform_joules_vm": "kepler_node_platform_joules_total{job='vm'}",
    "platform_joules_vm_bm" : "kepler_vm_platform_joules_total{job='metal'}"
}

#TODO: decide where to keep the scripts 


class Remote:
    def __init__(self, ip, script_path, key, user, port, prom_endpoint):
        self.ip = ip
        self.script_path = script_path
        self.key = key
        self.user = user
        self.port = port
        self.prom_endpoint = prom_endpoint

    def __repr__(self):
        return f"<Remote {self.user}@{self.ip}>"


pass_remote = click.make_pass_decorator(Remote)
    

@click.group(
    context_settings={"help_option_names": ["-h", "--help"]}, 
    invoke_without_command=False,
)
@click.version_option(version=__version__, prog_name="validator")
def validator():
    pass

@validator.group()
@click.option("--ip", required=True, type=str)
@click.option(
    "--script-path", "-s", 
    default="~/kepler-model-validation/docker-compose/vm/stressor.sh", 
    type=str,
)
@click.option("--key", "-i", default="~/.ssh/id_rsa", type=click.Path())
@click.option("--user", "-u", default="fedora", type=str)
@click.option("--port", "-p", default=22, type=int)
@click.option("--prom-endpoint", "-e", default="http://localhost:9090", type=str)
@click.pass_context
def remote(ctx: click.Context, ip: str, script_path: str, key: str, user: str, port: int, prom_endpoint: str):
    click.echo(f"remote: {user}@{ip} using {key}")
    ctx.obj = Remote(ip, script_path, key, user, port, prom_endpoint)


@remote.command()
@click.option("--vm-pid", type=str, required=True)
@pass_remote
def stress(remote: Remote, vm_pid: str):

    start_time, end_time  = ssh_vm_instance(
        vm_ip_address=remote.ip,
        username=remote.user,
        script_path=remote.script_path,
        vm_port=remote.port,
        pkey_path=remote.key,
    )

    # from prometheus_api_client.utils import parse_datetime
    # start_time=parse_datetime("2024-04-12 16:27:20.254648")
    # end_time = parse_datetime("2024-04-12 16:28:00.466223")
    click.echo(f"start_time: {start_time}, end_time: {end_time}")


    # TODO: clean up
    # expected_query = PROM_QUERIES["vm_process_joules_total"].format(vm_pid)

    expected_query = "kepler_process_package_joules_total{pid='2093543', job='metal'}"
    actual_query = PROM_QUERIES["platform_joules_vm"]

    prom_validator = PromMetricsValidator(prom_endpoint=remote.prom_endpoint, disable_ssl=True)
    validator_data, validated_data = prom_validator.compare_metrics(
        start_time=start_time, 
        end_time=end_time, 
        expected_query=expected_query, 
        actual_query=actual_query,
    )

    # NOTE: calc
    percentage_error = percentage_err(validator_data, validated_data)
    absolute_error = deltas_func(validator_data, validated_data)
    mae = statistics.mean(absolute_error)
    mape = statistics.mean(percentage_error)

    # TODO: print what the values mean
    click.secho(str(absolute_error), fg='green')
    click.secho(str(percentage_error), fg='blue')
    click.secho("-----------------------------", fg="white")
    click.secho(str(mae), fg="red")
    click.secho(str(mape), fg="red")

