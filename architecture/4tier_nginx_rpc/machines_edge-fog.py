import json
import make_arch as march

NUM_QUE = 30
CLI_LAT = 5000000

def main():
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

	l1 = march.make_machine_links(0, 1, 0, 100)
	l2 = march.make_machine_links(0, 2, 15000000, 100)
	l3 = march.make_machine_links(1, 2, 15000000, 100)
	l4 = march.make_machine_links(2, 3, 0, 100)

	machines = [m0, m1, m2, m3]
	links = [l1, l2, l3, l4]
	machine_json = march.make_machine_json(machines, links, CLI_LAT)

	with open("./json/machines.json", "w+") as f:
		json.dump(machine_json, f, indent=2)

if __name__ == "__main__":
	main()

