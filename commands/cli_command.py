import click
import paramiko
from utilities.bash import execute_local_linux_command_base

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
