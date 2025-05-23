from concurrent.futures import ThreadPoolExecutor
import concurrent
import logging
import time
from utilities.bash import execute_local_linux_command_base
from utilities.bash import execute_local_linux_command_base_silent

import click

CONTEXT_SETTINGS = dict(max_content_width=120)


@click.group()
def tests_module():
    pass


command_help = """
    Create vm range from golden image.

    Example: poetry run python main.py tests-module create-vm-golden-image-with-ssh-publickey-and-test --prefix fedora-server-large 
    --template fedora-server-large --data_source fedora --sleep 0 --user fedora --namespace scale-test --start 1 --end 10
    --start_vm False --is_alive False"""


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
def create_vm_golden_image_with_ssh_publickey_and_test(prefix, template, data_source, user, namespace, start, end,
                                                       sleep, start_vm, is_alive):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
    print("CREATE VMS")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
    execute_local_linux_command_base(
        f"poetry run python main.py openshift-oc-module oc-create-vm-golden-image-range --name {prefix} --template {template}  --cloud_user_password password --data_source {data_source} --namespace {namespace} --start {start} --end {end} --sleep 0")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
    print("PATCH TO VMS PUBLIC KEY")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
    execute_local_linux_command_base(
        f"poetry run python main.py openshift-oc-module patch-ssh-publickey-vm --namespace {namespace} --prefix {prefix}- --start {start} --end {end} --sleep 0")
    if (start_vm):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
        print("START VMS")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
        execute_local_linux_command_base(
            f"poetry run python main.py virtctl-module start-vms --prefix {prefix}- --start {start} --end {end} --sleep {sleep}")
    if (is_alive):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
        print("TEST IF VMS ARE ALIVE")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!)")
        time.sleep(10)
        execute_local_linux_command_base(
            f"poetry run python main.py virtctl-module check-vms-ssh-alive --prefix {prefix}- --username={user} --start {start} --end {end} --sleep 0 | grep -c testOSisAlive ")


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


command_help = """
    test nodes CPU and RAM  

    Example: poetry run python main.py tests-module test-nodes-avg-CPU-RAM --avg 10"""


@tests_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--avg', type=int, help=click.style('Number of samples to average'))
def test_nodes_avg_CPU_RAM(avg):
    print(f"Masters Average CPU %: {get_avg('master', 3, avg)}")
    print(f"Masters Average RAM %: {get_avg('master', 5, avg)}")
    print(f"Worker Average CPU %: {get_avg('worker', 3, avg)}")
    print(f"Worker Average RAM %: {get_avg('worker', 5, avg)}")


def get_avg(role, col, avg):
    command = f"kubectl top nodes --selector=node-role.kubernetes.io/{role} --no-headers | awk '{{sum+=${col}}} END {{print sum/NR}}'"
    #print(f"{command}")
    samples = []
    for i in range(1, avg + 1):
        samples.append(float(execute_local_linux_command_base_silent(command)))
    average = sum(samples) / len(samples)
    return round(average, 2)


command_help = """
    test start stop VMS  

    Example: poetry run python main.py test-start-stop-vms --prefix cirros-vm- --avg 10"""


@tests_module.command(context_settings=CONTEXT_SETTINGS, help=click.style(command_help, fg='yellow'))
@click.option('--avg', type=int, help=click.style('Number of samples to average'))
@click.option('--prefix', help=click.style('VM prefix'))
def test_start_stop_vms(avg, prefix):
    print(f"Start VM Average time : {get_avg_start_stop_vms('start',prefix, avg)}")
    print(f"Stop VM Average time : {get_avg_start_stop_vms('stop',prefix, avg)}")

def get_avg_start_stop_vms(op, prefix, avg):
    samples = []
    for i in range(1, avg + 1):
        vm_name = f'{prefix}{i}'
        # Start the VM using virtctl
        command = f"virtctl {op} {vm_name}"
        print(f"{command}")
        execute_local_linux_command_base_silent(command)
        # Measure the time until the VM is ready
        samples.append(float(check_vm_ready(op,vm_name)))

    # Calculate the average time it takes for VMs to be ready
    average = sum(samples) / len(samples) if samples else 0
    return round(average, 2)


def check_vm_ready(op,vm_name):
    # Define the command to check the Ready condition
    command = f"oc get VirtualMachine/{vm_name} -o jsonpath='{{.status.printableStatus}}'"
    print(f"{command}")

    # Record the start time
    start_time = time.time()

    if op == 'start':
        vm_condition = 'Running'
    else:
        vm_condition = 'Stopped'
    while True:
        # Execute the command to get the Ready status
        result = execute_local_linux_command_base_silent(command)

        if result == f"{vm_condition}":
            # VM is ready
            end_time = time.time()
            elapsed_time = end_time - start_time
            #print(f"VM {vm_name} running state is {result}")
            #print(f"Time taken: {elapsed_time:.2f} seconds")
            return float(f"{elapsed_time:.2f}")  # Return elapsed time as float
        else:
            #print(f"VM {vm_name} is not ready yet. Checking again...")
            #print(f"VM {vm_name} running state is {result}")
            time.sleep(1)

        # Wait for a short period before checking again
        time.sleep(1)
