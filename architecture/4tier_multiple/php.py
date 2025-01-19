import sys
import os
import json
import make_arch as march 

# mongodb
def main():
	# fcgi request
	recvTm = march.make_time_model("expo", [40000])
	respTm = march.make_time_model("expo", [40000])
	fcgi_req_stage = march.make_stage(stage_name = "php_fcgi_req", pathId = 0, pathStageId = 0, stageId = 0, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)

	# fopen request
	recvTm = march.make_time_model("expo", [48000])
	respTm = march.make_time_model("expo", [48000])
	fopen_req_stage = march.make_stage(stage_name = "php_fopen_req", pathId = 0, pathStageId = 1, stageId = 1, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)
	
	# fput
	recvTm = march.make_time_model("expo", [40000])
	respTm = march.make_time_model("expo", [40000])
	fput_stage = march.make_stage(stage_name = "php_fput", pathId = 0, pathStageId = 2, stageId = 2, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)

	# find done
	recvTm = march.make_time_model("expo", [40000])
	respTm = march.make_time_model("expo", [40000])
	find_done_stage = march.make_stage(stage_name = "php_find_done", pathId = 0, pathStageId = 3, stageId = 3, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = True, chunk = False, recvTm = recvTm, respTm = None, cm = None, criSec = False, threadLimit = None)

	#get bytes
	recvTm = march.make_time_model("expo", [40000])
	respTm = march.make_time_model("expo", [40000])
	get_bytes_stage = march.make_stage(stage_name = "php_get_bytes", pathId = 0, pathStageId = 4, stageId = 4, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = True, chunk = False, recvTm = recvTm, respTm = None, cm = None, criSec = False, threadLimit = None)

	#mmc store
	recvTm = march.make_time_model("expo", [40000])
	respTm = march.make_time_model("expo", [40000])
	mmc_store_stage = march.make_stage(stage_name = "php_mmc_store", pathId = 0, pathStageId = 5, stageId = 5, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = True, chunk = False, recvTm = recvTm, respTm = None, cm = None, criSec = False, threadLimit = None)

	php_path = march.make_code_path(pathId = 0, prob = None, stages=[fcgi_req_stage, fopen_req_stage, fput_stage, find_done_stage, get_bytes_stage, mmc_store_stage], priority = None)


	# php
	php = march.make_micro_service(servType = "micro_service", servName = "php", bindConn = False, paths = [php_path], 
										baseFreq = 2600, curFreq = 2600)

	with open("./json/microservice/php.json", "w+") as f:
		json.dump(php, f, indent=2)


if __name__ == "__main__":
	main();