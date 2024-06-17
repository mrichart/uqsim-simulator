import json
import make_arch as march 

# user_timeline_mongo_io
def main():
	# proc path
	recvTm = march.make_time_model("expo", [5000000])	# 5000 us
	respTm = None

	cmodel = march.make_chunk_model("expo", [2])

	#TODO: at some point I change chunk to False. Check if this is correct
	proc_stage = march.make_stage(stage_name = "disk_io", pathId = 0, pathStageId = 0, stageId = 0, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = False, net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = cmodel, criSec = False, threadLimit = None,
		scaleFactor = 0.0)

	path = march.make_code_path(pathId = 0, prob = 100, stages=[proc_stage], priority = None)
	
	user_timeline_mongo_io = march.make_micro_service(servType = "micro_service", servName = "user_timeline_mongo_io", bindConn = False, paths = [path], baseFreq = 2600, curFreq = 2600)

	with open("./json/microservice/user_timeline_mongo_io.json", "w+") as f:
		json.dump(user_timeline_mongo_io, f, indent=2)


if __name__ == "__main__":
	main();