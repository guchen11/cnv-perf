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
