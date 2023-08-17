import click
from commands.cli_command import cli_command_module
from commands.virtctl import virtctl_module
from commands.openshift_oc import openshift_oc_module
from commands.openshift_api import openshift_api_module
import time


class Timer:
    def __init__(self, description: str) -> None:
        self.description = description

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        self.end = time.time()
        elapsed_time = self.end - self.start
        print(f"{self.description}: {elapsed_time}")


# Context settings for Click commands
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """A command-line tool with multiple functions."""
    pass


cli.add_command(openshift_api_module)  # type: ignore
cli.add_command(virtctl_module)  # type: ignore
cli.add_command(openshift_oc_module)  # type: ignore
cli.add_command(cli_command_module)  # type: ignore

if __name__ == '__main__':
    with Timer("Command elapsed time (seconds) :"):
        cli()
