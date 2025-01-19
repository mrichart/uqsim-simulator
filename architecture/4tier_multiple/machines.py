import sys
import os
import json
import make_arch as march 

NUM_QUE = 20
NUM_CORES = 40
NUM_MACHINES = 9

def main():
	global NUM_QUE
	core_aff = []
	for i in range(0, NUM_QUE):
		aff = march.make_Simp_core_aff(i, [i])
		core_aff.append(aff)
	core_list = list(range(0, NUM_QUE))
	sched = march.make_service_sched("LinuxNetStack", [NUM_QUE, core_list], core_aff)

	machines = []
	for i in range (0, NUM_MACHINES):
		m = march.make_machine(mid = i, name = "machine_" + str(i), cores = NUM_CORES, netSched = sched)
		machines.append(m)

	with open("./json/machines.json", "w+") as f:
		json.dump(machines, f, indent=2)

if __name__ == "__main__":
	main()

