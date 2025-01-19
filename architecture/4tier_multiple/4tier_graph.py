import sys
import os
import json
import make_arch as march 

# This script creates the graph of a 4-tier web application with nginx, memcache, php, mongodb
# There can be multiple instances of php and mongodb
# It also adds a load balancer in front of php and mongodb instances
# The load balancer is a separate service and runs in a separate machine

PHP_INST = 1
MONGO_INST = 1

NGX_THREAD = 32
NGX_CORES = 4
PHP_THREAD = 32
PHP_CORES = 4
PHPIO_QUEUES = 16
MMC_THREAD = 32
MMC_CORES = 4
MONGO_THREAD = 32
MONGO_CORES = 4
MONGOIO_QUEUES = 16

def main():
	services = []
	edges = []

	# nginx service, only one instance in machine 0
	sched = march.make_service_sched("CMT", [NGX_THREAD, list(range(20, 20 + NGX_CORES))], None)
	nginx = march.make_serv_inst(servName = "nginx", servDomain = "", instName = "nginx", 
		modelName = "nginx", sched = sched, machId = 0)
	services.append(nginx)

	# load balancer service for php, only one instance in machine 1
	sched = march.make_service_sched("CMT", [32, [20]], None)
	balance = march.make_serv_inst(servName = "load_balancer_php", servDomain = "", instName = "load_balancer_php",
		modelName = "load_balancer", sched = sched, machId = 1)
	services.append(balance)
	
	# memcached service, only one instance in machine 2
	sched = march.make_service_sched("CMT", [MMC_THREAD,list(range(20, 20 + MMC_CORES))], None)
	memcached = march.make_serv_inst(servName = "memcached", servDomain = "", instName = "memcached", 
		modelName = "memcached", sched = sched, machId = 2)
	services.append(memcached)

	# current machine id for future deployments
	cur_machine = 3

	# php service, multiple instances
	# it includes a php_io service both deployed in the same machine
	for i in range(1, PHP_INST + 1):
		sched = march.make_service_sched("CMT", [PHP_THREAD, list(range(20, 20 + PHP_CORES))], None)
		inst_name = "php_inst_" + str(i - 1)
		php = march.make_serv_inst(servName = "php", servDomain = "", instName = inst_name,
			modelName = "php", sched = sched, machId = cur_machine)
		services.append(php)
		sched = march.make_service_sched("Simplified", [PHPIO_QUEUES, [20 + PHP_CORES]], None)
		inst_name = "php_io_inst_" + str(i - 1)
		php_io = march.make_serv_inst(servName = "php_io", servDomain = "", instName = inst_name, 
			modelName = "php_io", sched = sched, machId = cur_machine)
		services.append(php_io)
		cur_machine += 1

	# load balancer service for mongodb, only one instance one machine 
	sched = march.make_service_sched("CMT", [32, [20]], None)
	balance = march.make_serv_inst(servName = "load_balancer_mongo", servDomain = "", instName = "load_balancer_mongo",
		modelName = "load_balancer", sched = sched, machId = cur_machine)
	services.append(balance)
	cur_machine += 1

	# mongodb service, multiple instances
	# it includes a mongodb_io service both deployed in the same machine
	for i in range(1, MONGO_INST + 1):
		sched = march.make_service_sched("CMT", [MONGO_THREAD, list(range(20, 20 + MONGO_CORES))], None)
		inst_name = "mongodb_inst_" + str(i - 1)
		mongodb = march.make_serv_inst(servName = "mongodb", servDomain = "", instName = inst_name, 
			modelName = "mongodb", sched = sched, machId = cur_machine)
		services.append(mongodb)
		sched = march.make_service_sched("Simplified", [MONGOIO_QUEUES, [20 + MONGO_CORES]], None)
		inst_name = "mongo_io_inst_" + str(i - 1)
		mongodb_io = march.make_serv_inst(servName = "mongo_io", servDomain = "", instName = inst_name,
		modelName = "mongo_io", sched = sched, machId = cur_machine)
		services.append(mongodb_io)
		cur_machine += 1

	edge_0 = march.make_edge(src = "nginx", targ = "memcached", bidir = True)
	edges.append(edge_0)
	edge_1 = march.make_edge(src = "nginx", targ = "load_balancer_php", bidir = True)
	edges.append(edge_1)
	for i in range(1, PHP_INST + 1):		
		edge = march.make_edge(src = "load_balancer_php", targ = "php_inst_" + str(i - 1), bidir = True)
		edges.append(edge)
		edge = march.make_edge(src = "php_inst_" + str(i - 1), targ = "php_io_inst_" + str(i - 1), bidir = True)
		edges.append(edge)
		edge = march.make_edge(src = "php_inst_" + str(i - 1), targ = "load_balancer_mongo", bidir = True)
		edges.append(edge)
		edge = march.make_edge(src = "php_inst_" + str(i - 1), targ = "memcached", bidir = True)
		edges.append(edge)

	for i in range(1, MONGO_INST + 1):		
		edge = march.make_edge(src = "load_balancer_mongo", targ = "mongodb_inst_" + str(i - 1), bidir = True)
		edges.append(edge)
		edge = march.make_edge(src = "mongodb_inst_" + str(i - 1), targ = "mongo_io_inst_" + str(i - 1), bidir = True)
		edges.append(edge)

	graph = march.make_cluster(services = services, edges = edges, netLat = 5000000)

	with open("./json/graph.json", "w+") as f:
		json.dump(graph, f, indent=2)

if __name__ == "__main__":
	main()

