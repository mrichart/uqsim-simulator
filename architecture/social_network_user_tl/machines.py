import argparse
import json
import make_arch as march

NUM_QUE = 30

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--latency_0_1", type=int, default=0, help="Latency between machine 0 and 1")
	parser.add_argument("--latency_1_2", type=int, default=0, help="Latency between machine 1 and 2")
	parser.add_argument("--latency_1_3", type=int, default=0, help="Latency between machine 1 and 3")
	parser.add_argument("--latency_3_4", type=int, default=0, help="Latency between machine 3 and 4")
	parser.add_argument("--latency_1_5", type=int, default=0, help="Latency between machine 1 and 5")
	parser.add_argument("--latency_5_6", type=int, default=0, help="Latency between machine 5 and 6")
	parser.add_argument("--latency_5_7", type=int, default=0, help="Latency between machine 5 and 7")
	parser.add_argument("--latency_7_8", type=int, default=0, help="Latency between machine 7 and 8")
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
	m0 = march.make_machine(mid = 0, name = "machine_0", cores = 40, netSched = sched)
	m1 = march.make_machine(mid = 1, name = "machine_1", cores = 40, netSched = sched)
	m2 = march.make_machine(mid = 2, name = "machine_2", cores = 40, netSched = sched)
	m3 = march.make_machine(mid = 3, name = "machine_3", cores = 40, netSched = sched)
	m4 = march.make_machine(mid = 4, name = "machine_4", cores = 40, netSched = sched)
	m5 = march.make_machine(mid = 5, name = "machine_5", cores = 40, netSched = sched)
	m6 = march.make_machine(mid = 6, name = "machine_6", cores = 40, netSched = sched)
	m7 = march.make_machine(mid = 7, name = "machine_7", cores = 40, netSched = sched)
	m8 = march.make_machine(mid = 8, name = "machine_8", cores = 40, netSched = sched)

	l1 = march.make_machine_links(0, 1, args.latency_0_1*1000000, 100)
	l2 = march.make_machine_links(1, 2, args.latency_1_2*1000000, 100)
	l3 = march.make_machine_links(1, 3, args.latency_1_3*1000000, 100)
	l4 = march.make_machine_links(3, 4, args.latency_3_4*1000000, 100)
	l5 = march.make_machine_links(1, 5, args.latency_1_5*1000000, 100)
	l6 = march.make_machine_links(5, 6, args.latency_5_6*1000000, 100)
	l7 = march.make_machine_links(5, 7, args.latency_5_7*1000000, 100)
	l8 = march.make_machine_links(7, 8, args.latency_7_8*1000000, 100)

	machines = [m0, m1, m2, m3, m4, m5, m6, m7, m8]
	links = [l1, l2, l3, l4, l5, l6, l7, l8]
	machine_json = march.make_machine_json(machines, links, args.latency_cli*1000000)

	with open("./json/machines.json", "w+") as f:
		json.dump(machine_json, f, indent=2)

if __name__ == "__main__":
	main()

