import argparse
import json
import make_arch as march

# 2026-11-19: added --postStorageInstances/--mongoInstances replica support
# (mirroring 4tier_multiple/graph.py). Only post_storage and
# post_storage_mongodb are replicated - nginx, home_timeline,
# home_timeline_redis, and post_storage_memcached stay single-instance.
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

    parser.add_argument('--postStorageInstances', type=int, default=1, help='Number of instances of post_storage')
    parser.add_argument('--mongoInstances', type=int, default=1, help='Number of instances of post_storage_mongodb')

    parser.add_argument('--machNxg', type=int, default=0, help='Machine ID where NGINX is deployed')
    parser.add_argument('--machHt', type=int, default=1, help='Machine ID where Home Timeline is deployed')
    parser.add_argument('--machHtRedis', type=int, default=2, help='Machine ID where Home Timeline Redis is deployed')
    parser.add_argument('--machMmc', type=int, default=3, help='Machine ID where Memcached is deployed')
    parser.add_argument('--machBalancerPs', type=int, default=4, help='Machine ID where the post_storage load balancer is deployed')

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

    sched_home_timeline = march.make_service_sched("CMT", [args.htThreads, list(range(30, 30 + args.htCores))], None)
    home_timeline = march.make_serv_inst(servName="home_timeline", servDomain="", instName="home_timeline",
                               modelName="home_timeline", sched=sched_home_timeline, machId=args.machHt)
    services.append(home_timeline)

    sched_home_timeline_redis = march.make_service_sched("Simplified", [args.htRedisThreads, list(range(30, 30 + args.htRedisCores))], None)
    home_timeline_redis = march.make_serv_inst(servName="home_timeline_redis", servDomain="", instName="home_timeline_redis",
                                  modelName="home_timeline_redis", sched=sched_home_timeline_redis, machId=args.machHtRedis)
    services.append(home_timeline_redis)

    sched_memcached = march.make_service_sched("CMT", [args.mmcThreads, list(range(30, 30 + args.mmcCores))], None)
    memcached = march.make_serv_inst(servName="post_storage_memcached", servDomain="", instName="post_storage_memcached",
                                     modelName="post_storage_memcached", sched=sched_memcached, machId=args.machMmc)
    services.append(memcached)

    # load balancer for post_storage, one instance
    sched_bal = march.make_service_sched("CMT", [1, [30]], None)
    balancer_ps = march.make_serv_inst(servName="load_balancer_post_storage", servDomain="", instName="load_balancer_post_storage",
        modelName="load_balancer", sched=sched_bal, machId=args.machBalancerPs)
    services.append(balancer_ps)

    cur_machine = args.machBalancerPs + 1

    # post_storage, multiple instances
    for i in range(0, args.postStorageInstances):
        sched_ps = march.make_service_sched("CMT", [args.psThreads, list(range(30, 30 + args.psCores))], None)
        inst_name = "post_storage_inst_" + str(i)
        post_storage = march.make_serv_inst(servName="post_storage", servDomain="", instName=inst_name,
            modelName="post_storage", sched=sched_ps, machId=cur_machine)
        services.append(post_storage)
        cur_machine += 1

    # load balancer for post_storage_mongodb, one instance, shared across all post_storage instances
    mach_balancerMongo = cur_machine
    sched_bal2 = march.make_service_sched("CMT", [1, [30]], None)
    balancer_mongo = march.make_serv_inst(servName="load_balancer_mongo", servDomain="", instName="load_balancer_mongo",
        modelName="load_balancer", sched=sched_bal2, machId=mach_balancerMongo)
    services.append(balancer_mongo)
    cur_machine += 1

    # post_storage_mongodb, multiple instances, each with its own mongo_io
    for i in range(0, args.mongoInstances):
        sched_mongo = march.make_service_sched("CMT", [args.mongoThreads, list(range(30, 30 + args.mongoCores))], None)
        inst_name = "post_storage_mongodb_inst_" + str(i)
        mongodb = march.make_serv_inst(servName="post_storage_mongodb", servDomain="", instName=inst_name,
            modelName="post_storage_mongodb", sched=sched_mongo, machId=cur_machine)
        services.append(mongodb)

        sched_mongo_io = march.make_service_sched("Simplified", [args.mongoIOThreads, list(range(30, 30 + args.mongoIOCores))], None)
        inst_name_io = "mongo_io_inst_" + str(i)
        mongodb_io = march.make_serv_inst(servName="mongo_io", servDomain="", instName=inst_name_io,
            modelName="mongo_io", sched=sched_mongo_io, machId=cur_machine + args.mongoInstances)
        services.append(mongodb_io)
        cur_machine += 1

    edges.append(march.make_edge(src="nginx", targ="home_timeline", bidir=True))
    edges.append(march.make_edge(src="home_timeline", targ="home_timeline_redis", bidir=True))
    edges.append(march.make_edge(src="home_timeline", targ="load_balancer_post_storage", bidir=True))

    for i in range(0, args.postStorageInstances):
        ps_name = "post_storage_inst_" + str(i)
        edges.append(march.make_edge(src="load_balancer_post_storage", targ=ps_name, bidir=True))
        edges.append(march.make_edge(src=ps_name, targ="post_storage_memcached", bidir=True))
        edges.append(march.make_edge(src=ps_name, targ="load_balancer_mongo", bidir=True))

    for i in range(0, args.mongoInstances):
        mongo_name = "post_storage_mongodb_inst_" + str(i)
        mongo_io_name = "mongo_io_inst_" + str(i)
        edges.append(march.make_edge(src="load_balancer_mongo", targ=mongo_name, bidir=True))
        edges.append(march.make_edge(src=mongo_name, targ=mongo_io_name, bidir=True))

    graph = march.make_cluster(services=services, edges=edges)

    with open("./json/graph.json", "w+") as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
    main()
