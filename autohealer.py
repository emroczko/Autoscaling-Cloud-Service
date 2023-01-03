import pandas as pd
import requests
import subprocess

from io import StringIO

if __name__ == "__main__":
    while True:
        print("Checking health stats...")

        csv = requests.get('http://localhost:8404/stats;csv').text
        csvString = StringIO(csv)
        df = pd.read_csv(csvString, sep=",", header=0)

        filtered = df[(df.type == 2) & (df.status == 'DOWN')]

        for vm in filtered['svname']:
            print(f'Found down VM: {vm}; Trying to destroy it...')
            subprocess.call(["vagrant", "destroy", "-f", vm])

            print(f'Creating vm {vm} again...')
            subprocess.call(["vagrant", "up", vm])

        sleep(10)
        