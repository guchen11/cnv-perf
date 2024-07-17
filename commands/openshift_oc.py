import json
import time
import click
from utilities import files_access, oc
from utilities.bash import execute_local_linux_command_base
from commands.virtctl import run_virtctl


def create_debug_pod():
    template = files_access.load_template("utilities/manifests/debug-pod.json")
    template_str = json.dumps(template)
    command = f"echo '{template_str}' | oc create -f -"
    execute_local_linux_command_base(command)
    time.sleep(3)
    command = "oc exec -it my-debug-pod-automation -- /bin/bash -c \"yum install sshpass -y\""
    execute_local_linux_command_base(command)


def delete_debug_pod():
    command = "oc delete po my-debug-pod-automation"
    execute_local_linux_command_base(command)


@click.group()
def openshift_oc_module():
    pass


CONTEXT_SETTINGS = dict(max_content_width=120)

command_help = """
    get all windows boot time and data_source.

    Example: poetry run python main.py openshift-oc-module oc-get-windows-boot-time"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
def oc_get_windows_boot_time():
    # Execute the command
    create_debug_pod()
    command = ('oc get vmis -o json | jq -r \'.items[] | select(.metadata.name | startswith("win")) | '
               '.status.interfaces[0].ipAddress\' | xargs -I {} oc exec -i my-debug-pod-automation -- /bin/bash -c "echo {}; '
               'sshpass -p \'Heslo123\' ssh -o StrictHostKeyChecking=no Administrator@{} \'systeminfo\' | grep \'Boot '
               'Time\'"')
    execute_local_linux_command_base(command)
    delete_debug_pod()


command_help = """
    get templates and data_source.

    Example: poetry run python main.py openshift-oc-module oc-get-templates-and-data-source"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
def oc_get_templates_and_data_source():
    # Execute the command
    command = "/usr/local/bin/oc -n openshift get template -l template.kubevirt.io/type=base -o jsonpath=\'{range " \
              ".items[*]}{@.metadata.name}{\"\\t\"}{@.parameters[?(@.name==\"DATA_SOURCE_NAME\")].value}{\"\\n\"}\'"
    execute_local_linux_command_base(command)


command_help = """
    get the vms spread on the nodes.

    Example: poetry run python main.py openshift-oc-module oc_get_vms_node_spread"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
def oc_get_vms_node_spread():
    # Execute the command
    command = "for node in $(oc get nodes | grep -v master | grep -v NAME | awk '{print $1}'); do  echo $node ; oc " \
              "get vmi | grep -i $node | wc -l ; done"
    execute_local_linux_command_base(command)


def oc_create_vm_golden_image_base(name, template, data_source, cloud_user_password, namespace):
    """
    Basic golden image creation command
    """
    # Execute the command

    command = f'/usr/local/bin/oc process  -n openshift {template} -p NAME=\"{name}\" DATA_SOURCE_NAME=\"{data_source}\" ' \
              f'CLOUD_USER_PASSWORD=\"{cloud_user_password}\" ' \
              f'DATA_SOURCE_NAMESPACE=\"openshift-virtualization-os-images\"  | oc -n {namespace} create -f -'
    execute_local_linux_command_base(command)


command_help = """
    Create vm from golden image.g

    Example: poetry run python main.py openshift-oc-module oc-create-vm-golden-image --name fedora-test-1 --template fedora-desktop-tiny 
    --cloud_user_password 100yard- --data_source fedora --namespace scale-test"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--name', help=click.style('set VM name', fg='magenta'))
@click.option('--template', help=click.style('set template name', fg='magenta'))
@click.option('--cloud_user_password', help=click.style('set cloud user password', fg='magenta'))
@click.option('--data_source', help=click.style('get data source name of the image', fg='magenta'))
@click.option('--namespace', help=click.style('set namespace for the VM', fg='magenta'))
def oc_create_vm_golden_image(name, template, data_source, cloud_user_password, namespace):
    oc_create_vm_golden_image_base(name, template, data_source, cloud_user_password, namespace)


