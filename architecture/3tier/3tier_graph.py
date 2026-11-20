import sys
import os
import argparse
import json
import make_arch as march

# 2026-11-19: added --mongoInstances replica support (mirroring
# social_network/graph.py's post_storage_mongodb pattern). Only mongodb
# (+ its paired mongo_io) is replicated - nginx and memcached stay
# single-instance.
def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--mongoInstances", type=int, default=1, help="Number of instances of mongodb")

	parser.add_argument("--machNxg", type=int, default=0, help="Machine ID where NGINX is deployed")
	parser.add_argument("--machMmc", type=int, default=1, help="Machine ID where memcached is deployed")
	parser.add_argument("--machBalancerMongo", type=int, default=2, help="Machine ID where the mongodb load balancer is deployed")
	args = parser.parse_args()
	return args

def main():
	args = parse_arguments()

	sched = march.make_service_sched("CMT", [8, [20,21,22,23,24,25,26,27]], None)
	nginx = march.make_serv_inst(servName = "nginx", servDomain = "", instName = "nginx",
		modelName = "nginx", sched = sched, machId = args.machNxg)

	sched = march.make_service_sched("CMT", [4, [20,21,22,23]], None)
	memcached = march.make_serv_inst(servName = "memcached", servDomain = "", instName = "memcached",
		modelName = "memcached", sched = sched, machId = args.machMmc)

	services = [nginx, memcached]
	edges = [march.make_edge(src = "nginx", targ = "memcached", bidir = True)]

	# load balancer for mongodb, one instance
	sched_bal = march.make_service_sched("CMT", [1, [20]], None)
	balancer_mongo = march.make_serv_inst(servName = "load_balancer_mongo", servDomain = "", instName = "load_balancer_mongo",
		modelName = "load_balancer", sched = sched_bal, machId = args.machBalancerMongo)
	services.append(balancer_mongo)
	edges.append(march.make_edge(src = "nginx", targ = "load_balancer_mongo", bidir = True))

	cur_machine = args.machBalancerMongo + 1

	# mongodb, multiple instances, each with its own mongo_io
	for i in range(0, args.mongoInstances):
		sched_mongo = march.make_service_sched("CMT", [300, [20,21,22,23]], None)
		inst_name = "mongodb_inst_" + str(i)
		mongodb = march.make_serv_inst(servName = "mongodb", servDomain = "", instName = inst_name,
			modelName = "mongodb", sched = sched_mongo, machId = cur_machine)
		services.append(mongodb)

		sched_mongo_io = march.make_service_sched("Simplified", [1, [24]], None)
		inst_name_io = "mongo_io_inst_" + str(i)
		mongodb_io = march.make_serv_inst(servName = "mongo_io", servDomain = "", instName = inst_name_io,
			modelName = "mongo_io", sched = sched_mongo_io, machId = cur_machine + args.mongoInstances)
		services.append(mongodb_io)

		edges.append(march.make_edge(src = "load_balancer_mongo", targ = inst_name, bidir = True))
		edges.append(march.make_edge(src = inst_name, targ = inst_name_io, bidir = True))

		cur_machine += 1

	graph = march.make_cluster(services = services, edges = edges, netLat = 65000)

	with open("./json/graph.json", "w+") as f:
		json.dump(graph, f, indent=2)

if __name__ == "__main__":
	main()
