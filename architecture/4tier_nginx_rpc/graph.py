import argparse
import json
import make_arch as march

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
    
    parser.add_argument('--machNxg', type=int, default=0, help='Machine ID where NGINX is deployed')
    parser.add_argument('--machPhp', type=int, default=2, help='Machine ID where PHP is deployed')
    parser.add_argument('--machPhpIO', type=int, default=2, help='Machine ID where PHP IO is deployed')
    parser.add_argument('--machMmc', type=int, default=1, help='Machine ID where Memcached is deployed')
    parser.add_argument('--machMongo', type=int, default=3, help='Machine ID where MongoDB is deployed')
    parser.add_argument('--machMongoIO', type=int, default=3, help='Machine ID where MongoDB IO is deployed')

    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()

    sched_nginx = march.make_service_sched("CMT", [args.ngxThreads, list(range(20, 20 + args.ngxCores))], None)
    nginx = march.make_serv_inst(servName="nginx", servDomain="", instName="nginx",
                                modelName="nginx", sched=sched_nginx, machId=args.machNxg)

    sched_php = march.make_service_sched("CMT", [args.phpThreads, list(range(20, 20 + args.phpCores))], None)
    php = march.make_serv_inst(servName="php", servDomain="", instName="php",
                               modelName="php", sched=sched_php, machId=args.machPhp)

    sched_php_io = march.make_service_sched("Simplified", [args.phpIOThreads, list(range(20, 20 + args.phpIOCores))], None)
    php_io = march.make_serv_inst(servName="php_io", servDomain="", instName="php_io",
                                  modelName="php_io", sched=sched_php_io, machId=args.machPhpIO)

    sched_memcached = march.make_service_sched("CMT", [args.mmcThreads, list(range(20, 20 + args.mmcCores))], None)
    memcached = march.make_serv_inst(servName="memcached", servDomain="", instName="memcached",
                                     modelName="memcached", sched=sched_memcached, machId=args.machMmc)

    sched_mongo = march.make_service_sched("CMT", [args.mongoThreads, list(range(20, 20 + args.mongoCores))], None)
    mongodb = march.make_serv_inst(servName="mongodb", servDomain="", instName="mongodb",
                                   modelName="mongodb", sched=sched_mongo, machId=args.machMongo)

    sched_mongo_io = march.make_service_sched("Simplified", [args.mongoIOThreads, list(range(20, 20 + args.mongoIOCores))], None)
    mongodb_io = march.make_serv_inst(servName="mongo_io", servDomain="", instName="mongo_io",
                                      modelName="mongo_io", sched=sched_mongo_io, machId=args.machMongoIO)

    services = [nginx, php, php_io, memcached, mongodb, mongodb_io]

    edge_0 = march.make_edge(src="nginx", targ="memcached", bidir=True)
    edge_1 = march.make_edge(src="nginx", targ="php", bidir=True)
    edge_2 = march.make_edge(src="php", targ="mongodb", bidir=True)
    edge_3 = march.make_edge(src="php", targ="memcached", bidir=True)
    edge_4 = march.make_edge(src="php", targ="php_io", bidir=True)
    edge_5 = march.make_edge(src="mongodb", targ="mongo_io", bidir=True)

    edges = [edge_0, edge_1, edge_2, edge_3, edge_4, edge_5]

    graph = march.make_cluster(services=services, edges=edges)

    with open("./json/graph.json", "w+") as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
	main()