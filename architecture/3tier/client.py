import sys
import os
import json
import argparse
import make_arch as march

# 2026-11-20: added --end_seconds/--monitor_interval CLI args (previously
# hardcoded end_seconds=60, monitor_interval_sec=1). The monitor_interval=1
# default mattered more than it looked: main.cc clears the client's
# latency-record buffer after every monitor tick, and the final "total:"
# summary line only aggregates whatever accumulated since the *last* clear
# - with monitor_interval_sec=1, that's the tiny leftover fragment after
# the last 1-second tick (sometimes a single sample), making "total:" a
# noisy, occasionally wildly misleading statistic (traced empirically: a
# single bad sample from the legitimately fat right tail at ~2kqps load
# would make "total:" report all four stats collapsed to that one value,
# looking like a capacity collapse that wasn't real - the per-second
# "end2end:"/p99 lines were stable throughout). Defaulting to 0 (no
# periodic clear, matching social_network/4tier_multiple's client.py) makes
# "total:" a proper full-run aggregate instead.
def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--end_seconds", type=int, default=60, help="Epoch end time in seconds")
	parser.add_argument("--monitor_interval", type=int, default=0, help="Interval at which the client monitors the system (in seconds); 0 disables periodic monitoring")
	args = parser.parse_args()
	return args

def main():
	args = parse_arguments()
	end_seconds = [args.end_seconds]
	kqps = [8]

	client = march.make_client(epoch_end_seconds = end_seconds, epoch_kqps = kqps,
		monitor_interval_sec = args.monitor_interval)

	with open("./json/client.json", "w+") as f:
		json.dump(client, f, indent=2)

if __name__ == "__main__":
	main()
