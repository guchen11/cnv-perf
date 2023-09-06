import subprocess
import time
import click
from utilities.oc import get_vms_on_node
from utilities.bash import execute_local_linux_command_base, execute_local_linux_command_base_silent


def run_virtctl(args):
    command = ['virtctl'] + args
    print(command)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        output = result.stdout
        print(output)
        return result.returncode
    else:
        # Handle error case
        output = result.stderr
        print("Error: " + output)

        return result.returncode


@click.group()
def virtctl_module():
    pass


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)
command_help: str = """
    Stop VMs in the given range.

    Example: stop-vms --prefix vm- --start 1 --end 5 --sleep 1
    This will stop VMs from 'vm-1' to 'vm-5'.
    """


@virtctl_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--prefix', help='Prefix for VM names')
@click.option('--start', type=int, help='Start index for VMs')
@click.option('--end', type=int, help='End index for VMs')
@click.option('--sleep', type=int, help='sleep between VMs')
def stop_vms(prefix, start, end, sleep):
    for i in range(start, end + 1):
        vm_name = f'{prefix}{i}'
        output = run_virtctl(['stop', vm_name])
        time.sleep(sleep)
        print(output)


command_help: str = """
    Start VMs in the given range.

    Example: start-vms --prefix cirros-vm- --start 1 --end 5 --sleep 1
    This will start VMs from 'vm-1' to 'vm-5'.
    """


@virtctl_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--prefix', help='Prefix for VM names')
@click.option('--start', type=int, help='Start index for VMs')
@click.option('--end', type=int, help='End index for VMs')
@click.option('--sleep', type=int, help='sleep between VMs')
def start_vms(prefix, start, end, sleep):
    for i in range(start, end + 1):
        vm_name = f'{prefix}{i}'
        output = run_virtctl(['start', vm_name])
        time.sleep(sleep)
        print(output)


command_help: str = """
    Migrate all VMS from a node.

    Example: migrate_node --node worker000-740xd --sleep 1
    This will migrate all vms from the node with sleep of 1
    """


@virtctl_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--node', help='Node t migrate')
@click.option('--sleep', type=int, help='sleep between VMs')
def migrate_node(node, sleep):
    vms_list = get_vms_on_node(node)
    for vm in vms_list:
        run_virtctl(['migrate', vm])
        time.sleep(sleep)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)
command_help: str = """
    Attach hotplug pvc in the given range to VM.

    Example: hotplug-attach-pcv-to-vm --vm_name rhel9-server --prefix pvc-test- --start 1 --end 2 --final_attached_disk 2 --vm_up True --sleep 2 
    This will attach PVCs from 'pvc-test-1' to 'pvc-test-2'.
    """


@virtctl_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--vm_name', help='VM names')
@click.option('--prefix', help='Prefix for PVC names')
@click.option('--start', type=int, help='Start index for PVC')
@click.option('--end', type=int, help='End index for PVC')
@click.option('--final_attached_disk', type=int, help='expected final disk')
@click.option('--vm_up', help='write True if vm is up')
@click.option('--sleep', type=int, help='sleep between PVC attach')
def hotplug_attach_pcv_to_vm(vm_name, prefix, start, end, final_attached_disk, vm_up, sleep):
    error_result = 0
    start_time = time.time()
    if vm_up == "True":
        current_attached_disk = execute_local_linux_command_base(
            "sshpass -p '100yard-' ssh -o StrictHostKeyChecking=no -p 31302 cloud-user@console-openshift-console.apps.guchen734.alias.bos.scalelab.redhat.com 'lsblk | grep -c 1G'")
    virt_handler_logs_start = execute_local_linux_command_base("oc get po -n openshift-cnv | grep \"virt-handler-\" |  awk '{print $1}' |  xargs -I index sh -c 'oc logs index -c virt-handler -n openshift-cnv | grep -c \"Synchronizing the VirtualMachineInstance failed.\"'")
    for i in range(start, end + 1):
        pvc_name = f'{prefix}{i}'
        return_code = run_virtctl(['addvolume', vm_name, '--volume-name=' + pvc_name, '--persist'])
        if return_code != 0:
            error_result = error_result + 1
        while return_code != 0:
            time.sleep(2)
            return_code = run_virtctl(['addvolume', vm_name, '--volume-name=' + pvc_name, '--persist'])
        time.sleep(sleep)
    print(f'Out of {end + 1 - start} actions {error_result} have failed')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Add volume command time : {elapsed_time}")
    if vm_up == "True":
        print(f"final_attached_disk : {final_attached_disk}")
        print(f"current_attached_disk : {current_attached_disk}")
        if current_attached_disk != "":
            index = 0
            while int(current_attached_disk) != final_attached_disk:
                time.sleep(1)
                current_attached_disk = execute_local_linux_command_base_silent(
                    "sshpass -p '100yard-' ssh -o StrictHostKeyChecking=no -p 31302 cloud-user@console-openshift-console.apps.guchen734.alias.bos.scalelab.redhat.com 'lsblk | grep -c 1G'")
                if current_attached_disk == "":
                    break
                index = index + 1
                if index == 600:
                    print(f"Timeout on lsblk")
                    break

    print(f"virt_handler logs start on the test :")
    print(virt_handler_logs_start)
    print(f"virt_handler logs now on the test :")
    execute_local_linux_command_base(
        "oc get po -n openshift-cnv | grep \"virt-handler-\" |  awk '{print $1}' |  xargs -I index sh -c 'oc logs index -c virt-handler -n openshift-cnv | grep -c \"Synchronizing the VirtualMachineInstance failed.\"'")


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)
command_help: str = """
    Detach hotplug pvc in the given range to VM.

    Example: hotplug-detach-pcv-to-vm --vm_name rhel9-server --prefix pvc-test- --start 1 --end 2 --final_attached_disk 2 --vm_up True --sleep 2 
    This will detach PVCs from 'pvc-test-1' to 'pvc-test-2'.
    """


