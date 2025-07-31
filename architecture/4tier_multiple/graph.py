import argparse
import json
import make_arch as march

# This script creates the graph of a 4-tier web application with nginx, memcache, php, mongodb
# There can be multiple instances of php and mongodb
# It also adds a load balancer in front of php and mongodb instances
# The load balancer is a separate service and runs in a separate machine

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a service graph with input arguments')
    parser.add_argument('--ngxThreads', type=int, default=8, help='Number of Nginx threads')
    parser.add_argument('--phpThreads', type=int, default=8, help='Number of PHP threads')
    parser.add_argument('--phpIOThreads', type=int, default=8, help='Number of PHP IO threads')
    parser.add_argument('--mmcThreads', type=int, default=8, help='Number of Memcached threads')
    parser.add_argument('--mongoThreads', type=int, default=8, help='Number of MongoDB threads')
    parser.add_argument('--mongoIOThreads', type=int, default=1, help='Number of MongoDB IO threads')

    parser.add_argument('--ngxCores', type=int, default=4, help='Number of cores assigned to NGINX')
    parser.add_argument('--phpCores', type=int, default=4, help='Number of cores assigned to PHP')
    parser.add_argument('--phpIOCores', type=int, default=1, help='Number of cores assigned to PHP IO')
    parser.add_argument('--mmcCores', type=int, default=4, help='Number of cores assigned to Memcached')
    parser.add_argument('--mongoCores', type=int, default=4, help='Number of cores assigned to MongoDB')
    parser.add_argument('--mongoIOCores', type=int, default=1, help='Number of cores assigned to MongoDB IO')

    parser.add_argument('--phpInstances', type=int, default=1, help='Number of instances of PHP')
    parser.add_argument('--mongoInstances', type=int, default=1, help='Number of instances of MongoDB')
    
    parser.add_argument('--machNxg', type=int, default=0, help='Machine ID where NGINX is deployed')
    parser.add_argument('--machMmc', type=int, default=1, help='Machine ID where Memcached is deployed')
    parser.add_argument('--machBalancerPhp', type=int, default=2, help='Machine ID where LoadBalancerPHP is deployed')
    parser.add_argument('--machPhp', type=int, default=3, help='Machine ID where PHP is deployed')
    parser.add_argument('--machPhpIO', type=int, default=4, help='Machine ID where PHP IO is deployed')
    parser.add_argument('--machBalancerMongo', type=int, default=5, help='Machine ID where LoadBalancerMongo is deployed')
    parser.add_argument('--machMongo', type=int, default=6, help='Machine ID where MongoDB is deployed')
    parser.add_argument('--machMongoIO', type=int, default=7, help='Machine ID where MongoDB IO is deployed')

    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    services = []
    edges = []

    sched_nginx = march.make_service_sched("CMT", [args.ngxThreads, list(range(30, 30 + args.ngxCores))], None)
    nginx = march.make_serv_inst(servName="nginx", servDomain="", instName="nginx",
                                modelName="nginx", sched=sched_nginx, machId=args.machNxg)
    services.append(nginx)
    
	# memcached service, only one instance in machine 2
    sched_memcached = march.make_service_sched("CMT", [args.mmcThreads, list(range(30, 30 + args.mmcCores))], None)
    memcached = march.make_serv_inst(servName="memcached", servDomain="", instName="memcached",
                                     modelName="memcached", sched=sched_memcached, machId=args.machMmc)
    services.append(memcached)

    # load balancer service for php, only one instance in machine 1
    sched = march.make_service_sched("CMT", [1, [30]], None)
    balance = march.make_serv_inst(servName = "load_balancer_php", servDomain = "", instName = "load_balancer_php",
        modelName = "load_balancer", sched = sched, machId = args.machBalancerPhp)
    services.append(balance)

    # current machine id for future deployments
    cur_machine = args.machPhp

    # php service, multiple instances
    # it includes a php_io service both deployed in the same machine
    for i in range(1, args.phpInstances + 1):
        sched_php = march.make_service_sched("CMT", [args.phpThreads, list(range(30, 30 + args.phpCores))], None)
        serv_name = "php"
        serv_domain = str(i - 1)
        inst_name = serv_name + "_inst_" + str(i - 1)
        php = march.make_serv_inst(servName = serv_name, servDomain = serv_domain, instName = inst_name,
            modelName = "php", sched = sched_php, machId = cur_machine)
        services.append(php)

        sched_php_io = march.make_service_sched("Simplified", [args.phpIOThreads, list(range(30, 30 + args.phpIOCores))], None)
        serv_name = "php_io"
        serv_domain = str(i - 1)
        inst_name = serv_name + "_inst_" + str(i - 1)
        php_io = march.make_serv_inst(servName = serv_name, servDomain = serv_domain, instName = inst_name,
            modelName = "php_io", sched = sched_php_io, machId = cur_machine + args.phpInstances)
        services.append(php_io)
        cur_machine += 1

    cur_machine = args.machBalancerMongo + args.phpInstances * 2 - 2
    # load balancer service for mongodb, only one instance one machine 
    sched = march.make_service_sched("CMT", [1, [30]], None)
    balance = march.make_serv_inst(servName = "load_balancer_mongo", servDomain = "", instName = "load_balancer_mongo",
        modelName = "load_balancer", sched = sched, machId = cur_machine)
    services.append(balance)

    cur_machine += 1

    # mongodb service, multiple instances
    # it includes a mongodb_io service both deployed in the same machine
    for i in range(1, args.mongoInstances + 1):
        sched_mongo = march.make_service_sched("CMT", [args.mongoThreads, list(range(30, 30 + args.mongoCores))], None)
        serv_name = "mongodb"
        serv_domain = str(i - 1)
        inst_name = serv_name + "_inst_" + str(i - 1)
        mongodb = march.make_serv_inst(servName = serv_name, servDomain = serv_domain, instName = inst_name, 
            modelName = "mongodb", sched = sched_mongo, machId = cur_machine)
        services.append(mongodb)
        
        sched_mongo_io = march.make_service_sched("Simplified", [args.mongoIOThreads, list(range(30, 30 + args.mongoIOCores))], None)
        serv_name = "mongo_io"
        serv_domain = str(i - 1)
        inst_name = serv_name + "_inst_" + str(i - 1)
        mongodb_io = march.make_serv_inst(servName = serv_name, servDomain = serv_domain, instName = inst_name,
        modelName = "mongo_io", sched = sched_mongo_io, machId = cur_machine + args.mongoInstances)
        services.append(mongodb_io)
        cur_machine += 1

    edge_0 = march.make_edge(src = "nginx", targ = "memcached", bidir = True)
    edges.append(edge_0)
    edge_1 = march.make_edge(src = "nginx", targ = "load_balancer_php", bidir = True)
    edges.append(edge_1)
    for i in range(1, args.phpInstances + 1):        
        edge = march.make_edge(src = "load_balancer_php", targ = "php_inst_" + str(i - 1), bidir = True)
        edges.append(edge)
        edge = march.make_edge(src = "php_inst_" + str(i - 1), targ = "php_io_inst_" + str(i - 1), bidir = True)
        edges.append(edge)
        edge = march.make_edge(src = "php_inst_" + str(i - 1), targ = "load_balancer_mongo", bidir = True)
        edges.append(edge)
        edge = march.make_edge(src = "php_inst_" + str(i - 1), targ = "memcached", bidir = True)
        edges.append(edge)

    for i in range(1, args.mongoInstances + 1):        
        edge = march.make_edge(src = "load_balancer_mongo", targ = "mongodb_inst_" + str(i - 1), bidir = True)
        edges.append(edge)
        edge = march.make_edge(src = "mongodb_inst_" + str(i - 1), targ = "mongo_io_inst_" + str(i - 1), bidir = True)
        edges.append(edge)

    graph = march.make_cluster(services = services, edges = edges)

    with open("./json/graph.json", "w+") as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
    main()

