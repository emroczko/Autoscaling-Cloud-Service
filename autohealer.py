from time import sleep

import pandas as pd
import requests
import subprocess
import yaml
from numpy import mean

from yaml.loader import SafeLoader
from io import StringIO

DEFAULT_MIN_INSTANCES = 3
DEFAULT_MAX_INSTANCES = 3


def read_stats() -> pd.DataFrame:
    csv = requests.get('http://localhost:8404/stats;csv').text
    csv_string = StringIO(csv)
    return pd.read_csv(csv_string, sep=",", header=0)


def autohealing():
    while True:
        print("Checking health stats...")

        df = read_stats()
        filtered = df[(df.type == 2) & (df.status == 'DOWN')]

        for vm in filtered['svname']:
            print(f'Found down VM: {vm}; Trying to destroy it...')
            subprocess.call(["vagrant", "destroy", "-f", vm])

            print(f'Creating vm {vm} again...')
            subprocess.call(["vagrant", "up", vm])

        sleep(10)


def autoscaling():

    while True:
        print("Checking autoscaling policy...")

        minimum_instances = DEFAULT_MIN_INSTANCES
        maximum_instances = DEFAULT_MAX_INSTANCES

        try:
            with open('autoscaler_properties.yaml') as f:
                data = yaml.load(f, Loader=SafeLoader)
                minimum_instances = int(data['min_instances'])
                maximum_instances = int(data['max_instances'])
        except ValueError:
            print("Expected ints; fix the file, or default values will be used")
        except TypeError:
            print("Properties file empty!")
        except FileNotFoundError:
            print("Properties file not found! using default values")

        df = read_stats()
        filtered = df[(df.type == 2)]
        number_of_last_existing_vm = len(filtered)

        if mean(filtered['rate']) > 16:
            if len(filtered) < maximum_instances:
                add_machine_to_pool(number_of_last_existing_vm + 1)
                sleep(10)
            else:
                print("Maximum number of instances is already up")

        if mean(filtered['rate']) < 5:
            if len(filtered) > minimum_instances:
                remove_machine_from_pool(number_of_last_existing_vm)
                sleep(10)
            else:
                print("Minimum number of instances is already up")

        sleep(10)

def remove_machine_from_pool(vm_num: int):
    vm_num = str(vm_num) if vm_num > 9 else f'0{vm_num}'
    subprocess.call(["vagrant", "destroy", "-f", f'web{vm_num}'])




def add_machine_to_pool(vm_num: int):
    vm_num = str(vm_num) if vm_num > 9 else f'0{vm_num}'
    vm_declaration = """
  config.vm.define "web{0}" do |web|
    web.vm.box = "ubuntu/focal64"
    web.vm.network "private_network", ip: "192.168.50.1{1}"
    web.vm.provision "shell", path: "install_web.sh", args: "web{2}"
  end
    """.format(vm_num, vm_num, vm_num)

    with open('Vagrantfile', 'r') as vagrant_file:
        vagrant_lines = vagrant_file.readlines()

    vagrant_lines.insert(-1, vm_declaration)
    with open('Vagrantfile', 'w') as vagrant_file:
        vagrant_file.writelines(vagrant_lines)

    print(f'Creating vm web{vm_num} again...')
    subprocess.call(["vagrant", "up", f"web{vm_num}"])

    with open('haproxy.cfg', 'a') as haproxy:
        haproxy.write(f'    server  web3 192.168.50.1{vm_num}:9103 check')

    subprocess.call(["haproxy", "-f", "haproxy.cfg"])

    sleep(10)

    df = read_stats()
    filtered = df[(df.type == 2)]

    if f'web{vm_num}' in filtered['svname']:
        print("Autoscaled one VM up")
    else:
        print(f"Autoscaling up failed for VM: web{vm_num}")


if __name__ == "__main__":
    add_machine_to_pool(5)


        