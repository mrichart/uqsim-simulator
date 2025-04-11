import sys
import os
import json
import make_arch as march 

PHP_INST = 3
MONGO_INST = 1

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
	
	nodeList = [node_0, node_1, node_2]

	# node for load balaner for php
	node_3 = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 3, needSync = False, syncNodeId = None, childs = list(range(4, PHP_INST + 4)))
	nodeList.append(node_3)

	base_node = 4
	
	for i in range(1, PHP_INST + 1):
		cur_node = base_node + i - 1
		# php_fcgi_req
		# its child is php_io and syncs with next php instance (fopen)
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 0, endStage = 0,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*PHP_INST, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST
		node = march.make_serv_path_node(servName = "php_io_inst_"  + str(i - 1), servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST

		# php_fopen
		# its child is php_io and syncs with next php instance (fput)
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 0, endStage = 1,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*PHP_INST, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST
		node = march.make_serv_path_node(servName = "php_io_inst_"  + str(i - 1), servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST

		# php_fput
		# its child is load balancer for mongodb and syncs with next php instance (find_done)
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 1, endStage = 2,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + PHP_INST + MONGO_INST + 2, childs = [cur_node + PHP_INST - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + MONGO_INST)))
	nodeList.append(node)
	cur_node = cur_node + 1

	# mongodb instances (hit)
	# its child is the load balancer
	for i in range(1, MONGO_INST + 1):
		node = march.make_serv_path_node(servName = "mongodb_inst_"  + str(i - 1), servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + MONGO_INST - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are previous php instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + PHP_INST)))
	nodeList.append(node)
	cur_node = cur_node + 1

	for i in range(1, PHP_INST + 1):
		# php_find_done
		# its child is load balancer for mongo and syncs with next php instance (get_bytes)
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 2, endStage = 3,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + PHP_INST + MONGO_INST + 2, childs = [cur_node + PHP_INST - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + MONGO_INST)))
	nodeList.append(node)
	cur_node = cur_node + 1

	# mongodb instances (hit)
	# its child is the load balancer for mongo
	for i in range(1, MONGO_INST + 1):
		node = march.make_serv_path_node(servName ="mongodb_inst_"  + str(i - 1), servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + MONGO_INST - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are previous php instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + PHP_INST)))
	nodeList.append(node)
	cur_node = cur_node + 1
	
	# php instances
	# its child is the memcached and syncs with next php instance (mmc_store)
	base_node = cur_node
	for i in range(1, PHP_INST + 1):
		# php_get_bytes
		cur_node = base_node + i - 1
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 3, endStage = 4,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*PHP_INST, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST

		# memcached, same instance for all php instances
		node = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST

		# php_mmc_store
		# its child is php load balancer
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 4, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + PHP_INST - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for php
	node = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + 1])
	nodeList.append(node)
	cur_node = cur_node + 1

	node = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 2, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + 1])
	nodeList.append(node)
	cur_node = cur_node + 1

	node = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1, 
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node)

	path_memc_miss_mongo_hit = march.make_serv_path(pathId = 1, entry = 0, prob = 12, nodes = nodeList)

	# # path 2: memcached miss & mongodb miss
	#new memcache node for code path 1 (miss)
	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1, 
		nodeId = 1, needSync = False, syncNodeId = None, childs = [2])
	
	nodeList = [node_0, node_1, node_2]

	# node for load balaner for php
	node_3 = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 3, needSync = False, syncNodeId = None, childs = list(range(4, PHP_INST + 4)))
	nodeList.append(node_3)

	base_node = 4
	
	for i in range(1, PHP_INST + 1):
		cur_node = base_node + i - 1
		# php_fcgi_req
		# its child is php_io and syncs with next php instance (fopen)
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 0, endStage = 0,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*PHP_INST, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST
		node = march.make_serv_path_node(servName = "php_io_inst_"  + str(i - 1), servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST

		# php_fopen
		# its child is php_io and syncs with next php instance (fput)
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 0, endStage = 1,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*PHP_INST, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST
		node = march.make_serv_path_node(servName = "php_io_inst_"  + str(i - 1), servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST

		# php_fput
		# its child is load balancer for mongodb and syncs with next php instance (find_done)
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 1, endStage = 2,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + PHP_INST + 3*MONGO_INST + 2, childs = [cur_node + PHP_INST - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + MONGO_INST)))
	nodeList.append(node)
	cur_node = cur_node + 1

	# mongodb instances (miss)
	# its child is the load balancer
	base_node = cur_node
	for i in range(1, MONGO_INST + 1):
		cur_node = base_node + i - 1
		node = march.make_serv_path_node(servName ="mongodb_inst_"  + str(i - 1), servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + MONGO_INST])
		nodeList.append(node)
		cur_node = cur_node + MONGO_INST

		node = march.make_serv_path_node(servName = "mongo_io_inst_", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + MONGO_INST])
		nodeList.append(node)
		cur_node = cur_node + MONGO_INST

		node = march.make_serv_path_node(servName = "mongodb_inst_", servDomain = "", codePath = 1, startStage = 1, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + MONGO_INST - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are previous php instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + PHP_INST)))
	nodeList.append(node)
	cur_node = cur_node + 1

	for i in range(1, PHP_INST + 1):
		# php_find_done
		# its child is load balancer for mongo and syncs with next php instance (get_bytes)
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 2, endStage = 3,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + PHP_INST + MONGO_INST + 2, childs = [cur_node + PHP_INST - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + MONGO_INST)))
	nodeList.append(node)
	cur_node = cur_node + 1

	# mongodb instances (miss)
	# its child is the load balancer for mongo
	for i in range(1, MONGO_INST + 1):
		node = march.make_serv_path_node(servName = "mongodb_inst_"  + str(i - 1), servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + MONGO_INST - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are previous php instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + PHP_INST)))
	nodeList.append(node)
	cur_node = cur_node + 1
	
	# php instances
	# its child is the memcached and syncs with next php instance (mmc_store)
	base_node = cur_node
	for i in range(1, PHP_INST + 1):
		# php_get_bytes
		cur_node = base_node + i - 1
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 3, endStage = 4,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*PHP_INST, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST

		# memcached, same instance for all php instances
		node = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + PHP_INST])
		nodeList.append(node)
		cur_node = cur_node + PHP_INST

		# php_mmc_store
		# its child is php load balancer
		node = march.make_serv_path_node(servName = "php_inst_" + str(i - 1), servDomain = "", codePath = 0, startStage = 4, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + PHP_INST - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for php
	node = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + 1])
	nodeList.append(node)
	cur_node = cur_node + 1

	node = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 2, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + 1])
	nodeList.append(node)
	cur_node = cur_node + 1

	node = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1, 
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node)
	
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