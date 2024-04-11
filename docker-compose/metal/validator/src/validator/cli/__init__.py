# SPDX-FileCopyrightText: 2024-present Sunil Thaha <sthaha@redhat.com>
#
# SPDX-License-Identifier: APACHE-2.0
import click

from validator.__about__ import __version__

class Remote:
    def __init__(self, ip, key, user):
        self.ip = ip
        self.key = key
        self.user = user

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
@click.option("--key", "-i", default="~/.ssh/id_rsa", type=click.Path())
@click.option("--user", "-u", default="fedora", type=str)
@click.pass_context
def remote(ctx: click.Context, ip: str, key: str, user: str):
    click.echo(f"remote: {ip} with key {key} as {user}")
    ctx.obj = Remote(ip, key, user)

@remote.command()
@pass_remote
def stress(remote: Remote):
    click.echo(f"stress: run stress on {remote.ip}")
