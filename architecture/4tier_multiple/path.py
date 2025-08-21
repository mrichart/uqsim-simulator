import argparse
import json
import make_arch as march 

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--pPath0", type=int, default=86, help="Ratio (int 0-100) of memcached cache hit")
	parser.add_argument("--pPath1", type=int, default=12, help="Ratio (int 0-100) of memcached miss & mongodb hit")
	parser.add_argument("--pPath2", type=int, default=2, help="Ratio (int 0-100) of memcached miss & mongodb miss")

	parser.add_argument("--phpInstances", type=int, default=1, help="Number of PHP instances")
	parser.add_argument("--mongoInstances", type=int, default=1, help="Number of MongoDB instances")
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
		nodeId = 0, needSync = True, syncNodeId = 2, childs = [1])
	nodeList.append(node_0)

	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 0, startStage = 0, endStage = -1, 
		nodeId = 1, needSync = False, syncNodeId = None, childs = [2])
	nodeList.append(node_1)

	node_2 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 0, startStage = 3, endStage = -1, 
		nodeId = 2, needSync = False, syncNodeId = None, childs = [3])
	nodeList.append(node_2)

	node_3 = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1, 
		nodeId = 3, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node_3)

	path_memc_hit = march.make_serv_path(pathId = 0, entry = 0, prob = pPath0, nodes = nodeList)

	# path 1: memcached miss & mongodb hit

	node_0 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 1, startStage = 0, endStage = 2, 
		nodeId = 0, needSync = True, syncNodeId = 2, childs = [1])

	#new memcache node for code path 1 (miss)
	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1, 
		nodeId = 1, needSync = False, syncNodeId = None, childs = [2])
	
	syncNodeId = 2 + 1 + args.phpInstances*5 + 1 + args.mongoInstances + 1 + args.phpInstances + 1 + args.mongoInstances + 1 + args.phpInstances*3 + 1 + 1

	node_2 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 1, startStage = 3, endStage = 5, 
		nodeId = 2, needSync = True, syncNodeId = syncNodeId, childs = [3])
	
	nodeList = [node_0, node_1, node_2]

	# node for load balaner for php
	node_bal = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 3, needSync = False, syncNodeId = None, childs = list(range(4, args.phpInstances + 4)))
	nodeList.append(node_bal)

	base_node = 4
	
	for i in range(1, args.phpInstances + 1):
		cur_node = base_node + i - 1
		# php_fcgi_req
		# its child is php_io and syncs with next php instance (fopen)
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 0, endStage = 0,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*args.phpInstances, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances
		node = march.make_serv_path_node(servName = "php_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances

		# php_fopen
		# its child is php_io and syncs with next php instance (fput)
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 0, endStage = 1,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*args.phpInstances, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances
		node = march.make_serv_path_node(servName = "php_io", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances

		# php_fput
		# its child is load balancer for mongodb and syncs with next php instance (find_done)
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 1, endStage = 2,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + args.phpInstances + args.mongoInstances + 2, childs = [cur_node + args.phpInstances - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + args.mongoInstances)))
	nodeList.append(node)
	cur_node = cur_node + 1

	# mongodb instances (hit)
	# its child is the load balancer
	for i in range(1, args.mongoInstances + 1):
		node = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.mongoInstances - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are previous php instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + args.phpInstances)))
	nodeList.append(node)
	cur_node = cur_node + 1

	for i in range(1, args.phpInstances + 1):
		# php_find_done
		# its child is load balancer for mongo and syncs with next php instance (get_bytes)
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 2, endStage = 3,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + args.phpInstances + args.mongoInstances + 2, childs = [cur_node + args.phpInstances - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + args.mongoInstances)))
	nodeList.append(node)
	cur_node = cur_node + 1

	# mongodb instances (hit)
	# its child is the load balancer for mongo
	for i in range(1, args.mongoInstances + 1):
		node = march.make_serv_path_node(servName ="mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.mongoInstances - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are previous php instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + args.phpInstances)))
	nodeList.append(node)
	cur_node = cur_node + 1
	
	# php instances
	# its child is the memcached and syncs with next php instance (mmc_store)
	base_node = cur_node
	for i in range(1, args.phpInstances + 1):
		# php_get_bytes
		cur_node = base_node + i - 1
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 3, endStage = 4,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*args.phpInstances, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances

		# memcached, same instance for all php instances
		node = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances

		# php_mmc_store
		# its child is php load balancer
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 4, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.phpInstances - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for php
	node = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + 1])
	nodeList.append(node)
	
	cur_node = cur_node + 1

	node = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 1, startStage = 6, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + 1])
	nodeList.append(node)
	cur_node = cur_node + 1

	node = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1, 
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node)

	path_memc_miss_mongo_hit = march.make_serv_path(pathId = 1, entry = 0, prob = pPath1, nodes = nodeList)

	# path 2: memcached miss & mongodb miss
	
	#new memcache node for code path 1 (miss)
	node_1 = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1, 
		nodeId = 1, needSync = False, syncNodeId = None, childs = [2])
	
	syncNodeId = 2 + 1 + args.phpInstances*5 + 1 + args.mongoInstances*3 + 1 + args.phpInstances + 1 + args.mongoInstances + 1 + args.phpInstances*3 + 1 + 1

	node_2 = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 1, startStage = 3, endStage = 5, 
		nodeId = 2, needSync = True, syncNodeId = syncNodeId, childs = [3])
	
	nodeList = [node_0, node_1, node_2]

	# node for load balaner for php
	node_3 = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = 3, needSync = False, syncNodeId = None, childs = list(range(4, args.phpInstances + 4)))
	nodeList.append(node_3)

	base_node = 4
	
	for i in range(1, args.phpInstances + 1):
		cur_node = base_node + i - 1
		# php_fcgi_req
		# its child is php_io and syncs with next php instance (fopen)
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 0, endStage = 0,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*args.phpInstances, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances
		node = march.make_serv_path_node(servName = "php_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances

		# php_fopen
		# its child is php_io and syncs with next php instance (fput)
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 0, endStage = 1,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*args.phpInstances, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances
		node = march.make_serv_path_node(servName = "php_io", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances

		# php_fput
		# its child is load balancer for mongodb and syncs with next php instance (find_done)
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 1, endStage = 2,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + args.phpInstances + 3*args.mongoInstances + 2, childs = [cur_node + args.phpInstances - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + args.mongoInstances)))
	nodeList.append(node)
	cur_node = cur_node + 1

	# mongodb instances (miss)
	# its child is the load balancer
	base_node = cur_node
	for i in range(1, args.mongoInstances + 1):
		cur_node = base_node + i - 1
		node = march.make_serv_path_node(servName ="mongodb", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.mongoInstances])
		nodeList.append(node)
		cur_node = cur_node + args.mongoInstances

		node = march.make_serv_path_node(servName = "mongo_io", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.mongoInstances])
		nodeList.append(node)
		cur_node = cur_node + args.mongoInstances

		node = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 1, startStage = 1, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.mongoInstances - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are previous php instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + args.phpInstances)))
	nodeList.append(node)
	cur_node = cur_node + 1

	for i in range(1, args.phpInstances + 1):
		# php_find_done
		# its child is load balancer for mongo and syncs with next php instance (get_bytes)
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 2, endStage = 3,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + args.phpInstances + args.mongoInstances + 2, childs = [cur_node + args.phpInstances - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are mongodb instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + args.mongoInstances)))
	nodeList.append(node)
	cur_node = cur_node + 1

	# mongodb instances (miss)
	# its child is the load balancer for mongo
	for i in range(1, args.mongoInstances + 1):
		node = march.make_serv_path_node(servName = "mongodb", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.mongoInstances - i + 1])
		nodeList.append(node)
		cur_node = cur_node + 1

	# node for load balaner for mongodb
	# its childs are previous php instances
	node = march.make_serv_path_node(servName = "load_balancer_mongo", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = list(range(cur_node + 1, cur_node + 1 + args.phpInstances)))
	nodeList.append(node)
	cur_node = cur_node + 1
	
	# php instances
	# its child is the memcached and syncs with next php instance (mmc_store)
	base_node = cur_node
	for i in range(1, args.phpInstances + 1):
		# php_get_bytes
		cur_node = base_node + i - 1
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 3, endStage = 4,
			nodeId = cur_node, needSync = True, syncNodeId = cur_node + 2*args.phpInstances, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances

		# memcached, same instance for all php instances
		node = march.make_serv_path_node(servName = "memcached", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.phpInstances])
		nodeList.append(node)
		cur_node = cur_node + args.phpInstances

		# php_mmc_store
		# its child is php load balancer
		node = march.make_serv_path_node(servName = "php", servDomain = "", codePath = 0, startStage = 4, endStage = -1,
			nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + args.phpInstances - i + 1])
		nodeList.append(node)

	cur_node = cur_node + 1

	# node for load balaner for php
	node = march.make_serv_path_node(servName = "load_balancer_php", servDomain = "", codePath = 0, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + 1])
	nodeList.append(node)
	cur_node = cur_node + 1

	node = march.make_serv_path_node(servName = "nginx", servDomain = "", codePath = 1, startStage = 0, endStage = -1,
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [cur_node + 1])
	nodeList.append(node)
	cur_node = cur_node + 1

	node = march.make_serv_path_node(servName = "client", servDomain = "", codePath = -1, startStage = 0, endStage = -1, 
		nodeId = cur_node, needSync = False, syncNodeId = None, childs = [])
	nodeList.append(node)

	path_memc_miss_mongo_miss = march.make_serv_path(pathId = 2, entry = 0, prob = pPath2, nodes = nodeList)

	paths = [path_memc_hit, path_memc_miss_mongo_hit, path_memc_miss_mongo_miss]

	with open("./json/path.json", "w+") as f:
		json.dump(paths, f, indent=2)

if __name__ == "__main__":
	main()