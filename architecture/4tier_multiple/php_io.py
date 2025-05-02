import json
import make_arch as march 

# mongodb
def main():
	# read path
	recvTm = march.make_time_model("expo", [3000])
	respTm = None
	open_stage = march.make_stage(stage_name = "fopen", pathId = 0, pathStageId = 0, stageId = 0, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)

	read_path = march.make_code_path(pathId = 0, prob = None, stages=[open_stage], priority = None)

	# write path
	recvTm = march.make_time_model("expo", [1000])
	respTm = None
	put_stage = march.make_stage(stage_name = "fput", pathId = 1, pathStageId = 0, stageId = 1, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = False, scaleFactor = 0.0,
		net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None)

	write_path = march.make_code_path(pathId = 1, prob = None, stages=[put_stage], priority = None)

	# php_io
	php_io = march.make_micro_service(servType = "micro_service", servName = "php_io", bindConn = False, paths = [read_path, write_path], 
										baseFreq = 2600, curFreq = 2600)

	with open("./json/microservice/php_io.json", "w+") as f:
		json.dump(php_io, f, indent=2)


if __name__ == "__main__":
	main();