import subprocess
import time
import click
from utilities.oc import get_vms_on_node

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

    Example: hotplug-attach-pcv-to-vm --vm_name rhel9-server --prefix pvc-test- --start 1 --end 2 --sleep 2 
    This will attach PVCs from 'pvc-test-1' to 'pvc-test-2'.
    """


@virtctl_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--vm_name', help='VM names')
@click.option('--prefix', help='Prefix for PVC names')
@click.option('--start', type=int, help='Start index for PVC')
@click.option('--end', type=int, help='End index for PVC')
@click.option('--sleep', type=int, help='sleep between PVC attach')
def hotplug_attach_pcv_to_vm(vm_name, prefix, start, end, sleep):
    error_result = 0
    for i in range(start, end +1):
        pvc_name = f'{prefix}{i}'
        return_code = run_virtctl(['addvolume', vm_name,'--volume-name='+pvc_name, '--persist'])
        if return_code != 0:
            error_result = error_result+1
        time.sleep(sleep)
    print(f'Out of {i-1} actions {error_result} have failed')



CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)
command_help: str = """
    Detach hotplug pvc in the given range to VM.

    Example: hotplug-detach-pcv-to-vm --vm_name rhel9-server --prefix pvc-test- --start 1 --end 2 --sleep 2 
    This will detach PVCs from 'pvc-test-1' to 'pvc-test-2'.
    """


@virtctl_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--vm_name', help='VM names')
@click.option('--prefix', help='Prefix for PVC names')
@click.option('--start', type=int, help='Start index for PVC')
@click.option('--end', type=int, help='End index for PVC')
@click.option('--sleep', type=int, help='sleep between PVC attach')
def hotplug_detach_pcv_to_vm(vm_name, prefix, start, end, sleep):
    error_result = 0
    for i in range(start, end +1):
        pvc_name = f'{prefix}{i}'
        return_code = run_virtctl(['removevolume', vm_name,'--volume-name='+pvc_name, '--persist'])
        if return_code != 0:
            error_result = error_result + 1
        time.sleep(sleep)
    print(f'Out of {i-1} actions {error_result} have failed')

