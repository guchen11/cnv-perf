from utilities.bash import execute_local_linux_command_base


def get_vms_on_node(node):
    command="oc get vmi | grep -i "+node+" |  awk {'print $1'}"
    return execute_local_linux_command_base(command).strip().split('\n')
