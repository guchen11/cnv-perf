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
                Clone range of DV fom a singe DV.
                Example: poetry run python main.py openshift-oc-module oc-clone-vm --start 2 --end 2 --prefix win10 
                --namespace default --volume_mode Block --sleep 0
                """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--prefix', help=click.style('Prefix for PVC clone', fg='magenta'))
@click.option('--namespace', help=click.style('Namespace for PVC clone', fg='magenta'))
@click.option('--volume_mode', help=click.style('volumeMode for PVC clone, Filesystem or Block', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for PVC clone', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for PVC clone', fg='magenta'))
@click.option('--sleep', type=int, help=click.style('sleep between clones', fg='magenta'))
def oc_clone_vm(prefix, namespace, volume_mode, start, end, sleep):
    template = files_access.load_template("utilities/manifests/clone-vm.json")
    for i in range(start, end + 1):
        VM_NAME = f'{prefix}-{i}'

        template_str = json.dumps(template)
        modified_template = template_str.replace("{{VM_NAME}}", VM_NAME)
        modified_template = json.loads(modified_template)

        template_str = json.dumps(modified_template)
        modified_template = template_str.replace("{{NAMESPACE}}", namespace)
        modified_template = json.loads(modified_template)

        template_str = json.dumps(modified_template)
        modified_template = template_str.replace("{{VOLUME_MODE}}", volume_mode)
        modified_template = json.loads(modified_template)

        command = f"echo '{json.dumps(modified_template)}' | oc create -f -"
        execute_local_linux_command_base(command)

        command = f"oc wait --for=condition=Running VirtualMachine/{VM_NAME}"
        execute_local_linux_command_base(command)

        time.sleep(sleep)


command_help = """
                Clone range of DV from a singe DV.
                Example: poetry run python main.py openshift-oc-module oc-clone-pvc --start 2 --end 2 --source
                win10-1 --prefix win10 --namespace default --sleep 0 --size 70Gi
                """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--prefix', help=click.style('Prefix for PVC clone', fg='magenta'))
@click.option('--source', help=click.style('pvc source for PVC clone', fg='magenta'))
@click.option('--namespace', help=click.style('Namespace for PVC clone', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for PVC clone', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for PVC clone', fg='magenta'))
@click.option('--sleep', type=int, help=click.style('sleep between clones', fg='magenta'))
@click.option('--size', help=click.style('size of the disk clone', fg='magenta'))
def oc_clone_pvc(prefix, source, namespace, start, end, sleep, size):
    template = files_access.load_template("utilities/manifests/clone-pvc.json")
    for i in range(start, end + 1):
        PVC_NAME = f'{prefix}-{i}'

        template_str = json.dumps(template)
        modified_template = template_str.replace("{{PVC_NAME}}", PVC_NAME)
        modified_template = json.loads(modified_template)

        template_str = json.dumps(modified_template)
        modified_template = template_str.replace("{{PVC_SOURCE}}", source)
        modified_template = json.loads(modified_template)

        template_str = json.dumps(modified_template)
        modified_template = template_str.replace("{{namespace}}", namespace)
        modified_template = json.loads(modified_template)

        template_str = json.dumps(modified_template)
        modified_template = template_str.replace("{{size}}", size)
        modified_template = json.loads(modified_template)

        command = f"echo '{json.dumps(modified_template)}' | oc create -n {namespace} -f -"
        execute_local_linux_command_base(command)

        command = f"oc wait --for=condition=Ready datavolume/{PVC_NAME}"
        execute_local_linux_command_base(command)

        time.sleep(sleep)


command_help = """
    delete all windows events.

    Example: poetry run python main.py openshift-oc-module oc-delete-windows-events"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
def oc_delete_windows_events():
    # Execute the command
    create_debug_pod()
    command = ('oc get vmis -o json | jq -r \'.items[] | select(.metadata.name | startswith("win")) | '
               '.status.interfaces[0].ipAddress\' | xargs -I {} oc exec -i my-debug-pod-automation -- /bin/bash -c "echo {}; '
               'sshpass -p \'Heslo123\' ssh -o StrictHostKeyChecking=no Administrator@{} wevtutil cl Application "')
    execute_local_linux_command_base(command)
    command = ('oc get vmis -o json | jq -r \'.items[] | select(.metadata.name | startswith("win")) | '
               '.status.interfaces[0].ipAddress\' | xargs -I {} oc exec -i my-debug-pod-automation -- /bin/bash -c "echo {}; '
               'sshpass -p \'Heslo123\' ssh -o StrictHostKeyChecking=no Administrator@{} wevtutil cl System "')
    execute_local_linux_command_base(command)
    delete_debug_pod()


