from concurrent.futures import ThreadPoolExecutor
import concurrent
import logging
import time
from utilities.bash import execute_local_linux_command_base
import click

CONTEXT_SETTINGS = dict(max_content_width=120)

@click.group()
def tests_module():
    pass

command_help = """
    Create vm range from golden image.

    Example: poetry run python main.py tests-module create-vm_golden-image-with-ssh-publickey-and-test --prefix fedora-server-large 
    --template fedora-server-large --data_source fedora --sleep 0 --user fedora --namespace scale-test --start 1 --end 10
    --startVM False --isAlive False"""


@tests_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--prefix', help=click.style('set VM name'))
@click.option('--data_source', help=click.style('data_source'))
@click.option('--template', help=click.style('set template name'))
@click.option('--user', help=click.style('user of the vm'))
@click.option('--namespace', help=click.style('set namespace for the VM'))
@click.option('--start', type=int, help=click.style('Start index for VM creation'))
@click.option('--end', type=int, help=click.style('End index for VM creation'))
@click.option('--sleep', type=int, help=click.style('sleep between actions'))
@click.option('--start_vm', type=bool, default=False, help=click.style('Start the VM'))
@click.option('--is_alive', type=bool, default=False, help=click.style('Test if VM alive via ssh'))

def create_vm_golden_image_with_ssh_publickey_and_test(prefix, template, data_source, user, namespace, start, end, sleep,start_vm, is_alive):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
    print("CREATE VMS")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
    execute_local_linux_command_base(
        f"poetry run python main.py openshift-oc-module oc-create-vm-golden-image-range --name {prefix} --template {template}  --cloud_user_password password --data_source {data_source} --namespace {namespace} --start {start} --end {end} --sleep {sleep}")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
    print("PATCH TO VMS PUBLIC KEY")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
    execute_local_linux_command_base(
        f"poetry run python main.py openshift-oc-module patch-ssh-publickey-vm --namespace {namespace} --prefix {prefix}- --start {start} --end {end} --sleep {sleep}")
    if (start_vm):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
        print("START VMS")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
        execute_local_linux_command_base(
            f"poetry run python main.py virtctl-module start-vms --prefix {prefix}- --start {start} --end {end} --sleep {sleep}")
    if(is_alive):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
        print("TEST IF VMS ARE ALIVE")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
        time.sleep(10)
        execute_local_linux_command_base(
            f"poetry run python main.py virtctl-module check-vms-ssh-alive --prefix {prefix}- --username={user} --start {start} --end {end} --sleep {sleep} | grep -c {user}  ")

def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)


command_help = """
    Create vm range from golden image.

    Example: poetry run python main.py tests-module check-vms-ssh-alive-threadpool --prefix entos7-test 
    --sleep 0 --user centos --start 1 --end 2"""

@tests_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--prefix', help=click.style('set VM name'))
@click.option('--user', help=click.style('user of the vm'))
@click.option('--start', type=int, help=click.style('Start index for VM creation'))
@click.option('--end', type=int, help=click.style('End index for VM creation'))
@click.option('--sleep', type=int, help=click.style('sleep between actions'))
def check_vms_ssh_alive_threadpool(prefix, user, start, end, sleep):
    command = f"poetry run python main.py virtctl-module check-vms-ssh-alive --prefix {prefix}- --username={user} --start {start} --end {end} --sleep {sleep} | grep -c CentOS "
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(thread_function, range(3))