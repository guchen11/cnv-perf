import json
import warnings
import click
from kubernetes import client, config
from kubernetes.dynamic.exceptions import ResourceNotFoundError
from openshift.dynamic import DynamicClient
from utilities import files_access
import time

from utilities.bash import execute_local_linux_command_base


@click.group()
def openshift_api_module():
    pass


CONTEXT_SETTINGS = dict(max_content_width=120)

command_help: str = """
    Create namespaces with start and end index.

    Example: create-namespace --start 1 --end 5
    This will create namespaces from 'test-namespace-1' to 'test-namespace-5'.
    """


@openshift_api_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--start', type=int, help=click.style('Start index for namespace creation', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for namespace creation', fg='magenta'))
def create_namespace(start, end):
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    v1_services = dyn_client.resources.get(api_version='v1', kind='Namespace')

    template = files_access.load_template("utilities/manifests/namespace.json")

    for i in range(start, end + 1):
        namespace_name = f'test-namespace-{i}'
        modified_template = files_access.modify_template(template, namespace_name)

        v1_services.create(body=modified_template)
        print(f"Namespace {namespace_name} was created")


command_help: str = """
    Create VMs with start and end index.
    
    Example: create-vm-cirros --prefix cirros-vm- --volume_mode Block --storage_class_name ocs-storagecluster-ceph-rbd-virtualization 
    --namespace default --start 1 --end 5 --sleep 2 
    This will create VMs from 'cirros-vm-1' to 'cirros-vm-5' in the 'default' namespace with 2 secounds sleep.
    """


@openshift_api_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--prefix', help=click.style('Prefix for VM names', fg='magenta'))
@click.option('--namespace', help=click.style('Namespace for VM creation', fg='magenta'))
@click.option('--volume_mode', help=click.style('volumeMode for VM PVC, Filesystem or Block', fg='magenta'))
@click.option('--storage_class_name', help=click.style('storageClassName for VM PVC, iscsi-lun or ocs-storagecluster-ceph-rbd-virtualization', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for VM creation', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for VM creation', fg='magenta'))
@click.option('--sleep', type=int, help=click.style('sleep between VMSs', fg='magenta'))
def create_vm_cirros(prefix, namespace, volume_mode, storage_class_name, start, end, sleep):
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    v1_services = dyn_client.resources.get(api_version='kubevirt.io/v1', kind='VirtualMachine')

    template = files_access.load_template("utilities/manifests/cirros.json")

    for i in range(start, end + 1):
        VM_NAME = f'{prefix}{i}'
        template_str = json.dumps(template)
        modified_template = template_str.replace("{{VM_NAME}}", VM_NAME)
        modified_template = json.loads(modified_template)

        template_str = json.dumps(template)
        modified_template = template_str.replace("{{VOLUME_MODE}}", volume_mode)
        modified_template = json.loads(modified_template)

        template_str = json.dumps(template)
        modified_template = template_str.replace("{{STORAGE_CLASS_NAME}}", storage_class_name)
        modified_template = json.loads(modified_template)
        
        v1_services.create(body=modified_template, namespace=namespace)
        print(f"VM {VM_NAME} was created")
        time.sleep(sleep)
        command = f"oc wait --for=condition=Ready VirtualMachine/{VM_NAME}"
        execute_local_linux_command_base(command)


command_help = """
    Delete namespaces with start and end index.

    Example: delete-namespace --start 1 --end 5
    This will delete namespaces from 'test-namespace-1' to 'test-namespace-5'.
    """


@openshift_api_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--start', type=int, help=click.style('Start index for namespace deletion', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for namespace deletion', fg='magenta'))
def delete_namespace(start, end):
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    v1_services = dyn_client.resources.get(api_version='v1', kind='Namespace')

    for i in range(start, end + 1):
        namespace_name = f'test-namespace-{i}'
        v1_services.delete(name=namespace_name)
        print(f"Namespace {namespace_name} was deleted")


command_help = """
    Delete vm with start and end index.

    Example: delete-vm --prefix test-vm- --namespace default --start 1 --end 5
    This will delete vm from 'test-vm-1' to 'test-vm-5'.
    """


@openshift_api_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--prefix', help=click.style('Prefix for VM names', fg='magenta'))
@click.option('--namespace', help=click.style('Namespace for VM deletion', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for VM deletion', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for VM deletion', fg='magenta'))
def delete_vm(prefix, namespace, start, end):
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    v1_services = dyn_client.resources.get(api_version='kubevirt.io/v1', kind='VirtualMachine')

    for i in range(start, end + 1):
        vm_name = f'{prefix}{i}'
        try:
            v1_services.delete(name=vm_name, namespace=namespace)
            print(f"VM {vm_name} in Namespace {namespace} was deleted")
        except ResourceNotFoundError:
            warning_message = f"Virtual machine '{vm_name}' not found."
            warnings.warn(warning_message, category=UserWarning)

command_help: str = """
    Create pvc with start and end index.

    Example: create_pvc --prefix pvc-test- --namespace default --volume_mode Block --storage_class_name ocs-storagecluster-ceph-rbd-virtualization --start 1 --end 2 --sleep 2 
    Example: create-pvc --prefix fusion-pvc-test- --namespace fusion-vms  --volume_mode Filesystem --storage_class_name iscsi-lun --start 1 --end 2 --sleep 0
    This will create pvc from 'pvc-test-1' to 'pvc-test-2'.
    """

@openshift_api_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--prefix', help=click.style('Prefix for PVC names', fg='magenta'))
@click.option('--namespace', help=click.style('Namespace for PVC creation', fg='magenta'))
@click.option('--volume_mode', help=click.style('volumeMode for PVC, Filesystem or Block', fg='magenta'))
@click.option('--storage_class_name', help=click.style('storageClassName for PVC, iscsi-lun or ocs-storagecluster-ceph-rbd-virtualization', fg='magenta'))
@click.option('--start', type=int, help=click.style('Start index for PVC creation', fg='magenta'))
@click.option('--end', type=int, help=click.style('End index for PVC creation', fg='magenta'))
@click.option('--sleep', type=int, help=click.style('sleep between PVCs', fg='magenta'))
def create_pvc(prefix, namespace, volume_mode, storage_class_name, start, end, sleep):
    # Load OpenShift configuration from default kubeconfig file
    config.load_kube_config()

    # Initialize DynamicClient for OpenShift API
    dyn_client = DynamicClient(client.ApiClient())

    # Initialize Kubernetes API client
    api_instance = client.CoreV1Api()

    for i in range(start, end + 1):
        pvc_name = f'{prefix}{i}'
    # Set namespace, VM name, PVC details
        storage_class_name = storage_class_name
        access_modes = "ReadWriteMany"
        storage_size = "1Gi"

    # Create the PVC
        body = client.V1PersistentVolumeClaim(
            api_version="v1",
            kind="PersistentVolumeClaim",
            metadata=client.V1ObjectMeta(name=pvc_name),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=[access_modes],
                resources=client.V1ResourceRequirements(
                    requests={"storage": storage_size}
                ),
                storage_class_name=storage_class_name,
                volume_mode=volume_mode  # Specify the volume mode as "Block"
            )
        )

        api_response = api_instance.create_namespaced_persistent_volume_claim(
            namespace=namespace,
            body=body
        )
        print(f"PVC {pvc_name} created. Status={api_response.status}")
        time.sleep(sleep)