command_help = """
    get all windows boot time.

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
    get all windows system events from last 48 hoers.

    Example: poetry run python main.py openshift-oc-module oc-get-windows-system-events"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
def oc_get_windows_system_events():
    # Execute the command
    create_debug_pod()
    command = ('oc get vmis -o json | jq -r \'.items[] | select(.metadata.name | startswith("win")) | '
               '.status.interfaces[0].ipAddress\' | xargs -I {} -P 100 oc exec -i my-debug-pod-automation -- /bin/bash -c "echo {}; '
               'sshpass -p \'Heslo123\' ssh -o StrictHostKeyChecking=no Administrator@{} wevtutil qe System /f:text "')
    execute_local_linux_command_base(command)
    delete_debug_pod()


command_help = """
    get all windows system application from last 48 hoers.

    Example: poetry run python main.py openshift-oc-module oc-get-windows-application-events"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
def oc_get_windows_application_events():
    # Execute the command
    create_debug_pod()
    command = ('oc get vmis -o json | jq -r \'.items[] | select(.metadata.name | startswith("win")) | '
               '.status.interfaces[0].ipAddress\' | xargs -I {} oc exec -i my-debug-pod-automation -- /bin/bash -c "echo {}; '
               'sshpass -p \'Heslo123\' ssh -o StrictHostKeyChecking=no Administrator@{} wevtutil qe Application /f:text "')
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
    
    If need to connect to default NIC the check the ethernet on the workers with nmcli con show --active.
    
    Example: create-delete-nncp --op create --start 1 --end 1 --sleep 0 --vlan True --base_interface ens1f0
    This will create NodeNetworkConfigurationPolicy from 'br-scale-1' to 'br-scale-2' connected to base interface.
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--op', help=click.style('operation for NNCPs', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for NNCPs', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for NNCPs', fg='magenta'))
@click.option('--sleep', type=int, help=click.style('sleep between NNCPs attach', fg='magenta'))
@click.option('--vlan', type=bool, default=False, help=click.style('True if added vlan connected to node'))
@click.option('--base_interface', help=click.style('base interface for NNCPs VLAN', fg='magenta'))

def create_delete_nncp(op, start, end, sleep, vlan, base_interface):
    for i in range(start, end + 1):
        if vlan:
            template = files_access.load_template("utilities/manifests/NodeNetworkConfigurationPolicyWithVLAN.json")
            template_str = json.dumps(template)
            modified_template = template_str.replace("{{index}}", f'{i}')
            modified_template = json.loads(modified_template)
            template_str = json.dumps(modified_template)
            modified_template = template_str.replace("{{base_interface}}", f'{base_interface}')
            modified_template = json.loads(modified_template)
        else:
            template = files_access.load_template("utilities/manifests/NodeNetworkConfigurationPolicy.json")
            template_str = json.dumps(template)
            modified_template = template_str.replace("{{index}}", f'{i}')
            modified_template = json.loads(modified_template)
        if op == 'create':
            template_str = json.dumps(modified_template)
            modified_template = template_str.replace("{{state}}", 'up')
            modified_template = json.loads(modified_template)
        else:
            template_str = json.dumps(modified_template)
            modified_template = template_str.replace("{{state}}", 'absent')
            modified_template = json.loads(modified_template)
        command = f"echo '{json.dumps(modified_template)}' | oc apply -f -"
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
    command = ("oc get nodes -l node-role.kubernetes.io/worker -o name | xargs -I{} sh -c 'echo -n \"{}: \"; oc "
               "describe {} | awk \"/Allocated resources/,/Events:/ {print}\" | grep -c "
               "\"bridge.network.kubevirt.io/br-scale-\"'")
    execute_local_linux_command_base(command)

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


command_help: str = """
    create custom_kubelet_config with the following params.

    autoSizingReserved: true
    kubeletConfig:
    nodeStatusMaxImages: -1
    maxPods: 1000 
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))

def custom_kubelet_config():

    command = f"oc label mcp master custom-kubelet-config=enabled"
    execute_local_linux_command_base(command)
    time.sleep(1)
    command = f"oc label mcp worker custom-kubelet-config=enabled"
    execute_local_linux_command_base(command)
    time.sleep(1)
    template = files_access.load_template("utilities/manifests/customKubeletConfig.json")
    template_str = json.dumps(template)
    command = f"echo '{template_str}' | oc create -f -"
    execute_local_linux_command_base(command)
