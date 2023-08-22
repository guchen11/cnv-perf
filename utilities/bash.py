import subprocess


def execute_local_linux_command_base(command):
    """
    Basic linux bash command
    """
    print(command)
    # Execute the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Check the command's return code
    if result.returncode == 0:
        # Command executed successfully
        output = result.stdout
        print(output)
        return output.strip()
    else:
        # Command encountered an error
        error_message = result.stderr
        print(f"Error executing command: {error_message}")


def deploy_test_at_grafana(test_name):
    command = f"sshpass -p 100yard- ssh -p 22000 -o StrictHostKeyChecking=no fedora@10.46.41.94 sh import_test_promdb.sh {test_name}"
    execute_local_linux_command_base(command)


def scp_promdb_to_grafana(test_name):
    command = f"sshpass -p 100yard- scp -P 22000 {test_name}.tar.gz fedora@10.46.41.94:/home/fedora"
    execute_local_linux_command_base(command)
