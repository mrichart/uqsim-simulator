import argparse
import json
import make_arch as march

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a service graph with input arguments')
    parser.add_argument('--ngxThreads', type=int, default=8, help='Number of Nginx threads')
    parser.add_argument('--utThreads', type=int, default=8, help='Number of User Timeline threads')
    parser.add_argument('--utRedisThreads', type=int, default=8, help='Number of User Timeline Redis threads')
    parser.add_argument('--utMongoThreads', type=int, default=8, help='Number of User Timeline MongoDB threads')
    parser.add_argument('--utMongoIOThreads', type=int, default=8, help='Number of User Timeline MongoDB IO threads')
    parser.add_argument('--psThreads', type=int, default=8, help='Number of Post Storage threads')
    parser.add_argument('--psMmcThreads', type=int, default=8, help='Number of Post Storage Memcached threads')
    parser.add_argument('--psMongoThreads', type=int, default=8, help='Number of Post Storage MongoDB threads')
    parser.add_argument('--psMongoIOThreads', type=int, default=8, help='Number of Post Storage MongoDB IO threads')

    parser.add_argument('--ngxCores', type=int, default=4, help='Number of cores assigned to NGINX')
    parser.add_argument('--utCores', type=int, default=4, help='Number of cores assigned to User Timeline')
    parser.add_argument('--utRedisCores', type=int, default=4, help='Number of cores assigned to User Timeline Redis')
    parser.add_argument('--utMongoCores', type=int, default=4, help='Number of cores assigned to User Timeline MongoDB')
    parser.add_argument('--utMongoIOCores', type=int, default=4, help='Number of cores assigned to User Timeline MongoDB IO')
    parser.add_argument('--psCores', type=int, default=4, help='Number of cores assigned to Post Storage')
    parser.add_argument('--psMmcCores', type=int, default=4, help='Number of cores assigned to Post Storage Memcached')
    parser.add_argument('--psMongoCores', type=int, default=4, help='Number of cores assigned to Post Storage MongoDB')
    parser.add_argument('--psMongoIOCores', type=int, default=4, help='Number of cores assigned to Post Storage MongoDB IO')
    
    parser.add_argument('--machNxg', type=int, default=0, help='Machine ID where NGINX is deployed')
    parser.add_argument('--machUt', type=int, default=1, help='Machine ID where User Timeline is deployed')
    parser.add_argument('--machUtRedis', type=int, default=2, help='Machine ID where User Timeline Redis is deployed')
    parser.add_argument('--machUtMongo', type=int, default=3, help='Machine ID where User Timeline MongoDB is deployed')
    parser.add_argument('--machUtMongoIO', type=int, default=4, help='Machine ID where User Timeline MongoDB IO is deployed')
    parser.add_argument('--machPs', type=int, default=5, help='Machine ID where Post Storage is deployed')
    parser.add_argument('--machPsMmc', type=int, default=6, help='Machine ID where Post Storage Memcached is deployed')
    parser.add_argument('--machPsMongo', type=int, default=7, help='Machine ID where Post Storage MongoDB is deployed')
    parser.add_argument('--machPsMongoIO', type=int, default=8, help='Machine ID where Post Storage MongoDB IO is deployed')

    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()

    sched_nginx = march.make_service_sched("CMT", [args.ngxThreads, list(range(30, 30 + args.ngxCores))], None)
    nginx = march.make_serv_inst(servName="nginx", servDomain="", instName="nginx",
                                modelName="nginx", sched=sched_nginx, machId=args.machNxg)

    sched_user_timeline = march.make_service_sched("CMT", [args.utThreads, list(range(30, 30 + args.utCores))], None)
    user_timeline = march.make_serv_inst(servName="user_timeline", servDomain="", instName="user_timeline",
                               modelName="user_timeline", sched=sched_user_timeline, machId=args.machUt)

    sched_user_timeline_redis = march.make_service_sched("Simplified", [args.utRedisThreads, list(range(30, 30 + args.utRedisCores))], None)
    user_timeline_redis = march.make_serv_inst(servName="user_timeline_redis", servDomain="", instName="user_timeline_redis",
                                  modelName="user_timeline_redis", sched=sched_user_timeline_redis, machId=args.machUtRedis)

    sched_user_timeline_mongo = march.make_service_sched("CMT", [args.utMongoThreads, list(range(30, 30 + args.utMongoCores))], None)
    user_timeline_mongo = march.make_serv_inst(servName="user_timeline_mongodb", servDomain="", instName="user_timeline_mongodb",
                                    modelName="user_timeline_mongodb", sched=sched_user_timeline_mongo, machId=args.machUtMongo)

    sched_user_timeline_mongo_io = march.make_service_sched("Simplified", [args.utMongoIOThreads, list(range(30, 30 + args.utMongoIOCores))], None)
    user_timeline_mongo_io = march.make_serv_inst(servName="user_timeline_mongo_io", servDomain="", instName="user_timeline_mongo_io",
                                        modelName="user_timeline_mongo_io", sched=sched_user_timeline_mongo_io, machId=args.machUtMongoIO)                                
    
    sched_post_storage = march.make_service_sched("CMT", [args.psThreads, list(range(30, 30 + args.psCores))], None)
    post_storage = march.make_serv_inst(servName="post_storage", servDomain="", instName="post_storage",
                                  modelName="post_storage", sched=sched_post_storage, machId=args.machPs)

    sched_post_storage_memcached = march.make_service_sched("CMT", [args.psMmcThreads, list(range(30, 30 + args.psMmcCores))], None)
    post_storage_memcached = march.make_serv_inst(servName="post_storage_memcached", servDomain="", instName="post_storage_memcached",
                                     modelName="post_storage_memcached", sched=sched_post_storage_memcached, machId=args.machPsMmc)

    sched_post_storage_mongodb = march.make_service_sched("CMT", [args.psMongoThreads, list(range(30, 30 + args.psMongoCores))], None)
    post_storage_mongodb = march.make_serv_inst(servName="post_storage_mongodb", servDomain="", instName="post_storage_mongodb",
                                   modelName="post_storage_mongodb", sched=sched_post_storage_mongodb, machId=args.machPsMongo)

    sched_post_storage_mongo_io = march.make_service_sched("Simplified", [args.psMongoIOThreads, list(range(30, 30 + args.psMongoIOCores))], None)
    post_storage_mongo_io = march.make_serv_inst(servName="post_storage_mongo_io", servDomain="", instName="post_storage_mongo_io",
                                      modelName="post_storage_mongo_io", sched=sched_post_storage_mongo_io, machId=args.machPsMongoIO)

    services = [nginx, user_timeline, user_timeline_redis, user_timeline_mongo, user_timeline_mongo_io, post_storage, post_storage_memcached, post_storage_mongodb, post_storage_mongo_io]

    edge_0 = march.make_edge(src="nginx", targ="user_timeline", bidir=True)
    edge_1 = march.make_edge(src="user_timeline", targ="user_timeline_redis", bidir=True)
    edge_2 = march.make_edge(src="user_timeline", targ="user_timeline_mongodb", bidir=True)
    edge_3 = march.make_edge(src="user_timeline_mongodb", targ="user_timeline_mongo_io", bidir=True)
    edge_4 = march.make_edge(src="user_timeline", targ="post_storage", bidir=True)
    edge_5 = march.make_edge(src="post_storage", targ="post_storage_memcached", bidir=True)
    edge_6 = march.make_edge(src="post_storage", targ="post_storage_mongodb", bidir=True)
    edge_7 = march.make_edge(src="post_storage_mongodb", targ="post_storage_mongo_io", bidir=True)

    edges = [edge_0, edge_1, edge_2, edge_3, edge_4, edge_5, edge_6, edge_7]

    graph = march.make_cluster(services=services, edges=edges)

    with open("./json/graph.json", "w+") as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
	main()