import argparse
import json
import make_arch as march

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--pPath0", type=int, default=64, help="Ratio (int 0-100) of redis hit & memcached cache hit")
	parser.add_argument("--pPath1", type=int, default=12, help="Ratio (int 0-100) of redis hit & memcached miss & mongodb hit")
	parser.add_argument("--pPath2", type=int, default=3, help="Ratio (int 0-100) of redis hit & memcached miss & mongodb miss")
	parser.add_argument("--pPath3", type=int, default=16, help="Ratio (int 0-100) of redis miss & mongo hit & memcached hit")
	parser.add_argument("--pPath4", type=int, default=3, help="Ratio (int 0-100) of redis miss & mongo hit & memcached miss & mongodb hit")
	parser.add_argument("--pPath5", type=int, default=2, help="Ratio (int 0-100) of redis miss & mongo hit & memcached miss & mongodb miss")
	args = parser.parse_args()
	return args

# 2026-11-19 (replica support): post_storage + post_storage_mongodb are
# replicated (same choice as plain social_network/path.py), exactly mirroring
# 4tier_multiple's pattern: path.json's node structure does NOT depend on
# instance count (start_architecture.py never forwards instance counts to
# path.py - confirmed empirically). What's needed instead is a dedicated,
# non-syncing load_balancer-named dispatch node at EVERY crossing into or out
# of the replicated domain, in BOTH directions, and sync_node_id pairs must
# keep matching servName on both ends (so the existing post_storage /
# post_storage_mongodb nodes and their sync chains are left untouched; only
# the routing edges feeding INTO them are redirected through a balancer node).
#
# Unlike plain social_network (one redis-hit/miss-free entry point), this app
# forks on user_timeline_redis hit/miss BEFORE reaching post_storage, so the
# user_timeline->post_storage crossing and the post_storage->user_timeline
# return crossing each occur at TWO independent, non-unifiable points in the
# graph (one per redis branch) - hence 2 distinct load_balancer_post_storage
# dispatch nodes for entry and 2 for return, not 1. Same reasoning applies to
# the post_storage<->post_storage_mongodb crossing (2 for entry, 2 for
# return), since it's nested once per redis branch. Total: 8 new nodes.
def main():
	args = parse_arguments()
	pPath0 = args.pPath0
	pPath1 = args.pPath1
	pPath2 = args.pPath2
	pPath3 = args.pPath3
	pPath4 = args.pPath4
	pPath5 = args.pPath5
	assert pPath0 + pPath1 + pPath2 + pPath3 + pPath4 + pPath5 == 100, "Probabilities do not sum to 100"

	# path 0: redis hit and memcached cache hit
	nodeList = []

	node_0 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = 2,
		nodeId = 0, needSync = True, syncNodeId = 8, childs = [1])
	nodeList.append(node_0)

	node_1 = march.make_serv_path_node(servName = "user_timeline", servDomain = "", codePath = 0, startStage = 0, endStage = 2,
		nodeId = 1, needSync = True, syncNodeId = 3, childs = [2])
	nodeList.append(node_1)

	node_2 = march.make_serv_path_node(servName = "user_timeline_redis", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 2, needSync = False, syncNodeId = None, childs = [3])
	nodeList.append(node_2)

	# node_3's childs redirected 4 -> 19 (B_ps_in_1): entry crossing into the
	# replicated post_storage domain. Shared unchanged by path1/path2 below
	# (they reuse this same node_3 object).
	node_3 = march.make_serv_path_node(servName = "user_timeline", servDomain = "", codePath = 0, startStage = 2, endStage = 4,
		nodeId = 3, needSync = True, syncNodeId = 7, childs = [19])
	nodeList.append(node_3)

	node_19 = march.make_serv_path_node(servName = "load_balancer_post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 19, needSync = False, syncNodeId = None, childs = [4])
	nodeList.append(node_19)

	node_4 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = 0,
		nodeId = 4, needSync = True, syncNodeId = 6, childs = [5])
	nodeList.append(node_4)

	node_5 = march.make_serv_path_node(servName = "post_storage_memcached", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 5, needSync = False, syncNodeId = None, childs = [6])
	nodeList.append(node_5)

	# node_6's childs redirected 7 -> 25 (B_ps_out_1): return crossing out of
	# the replicated post_storage domain back to user_timeline.
	node_6 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 6, needSync = False, syncNodeId = None, childs = [25])
	nodeList.append(node_6)

	node_25 = march.make_serv_path_node(servName = "load_balancer_post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 25, needSync = False, syncNodeId = None, childs = [7])
	nodeList.append(node_25)

	node_7 = march.make_serv_path_node(servName = "user_timeline", servDomain = "", codePath = 0, startStage = 5, endStage = -1,
		nodeId = 7, needSync = False, syncNodeId = None, childs = [8])
	nodeList.append(node_7)

	node_8 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 3, endStage = -1,
		nodeId = 8, needSync = False, syncNodeId = None, childs = [9])
	nodeList.append(node_8)

	node_9 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1,
		nodeId = 9, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node_9)

	path_memc_hit = march.make_serv_path(pathId = 0, entry = 0, prob = pPath0, nodes = nodeList)

	# path 1: redis hit & memcached miss & mongodb hit

	node_4 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 0, endStage = 0,
		nodeId = 4, needSync = True, syncNodeId = 6, childs = [5])

	# node_6's childs redirected 10 -> 21 (B_mongo_in_1): entry crossing into
	# the replicated post_storage_mongodb domain.
	node_6 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 0, endStage = 1,
		nodeId = 6, needSync = True, syncNodeId = 11, childs = [21])

	node_21 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 21, needSync = False, syncNodeId = None, childs = [10])

	# node_10's childs redirected 11 -> 23 (B_mongo_out_1): return crossing out
	# of post_storage_mongodb back into post_storage. Shared unchanged by
	# path2's node_15 below (same target balancer, different source node).
	node_10 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 10, needSync = False, syncNodeId = None, childs = [23])

	node_23 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 23, needSync = False, syncNodeId = None, childs = [11])

	node_11 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 1, endStage = 2,
		nodeId = 11, needSync = True, syncNodeId = 13, childs = [12])

	node_12 = march.make_serv_path_node(servName = "post_storage_memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 12, needSync = False, syncNodeId = None, childs = [13])

	# node_13's childs redirected 7 -> 25 (B_ps_out_1, reused from path0).
	node_13 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 2, endStage = -1,
		nodeId = 13, needSync = False, syncNodeId = None, childs = [25])

	nodeList = [node_0, node_1, node_2, node_3, node_19, node_4, node_5, node_6, node_21, node_10, node_23, node_11, node_12, node_13, node_25, node_7, node_8, node_9]

	path_memc_miss_mongo_hit = march.make_serv_path(pathId = 1, entry = 0, prob = pPath1, nodes = nodeList)

	# path 2: redis hit & memcached miss & mongodb miss

	node_10 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 1, startStage = 0, endStage = 1,
		nodeId = 10, needSync = True, syncNodeId = 15, childs = [14])

	node_14 = march.make_serv_path_node(servName = "post_storage_mongo_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 14, needSync = False, syncNodeId = None, childs = [15])

	# node_15's childs redirected 11 -> 23 (B_mongo_out_1, reused from path1).
	node_15 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 1, startStage = 1, endStage = -1,
		nodeId = 15, needSync = False, syncNodeId = None, childs = [23])

	nodeList = [node_0, node_1, node_2, node_3, node_19, node_4, node_5, node_6, node_21, node_10, node_14, node_15, node_23, node_11,
		node_12, node_13, node_25, node_7, node_8, node_9]

	path_memc_miss_mongo_miss = march.make_serv_path(pathId = 2, entry = 0, prob = pPath2, nodes = nodeList)

	# path 3: redis miss & memcached hit

	nodeList = []

	node_0 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = 2,
		nodeId = 0, needSync = True, syncNodeId = 11, childs = [1])
	nodeList.append(node_0)

	node_1 = march.make_serv_path_node(servName = "user_timeline", servDomain = "", codePath = 0, startStage = 0, endStage = 2,
		nodeId = 1, needSync = True, syncNodeId = 3, childs = [2])
	nodeList.append(node_1)

	node_2 = march.make_serv_path_node(servName = "user_timeline_redis", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 2, needSync = False, syncNodeId = None, childs = [3])
	nodeList.append(node_2)

	node_3 = march.make_serv_path_node(servName = "user_timeline", servDomain = "", codePath = 0, startStage = 2, endStage = 3,
		nodeId = 3, needSync = True, syncNodeId = 5, childs = [4])
	nodeList.append(node_3)

	node_4 = march.make_serv_path_node(servName = "user_timeline_mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 4, needSync = False, syncNodeId = None, childs = [5])
	nodeList.append(node_4)

	# node_5's fork childs redirected [6,7] -> [6,20] (B_ps_in_2): entry
	# crossing into post_storage for the redis-miss branch. This is the
	# SECOND, independent entry point into the post_storage domain (the
	# redis-hit branch's entry is node_19 above) - cannot be unified since
	# the source node and sync chain differ.
	node_5 = march.make_serv_path_node(servName = "user_timeline", servDomain = "", codePath = 0, startStage = 3, endStage = 4,
		nodeId = 5, needSync = True, syncNodeId = 10, childs = [6, 20])
	nodeList.append(node_5)

	node_6 = march.make_serv_path_node(servName = "user_timeline_redis", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 6, needSync = False, syncNodeId = None, childs = [10])
	nodeList.append(node_6)

	node_20 = march.make_serv_path_node(servName = "load_balancer_post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 20, needSync = False, syncNodeId = None, childs = [7])
	nodeList.append(node_20)

	node_7 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = 0,
		nodeId = 7, needSync = True, syncNodeId = 9, childs = [8])
	nodeList.append(node_7)

	node_8 = march.make_serv_path_node(servName = "post_storage_memcached", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 8, needSync = False, syncNodeId = None, childs = [9])
	nodeList.append(node_8)

	# node_9's childs redirected 10 -> 26 (B_ps_out_2): return crossing out of
	# post_storage for the redis-miss branch (second, independent return
	# point - the redis-hit branch's return is node_25 above).
	node_9 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 9, needSync = False, syncNodeId = None, childs = [26])
	nodeList.append(node_9)

	node_26 = march.make_serv_path_node(servName = "load_balancer_post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 26, needSync = False, syncNodeId = None, childs = [10])
	nodeList.append(node_26)

	node_10 = march.make_serv_path_node(servName = "user_timeline", servDomain = "", codePath = 0, startStage = 5, endStage = -1,
		nodeId = 10, needSync = False, syncNodeId = None, childs = [11])
	nodeList.append(node_10)

	node_11 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 3, endStage = -1,
		nodeId = 11, needSync = False, syncNodeId = None, childs = [12])
	nodeList.append(node_11)

	node_12 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1,
		nodeId = 12, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node_12)

	path_redis_miss_mmc_hit = march.make_serv_path(pathId = 3, entry = 0, prob = pPath3, nodes = nodeList)

	# path 4: redis miss & memcached miss & mongodb hit

	node_7 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 0, endStage = 0,
		nodeId = 7, needSync = True, syncNodeId = 9, childs = [8])

	# node_9's childs redirected 13 -> 22 (B_mongo_in_2): entry crossing into
	# post_storage_mongodb for the redis-miss branch (second, independent
	# entry point into mongo - the redis-hit branch's is node_21 above).
	node_9 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 0, endStage = 1,
		nodeId = 9, needSync = True, syncNodeId = 14, childs = [22])

	node_22 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 22, needSync = False, syncNodeId = None, childs = [13])

	# node_13's childs redirected 14 -> 24 (B_mongo_out_2): return crossing out
	# of post_storage_mongodb (second, independent return point - the
	# redis-hit branch's is node_23 above). Shared unchanged by path5's
	# node_18 below.
	node_13 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 13, needSync = False, syncNodeId = None, childs = [24])

	node_24 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 24, needSync = False, syncNodeId = None, childs = [14])

	node_14 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 1, endStage = 2,
		nodeId = 14, needSync = True, syncNodeId = 16, childs = [15])

	node_15 = march.make_serv_path_node(servName = "post_storage_memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 15, needSync = False, syncNodeId = None, childs = [16])

	# node_16's childs redirected 10 -> 26 (B_ps_out_2, reused from path3).
	node_16 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 2, endStage = -1,
		nodeId = 16, needSync = False, syncNodeId = None, childs = [26])

	nodeList = [node_0, node_1, node_2, node_3, node_4, node_5, node_6, node_20, node_7, node_8, node_9, node_22, node_13, node_24, node_14, node_15, node_16, node_26, node_10, node_11, node_12]

	path_redis_miss_mmc_miss_mongo_hit = march.make_serv_path(pathId = 4, entry = 0, prob = pPath4, nodes = nodeList)

	# path 5: redis miss & memcached miss & mongodb miss

	node_13 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 1, startStage = 0, endStage = 1,
		nodeId = 13, needSync = True, syncNodeId = 18, childs = [17])

	node_17 = march.make_serv_path_node(servName = "post_storage_mongo_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 17, needSync = False, syncNodeId = None, childs = [18])

	# node_18's childs redirected 14 -> 24 (B_mongo_out_2, reused from path4).
	node_18 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 1, startStage = 1, endStage = -1,
		nodeId = 18, needSync = False, syncNodeId = None, childs = [24])

	nodeList = [node_0, node_1, node_2, node_3, node_4, node_5, node_6, node_20, node_7, node_8, node_9, node_22, node_13, node_17, node_18, node_24, node_14, node_15, node_16, node_26, node_10, node_11, node_12]

	path_redis_miss_mmc_miss_mongo_miss = march.make_serv_path(pathId = 5, entry = 0, prob = pPath5, nodes = nodeList)

	paths = [path_memc_hit, path_memc_miss_mongo_hit, path_memc_miss_mongo_miss, path_redis_miss_mmc_hit, path_redis_miss_mmc_miss_mongo_hit, path_redis_miss_mmc_miss_mongo_miss]

	with open("./json/path.json", "w+") as f:
		json.dump(paths, f, indent=2)

if __name__ == "__main__":
	main()
