import argparse
import json
import make_arch as march

NUM_QUE = 30

# 2026-11-19: added --postStorageInstances/--mongoInstances replica support,
# mirroring 4tier_multiple/machines.py's pattern (a dedicated load-balancer
# machine per replicated service, one machine per instance). Only
# post_storage and post_storage_mongodb are replicated (the business-logic +
# database analogues of 4tier_multiple's php/mongodb) - nginx, home_timeline,
# home_timeline_redis, and post_storage_memcached stay single-instance, same
# as 4tier_multiple leaves memcached single-instance.
def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--postStorageInstances", type=int, default=1, help="Number of post_storage instances")
	parser.add_argument("--mongoInstances", type=int, default=1, help="Number of post_storage_mongodb instances")

	parser.add_argument("--latency_0_1", type=int, default=0, help="Latency between nginx and home_timeline")
	parser.add_argument("--latency_1_2", type=int, default=0, help="Latency between home_timeline and home_timeline_redis")
	parser.add_argument("--latency_ht_balancerPs", type=int, default=0, help="Latency between home_timeline and the post_storage load balancer")
	parser.add_argument("--latency_balancerPs_ps", type=int, default=0, help="Latency between the post_storage load balancer and each post_storage instance")
	parser.add_argument("--latency_ps_mmc", type=int, default=0, help="Latency between each post_storage instance and post_storage_memcached")
	parser.add_argument("--latency_ps_balancerMongo", type=int, default=0, help="Latency between each post_storage instance and the mongo load balancer")
	parser.add_argument("--latency_balancerMongo_mongo", type=int, default=0, help="Latency between the mongo load balancer and each post_storage_mongodb instance")
	parser.add_argument("--latency_mongo_mongoIo", type=int, default=0, help="Latency between each post_storage_mongodb instance and its mongo_io")
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
	m_ht = march.make_machine(mid = 1, name = "machine_1", cores = 40, netSched = sched)
	m_ht_redis = march.make_machine(mid = 2, name = "machine_2", cores = 40, netSched = sched)
	m_ps_mmc = march.make_machine(mid = 3, name = "machine_3", cores = 40, netSched = sched)
	machines += [m_nginx, m_ht, m_ht_redis, m_ps_mmc]

	l_nginx_ht = march.make_machine_links(0, 1, args.latency_0_1*1000000, 100)
	l_ht_htRedis = march.make_machine_links(1, 2, args.latency_1_2*1000000, 100)
	links += [l_nginx_ht, l_ht_htRedis]

	# load balancer for post_storage
	mach_balancerPs = 4
	m_balancerPs = march.make_machine(mid = mach_balancerPs, name = "machine_" + str(mach_balancerPs), cores = 40, netSched = sched)
	machines.append(m_balancerPs)
	links.append(march.make_machine_links(1, mach_balancerPs, args.latency_ht_balancerPs*1000000, 100))

	cur_machine = mach_balancerPs + 1
	for i in range(0, args.postStorageInstances):
		m_ps = march.make_machine(mid = cur_machine, name = "machine_" + str(cur_machine), cores = 40, netSched = sched)
		machines.append(m_ps)
		links.append(march.make_machine_links(mach_balancerPs, cur_machine, args.latency_balancerPs_ps*1000000, 100))
		links.append(march.make_machine_links(cur_machine, 3, args.latency_ps_mmc*1000000, 100))
		cur_machine += 1

	# load balancer for post_storage_mongodb
	mach_balancerMongo = cur_machine
	m_balancerMongo = march.make_machine(mid = mach_balancerMongo, name = "machine_" + str(mach_balancerMongo), cores = 40, netSched = sched)
	machines.append(m_balancerMongo)
	for i in range(0, args.postStorageInstances):
		# every post_storage instance can reach the (single, shared) mongo load balancer
		links.append(march.make_machine_links(mach_balancerPs + 1 + i, mach_balancerMongo, args.latency_ps_balancerMongo*1000000, 100))
	cur_machine += 1

	for i in range(0, args.mongoInstances):
		m_mongo = march.make_machine(mid = cur_machine, name = "machine_" + str(cur_machine), cores = 40, netSched = sched)
		machines.append(m_mongo)
		links.append(march.make_machine_links(mach_balancerMongo, cur_machine, args.latency_balancerMongo_mongo*1000000, 100))
		m_mongoIo = march.make_machine(mid = cur_machine + args.mongoInstances, name = "machine_" + str(cur_machine + args.mongoInstances), cores = 40, netSched = sched)
		machines.append(m_mongoIo)
		links.append(march.make_machine_links(cur_machine, cur_machine + args.mongoInstances, args.latency_mongo_mongoIo*1000000, 100))
		cur_machine += 1
	cur_machine += args.mongoInstances

	machine_json = march.make_machine_json(machines, links, args.latency_cli*1000000)

	with open("./json/machines.json", "w+") as f:
		json.dump(machine_json, f, indent=2)

if __name__ == "__main__":
	main()
