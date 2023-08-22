import click
import paramiko
from utilities.bash import execute_local_linux_command_base
from utilities import bash

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)


@click.group()
def cli_command_module():
    pass


@cli_command_module.command(context_settings=CONTEXT_SETTINGS, help='Execute local linux command')
@click.argument('command', type=click.STRING, required=True)
def execute_local_linux_command(command):
    """
    Execute a command on the local Linux machine.

    This command executes the specified command on the local Linux machine.

    Args:
        command (str): The command to execute.

    Examples:
        execute-local-linux-command "ls -l"
            Execute the 'ls -l' command on the local machine.
    """
    execute_local_linux_command_base(command)


@cli_command_module.command(context_settings=CONTEXT_SETTINGS, help='Execute remote ssh command')
@click.argument('hostname', type=str, required=True)
@click.argument('username', type=str, required=True)
@click.argument('command', type=str, required=True)
def execute_ssh_command(hostname, username, command):
    """
    Execute a command on a remote machine via SSH.

    This command executes the specified command on a remote machine via SSH.

    Args:
        hostname (str): The hostname or IP address of the remote machine.
        username (str): The username to use for SSH authentication.
        command (str): The command to execute on the remote machine.

    Examples:
        execute-ssh-command example.com myuser "ls -l"
            Execute the 'ls -l' command on the remote machine 'example.com' as 'myuser'.
    """
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote host
    client.connect(hostname, username=username)

    # Execute the command
    stdin, stdout, stderr = client.exec_command(command)

    # Print the command output
    print(stdout.read().decode())

    # Close the SSH connection
    client.close()


command_help: str = """
    scp PromDB to Grafana

    Args:
        test_name (str): The name to name the test.

    Examples:
        scp-promdb-to-grafana "scale_up_test_1"
            send the promdb to grafana server.
    """


@cli_command_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.argument('test_name', type=click.STRING, required=True)
def scp_promdb_to_grafana(test_name):
    bash.scp_promdb_to_grafana(test_name)


command_help: str = """
    deploy test at Grafana

    Args:
        test_name (str): The name to name the test.

    Examples:
        deploy-test-at-grafana "scale_up_test_1"
            deploy promdb to grafana server.
    """


@cli_command_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.argument('test_name', type=click.STRING, required=True)
def deploy_test_at_grafana(test_name):
    bash.deploy_test_at_grafana(test_name)
