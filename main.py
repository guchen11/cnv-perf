import sys
import click
from commands.cli_command import cli_command_module
from commands.virtctl import virtctl_module
from commands.openshift_oc import openshift_oc_module
from commands.openshift_api import openshift_api_module
from commands.tests import tests_module
import time
from utilities import bash
from utilities import files_access, oc


class Timer:

    def __init__(self, description: str) -> None:
        self.description = description
        oc.execute_local_linux_command_base("echo Star time : `date`")

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):

        oc.execute_local_linux_command_base("echo End time : `date`")
        self.end = time.time()
        elapsed_time = self.end - self.start
        print(f"{self.description}: {elapsed_time}")
        self.test_constractor = files_access.get_json_value("utilities/manifests/perf_param.json", "test_constractor")
        self.performance_test = files_access.get_json_value("utilities/manifests/perf_param.json", "performance_test")
        self.test_name = files_access.get_json_value("utilities/manifests/perf_param.json", "test_name")
        if self.performance_test == "True":
            # If we are inside the test constractor function, switch it off so we will know next command is the test
            if self.test_constractor == "True":
                oc.empty_prometheus()
                files_access.update_json_value("utilities/manifests/perf_param.json", "test_constractor", "False")
            else:
                # If we are inside a performance test execution, switch it off since we have finished
                time.sleep(10)
                oc.dump_prometheus(self.test_name)
                bash.scp_promdb_to_grafana(self.test_name)
                bash.deploy_test_at_grafana(self.test_name)
                files_access.update_json_value("utilities/manifests/perf_param.json", "test_name", "currentTest")
                files_access.update_json_value("utilities/manifests/perf_param.json", "performance_test", "False")
                files_access.update_json_value("utilities/manifests/perf_param.json", "test_name", "currentTest")
            oc.execute_local_linux_command_base("cat utilities/manifests/perf_param.json")


# Context settings for Click commands
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)

command_help: str = """
    Performance test constructor load run

    Args:
        test_name (str): The name to name the test.

    Examples:
        test_constructor "scale_up_test_1"
    """


@click.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.argument('test_name', type=click.STRING, required=True)
def test_constructor(test_name):
    files_access.update_json_value("utilities/manifests/perf_param.json", "performance_test", "True")
    files_access.update_json_value("utilities/manifests/perf_param.json", "test_constractor", "True")
    files_access.update_json_value("utilities/manifests/perf_param.json", "test_name", test_name)


command_help: str = """
    Set test name

    Args:
        test_name (str): The name to name the test.

    Examples:
        set-test-name "scale_up_test_1"
    """


@click.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.argument('test_name', type=click.STRING, required=True)
def set_test_name(test_name):
    files_access.update_json_value("utilities/manifests/perf_param.json", "test_name", test_name)


command_help: str = """
    Performance test destructor

    Examples:
        test-destructor "scale_up_test_1"
    """


@click.command(context_settings=CONTEXT_SETTINGS, help=command_help)
def test_destructor():
    files_access.update_json_value("utilities/manifests/perf_param.json", "performance_test", "False")
    files_access.update_json_value("utilities/manifests/perf_param.json", "test_constractor", "False")
    files_access.update_json_value("utilities/manifests/perf_param.json", "test_name", "currentTest")


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """A command-line tool with multiple functions."""
    pass


cli.add_command(set_test_name)
cli.add_command(test_constructor)
cli.add_command(test_destructor)
cli.add_command(openshift_api_module)  # type: ignore
cli.add_command(virtctl_module)  # type: ignore
cli.add_command(openshift_oc_module)  # type: ignore
cli.add_command(cli_command_module)  # type: ignore
cli.add_command(tests_module)


def print_module_commands(module):
    # ANSI color codes
    module_color = "\033[1;33m"  # Yellow
    command_color = "\033[1;35m"  # Magenta
    reset_color = "\033[0m"  # Reset color

    first_line = True

    for command_name, command_obj in module.commands.items():
        if first_line:
            click.echo(f"{module_color}Module: {module.name}{reset_color}")
            first_line = False

        click.echo(f"  {command_color}{command_name:<20}{reset_color}")


def print_help():
    """Print help messages for all commands, including child commands."""
    description_color = "\033[1;34m"  # Blue
    click.echo(f"\n{description_color}Available commands and their associated modules:")
    click.echo("=" * 50 + "\n")

    modules = {
        "cli-command-module": cli_command_module,
        "virtctl-module": virtctl_module,
        "openshift-oc-module": openshift_oc_module,
        "openshift-api-module": openshift_api_module,
        "tests-module": tests_module
    }

    for module_name, module in modules.items():
        print_module_commands(module)

if __name__ == '__main__':
    with Timer("Command elapsed time (seconds) :"):
        if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
            print_help()
            # Print all Click commands under main module
            module_color = "\033[1;33m"  # Yellow
            reset_color = "\033[0m"  # Reset color
            command_color = "\033[1;35m"  # Magenta
            all_commands = [cmd.name for cmd in cli.commands.values()]
            click.echo(f"{module_color}Module: main{reset_color}")
            for command in all_commands:
                click.echo(f"  {command_color}{command}{reset_color}")
            description_color = "\033[1;34m"  # Blue
            click.echo(f"{description_color}")
            click.echo("For command help run poetry run python main.py {module} {command} -h")
            click.echo("Example:")
            click.echo("poetry run python main.py openshift-oc-module oc-create-vm-golden-image-range -h")
            click.echo(f"{reset_color}")
        else:
            cli()
