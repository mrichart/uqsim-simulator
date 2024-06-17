import json
import make_arch as march 

# mongodb
def main():
	# read path
	recvTm = march.make_time_model("expo", [200000])
	respTm = None
	find_stage = march.make_stage(stage_name = "find_client", pathId = 0, pathStageId = 0, stageId = 0, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)

	read_path = march.make_code_path(pathId = 0, prob = None, stages=[find_stage], priority = None)

	# write path
	recvTm = march.make_time_model("expo", [200000])
	respTm = None
	put_stage = march.make_stage(stage_name = "put_client", pathId = 1, pathStageId = 0, stageId = 1, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)

	write_path = march.make_code_path(pathId = 1, prob = None, stages=[put_stage], priority = None)

	# user_timeline_redis
	user_timeline_redis = march.make_micro_service(servType = "micro_service", servName = "user_timeline_redis", bindConn = False, paths = [read_path, write_path], 
										baseFreq = 2600, curFreq = 2600)

	with open("./json/microservice/user_timeline_redis.json", "w+") as f:
		json.dump(user_timeline_redis, f, indent=2)


if __name__ == "__main__":
	main();