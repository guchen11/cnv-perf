import json
import time
import click
from utilities import files_access, oc
from utilities.bash import execute_local_linux_command_base


@click.group()
def openshift_oc_module():
    pass


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)

command_help = """
    get templates and data_source.

    Example: poetry run python main.py openshift_oc_module oc-get-templates-and-data-source"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
def oc_get_templates_and_data_source():
    # Execute the command
    command = "/usr/local/bin/oc -n openshift get template -l template.kubevirt.io/type=base -o jsonpath=\'{range " \
              ".items[*]}{@.metadata.name}{\"\\t\"}{@.parameters[?(@.name==\"DATA_SOURCE_NAME\")].value}{\"\\n\"}\'"
    execute_local_linux_command_base(command)


command_help = """
    get the vms spread on the nodes.

    Example: poetry run python main.py openshift_oc_module oc_get_vms_node_spread"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
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
    Create vm from golden image.

    Example: poetry run python main.py openshift_oc_module oc-create-vm-golden-image --name fedora-test-1 --template fedora-desktop-tiny 
    --cloud_user_password 100yard- --data_source fedora --namespace scale-test"""


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--name', help='set VM name')
@click.option('--template', help='set template name')
@click.option('--cloud_user_password', help='set cloud user password')
@click.option('--data_source', help='get data source name of the image')
@click.option('--namespace', help='set namespace for the VM')
def oc_create_vm_golden_image(name, template, data_source, cloud_user_password, namespace):
    oc_create_vm_golden_image_base(name, template, data_source, cloud_user_password, namespace)


command_help = """
    Create vm range from golden image.

    Example: poetry run python main.py openshift_oc_module oc-create-vm-golden-image-range --name fedora-test --template fedora-desktop-tiny 
    Example: poetry run python main.py openshift_oc_module oc-create-vm-golden-image-range --name fedora-test --template fedora-desktop-tiny 
    --cloud_user_password 100yard- --data_source fedora --namespace scale-test --start 1 --end 2 """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--name', help='set VM name')
@click.option('--template', help='set template name')
@click.option('--cloud_user_password', help='set cloud user password')
@click.option('--data_source', help='get data source name of the image')
@click.option('--namespace', help='set namespace for the VM')
@click.option('--start', type=int, help='Start index for VM creation')
@click.option('--end', type=int, help='End index for VM creation')
def oc_create_vm_golden_image_range(name, template, data_source, cloud_user_password, namespace, start, end):
    for i in range(start, end + 1):
        VM_NAME = f"{name}-{i}"
        oc_create_vm_golden_image_base(VM_NAME, template, data_source, cloud_user_password, namespace)


command_help: str = """
    Attach or detach pvc in the given range to VM.

    Example: attach-detach-pcv-vm --vm_name rhel9-server --namespace default --op add --prefix pvc-test- --start 1 --end 2 --sleep 0 
    This will attach PVCs from 'pvc-test-1' to 'pvc-test-2'.
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--vm_name', help='VM names')
@click.option('--namespace', help='Namespace for VM creation')
@click.option('--op', help='operation on the vm')
@click.option('--prefix', help='Prefix for PVC names')
@click.option('--start', type=int, help='Start index for PVC')
@click.option('--end', type=int, help='End index for PVC')
@click.option('--sleep', type=int, help='sleep between PVC attach')
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


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--vm_name', help='VM names')
@click.option('--namespace', help='Namespace for VM')
@click.option('--interface', help='Interface of the pvc')
@click.option('--prefix', help='Prefix for PVC names')
@click.option('--start', type=int, help='Start index for PVC')
@click.option('--end', type=int, help='End index for PVC')
@click.option('--sleep', type=int, help='sleep between PVC attach')
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

    Example: create-delete-nncp --op create --start 1 --end 1 --sleep 0 
    This will create NodeNetworkConfigurationPolicy from 'br-scale-1' to 'br-scale-2'.
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--op', help='operation for NNCPs')
@click.option('--start', type=int, help='Start index for NNCPs')
@click.option('--end', type=int, help='End index for NNCPs')
@click.option('--sleep', type=int, help='sleep between NNCPs attach')
def create_delete_nncp(op, start, end, sleep):
    for i in range(start, end + 1):
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


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
def empty_prometheus():
    oc.empty_prometheus()


command_help: str = """
    Dump prometheus data base
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.argument('test_name', type=click.STRING, required=True)
def dump_prometheus(test_name):
    oc.dump_prometheus(test_name)


command_help: str = """
    Test maximum pods on a cluster.

    Example: test-maximum-pod --replicas 2000
    This will create 2000 pods.
    """


@openshift_oc_module.command(context_settings=CONTEXT_SETTINGS, help=command_help)
@click.option('--replicas', help='number of replicas')
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
