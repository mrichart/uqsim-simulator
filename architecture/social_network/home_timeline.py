import json
import make_arch as march 

def main():
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
	respTm = march.make_time_model("expo", [40000])
	redis_find_client_req_stage = march.make_stage(stage_name = "redis_find_client_req", pathId = 0, pathStageId = 2, stageId = 2, blocking = True, batching = False, socket = False, 
		epoll = False, ngx = False,  net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None, 
		scaleFactor = 0.0)

	recvTm = march.make_time_model("expo", [40000])
	respTm = None
	read_posts_req_stage = march.make_stage(stage_name = "read_posts_req", pathId = 0, pathStageId = 3, stageId = 3, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = False,  net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None, 
		scaleFactor = 0.0)
	
	recvTm = march.make_time_model("expo", [1500])
	respTm = None
	epoll_stage_resp_read_posts = march.make_stage(stage_name = "epoll", pathId = 0, pathStageId = 4, stageId = 4, blocking = False, batching = True, socket = False, 
		epoll = True, ngx = False,  net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None, 
		scaleFactor = 0.0)
	
	recvTm = march.make_time_model("expo", [2000])
	respTm = None
	socket_stage_resp_read_posts = march.make_stage(stage_name = "socket", pathId = 0, pathStageId = 5, stageId = 5, blocking = False, batching = True, socket = True, 
		epoll = False, ngx = False, net = False, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None,
		scaleFactor = 0.0)

	recvTm = march.make_time_model("expo", [40000])
	respTm = None
	read_posts_resp_stage = march.make_stage(stage_name = "read_posts_resp", pathId = 0, pathStageId = 6, stageId = 7, blocking = False, batching = False, socket = False, 
		epoll = False, ngx = False,  net = True, chunk = False, recvTm = recvTm, respTm = respTm, cm = None, criSec = False, threadLimit = None, 
		scaleFactor = 0.0)

	home_timeline_path = march.make_code_path(pathId = 0, prob = None, stages = [epoll_stage, socket_stage, redis_find_client_req_stage, read_posts_req_stage, epoll_stage_resp_read_posts, socket_stage_resp_read_posts, read_posts_resp_stage] , priority = None)

	home_timeline = march.make_micro_service(servType = "micro_service", servName = "home_timeline", bindConn = True, paths = [home_timeline_path], 
		baseFreq = 2600, curFreq = 2600)

	with open("./json/microservice/home_timeline.json", "w+") as f:
		json.dump(home_timeline, f, indent=2)


if __name__ == "__main__":
	main();