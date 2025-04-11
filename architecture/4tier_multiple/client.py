import json
import argparse
import make_arch as march

def parse_arguments():
	parser = argparse.ArgumentParser(description='Generate a service graph with input arguments')
	parser.add_argument('--end_seconds', type=int, default=60, help='Epoch end time in seconds')
	parser.add_argument('--monitor_interval', type=int, default=0, help='Interval at which the client will monitor the system (in seconds)')
	args = parser.parse_args()
	return args

def main():
	args = parse_arguments()
	# lists of epochs end time in seconds and their corresponding kqps
	# this allows to define a piecewise linear function for the kqps
	end_seconds = [args.end_seconds]
	# this is overwriten by the kqps defined as an argument to the program
	kqps = [1]

	# monitor_interval_sec is the interval at which the client will monitor the system and pruduce a report
	# if monitor_interval_sec = 0, then the client will not monitor the system
	monitor_interval = args.monitor_interval

	client = march.make_client(epoch_end_seconds = end_seconds, epoch_kqps = kqps, 
		monitor_interval_sec = monitor_interval)

	with open("./json/client.json", "w+") as f:
		json.dump(client, f, indent=2)

if __name__ == "__main__":
	main()
