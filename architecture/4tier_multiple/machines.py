import argparse
import json
import make_arch as march

NUM_QUE = 30

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--phpInstances', type=int, default=1, help='Number of PHP instances')
	parser.add_argument('--mongoInstances', type=int, default=1, help='Number of MongoDB instances')

	parser.add_argument('--latency_nginx_mmc', type=int, default=0, help='Latency between machine 0 and 1')
	parser.add_argument('--latency_nginx_balancerPhp', type=int, default=0, help='Latency between machine 0 and 2')
	parser.add_argument('--latency_mmc_php', type=int, default=0, help='Latency between machine 1 and phpInstances')
	parser.add_argument('--latency_balancerPhp_php', type=int, default=0, help='Latency between machine 2 and phpInstances')
	parser.add_argument('--latency_php_phpIo', type=int, default=0, help='Latency between machine phpInstances and phpIoInstances')
	parser.add_argument('--latency_php_balancerMongo', type=int, default=0, help='Latency between machine phpInstances and balancerMongo')
	parser.add_argument('--latency_balancerMongo_mongo', type=int, default=0, help='Latency between machine balancerMongo and mongoInstances')
	parser.add_argument('--latency_mongo_mongoIo', type=int, default=0, help='Latency between machine mongoInstances and mongoIoInstances')
	parser.add_argument("--latency_cli", type=int, default=0, help="Latency between client and machine 0")
	args = parser.parse_args()
	return args

def main():
	args = parse_args()
	global NUM_QUE
	core_aff = []
	for i in range(0, NUM_QUE):
		aff = march.make_Simp_core_aff(i, [i])
		core_aff.append(aff)
	core_list = list(range(0, NUM_QUE))
	sched = march.make_service_sched("LinuxNetStack", [NUM_QUE, core_list], core_aff)

	machines = []
	links = []

	
	m_nginx = march.make_machine(mid = 0, name = "machine_0", cores = 40, netSched = sched)
	m_mmc = march.make_machine(mid = 1, name = "machine_1", cores = 40, netSched = sched)
	m_balancerPhp = march.make_machine(mid = 2, name = "machine_2", cores = 40, netSched = sched)
	machines.append(m_nginx)
	machines.append(m_mmc)
	machines.append(m_balancerPhp)

	l_nginx_mmc = march.make_machine_links(0, 1, args.latency_nginx_mmc*1000000, 100)
	l_nginx_balancerPhp = march.make_machine_links(0, 2, args.latency_nginx_balancerPhp*1000000, 100)
	links.append(l_nginx_mmc)
	links.append(l_nginx_balancerPhp)

	for i in range(3, 3 + args.phpInstances):
		m_php = march.make_machine(mid = i, name = "machine_" + str(i), cores = 40, netSched = sched)
		machines.append(m_php)
		m_phpIo = march.make_machine(mid = i + args.phpInstances, name = "machine_" + str(i + args.phpInstances), cores = 40, netSched = sched)
		machines.append(m_phpIo)
		l_mmc_php = march.make_machine_links(1, i, args.latency_mmc_php*1000000, 100)
		l_balancerPhp_php = march.make_machine_links(2, i, args.latency_balancerPhp_php*1000000, 100)
		l_php_phpIo = march.make_machine_links(i, i + args.phpInstances, args.latency_php_phpIo*1000000, 100)
		l_php_balancerMongo = march.make_machine_links(i, 3 + 2*args.phpInstances, args.latency_php_balancerMongo*1000000, 100)
		links.append(l_mmc_php)
		links.append(l_balancerPhp_php)
		links.append(l_php_phpIo)
		links.append(l_php_balancerMongo)

	# current machine id for future deployments
	cur_machine = 3 + 2*args.phpInstances

	mach_balancerMongo = march.make_machine(mid = cur_machine, name = "machine_" + str(cur_machine), cores = 40, netSched = sched)
	machines.append(mach_balancerMongo)
	cur_machine += 1
	
	for i in range(cur_machine, cur_machine + args.mongoInstances):
		m_mongo = march.make_machine(mid = i, name = "machine_" + str(i), cores = 40, netSched = sched)
		machines.append(m_mongo)
		m_mongoIo = march.make_machine(mid = i + args.mongoInstances, name = "machine_" + str(i + args.mongoInstances), cores = 40, netSched = sched)
		machines.append(m_mongoIo)
		l_balancerMongo_mongo = march.make_machine_links(cur_machine-1, i, args.latency_balancerMongo_mongo*1000000, 100)
		l_mongo_mongoIo = march.make_machine_links(i, i + args.mongoInstances, args.latency_mongo_mongoIo*1000000, 100)
		links.append(l_balancerMongo_mongo)
		links.append(l_mongo_mongoIo)


	machine_json = march.make_machine_json(machines, links, args.latency_cli*1000000)

	with open("./json/machines.json", "w+") as f:
		json.dump(machine_json, f, indent=2)

if __name__ == "__main__":
	main()

