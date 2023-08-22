import time

from utilities import files_access
from utilities.bash import execute_local_linux_command_base


def get_vms_on_node(node):
    command = "oc get vmi | grep -i " + node + " |  awk {'print $1'}"
    return execute_local_linux_command_base(command).strip().split('\n')


def empty_prometheus():
    count = 0
    while count < 2:
        command = f"oc delete po prometheus-k8s-{count} -n openshift-monitoring"
        execute_local_linux_command_base(command)
        time.sleep(2)
        command = f"oc exec -n openshift-monitoring prometheus-k8s-{count} -- du -sh /prometheus"
        execute_local_linux_command_base(command)
        time.sleep(2)
        count += 1


def dump_prometheus(test_name):
    command = f"mkdir -p {test_name}"
    execute_local_linux_command_base(command)
    time.sleep(2)
    command = f"oc cp -n  openshift-monitoring prometheus-k8s-0:/prometheus -c prometheus  {test_name}"
    execute_local_linux_command_base(command)
    time.sleep(2)
    command = f"tar -czvf {test_name}.tar.gz {test_name}"
    execute_local_linux_command_base(command)
    time.sleep(2)