command_help = """
    Create vm range from golden image.

    Example: poetry run python main.py openshift-oc-module oc-create-vm-golden-image-range --name fedora-test 
    --template fedora-desktop-tiny --sleep 0 --cloud-user-password 100yard- --data_source fedora --namespace 
    scale-test --start 1 --end 2 --running True"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--name', help=click.style('set VM name', fg='magenta'))
@click.option('--template', help=click.style('set template name', fg='magenta'))
@click.option('--cloud_user_password', help=click.style('set cloud user password', fg='magenta'))
@click.option('--data_source', help=click.style('get data source name of the image', fg='magenta'))
@click.option('--namespace', help=click.style('set namespace for the VM', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for VM creation', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for VM creation', fg='magenta'))
@click.option('--sleep', type=int, help=click.style('sleep between actions', fg='magenta'))
@click.option('--running', type=bool, help=click.style('True if to run the VMS', fg='magenta'))
def oc_create_vm_golden_image_range(name, template, data_source, cloud_user_password, namespace, start, end, sleep,
                                    running):
    for i in range(start, end + 1):
        VM_NAME = f"{name}-{i}"
        oc_create_vm_golden_image_base(VM_NAME, template, data_source, cloud_user_password, namespace)
        time.sleep(sleep)
        if running:
            click.echo(run_virtctl(['start', VM_NAME]))
            time.sleep(sleep)


command_help: str = """
    Attach or detach pvc in the given range to VM.

    Example: attach-detach-pcv-vm --vm_name rhel9-server --namespace default --op add --prefix pvc-test- --start 1 --end 2 --sleep 0 
    This will attach PVCs from 'pvc-test-1' to 'pvc-test-2'.
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--vm_name', help=click.style('VM names', fg='magenta'))
@click.option('--namespace', help=click.style('Namespace for VM creation', fg='magenta'))
@click.option('--op', help=click.style('operation on the vm', fg='magenta'))
@click.option('--prefix', help=click.style('Prefix for PVC names', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for PVC', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for PVC', fg='magenta'))
@click.option('--sleep', type=int, help=click.style('sleep between PVC attach', fg='magenta'))
def attach_detach_pcv_vm(vm_name, namespace, op, prefix, start, end, sleep):
    for i in range(start, end + 1):
        template = files_access.load_template("utilities/manifests/add_pvc_to_vm.json")
        template_str = json.dumps(template)
        modified_template = template_str.replace("{{PVC_NAME}}", f'{prefix}{i}')
        modified_template = json.loads(modified_template)
        template_str = json.dumps(modified_template)
        modified_template = template_str.replace("{{OP}}", f'{op}')
        modified_template = json.loads(modified_template)
        command = f"oc patch vm {vm_name} -n {namespace} --type='json' -p='{modified_template}'"
        execute_local_linux_command_base(command)
        time.sleep(sleep)


