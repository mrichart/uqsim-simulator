import json
import make_arch as march 

def main():

	recvTm = march.make_time_model("expo", [40000])
	respTm = march.make_time_model("expo", [40000])
	mmc_get_client_stage = march.make_stage(stage_name = "mmc_get_client", pathId = 0, pathStageId = 0, stageId = 0, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)
	
	mmc_hit_path = march.make_code_path(pathId = 0, prob = None, stages=[mmc_get_client_stage], priority = None)

	recvTm = march.make_time_model("expo", [48000])
	respTm = march.make_time_model("expo", [48000])
	mongo_find_client_stage = march.make_stage(stage_name = "mongo_find_client", pathId = 1, pathStageId = 1, stageId = 1, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)
	
	recvTm = march.make_time_model("expo", [40000])
	respTm = march.make_time_model("expo", [40000])
	mmc_set_client_stage = march.make_stage(stage_name = "mmc_set_client", pathId = 1, pathStageId = 2, stageId = 2, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)

	mmc_miss_path = march.make_code_path(pathId = 1, prob = None, stages=[mmc_get_client_stage, mongo_find_client_stage, mmc_set_client_stage], priority = None)


	# post_storage
	post_storage = march.make_micro_service(servType = "micro_service", servName = "post_storage", bindConn = False, paths = [mmc_hit_path, mmc_miss_path], 
										baseFreq = 2600, curFreq = 2600)

	with open("./json/microservice/post_storage.json", "w+") as f:
		json.dump(post_storage, f, indent=2)


if __name__ == "__main__":
	main();