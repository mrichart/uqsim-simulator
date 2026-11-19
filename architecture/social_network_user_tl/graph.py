import argparse
import json
import make_arch as march

# 2026-11-19: added --postStorageInstances/--mongoInstances replica support
# (mirroring social_network/graph.py, itself mirroring 4tier_multiple). Only
# post_storage and post_storage_mongodb are replicated - nginx,
# user_timeline, user_timeline_redis, user_timeline_mongodb, and
# post_storage_memcached stay single-instance.
def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a service graph with input arguments')
    parser.add_argument('--ngxThreads', type=int, default=8, help='Number of Nginx threads')
    parser.add_argument('--utThreads', type=int, default=8, help='Number of User Timeline threads')
    parser.add_argument('--utRedisThreads', type=int, default=8, help='Number of User Timeline Redis threads')
    parser.add_argument('--utMongoThreads', type=int, default=8, help='Number of User Timeline MongoDB threads')
    parser.add_argument('--psThreads', type=int, default=8, help='Number of Post Storage threads')
    parser.add_argument('--psMmcThreads', type=int, default=8, help='Number of Post Storage Memcached threads')
    parser.add_argument('--psMongoThreads', type=int, default=8, help='Number of Post Storage MongoDB threads')
    parser.add_argument('--psMongoIOThreads', type=int, default=8, help='Number of Post Storage MongoDB IO threads')

    parser.add_argument('--ngxCores', type=int, default=4, help='Number of cores assigned to NGINX')
    parser.add_argument('--utCores', type=int, default=4, help='Number of cores assigned to User Timeline')
    parser.add_argument('--utRedisCores', type=int, default=4, help='Number of cores assigned to User Timeline Redis')
    parser.add_argument('--utMongoCores', type=int, default=4, help='Number of cores assigned to User Timeline MongoDB')
    parser.add_argument('--psCores', type=int, default=4, help='Number of cores assigned to Post Storage')
    parser.add_argument('--psMmcCores', type=int, default=4, help='Number of cores assigned to Post Storage Memcached')
    parser.add_argument('--psMongoCores', type=int, default=4, help='Number of cores assigned to Post Storage MongoDB')
    parser.add_argument('--psMongoIOCores', type=int, default=4, help='Number of cores assigned to Post Storage MongoDB IO')

    parser.add_argument('--postStorageInstances', type=int, default=1, help='Number of instances of post_storage')
    parser.add_argument('--mongoInstances', type=int, default=1, help='Number of instances of post_storage_mongodb')

    parser.add_argument('--machNxg', type=int, default=0, help='Machine ID where NGINX is deployed')
    parser.add_argument('--machUt', type=int, default=1, help='Machine ID where User Timeline is deployed')
    parser.add_argument('--machUtRedis', type=int, default=2, help='Machine ID where User Timeline Redis is deployed')
    parser.add_argument('--machUtMongo', type=int, default=3, help='Machine ID where User Timeline MongoDB is deployed')
    parser.add_argument('--machMmc', type=int, default=4, help='Machine ID where Post Storage Memcached is deployed')
    parser.add_argument('--machBalancerPs', type=int, default=5, help='Machine ID where the post_storage load balancer is deployed')

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

    sched_user_timeline = march.make_service_sched("CMT", [args.utThreads, list(range(30, 30 + args.utCores))], None)
    user_timeline = march.make_serv_inst(servName="user_timeline", servDomain="", instName="user_timeline",
                               modelName="user_timeline", sched=sched_user_timeline, machId=args.machUt)
    services.append(user_timeline)

    sched_user_timeline_redis = march.make_service_sched("Simplified", [args.utRedisThreads, list(range(30, 30 + args.utRedisCores))], None)
    user_timeline_redis = march.make_serv_inst(servName="user_timeline_redis", servDomain="", instName="user_timeline_redis",
                                  modelName="user_timeline_redis", sched=sched_user_timeline_redis, machId=args.machUtRedis)
    services.append(user_timeline_redis)

    sched_user_timeline_mongo = march.make_service_sched("CMT", [args.utMongoThreads, list(range(30, 30 + args.utMongoCores))], None)
    user_timeline_mongo = march.make_serv_inst(servName="user_timeline_mongodb", servDomain="", instName="user_timeline_mongodb",
                                    modelName="user_timeline_mongodb", sched=sched_user_timeline_mongo, machId=args.machUtMongo)
    services.append(user_timeline_mongo)

    sched_memcached = march.make_service_sched("CMT", [args.psMmcThreads, list(range(30, 30 + args.psMmcCores))], None)
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
        sched_mongo = march.make_service_sched("CMT", [args.psMongoThreads, list(range(30, 30 + args.psMongoCores))], None)
        inst_name = "post_storage_mongodb_inst_" + str(i)
        mongodb = march.make_serv_inst(servName="post_storage_mongodb", servDomain="", instName=inst_name,
            modelName="post_storage_mongodb", sched=sched_mongo, machId=cur_machine)
        services.append(mongodb)

        sched_mongo_io = march.make_service_sched("Simplified", [args.psMongoIOThreads, list(range(30, 30 + args.psMongoIOCores))], None)
        inst_name_io = "post_storage_mongo_io_inst_" + str(i)
        mongodb_io = march.make_serv_inst(servName="post_storage_mongo_io", servDomain="", instName=inst_name_io,
            modelName="post_storage_mongo_io", sched=sched_mongo_io, machId=cur_machine + args.mongoInstances)
        services.append(mongodb_io)
        cur_machine += 1

    edges.append(march.make_edge(src="nginx", targ="user_timeline", bidir=True))
    edges.append(march.make_edge(src="user_timeline", targ="user_timeline_redis", bidir=True))
    edges.append(march.make_edge(src="user_timeline", targ="user_timeline_mongodb", bidir=True))
    edges.append(march.make_edge(src="user_timeline", targ="load_balancer_post_storage", bidir=True))

    for i in range(0, args.postStorageInstances):
        ps_name = "post_storage_inst_" + str(i)
        edges.append(march.make_edge(src="load_balancer_post_storage", targ=ps_name, bidir=True))
        edges.append(march.make_edge(src=ps_name, targ="post_storage_memcached", bidir=True))
        edges.append(march.make_edge(src=ps_name, targ="load_balancer_mongo", bidir=True))

    for i in range(0, args.mongoInstances):
        mongo_name = "post_storage_mongodb_inst_" + str(i)
        mongo_io_name = "post_storage_mongo_io_inst_" + str(i)
        edges.append(march.make_edge(src="load_balancer_mongo", targ=mongo_name, bidir=True))
        edges.append(march.make_edge(src=mongo_name, targ=mongo_io_name, bidir=True))

    graph = march.make_cluster(services=services, edges=edges)

    with open("./json/graph.json", "w+") as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
    main()
