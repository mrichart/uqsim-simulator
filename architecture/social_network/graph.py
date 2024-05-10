import argparse
import json
import make_arch as march

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a service graph with input arguments')
    parser.add_argument('--ngxThreads', type=int, default=8, help='Number of Nginx threads')
    parser.add_argument('--htThreads', type=int, default=8, help='Number of Home Timeline threads')
    parser.add_argument('--htRedisThreads', type=int, default=8, help='Number of Home Timeline Redis threads')
    parser.add_argument('--psThreads', type=int, default=8, help='Number of Post Storage threads')
    parser.add_argument('--mmcThreads', type=int, default=8, help='Number of Memcached threads')
    parser.add_argument('--mongoThreads', type=int, default=8, help='Number of MongoDB threads')
    parser.add_argument('--mongoIOThreads', type=int, default=1, help='Number of MongoDB IO threads')

    parser.add_argument('--ngxCores', type=int, default=4, help='Number of cores assigned to NGINX')
    parser.add_argument('--htCores', type=int, default=4, help='Number of cores assigned to Home Timeline')
    parser.add_argument('--htRedisCores', type=int, default=1, help='Number of cores assigned to Home Timeline Redis')
    parser.add_argument('--psCores', type=int, default=4, help='Number of cores assigned to Post Storage')
    parser.add_argument('--mmcCores', type=int, default=4, help='Number of cores assigned to Memcached')
    parser.add_argument('--mongoCores', type=int, default=4, help='Number of cores assigned to MongoDB')
    parser.add_argument('--mongoIOCores', type=int, default=1, help='Number of cores assigned to MongoDB IO')
    
    parser.add_argument('--machNxg', type=int, default=0, help='Machine ID where NGINX is deployed')
    parser.add_argument('--machHt', type=int, default=1, help='Machine ID where Home Timeline is deployed')
    parser.add_argument('--machHtRedis', type=int, default=1, help='Machine ID where Home Timeline Redis is deployed')
    parser.add_argument('--machPs', type=int, default=2, help='Machine ID where Post Storage is deployed')
    parser.add_argument('--machMmc', type=int, default=2, help='Machine ID where Memcached is deployed')
    parser.add_argument('--machMongo', type=int, default=3, help='Machine ID where MongoDB is deployed')
    parser.add_argument('--machMongoIO', type=int, default=3, help='Machine ID where MongoDB IO is deployed')

    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()

    sched_nginx = march.make_service_sched("CMT", [args.ngxThreads, list(range(30, 30 + args.ngxCores))], None)
    nginx = march.make_serv_inst(servName="nginx", servDomain="", instName="nginx",
                                modelName="nginx", sched=sched_nginx, machId=args.machNxg)

    sched_home_timeline = march.make_service_sched("CMT", [args.htThreads, list(range(30, 30 + args.htCores))], None)
    home_timeline = march.make_serv_inst(servName="home_timeline", servDomain="", instName="home_timeline",
                               modelName="home_timeline", sched=sched_home_timeline, machId=args.machHt)

    sched_home_timeline_redis = march.make_service_sched("Simplified", [args.htRedisThreads, list(range(30, 30 + args.htRedisCores))], None)
    home_timeline_redis = march.make_serv_inst(servName="home_timeline_redis", servDomain="", instName="home_timeline_redis",
                                  modelName="home_timeline_redis", sched=sched_home_timeline_redis, machId=args.machHtRedis)
    
    sched_post_storage = march.make_service_sched("CMT", [args.psThreads, list(range(30, 30 + args.psCores))], None)
    post_storage = march.make_serv_inst(servName="post_storage", servDomain="", instName="post_storage",
                                  modelName="post_storage", sched=sched_post_storage, machId=args.machPs)

    sched_memcached = march.make_service_sched("CMT", [args.mmcThreads, list(range(30, 30 + args.mmcCores))], None)
    memcached = march.make_serv_inst(servName="post_storage_memcached", servDomain="", instName="post_storage_memcached",
                                     modelName="post_storage_memcached", sched=sched_memcached, machId=args.machMmc)

    sched_mongo = march.make_service_sched("CMT", [args.mongoThreads, list(range(30, 30 + args.mongoCores))], None)
    mongodb = march.make_serv_inst(servName="post_storage_mongodb", servDomain="", instName="post_storage_mongodb",
                                   modelName="post_storage_mongodb", sched=sched_mongo, machId=args.machMongo)

    sched_mongo_io = march.make_service_sched("Simplified", [args.mongoIOThreads, list(range(30, 30 + args.mongoIOCores))], None)
    mongodb_io = march.make_serv_inst(servName="mongo_io", servDomain="", instName="mongo_io",
                                      modelName="mongo_io", sched=sched_mongo_io, machId=args.machMongoIO)

    services = [nginx, home_timeline, home_timeline_redis, post_storage, memcached, mongodb, mongodb_io]

    edge_0 = march.make_edge(src="nginx", targ="home_timeline", bidir=True)
    edge_1 = march.make_edge(src="home_timeline", targ="home_timeline_redis", bidir=True)
    edge_2 = march.make_edge(src="home_timeline", targ="post_storage", bidir=True)
    edge_3 = march.make_edge(src="post_storage", targ="post_storage_memcached", bidir=True)
    edge_4 = march.make_edge(src="post_storage", targ="post_storage_mongodb", bidir=True)
    edge_5 = march.make_edge(src="post_storage_mongodb", targ="mongo_io", bidir=True)

    edges = [edge_0, edge_1, edge_2, edge_3, edge_4, edge_5]

    graph = march.make_cluster(services=services, edges=edges)

    with open("./json/graph.json", "w+") as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
	main()