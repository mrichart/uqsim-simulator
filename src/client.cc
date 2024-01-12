#include <iostream>
#include <stdio.h>

#include "client.hh"

int compareDouble(const void* a, const void* b) {
	if(*(double*)a == *(double*)b)
		return 0;
	else if(*(double*)a > *(double*)b)
		return 1;
	else
		return -1;
}

Client::Client(unsigned total, unsigned nconn, Time net_lat, bool debug, Time monitor_interval): 
		numTotal(total), numConn(nconn), netLat(net_lat), debug(debug), monitorInterval(monitor_interval), 
		lastMonitorTime(0), targTailLat(0), tailLat(0) {
	count = 0;
	nextTime = 0;
	srand(time(NULL));
	if(numTotal > 0) {
		finalTime = new Time[numTotal];
		startTime = new Time[numTotal];
		complete = new bool[numTotal];
		for(unsigned i = 0; i < numTotal; ++i)
			complete[i] = false;
	}

	allJobIssued = false;
	curEpoch = 0;

	// performance monitoring, assume 50k qps
	uint64_t init_size = uint64_t(monitorInterval/1000000000.0*50);
	respTimeRecords = new JobTimeRecords(init_size);
}

Client::~Client() {
	delete tm;
	delete finalTime;
	delete respTimeRecords;
}

void 
Client::setEntry(Cluster* c) {
	entry = c;
}

void
Client::setTimeModel(TimeModel* t) {
	tm = t;
}

void
Client::addEpoch(Time epoch_end_time, uint64_t rps) {
	if(epochEndTime.size() > 0)
		assert(epochEndTime[epochEndTime.size() - 1] < epoch_end_time);
	assert(rps > 0);
	epochEndTime.push_back(epoch_end_time);
	epochQps.push_back(rps);
}

bool
Client::isAllJobIssued() {
	return allJobIssued;
}

// TODO:change this logic to include monitor event & epoch defined approach
Time 
Client::nextEventTime() {
	// first check if all job issued
	if(allJobIssued)
		// return lastMonitorTime + monitorInterval;
		return INVALID_TIME;
	else {
		return (lastMonitorTime + monitorInterval) < nextTime ? (lastMonitorTime + monitorInterval): nextTime;
		// return nextTime;
	}
}

bool
Client::needSched(Time cur_time) {
	// std::cout << "in need sched" << std::endl;
	// std::cout << "cur_time = " << cur_time << std::endl;
	// std::cout << "lastMonitorTime = " << lastMonitorTime << std::endl;
	// std::cout << "monitorInterval = " << monitorInterval << std::endl;
	if(cur_time >= lastMonitorTime + monitorInterval) {
		// std::cout << "cur_time = " << cur_time << std::endl;
		// std::cout << "lastMonitorTime = " << lastMonitorTime << std::endl;
		// std::cout << "monitorInterval = " << monitorInterval << std::endl;
		return true;
	}
	else 
		return false;
}

bool
Client::needRun(Time cur_time) {
	if(allJobIssued)
		return false;
	if(cur_time >= nextTime)
		return true;
	else
		return false;
}

void
Client::setLastMonitorTime(Time cur_time) {
	lastMonitorTime = cur_time;
}

void
Client::run(Time time) {
	if(!allJobIssued && time >= nextTime) {
		unsigned connId = rand() % numConn;
		// if(numTotal > 0)
		startTime[count] = nextTime;

		Job *j = new Job(count, connId, respTimeRecords, nullptr, nextTime, &(finalTime[count]), &(complete[count]), debug);

		if(debug) {
			// std::cout << "client interval = " << interval << std::endl;
			std::cout << "In Client job: " << j->id << " start at " << nextTime << std::endl << std::endl;
			// std::cout << std::endl;
		}

		j->time += netLat;
		entry->enqueue(j);
		++count;
		Time interval = tm->lat();

		// if(debug) {
		// 	std::cout << "client interval = " << interval << std::endl;
		// 	std::cout << "job: " << j->idx << " start at " << nextTime << std::endl;
		// 	std::cout << std::endl;
		// }
		nextTime += interval;

		// check epoch change and all job issued
		if(count >= numTotal && numTotal != 0)
			allJobIssued = true;
		// check epoch change
		if(epochEndTime.size() > 0 && nextTime >= epochEndTime[curEpoch]) {
			assert(!allJobIssued);
			if(curEpoch == epochEndTime.size() - 1)
				allJobIssued = true;
			else {
				// change epoch, reset time distribution
				++curEpoch;
				Time new_lat = (Time)(1000000000.0/epochQps[curEpoch]);
				tm->reset(new_lat);
			}
		}
	}
	
	curTime = time;
}

void
Client::show() {
	Time avg_lat = respTimeRecords->getAvgLat();
	Time lat_50 = respTimeRecords->getPercentileLat(0.5);
	Time tail_lat_95 = respTimeRecords->getPercentileLat(0.95);
	Time tail_lat_99 = respTimeRecords->getPercentileLat(0.99);
	if (debug) {
		std::vector<uint64_t> latencies = respTimeRecords->getAllLat();
		std::cout << "***begin latencies***" << std::endl;
		for (Time lat: latencies)
			std::cout << (double)lat/1000000.0 << std::endl;
		std::cout << "***end latencies***" << std::endl;
		std::cout << "average lat within [" << (double)lastMonitorTime/1000000000.0 << "s, sim_end) = " << (double)avg_lat/1000000.0
			<< "ms" << std::endl; 
		std::cout << "95% tail lat within [" << (double)lastMonitorTime/1000000000.0 << "s, sim_end) = " << (double)tail_lat_95/1000000.0
			<< "ms" << std::endl; 
		std::cout << "99% tail lat within [" << (double)lastMonitorTime/1000000000.0 << "s, sim_end) = " << (double)tail_lat_99/1000000.0
			<< "ms" << std::endl;
	}
	std::cout << (double)avg_lat/1000000.0 << ";" << (double)lat_50/1000000.0 << ";" << (double)tail_lat_95/1000000.0 << ";" << (double)tail_lat_99/1000000.0 << std::endl;
}

void
Client::setTimeArray() {
	if(numTotal == 0) {
		Time lastTime = 0;
		for(unsigned i = 0; i < epochEndTime.size(); ++i) {
			Time interval = epochEndTime[i] - lastTime;
			lastTime = epochEndTime[i];		// in nanoseconds
			numTotal += uint64_t(interval/1000000000.0 * epochQps[i]);
		}

		std::cout << "numTotal = " << numTotal << std::endl;

		finalTime = new Time[numTotal];
		startTime = new Time[numTotal];
		complete  = new bool[numTotal];
		for(uint64_t i = 0; i < numTotal; ++i)
			complete[i] = false;

		// also set up cli time model according to first epoch
		Time new_lat = (Time)(1000000000/epochQps[0]);
		assert(tm != nullptr);
		tm->reset(new_lat);
	} else {
		finalTime = new Time[numTotal];
		startTime = new Time[numTotal];
		complete = new bool[numTotal];
		for(uint64_t i = 0; i < numTotal; ++i)
			complete[i] = false;
	}
}

Time
Client::getTailLat() {
	return respTimeRecords->getPercentileLat(0.99);
}

void
Client::clearRespTime() {
	respTimeRecords->clear();
}

uint64_t
Client::getCurQps() {
	return epochQps[curEpoch];
}