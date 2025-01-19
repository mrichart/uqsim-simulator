import sys
import os
import json
import make_arch as march 

def main():
	# path 0: memcached cache hit
	nodeList = []

	node_0 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 0, endStage = -1, 
		nodeId = 0, needSync = False, syncNodeId = None, childs = [1])
	nodeList.append(node_0)

	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 0, startStage = 0, endStage = -1, 
		nodeId = 1, needSync = False, syncNodeId = None, childs = [2])
	nodeList.append(node_1)

	node_2 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 1, startStage = 0, endStage = -1, 
		nodeId = 2, needSync = False, syncNodeId = None, childs = [3])
	nodeList.append(node_2)

	node_3 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1, 
		nodeId = 3, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node_3)

	path_memc_hit = march.make_serv_path(pathId = 0, entry = 0, prob = 86, nodes = nodeList)

	# path 1: memcached miss & mongodb hit

	#new memcache node for code path 1 (miss)
	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1, 
		nodeId = 1, needSync = False, syncNodeId = None, childs = [2])

	# node for load balaner for php
	node_3 = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 3, needSync = False, syncNodeId = None, childs = [4])

	# php_fcgi_req
	# its child is php_io and syncs with next php instance (fopen)
	node_4 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 0, endStage = 0,
		nodeId = 4, needSync = True, syncNodeId = 6, childs = [5])

	node_5 = march.make_serv_path_node(servName = "php_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 5, needSync = False, syncNodeId = None, childs = [6])

	# php_fopen
	# its child is php_io and syncs with next php instance (fput)
	node_6 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 0, endStage = 1,
		nodeId = 6, needSync = True, syncNodeId = 8, childs = [7])

	node_7 = march.make_serv_path_node(servName = "php_io", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 7, needSync = False, syncNodeId = None, childs = [8])

	# php_fput
	# its child is load balancer for mongodb and syncs with next php instance (find_done)
	node_8 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 1, endStage = 2,
		nodeId = 8, needSync = True, syncNodeId = 12, childs = [9])

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node_9 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 9, needSync = False, syncNodeId = None, childs = [10])

	# mongodb instances (hit)
	# its child is the load balancer
	node_10 = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 10, needSync = False, syncNodeId = None, childs = [11])
		
	# node for load balaner for mongodb
	# its childs are previous php instances
	node_11 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 11, needSync = False, syncNodeId = None, childs = [12])

	# php_find_done
	# its child is load balancer for mongo and syncs with next php instance (get_bytes)
	node_12 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 2, endStage = 3,
		nodeId = 12, needSync = True, syncNodeId = 16, childs = [13])

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node_13 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 13, needSync = False, syncNodeId = None, childs = [14])

	# mongodb instances (hit)
	# its child is the load balancer for mongo
	node_14 = march.make_serv_path_node(servName ="mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 14, needSync = False, syncNodeId = None, childs = [15])

	# node for load balaner for mongodb
	# its childs are previous php instances
	node_15 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 15, needSync = False, syncNodeId = None, childs = [16])
	
	# php instances
	# its child is the memcached and syncs with next php instance (mmc_store)
	# php_get_bytes
	node_16 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 3, endStage = 4,
		nodeId = 16, needSync = True, syncNodeId = 18, childs = [17])

	# memcached, same instance for all php instances
	node_17 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 17, needSync = False, syncNodeId = None, childs = [18])

	# php_mmc_store
	# its child is php load balancer
	node_18 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 4, endStage = -1,
		nodeId = 18, needSync = False, syncNodeId = None, childs = [19])

	# node for load balaner for php
	node_19 = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 19, needSync = False, syncNodeId = None, childs = [20])

	node_20 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 2, startStage = 0, endStage = -1,
		nodeId = 20, needSync = False, syncNodeId = None, childs = [21])

	node_21 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1, 
		nodeId = 21, needSync = False, syncNodeId = None, childs = [])
	
	nodeList = [node_0, node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8, node_9, node_10, node_11, node_12, node_13,
			 node_14, node_15, node_16, node_17, node_18, node_19, node_20, node_21]

	path_memc_miss_mongo_hit = march.make_serv_path(pathId = 1, entry = 0, prob = 12, nodes = nodeList)

	# # path 2: memcached miss & mongodb miss #########################################################
	#new memcache node for code path 1 (miss)
	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1, 
		nodeId = 1, needSync = False, syncNodeId = None, childs = [2])

	# node for load balaner for php
	node_3 = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 3, needSync = False, syncNodeId = None, childs = [4])
	
	# php_fcgi_req
	# its child is php_io and syncs with next php instance (fopen)
	node_4 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 0, endStage = 0,
		nodeId = 4, needSync = True, syncNodeId = 6, childs = [5])

	node_5 = march.make_serv_path_node(servName = "php_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 5, needSync = False, syncNodeId = None, childs = [6])

	# php_fopen
	# its child is php_io and syncs with next php instance (fput)
	node_6 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 0, endStage = 1,
		nodeId = 6, needSync = True, syncNodeId = 8, childs = [7])

	node_7 = march.make_serv_path_node(servName = "php_io", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 7, needSync = False, syncNodeId = None, childs = [8])

	# php_fput
	# its child is load balancer for mongodb and syncs with next php instance (find_done)
	node_8 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 1, endStage = 2,
		nodeId = 8, needSync = True, syncNodeId = 14, childs = [9])

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node_9 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 9, needSync = False, syncNodeId = None, childs = [10])

	# mongodb instances (miss)
	node_10 = march.make_serv_path_node(servName ="mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 10, needSync = False, syncNodeId = None, childs = [11])

	node_11 = march.make_serv_path_node(servName = "mongo_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 11, needSync = False, syncNodeId = None, childs = [12])

	node_12 = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 1, startStage = 1, endStage = -1,
		nodeId = 12, needSync = False, syncNodeId = None, childs = [13])

	# node for load balaner for mongodb
	# its childs are previous php instances
	node_13 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 13, needSync = False, syncNodeId = None, childs = [14])

	# php_find_done
	# its child is load balancer for mongo and syncs with next php instance (get_bytes)
	node_14 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 2, endStage = 3,
		nodeId = 14, needSync = True, syncNodeId = 18, childs = [15])

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node_15 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 15, needSync = False, syncNodeId = None, childs = [16])

	# mongodb instances (miss)
	# its child is the load balancer for mongo
	node_16 = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 16, needSync = False, syncNodeId = None, childs = [17])

	# node for load balaner for mongodb
	# its childs are previous php instances
	node_17 = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 17, needSync = False, syncNodeId = None, childs = [18])
	
	# php instances
	# its child is the memcached and syncs with next php instance (mmc_store)
	# php_get_bytes
	node_18 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 3, endStage = 4,
		nodeId = 18, needSync = True, syncNodeId = 20, childs = [19])

	# memcached, same instance for all php instances
	node_19 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = 19, needSync = False, syncNodeId = None, childs = [20])

	# php_mmc_store
	# its child is php load balancer
	node_20 = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 4, endStage = -1,
		nodeId = 20, needSync = False, syncNodeId = None, childs = [21])

	# node for load balaner for php
	node_21 = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 21, needSync = False, syncNodeId = None, childs = [22])

	node_22 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 2, startStage = 0, endStage = -1,
		nodeId = 22, needSync = False, syncNodeId = None, childs = [23])

	node_23 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1, 
		nodeId = 23, needSync = False, syncNodeId = None, childs = [])
	
	nodeList = [node_0, node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8, node_9, node_10, node_11, node_12, node_13,
			 node_14, node_15, node_16, node_17, node_18, node_19, node_20, node_21, node_22, node_23]
	
	# # first access to mongo
	# node_8 = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 1, startStage = 0, endStage = 1,
	# 	nodeId = 8, needSync = True, syncNodeId = 19, childs = [18])

	# node_18 = march.make_serv_path_node(servName = "mongo_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
	# 	nodeId = 18, needSync = False, syncNodeId = None, childs = [19])

	# node_19 = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 1, startStage = 1, endStage = -1,
	# 	nodeId = 19, needSync = False, syncNodeId = None, childs = [9])

	# # second access to mongo, should also access mongo_io, here just for testing internal chunking
	# node_10 = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
	# 	nodeId = 10, needSync = False, syncNodeId = None, childs = [11])

	# nodeList = [node_0, node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8, node_18, node_19, node_9, node_10, node_11, node_12,
	# 	node_13, node_14, node_15]

	path_memc_miss_mongo_miss = march.make_serv_path(pathId = 2, entry = 0, prob = 2, nodes = nodeList)

	paths = [path_memc_hit, path_memc_miss_mongo_hit, path_memc_miss_mongo_miss]

	with open("./json/path.json", "w+") as f:
		json.dump(paths, f, indent=2)

if __name__ == "__main__":
	main()