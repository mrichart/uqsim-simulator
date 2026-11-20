import sys
import os
import json
import argparse
import make_arch as march


# 2026-11-19: added --pPath0/1/2 CLI args (previously hardcoded 86/12/2) and
# --mongoInstances replica support. Per the pattern established for
# social_network/social_network_user_tl: path.json's structure is
# instance-count-invariant (the actual N-way fan-out across mongodb replicas
# is resolved at the graph.json/machines.json level + the simulator's
# sendChn-based runtime resolution), so path.py takes no instance-count args.
# What path.py *does* need is a dedicated, non-syncing "load_balancer_mongo"
# node inserted at every crossing between the replicated mongodb domain and
# anything else (nginx), in both directions - one pair for path 1 (mongo
# hit) and a separate pair for path 2 (mongo miss), since the surrounding
# node ids differ between the two paths and can't be shared. The
# mongodb -> mongo_io -> mongodb handoff inside path 2 stays untouched: it's
# internal to a single mongodb instance (paired per-instance in graph.py),
# not a crossing.
def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--pPath0", type=int, default=86, help="Ratio (int 0-100) of memcached cache hit")
	parser.add_argument("--pPath1", type=int, default=12, help="Ratio (int 0-100) of memcached miss & mongodb hit")
	parser.add_argument("--pPath2", type=int, default=2, help="Ratio (int 0-100) of memcached miss & mongodb miss")
	args = parser.parse_args()
	return args

def main():
	args = parse_arguments()
	assert args.pPath0 + args.pPath1 + args.pPath2 == 100, "Probabilities do not sum to 100"

	# path 0: memcached cache hit
	nodeList = []

	node_0 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 0, needSync = False, syncNodeId = None, childs = [1])
	nodeList.append(node_0)

	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 1, needSync = False, syncNodeId = None, childs = [2])
	nodeList.append(node_1)

	# should be a different nginx path
	node_2 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 2, needSync = False,  syncNodeId = None, childs = [3])
	nodeList.append(node_2)

	node_3 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1,
		nodeId = 3, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node_3)

	path_memc_hit = march.make_serv_path(pathId = 0, entry = 0, prob = args.pPath0, nodes = nodeList)


	# path 1: memcached miss mongo hit
	base_node_id = 4
	nodeList = []
	node_0 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 0 + base_node_id, needSync = False, syncNodeId = None, childs = [1 + base_node_id])
	nodeList.append(node_0)

	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 1 + base_node_id, needSync = False, syncNodeId = None, childs = [2 + base_node_id])
	nodeList.append(node_1)

	# should be a different nginx path
	node_2 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 2 + base_node_id, needSync = False, syncNodeId = None, childs = [22])
	nodeList.append(node_2)

	# non-syncing dispatch hop into the mongodb domain (replica support,
	# 2026-11-19) - NOT a rename of node_3: the simulator's LoadBalancer
	# model resolves this to a specific mongodb_inst_N (see graph.py).
	node_22 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 22, needSync = False, syncNodeId = None, childs = [3 + base_node_id])
	nodeList.append(node_22)

	node_3 = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 3 + base_node_id, needSync = False, syncNodeId = None, childs = [23])
	nodeList.append(node_3)

	# return hop (mongodb -> nginx) - the dispatched mongodb instance has no
	# sendChn visibility into "nginx" directly, only the balancer does.
	node_23 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 23, needSync = False, syncNodeId = None, childs = [4 + base_node_id])
	nodeList.append(node_23)

	node_4 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 4 + base_node_id, needSync = False, syncNodeId = None, childs = [5 + base_node_id])
	nodeList.append(node_4)

	node_5 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 5 + base_node_id, needSync = False, syncNodeId = None, childs = [6 + base_node_id])
	nodeList.append(node_5)

	node_6 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 6 + base_node_id, needSync = False, syncNodeId = None, childs = [7 + base_node_id])
	nodeList.append(node_6)

	node_7 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1,
		nodeId = 7 + base_node_id, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node_7)

	path_memc_miss_mongo_hit = march.make_serv_path(pathId = 1, entry = base_node_id, prob = args.pPath1, nodes = nodeList)


	base_node_id = 12

	# path 2: memcached miss mongo miss
	nodeList = []
	node_0 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 0 + base_node_id, needSync = False, syncNodeId = None, childs = [1 + base_node_id])
	nodeList.append(node_0)

	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 1 + base_node_id, needSync = False, syncNodeId = None, childs = [2 + base_node_id])
	nodeList.append(node_1)

	# should be a different nginx path
	node_2 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 2 + base_node_id, needSync = False, syncNodeId = None, childs = [24])
	nodeList.append(node_2)

	# non-syncing dispatch hop into the mongodb domain (replica support,
	# 2026-11-19), mirrors node_22 above (separate node: the surrounding
	# node ids differ between path 1 and path 2, so the balancer node can't
	# be shared between them).
	node_24 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 24, needSync = False, syncNodeId = None, childs = [3 + base_node_id])
	nodeList.append(node_24)

	node_3 = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 1, startStage = 0, endStage = 1,
		nodeId = 3 + base_node_id, needSync = True, syncNodeId = 5 + base_node_id, childs = [4 + base_node_id])
	nodeList.append(node_3)

	node_4 = march.make_serv_path_node(servName = "mongo_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 4 + base_node_id, needSync = False, syncNodeId = None, childs = [5 + base_node_id])
	nodeList.append(node_4)

	node_5 = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 1, startStage = 2, endStage = -1,
		nodeId = 5 + base_node_id, needSync = False, syncNodeId = None, childs = [25])
	nodeList.append(node_5)

	# return hop (mongodb -> nginx), mirrors node_23 above.
	node_25 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 25, needSync = False, syncNodeId = None, childs = [6 + base_node_id])
	nodeList.append(node_25)

	node_6 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 6 + base_node_id, needSync = False, syncNodeId = None, childs = [7 + base_node_id])
	nodeList.append(node_6)

	node_7 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 7 + base_node_id, needSync = False, syncNodeId = None, childs = [8 + base_node_id])
	nodeList.append(node_7)

	node_8 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 8 + base_node_id, needSync = False, syncNodeId = None, childs = [9 + base_node_id])
	nodeList.append(node_8)

	node_9 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1,
		nodeId = 9 + base_node_id, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node_9)

	path_memc_miss_mongo_miss = march.make_serv_path(pathId = 2, entry = base_node_id, prob = args.pPath2, nodes = nodeList)



	paths = [path_memc_hit, path_memc_miss_mongo_hit, path_memc_miss_mongo_miss]

	with open("./json/path.json", "w+") as f:
		json.dump(paths, f, indent=2)

if __name__ == "__main__":
	main()
