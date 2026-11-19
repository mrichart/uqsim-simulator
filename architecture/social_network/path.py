import argparse
import json
import make_arch as march 

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--pPath0", type=int, default=80, help="Ratio (int 0-100) of memcached cache hit")
	parser.add_argument("--pPath1", type=int, default=15, help="Ratio (int 0-100) of memcached miss & mongodb hit")
	parser.add_argument("--pPath2", type=int, default=5, help="Ratio (int 0-100) of memcached miss & mongodb miss")
	args = parser.parse_args()
	return args

def main():
	args = parse_arguments()
	pPath0 = args.pPath0
	pPath1 = args.pPath1
	pPath2 = args.pPath2
	assert pPath0 + pPath1 + pPath2 == 100, "Probabilities do not sum to 100"

	# path 0: memcached cache hit
	nodeList = []

	node_0 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = 2, 
		nodeId = 0, needSync = True, syncNodeId = 8, childs = [1])
	nodeList.append(node_0)

	node_1 = march.make_serv_path_node(servName = "home_timeline", servDomain = "", codePath = 0, startStage = 0, endStage = 2, 
		nodeId = 1, needSync = True, syncNodeId = 3, childs = [2])
	nodeList.append(node_1)
	
	node_2 = march.make_serv_path_node(servName = "home_timeline_redis", servDomain = "", codePath = 0, startStage = 0, endStage = -1, 
		nodeId = 2, needSync = False, syncNodeId = None, childs = [3])
	nodeList.append(node_2)
	
	node_3 = march.make_serv_path_node(servName = "home_timeline", servDomain = "", codePath = 0, startStage = 2, endStage = 3,
		nodeId = 3, needSync = True, syncNodeId = 7, childs = [17])
	nodeList.append(node_3)

	# 2026-11-19 (replica support): a separate, non-syncing dispatch hop into
	# post_storage, mirroring 4tier_multiple/path.py's load_balancer_php node
	# exactly. NOT a rename of node_4 - sync_node_id pairs require matching
	# servName on both ends (confirmed by the simulator's own assertion:
	# "syncNode 6 is not in the same (servName,...) tuple"), and node_4's own
	# internal sync chain (4 -> 6 -> 12 -> 14) must keep servName="post_storage"
	# throughout, exactly as before replicas existed. This new node_17 is
	# purely a one-way routing hop the LoadBalancer resolves to a specific
	# post_storage_inst_N (see graph.py); node_4 onward is unchanged.
	node_17 = march.make_serv_path_node(servName = "load_balancer_post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 17, needSync = False, syncNodeId = None, childs = [4])
	nodeList.append(node_17)

	node_4 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = 0,
		nodeId = 4, needSync = True, syncNodeId = 6, childs = [5])
	nodeList.append(node_4)

	node_5 = march.make_serv_path_node(servName = "post_storage_memcached", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 5, needSync = False, syncNodeId = None, childs = [6])
	nodeList.append(node_5)

	node_6 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 6, needSync = False, syncNodeId = None, childs = [20])
	nodeList.append(node_6)

	# 2026-11-19 (replica support): the RETURN hop (post_storage ->
	# home_timeline) also needs a fresh load_balancer_post_storage node -
	# the specific post_storage_inst that was dispatched to has no sendChn
	# visibility into "home_timeline" directly, only the balancer does (via
	# its bidirectional edge to home_timeline in graph.py). Mirrors
	# 4tier_multiple's final load_balancer_php->nginx hop.
	node_20 = march.make_serv_path_node(servName = "load_balancer_post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 20, needSync = False, syncNodeId = None, childs = [7])
	nodeList.append(node_20)

	node_7 = march.make_serv_path_node(servName = "home_timeline", servDomain = "", codePath = 0, startStage = 4, endStage = -1,
		nodeId = 7, needSync = False, syncNodeId = None, childs = [8])
	nodeList.append(node_7)

	node_8 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 3, endStage = -1,
		nodeId = 8, needSync = False, syncNodeId = None, childs = [9])
	nodeList.append(node_8)

	node_9 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1, 
		nodeId = 9, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node_9)

	path_memc_hit = march.make_serv_path(pathId = 0, entry = 0, prob = pPath0, nodes = nodeList)

	# path 1: memcached miss & mongodb hit

	node_4 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 0, endStage = 0,
		nodeId = 4, needSync = True, syncNodeId = 6, childs = [5])

	node_6 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 0, endStage = 1,
		nodeId = 6, needSync = True, syncNodeId = 12, childs = [18])

	# 2026-11-19 (replica support): same rationale as node_17 above - a
	# separate, non-syncing dispatch hop into post_storage_mongodb, mirroring
	# 4tier_multiple's load_balancer_mongo node. node_11 onward keeps its
	# original sync chain (11 -> [16 ->] 12 -> 14) with servName unchanged.
	node_18 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 18, needSync = False, syncNodeId = None, childs = [11])

	node_11 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 11, needSync = False, syncNodeId = None, childs = [19])

	# 2026-11-19 (replica support): the RETURN hop (post_storage_mongodb ->
	# post_storage) needs its own fresh load_balancer_mongo node too - every
	# crossing between two replicated domains needs an explicit balancer hop
	# in EACH direction (confirmed against 4tier_multiple/path.py, which
	# inserts a new load_balancer_mongo node for every single php<->mongodb
	# handoff, not just the first). Without this, the mongodb instance that
	# was dispatched to has no sendChn visibility into "post_storage" at all.
	node_19 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 19, needSync = False, syncNodeId = None, childs = [12])

	node_12 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 1, endStage = 2,
		nodeId = 12, needSync = True, syncNodeId = 14, childs = [13])

	node_13 = march.make_serv_path_node(servName = "post_storage_memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 13, needSync = False, syncNodeId = None, childs = [14])

	# See 2026-11-19 note above (node_20) - same return-hop requirement.
	node_14 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 2, endStage = -1,
		nodeId = 14, needSync = False, syncNodeId = None, childs = [20])

	nodeList = [node_0, node_1, node_2, node_3, node_17, node_4, node_5, node_6, node_18, node_11, node_19, node_12, node_13, node_14, node_20, node_7, node_8, node_9]

	path_memc_miss_mongo_hit = march.make_serv_path(pathId = 1, entry = 0, prob = pPath1, nodes = nodeList)

	# path 2: memcached miss & mongodb miss

	node_11 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 1, startStage = 0, endStage = 1,
		nodeId = 11, needSync = True, syncNodeId = 16, childs = [15])

	node_15 = march.make_serv_path_node(servName = "mongo_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 15, needSync = False, syncNodeId = None, childs = [16])

	# See 2026-11-19 note above (node_19) - node_16 is the other path's
	# return point into post_storage, needs the same fresh balancer hop.
	node_16 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 1, startStage = 1, endStage = -1,
		nodeId = 16, needSync = False, syncNodeId = None, childs = [19])

	nodeList = [node_0, node_1, node_2, node_3, node_17, node_4, node_5, node_6, node_18, node_11, node_15, node_16, node_19, node_12,
		node_13, node_14, node_20, node_7, node_8, node_9]

	path_memc_miss_mongo_miss = march.make_serv_path(pathId = 2, entry = 0, prob = pPath2, nodes = nodeList)

	paths = [path_memc_hit, path_memc_miss_mongo_hit, path_memc_miss_mongo_miss]

	with open("./json/path.json", "w+") as f:
		json.dump(paths, f, indent=2)

if __name__ == "__main__":
	main()