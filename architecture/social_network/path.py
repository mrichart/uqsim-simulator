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
		nodeId = 3, needSync = True, syncNodeId = 7, childs = [4])
	nodeList.append(node_3)

	node_4 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = 0,
		nodeId = 4, needSync = True, syncNodeId = 6, childs = [5])
	nodeList.append(node_4)

	node_5 = march.make_serv_path_node(servName = "post_storage_memcached", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 5, needSync = False, syncNodeId = None, childs = [6])
	nodeList.append(node_5)

	node_6 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 6, needSync = False, syncNodeId = None, childs = [7])
	nodeList.append(node_6)

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
		nodeId = 6, needSync = True, syncNodeId = 12, childs = [11])

	node_11 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 11, needSync = False, syncNodeId = None, childs = [12])
	
	node_12 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 1, endStage = 2,
		nodeId = 12, needSync = True, syncNodeId = 14, childs = [13])

	node_13 = march.make_serv_path_node(servName = "post_storage_memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 13, needSync = False, syncNodeId = None, childs = [14])

	node_14 = march.make_serv_path_node(servName = "post_storage", servDomain = "", codePath = 1, startStage = 2, endStage = -1,
		nodeId = 14, needSync = False, syncNodeId = None, childs = [7])
	
	nodeList = [node_0, node_1, node_2, node_3, node_4, node_5, node_6, node_11, node_12, node_13, node_14, node_7, node_8, node_9]

	path_memc_miss_mongo_hit = march.make_serv_path(pathId = 1, entry = 0, prob = pPath1, nodes = nodeList)

	# path 2: memcached miss & mongodb miss
	
	node_11 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 1, startStage = 0, endStage = 1,
		nodeId = 11, needSync = True, syncNodeId = 16, childs = [15])

	node_15 = march.make_serv_path_node(servName = "mongo_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 15, needSync = False, syncNodeId = None, childs = [16])

	node_16 = march.make_serv_path_node(servName = "post_storage_mongodb", servDomain = "", codePath = 1, startStage = 1, endStage = -1,
		nodeId = 16, needSync = False, syncNodeId = None, childs = [12])

	nodeList = [node_0, node_1, node_2, node_3, node_4, node_5, node_6, node_11, node_15, node_16, node_12,
		node_13, node_14, node_7, node_8, node_9]

	path_memc_miss_mongo_miss = march.make_serv_path(pathId = 2, entry = 0, prob = pPath2, nodes = nodeList)

	paths = [path_memc_hit, path_memc_miss_mongo_hit, path_memc_miss_mongo_miss]

	with open("./json/path.json", "w+") as f:
		json.dump(paths, f, indent=2)

if __name__ == "__main__":
	main()