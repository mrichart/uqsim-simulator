import sys
import os
import argparse
import json
import make_arch as march

NUM_QUE = 20

# 2026-11-19: added --mongoInstances replica support - one machine per
# mongodb instance plus one for its paired mongo_io, on top of the fixed
# nginx/memcached/load_balancer_mongo machines (mirrors 3tier_graph.py's
# machine id scheme exactly).
def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--mongoInstances", type=int, default=1, help="Number of instances of mongodb")
	parser.add_argument("--machBalancerMongo", type=int, default=2, help="Machine ID where the mongodb load balancer is deployed")
	args = parser.parse_args()
	return args

def main():
	args = parse_arguments()
	global NUM_QUE
	core_aff = []
	for i in range(0, NUM_QUE):
		aff = march.make_Simp_core_aff(i, [i])
		core_aff.append(aff)
	core_list = list(range(0, NUM_QUE))
	sched = march.make_service_sched("LinuxNetStack", [NUM_QUE, core_list], core_aff)

	num_machines = args.machBalancerMongo + 1 + 2 * args.mongoInstances
	machines = []
	for mid in range(0, num_machines):
		machines.append(march.make_machine(mid = mid, name = "machine_" + str(mid), cores = 40, netSched = sched))

	def make_link(mid1, mid2):
		return {"machine_id_1": mid1, "machine_id_2": mid2, "latency": 0, "capacity": 100}

	# 2026-11-19: links must mirror 3tier_graph.py's edges exactly - every
	# machine pair whose services communicate needs an explicit entry here
	# (confirmed by reading src/cluster_parser.cc: NetStack::send() asserts a
	# connection exists for a pair, and connections are only created for
	# listed links). nginx<->memcached, nginx<->load_balancer_mongo,
	# load_balancer_mongo<->each mongodb instance, mongodb<->its own mongo_io.
	mach_nxg, mach_mmc, mach_bal = 0, 1, args.machBalancerMongo
	links = [make_link(mach_nxg, mach_mmc), make_link(mach_nxg, mach_bal)]

	cur_machine = mach_bal + 1
	for i in range(0, args.mongoInstances):
		links.append(make_link(mach_bal, cur_machine))
		links.append(make_link(cur_machine, cur_machine + args.mongoInstances))
		cur_machine += 1

	# 2026-11-19: wrap machines in the {"machines", "links", "client_latency"}
	# shape cluster_parser.cc actually expects (confirmed by reading
	# src/cluster_parser.cc directly) - the previous bare-list output was
	# never compatible with the current simulator (a latent, pre-existing
	# bug, same vein as the python2 print statements and the range()/list()
	# issue fixed alongside this). No per-link latency modeling requested for
	# 3tier, so every link carries latency 0.
	machine_json = {"machines": machines, "links": links, "client_latency": 0}

	with open("./json/machines.json", "w+") as f:
		json.dump(machine_json, f, indent=2)

if __name__ == "__main__":
	main()
