from time import sleep

import pandas as pd
import requests
import subprocess
import yaml

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

    for session_rate in filtered['rate']:
        if session_rate > 10 and len(filtered) < maximum_instances:
            print("Adding instance")
            sleep(10)
            break


if __name__ == "__main__":
    autoscaling()


        