command_help: str = """
    Set pvc interface in the given range.

    Example: set-pvc-interface --vm_name rhel9-server --namespace default --interface virtio --prefix pvc-test- --start 1 --end 2 --sleep 0 
    This will attach PVCs from 'pvc-test-1' to 'pvc-test-2'.
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--vm_name', help=click.style('VM names', fg='magenta'))
@click.option('--namespace', help=click.style('Namespace for VM', fg='magenta'))
@click.option('--interface', help=click.style('Interface of the pvc', fg='magenta'))
@click.option('--prefix', help=click.style('Prefix for PVC names', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for PVC', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for PVC', fg='magenta'))
@click.option('--sleep', type=int, help=click.style('sleep between PVC attach', fg='magenta'))
def set_pvc_interface(vm_name, namespace, interface, prefix, start, end, sleep):
    for i in range(start, end + 1):
        template = files_access.load_template("utilities/manifests/set_pvc_interface.json")
        template_str = json.dumps(template)
        modified_template = template_str.replace("{{PVC_NAME}}", f'{prefix}{i}')
        modified_template = json.loads(modified_template)
        template_str = json.dumps(modified_template)
        modified_template = template_str.replace("{{INTERFACE}}", f'{interface}')
        modified_template = json.loads(modified_template)
        command = f"oc patch vm {vm_name} -n {namespace} --type='json' -p='{modified_template}'"
        execute_local_linux_command_base(command)
        time.sleep(sleep)


command_help: str = """
    Create or delete basic NNCPs on each worker node 

    Example: create-delete-nncp --op create --start 1 --end 1 --sleep 0 --vlan True
    This will create NodeNetworkConfigurationPolicy from 'br-scale-1' to 'br-scale-2'.
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--op', help=click.style('operation for NNCPs', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for NNCPs', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for NNCPs', fg='magenta'))
@click.option('--sleep', type=int, help=click.style('sleep between NNCPs attach', fg='magenta'))
@click.option('--vlan', type=bool, default=False, help=click.style('True if added vlan connected to node'))
def create_delete_nncp(op, start, end, sleep, vlan):
    for i in range(start, end + 1):
        if (vlan):
            template = files_access.load_template("utilities/manifests/NodeNetworkConfigurationPolicyWithVLAN.json")
        else:
            template = files_access.load_template("utilities/manifests/NodeNetworkConfigurationPolicy.json")
        template_str = json.dumps(template)
        modified_template = template_str.replace("{{index}}", f'{i}')
        command = f"echo '{modified_template}' | oc '{op}' -f -"
        execute_local_linux_command_base(command)
        time.sleep(sleep)
    SuccessfullyConfigured = 0
    if op == 'create':
        while int(SuccessfullyConfigured) != end:
            command = "oc get nncp | grep br-nncp-scale | grep SuccessfullyConfigured | wc -l"
            SuccessfullyConfigured = execute_local_linux_command_base(command)
            print(f"SuccessfullyConfigured: '{SuccessfullyConfigured}', end: '{end}'")
            time.sleep(2)
    else:
        SuccessfullyConfigured = 1
        while int(SuccessfullyConfigured) != 0:
            command = "oc get nncp | grep br-nncp-scale | grep SuccessfullyConfigured | wc -l"
            SuccessfullyConfigured = execute_local_linux_command_base(command)
            print(f"SuccessfullyConfigured: '{SuccessfullyConfigured}', end: 0")
            time.sleep(2)


command_help: str = """
    Empty prometheus data base
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
def empty_prometheus():
    oc.empty_prometheus()


command_help: str = """
    Dump prometheus data base
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.argument('test_name', type=click.STRING, required=True)
def dump_prometheus(test_name):
    oc.dump_prometheus(test_name)


command_help: str = """
    Test maximum pods on a cluster.

    Example: test-maximum-pod --replicas 2000
    This will create 2000 pods.
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--replicas', help=click.style('number of replicas'))
def test_maximum_pod(replicas):
    template = files_access.load_template("utilities/manifests/maxPod.json")
    template["spec"]["replicas"] = int(replicas)
    template_str = json.dumps(template)
    command = f"echo '{template_str}' | oc create -f -"
    execute_local_linux_command_base(command)

    availableReplicas = 0
    command = "oc get deployment pod-scale-test-dep -o json | jq -r '.status.availableReplicas'"
    while int(availableReplicas) != int(replicas):
        time.sleep(1)
        availableReplicas = execute_local_linux_command_base(command)
        if availableReplicas == "null":
            time.sleep(1)
            availableReplicas = 0

    command = f"echo '{template_str}' | oc delete -f -"
    execute_local_linux_command_base(command)


command_help: str = """
    patch_ssh_publickey_vm in the given range to VM.
    
    First make sure you have a secret : oc create secret generic ssh-rsa-pub-guykey --from-file=ssh-publickey=/root/.ssh/public_key.pub
    
    Then add it after the vm created : 
    Example: patch-ssh-publickey-vm --namespace scale-test --prefix centos7-test- --start 1 --end 1 --sleep 0 
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--namespace', help=click.style('Namespace for VM creation'))
@click.option('--prefix', help=click.style('Prefix for PVC names'))
@click.option('--start', type=int, help=click.style('Start index for PVC'))
@click.option('--end', type=int, help=click.style('End index for PVC'))
@click.option('--sleep', type=int, help=click.style('sleep between PVC attach'))
def patch_ssh_publickey_vm(namespace, prefix, start, end, sleep):
    for i in range(start, end + 1):
        template = files_access.load_template("utilities/manifests/sshKeySecret.json")
        template_str = json.dumps(template)
        command = f"oc patch vm '{prefix}{i}' -n {namespace} --type merge -p='{template_str}'"
        execute_local_linux_command_base(command)
        time.sleep(sleep)
