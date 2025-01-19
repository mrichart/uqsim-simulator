import sys
import os
import json
import make_arch as march 

# nginx
def main():
	# req path
	recvTm = march.make_time_model("expo", [1500])
	respTm = None
	epoll_stage = march.make_stage(stage_name = "epoll", pathId = 0, pathStageId = 0, stageId = 0, blocking = False, batching = True, socket = False, 
		epoll = True, ngx = False,  net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None, 
		scaleFactor = 0.0)
	
	recvTm = march.make_time_model("expo", [2000])
	respTm = None
	socket_stage = march.make_stage(stage_name = "socket", pathId = 0, pathStageId = 1, stageId = 1, blocking = False, batching = True, socket = True, 
		epoll = False, ngx = False, net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None,
		scaleFactor = 0.0)

	recvTm = march.make_time_model("expo", [40000])
	respTm = None
	proc_req_stage = march.make_stage(stage_name = "proc_req", pathId = 0, pathStageId = 2, stageId = 2, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = True,  net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None, 
		scaleFactor = 0.0)

	req_path = march.make_code_path(pathId = 0, prob = None, stages=[epoll_stage, socket_stage, proc_req_stage], priority = None)

	# resp mmc path

	recvTm = march.make_time_model("expo", [40000])
	respTm = None
	proc_mmc_stage = march.make_stage(stage_name = "proc_mmc", pathId = 1, pathStageId = 2, stageId = 3, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = True,  net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None, 
		scaleFactor = 0.0)

	resp_mmc_path = march.make_code_path(pathId = 1, prob = None, stages=[epoll_stage, socket_stage, proc_mmc_stage], priority = None)

	# resp php path

	recvTm = march.make_time_model("expo", [40000])
	respTm = None
	proc_php_stage = march.make_stage(stage_name = "proc_php", pathId = 2, pathStageId = 2, stageId = 4, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = True,  net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None, 
		scaleFactor = 0.0)

	resp_php_path = march.make_code_path(pathId = 1, prob = None, stages=[epoll_stage, socket_stage, proc_php_stage], priority = None)

	# nginx
	nginx = march.make_micro_service(servType = "micro_service", servName = "nginx", bindConn = True, paths = [req_path, resp_mmc_path, resp_php_path], 
		baseFreq = 2600, curFreq = 2600)

	with open("./json/microservice/nginx.json", "w+") as f:
		json.dump(nginx, f, indent=2)


if __name__ == "__main__":
	main();