@virtctl_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--vm_name', help='VM names')
@click.option('--prefix', help='Prefix for PVC names')
@click.option('--start', type=int, help='Start index for PVC')
@click.option('--end', type=int, help='End index for PVC')
@click.option('--vm_up', help='write True if vm is up')
@click.option('--sleep', type=int, help='sleep between PVC attach')
@click.option('--final_attached_disk', type=int, help='expected final disk')
def hotplug_detach_pcv_to_vm(vm_name, prefix, start, end, final_attached_disk, vm_up, sleep):
    error_result = 0
    start_time = time.time()
    if vm_up == "True":
        current_attached_disk = execute_local_linux_command_base(
            "sshpass -p '100yard-' ssh -o StrictHostKeyChecking=no -p 31302 cloud-user@console-openshift-console.apps.guchen734.alias.bos.scalelab.redhat.com 'lsblk | grep -c 1G'")
    virt_handler_logs_start = execute_local_linux_command_base("oc get po -n openshift-cnv | grep \"virt-handler-\" |  awk '{print $1}' |  xargs -I index sh -c 'oc logs index -c virt-handler -n openshift-cnv | grep -c \"Synchronizing the VirtualMachineInstance failed.\"'")
    for i in range(start, end + 1):
        pvc_name = f'{prefix}{i}'
        return_code = run_virtctl(['removevolume', vm_name, '--volume-name=' + pvc_name, '--persist'])
        if return_code != 0:
            error_result = error_result + 1
        while return_code != 0:
            time.sleep(2)
            return_code = run_virtctl(['removevolume', vm_name, '--volume-name=' + pvc_name, '--persist'])
        time.sleep(sleep)
    print(f'Out of {end +1 - start} actions {error_result} have failed')
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Remove volume command time : {elapsed_time}")
    if vm_up == "True":
        print(f"final_attached_disk : {final_attached_disk}")
        print(f"current_attached_disk : {current_attached_disk}")
        if current_attached_disk != "":
            index = 0
            while int(current_attached_disk) != final_attached_disk:
                time.sleep(1)
                current_attached_disk = execute_local_linux_command_base_silent(
                    "sshpass -p '100yard-' ssh -o StrictHostKeyChecking=no -p 31302 cloud-user@console-openshift-console.apps.guchen734.alias.bos.scalelab.redhat.com 'lsblk | grep -c 1G'")
                if current_attached_disk == "":
                    break
                index = index+1
                if index == 600:
                    print(f"Timeout on lsblk")
                    break

    print(f"virt_handler logs start on the test :")
    print(virt_handler_logs_start)
    print(f"virt_handler logs now on the test :")
    execute_local_linux_command_base("oc get po -n openshift-cnv | grep \"virt-handler-\" |  awk '{print $1}' |  xargs -I index sh -c 'oc logs index -c virt-handler -n openshift-cnv | grep -c \"Synchronizing the VirtualMachineInstance failed.\"'")


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)
command_help: str = """
    test_vm_start_time 

    Example: test-vm-start-time --vm_name rhel9-server --final_attached_disk 254
    """


@virtctl_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--vm_name', help='VM names')
@click.option('--final_attached_disk', type=int, help='expected final disk')
def test_vm_start_time(vm_name, final_attached_disk):
    virt_handler_logs_start = execute_local_linux_command_base("oc get po -n openshift-cnv | grep \"virt-handler-\" |  awk '{print $1}' |  xargs -I index sh -c 'oc logs index -c virt-handler -n openshift-cnv | grep -c \"Synchronizing the VirtualMachineInstance failed.\"'")
    execute_local_linux_command_base(f"virtctl start {vm_name}")
    current_attached_disk = execute_local_linux_command_base(
        "sshpass -p '100yard-' ssh -o StrictHostKeyChecking=no -p 31302 cloud-user@console-openshift-console.apps.guchen734.alias.bos.scalelab.redhat.com 'lsblk | grep -c 1G'")
    while current_attached_disk == "error":
        time.sleep(1)
        current_attached_disk = execute_local_linux_command_base(
            "sshpass -p '100yard-' ssh -o StrictHostKeyChecking=no -p 31302 cloud-user@console-openshift-console.apps.guchen734.alias.bos.scalelab.redhat.com 'lsblk | grep -c 1G'")
    while int(current_attached_disk) != final_attached_disk:
        time.sleep(1)
        current_attached_disk = execute_local_linux_command_base(
            "sshpass -p '100yard-' ssh -o StrictHostKeyChecking=no -p 31302 cloud-user@console-openshift-console.apps.guchen734.alias.bos.scalelab.redhat.com 'lsblk | grep -c 1G'")

    print(f"virt_handler logs start on the test :")
    print(virt_handler_logs_start)
    print(f"virt_handler logs now on the test :")
    execute_local_linux_command_base("oc get po -n openshift-cnv | grep \"virt-handler-\" |  awk '{print $1}' |  xargs -I index sh -c 'oc logs index -c virt-handler -n openshift-cnv | grep -c \"Synchronizing the VirtualMachineInstance failed.\"'")



