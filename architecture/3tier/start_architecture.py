# This file is used to generate the microservices, machines, graph and path
# for the 3tier architecture. 3tier previously had no orchestration script -
# each generator was run by hand; added 2026-11-19 alongside
# --mongoInstances replica support and the --pPath0/1/2 CLI args
# (mirroring social_network/start_architecture.py).

import subprocess
import argparse
import os

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a service graph with input arguments')
    parser.add_argument('--end_seconds', type=int, default=60, help='Epoch end time in seconds')
    parser.add_argument('--monitor_interval', type=int, default=1, help='Interval at which the client will monitor the system (in seconds)')

    parser.add_argument('--mongoInstances', type=int, default=1, help='Number of mongodb instances')

    parser.add_argument('--pPath0', type=int, default=86, help='Ratio (int 0-100) of memcached cache hit')
    parser.add_argument('--pPath1', type=int, default=12, help='Ratio (int 0-100) of memcached miss & mongodb hit')
    parser.add_argument('--pPath2', type=int, default=2, help='Ratio (int 0-100) of memcached miss & mongodb miss')

    parser.add_argument('--machNxg', type=int, default=0, help='Machine ID where NGINX is deployed')
    parser.add_argument('--machMmc', type=int, default=1, help='Machine ID where memcached is deployed')
    parser.add_argument('--machBalancerMongo', type=int, default=2, help='Machine ID where the mongodb load balancer is deployed')

    args = parser.parse_args()
    return args

# Generate microservices
def generate_microservices():
    try:
        for script in ['net_stack.py', 'nginx_new.py', 'memcached.py', 'mongodb.py', 'mongo_io.py', 'load_balancer.py']:
            proc = subprocess.run(['python3', script])
            if proc.returncode == 0:
                print(script + " successfully executed")
    except FileNotFoundError as e:
        print(e)

def generate_client(end_seconds, monitor_interval):
    try:
        proc = subprocess.run(['python3', 'client.py'])
        if proc.returncode == 0:
            print("client.py successfully executed")
    except FileNotFoundError as e:
        print(e)

def generate_machines(mongoInstances, machBalancerMongo):
    try:
        proc = subprocess.run(['python3', 'machines.py',
            f"--mongoInstances={mongoInstances}", f"--machBalancerMongo={machBalancerMongo}"])
        if proc.returncode == 0:
            print("machines.py successfully executed")
    except FileNotFoundError as e:
        print(e)

def generate_graph(mongoInstances, machNxg, machMmc, machBalancerMongo):
    try:
        proc = subprocess.run(['python3', '3tier_graph.py',
            f"--mongoInstances={mongoInstances}", f"--machNxg={machNxg}",
            f"--machMmc={machMmc}", f"--machBalancerMongo={machBalancerMongo}"])
        if proc.returncode == 0:
            print("3tier_graph.py successfully executed")
    except FileNotFoundError as e:
        print(e)

def generate_path(pPath0, pPath1, pPath2):
    try:
        proc = subprocess.run(['python3', '3tier_path.py',
            f"--pPath0={pPath0}", f"--pPath1={pPath1}", f"--pPath2={pPath2}"])
        if proc.returncode == 0:
            print("3tier_path.py successfully executed")
    except FileNotFoundError as e:
        print(e)

def main():
    os.makedirs("json/microservice", exist_ok=True)
    args = parse_arguments()
    generate_microservices()
    generate_client(args.end_seconds, args.monitor_interval)
    generate_machines(args.mongoInstances, args.machBalancerMongo)
    generate_graph(args.mongoInstances, args.machNxg, args.machMmc, args.machBalancerMongo)
    generate_path(args.pPath0, args.pPath1, args.pPath2)

if __name__ == "__main__":
    main()
