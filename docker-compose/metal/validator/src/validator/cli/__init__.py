# SPDX-FileCopyrightText: 2024-present Sunil Thaha <sthaha@redhat.com>
#
# SPDX-License-Identifier: APACHE-2.0
import click
from click.testing import CliRunner
from validator.__about__ import __version__
from validator.stresser.stresser import ssh_vm_instance
from validator.prom_query_validator.prom_query_validator import PromMetricsValidator, deltas_func, percentage_err


import statistics

def output(message):
    click.echo(message)


PROM_QUERIES = {
    "package_joules_qemu_system_x86": "kepler_process_package_joules_total{command='qemu-system-x86'}",
    "platform_joules_vm": "kepler_node_platform_joules_total{job='vm'}",
    "platform_joules_vm_bm" : "kepler_vm_platform_joules_total{job='metal'}"
}


class Remote:
    def __init__(self, ip, script_path, key, user, port, prom_endpoint, disable_ssl):
        self.ip = ip
        self.script_path = script_path
        self.key = key
        self.user = user
        self.port = port
        self.prom_endpoint = prom_endpoint
        self.disable_ssl = disable_ssl

    def __repr__(self):
        return f"<Remote {self.user}@{self.ip}>"


pass_remote = click.make_pass_decorator(Remote)
    
class StresserTimeStamps:
    def __init__(self, start_time, end_time, duration):
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
    def __repr__(self):
        return f"<Time Stamps {self.start_time}, {self.end_time}, {self.duration}>"

pass_stressertimestamps = click.make_pass_decorator(StresserTimeStamps)


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]}, 
    invoke_without_command=False,
)
@click.version_option(version=__version__, prog_name="validator")
@click.pass_context
def validator(ctx: click.Context):
    ctx.ensure_object(dict)

@validator.group()
@click.option("--ip", required=True, type=str)
@click.option("--script-path", "-s", required=True, type=click.Path())
@click.option("--key", "-i", default="~/.ssh/id_rsa", type=click.Path())
@click.option("--user", "-u", default="fedora", type=str)
@click.option("--port", "-p", default=22, type=int)
@click.option("--prom-endpoint", "-e", default="http://localhost:9090", type=str)
@click.option("--disable-ssl", "-d", default=True, type=bool)
@click.pass_context
def remote(ctx: click.Context, ip: str, script_path: str, key: str, user: str, port: int, prom_endpoint: str, disable_ssl: bool):
    click.echo(f"remote: {ip} with key {key} as {user}")
    ctx.obj["remote"] = Remote(ip, script_path, key, user, port, prom_endpoint, disable_ssl)


@remote.command()
@click.pass_context
def stress(ctx: click.Context):
    remote = ctx.obj['remote']
    click.echo(remote.port)
    if remote.key == "":
        start_time, end_time, duration = ssh_vm_instance(output, vm_ip_address=remote.ip, username=remote.user, script_path=remote.script_path, vm_port=remote.port, private_ssh_key=remote.key)
    else:
        start_time, end_time, duration = ssh_vm_instance(output, vm_ip_address=remote.ip, username=remote.user, script_path=remote.script_path, vm_port=remote.port)
    ctx.obj["stressertimestamps"] = StresserTimeStamps(start_time, end_time, duration)
    click.echo(ctx.obj["stressertimestamps"])


@remote.command()
@click.option("--true-query", "-t", required=True, type=click.Choice(PROM_QUERIES.keys()), default="package_joules_qemu_system_x86")
@click.option("--pred-query", "-p", required=True, type=click.Choice(PROM_QUERIES.keys()), default="platform_joules_vm")
@pass_remote
@pass_stressertimestamps
def validate(true_query: str, pred_query: str, remote: Remote, stressertimestamps: StresserTimeStamps):
    validator_query = PROM_QUERIES[true_query]
    validated_query = PROM_QUERIES[pred_query]
    prom_validator = PromMetricsValidator(prom_endpoint=remote.prom_endpoint, disable_ssl=remote.disable_ssl)
    validator_data, validated_data = prom_validator.retrieve_energy_metrics_with_queries(start_time=stressertimestamps.start_time, end_time=stressertimestamps.end_time, validator_query=validator_query, validated_query=validated_query)
    percentage_error = percentage_err(validator_data, validated_data)
    absolute_error = deltas_func(validator_data, validated_data)
    mae = statistics.mean(absolute_error)
    mape = statistics.mean(percentage_error)

    click.secho(str(absolute_error), fg='green')
    click.secho(str(percentage_error), fg='blue')
    click.secho("-----------------------------", fg="white")
    click.secho(str(mae), fg="red")
    click.secho(str(mape), fg="orange")


if __name__ == "__main__":
    runner = CliRunner()

    # Testing greet command
    result_base = runner.invoke(validator)
    result_remote = runner.invoke(validator, ["remote", "--ip", "192.168.122.51", "--script-path", './Documents/kepler-model-validation/docker-compose/vm/stressor.sh'])