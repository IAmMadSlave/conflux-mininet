/**
 * \file ssfnet_stats.cc
 * \brief Source file for for collecting system-wide simulation statistics.
 * \author Rong Rong
 * 
 * 
 * Copyright (c) 2011 Florida International University.
 *
 * Permission is hereby granted, free of charge, to any individual or
 * institution obtaining a copy of this software and associated
 * documentation files (the "software"), to use, copy, modify, and
 * distribute without restriction.
 *
 * The software is provided "as is", without warranty of any kind,
 * express or implied, including but not limited to the warranties of
 * merchantability, fitness for a particular purpose and
 * non-infringement.  In no event shall Florida International
 * University be liable for any claim, damages or other liability,
 * whether in an action of contract, tort or otherwise, arising from,
 * out of or in connection with the software or the use or other
 * dealings in the software.
 *
 * This software is developed and maintained by
 *
 *   Modeling and Networking Systems Research Group
 *   School of Computing and Information Sciences
 *   Florida International University
 *   Miami, Florida 33199, USA
 *
 * You can find our research at http://www.primessf.net/.
 */
#include <string.h>
#include <float.h>
#include <iomanip>
#include "os/logger.h"
#include "os/ssfnet_stats.h"
#include "os/virtual_time.h"
#include "os/partition.h"
#include <string>


using namespace prime::ssf;
using namespace prime::ssfnet;
#define PROBE_INTERVAL 1
//#define NOT_AVERAGE
//#define MODEL_FILE "/Users/rong/Documents/workspace/primex/netsim/downscale_file"
//#define PIPE_OUTPUT_FILE "/Users/rong/Documents/workspace/primex/netsim/pipe_output"

LOGGING_COMPONENT(ssfnet_stats);

SimulationSamplingTimer::SimulationSamplingTimer(Community* comm, double ltime, SSFNET_STRING downscale, SSFNET_STRING update):Timer(comm), end_time(ltime), comm_(comm), downscale_file(downscale), update_file(update)
{
	Net* net = comm_->getPartition()->getTopnet();
	int number_subnets = 0;
	ChildIterator<Net*> rvv = net->getNets(& number_subnets);
	nameMap name_interface;
	if (number_subnets != 0){
		while(rvv.hasMoreElements()){
								BaseEntity* rr = rvv.nextElement();
								Net* subnet = SSFNET_DYNAMIC_CAST(Net*,rr);
								int number_host = 0;
								ChildIterator<Host*> rv = subnet->getHosts(& number_host);
								while(rv.hasMoreElements()){
									BaseEntity* r = rv.nextElement();
									Host* host = SSFNET_DYNAMIC_CAST(Host*,r);
									ChildIterator<Interface*> iv = host->getInterfaces();
									while(iv.hasMoreElements()){
										BaseEntity* i = iv.nextElement();
										Interface* iface = SSFNET_DYNAMIC_CAST(Interface*, i);
										name_interface.insert(SSFNET_MAKE_PAIR(*(UName(iface).toString()),iface));
									}
								}
							}
	}
	else {
		int number_host = 0;
		ChildIterator<Host*> rv = net->getHosts(& number_host);
			while(rv.hasMoreElements()){
				BaseEntity* r = rv.nextElement();
				Host* host = SSFNET_DYNAMIC_CAST(Host*,r);
				ChildIterator<Interface*> iv = host->getInterfaces();
				while(iv.hasMoreElements()){
					BaseEntity* i = iv.nextElement();
					Interface* iface = SSFNET_DYNAMIC_CAST(Interface*, i);
					name_interface.insert(SSFNET_MAKE_PAIR(*(UName(iface).toString()),iface));
				}
			}
	}
//	ifstream mfile(MODEL_FILE);
	ifstream mfile(downscale_file.c_str());
	string line;
	if (mfile.is_open()) {
		while(mfile.good()){
			getline(mfile,line);
			stringstream ss(line);
			string item;
			int item_id = 0;
			interfaces temp;
			string pipe_id;
			while(getline(ss, item, ' ') ){
				SSFNET_STRING name = item.c_str();
				if(item_id == 0){pipe_id = name;}
				else{
				assert(name_interface.find(name) != name_interface.end());
				temp.push_back(SSFNET_MAKE_PAIR(name_interface[name],0));
				}
				item_id ++;
			}
			if(!temp.empty()){
			pid_interfaces.insert(SSFNET_MAKE_PAIR(pipe_id, temp));
			}
		}
	}
	else{std::cout << "SSFNET STATS ERROR: unable to open downscale model file!" << endl;}
	}

void SimulationSamplingTimer::resched(double delay){
		if(isRunning())  cancel();
					  VirtualTime delay_(delay, VirtualTime::SECOND);
					  set(delay_);
	}

void SimulationSamplingTimer::interfaceStats (interfaces& ifaces, double& path_loss, double& mu_star){
		double total_w_s = 0.0;
		double total_w_s_mean = 0.0;
		float min_lamda_p_e = FLT_MAX;
		double path_no_loss = 1.0;
		double bottle_mu = FLT_MAX;
		for (SSFNET_LIST(SSFNET_PAIR(Interface*, int))::iterator li = ifaces.begin(); li != ifaces.end(); li ++){
			Interface* i = (*li).first;
			double p = i->getDropProbability();
			double mu = i->getBitRate();
			float lamda_p = (i->getSymbioBytes() - (*li).second)*8.00/(PROBE_INTERVAL*1000000);
			(*li).second= i->getSymbioBytes();
			NicQueue* queue = i->getNicQueue();
			int queue_size = 0;
			int average_size = 0;
			if (queue->type() == 1) {
				DropTailQueue* dqueue = SSFNET_DYNAMIC_CAST(DropTailQueue*, queue);
				average_size = dqueue->getAverageLength();
				queue_size = dqueue->getInstantLength();
				if (queue_size > i->getBufferSize()) p = 1;
			}
			else if (queue->type() == 2){
				RedQueue* rqueue = SSFNET_DYNAMIC_CAST(RedQueue*, queue);
				average_size = rqueue->getAverageLength();
				queue_size = rqueue->getInstantLength();
				p = rqueue->getLossRate();
			}
			float lamda_p_e = lamda_p * (1-p);
			double w_s = queue_size*8/mu;
			double w_s_mean= average_size*8/mu;
#if RONG_DEBUG
			std::cout << "SSFNET STATS DEBUG: interface: " << i->getUName()
					<< " arrival_bytes: " << i->getSymbioBytes() << " arrival_rate: " << lamda_p
					<< " drop_prob: " << p
					<< " wait_time: " << w_s << " average_wait_time: " << w_s_mean << endl;
#endif
// acummulated statistics
			total_w_s += w_s;
			total_w_s_mean += w_s_mean;
			path_no_loss = path_no_loss * (1-p);
			if(lamda_p_e < min_lamda_p_e) min_lamda_p_e = lamda_p_e;
			if(mu < bottle_mu) bottle_mu = mu;
		}
		path_loss = 1 - path_no_loss;
#if RONG_DEBUG
		std::cout << "SSFNET STATS DEBUG: path loss: " << path_loss
							<< " wait_time: " << total_w_s
							<< " arrival_rate: " << min_lamda_p_e << endl;
#endif
// Use instantaneous  waiting time
#ifdef NOT_AVERAGE
		mu_star = min_lamda_p_e/(1 + total_w_s * min_lamda_p_e - sqrt(1 + pow((total_w_s * min_lamda_p_e),2)));
		if (min_lamda_p_e == 0) {mu_star = 0;}
		else{
		if(mu_star > bottle_mu) mu_star = bottle_mu;
		}
#else
// Use average waiting time
		mu_star = min_lamda_p_e/(1 + total_w_s_mean * min_lamda_p_e - sqrt(1 + pow(total_w_s_mean * min_lamda_p_e,2)));
		if(min_lamda_p_e == 0) {
			mu_star = 0;
		}
		else{
		if(mu_star > bottle_mu) mu_star = bottle_mu;
		}
#endif
	}


void SimulationSamplingTimer::callback(){
		double current_time = VirtualTime(now()).second();
#if RONG_DEBUG
		std::cout<< "SSFNET STATS DEBUG: Statistics --------------------------------------------"<< endl;
		std::cout<<"SSFNET STATS DEBUG: Probe at simulation time: "<< current_time << " second." <<endl;
#endif
//		ofstream pfile(PIPE_OUTPUT_FILE, ios::out|ios::trunc);
		ofstream pfile(update_file.c_str(), ios::out|ios::trunc);
		if (pfile.is_open()){
#if RONG_DEBUG
		std::cout << setiosflags(ios::left);
		std::cout << "time: " << current_time << endl;
		std::cout<< setw(10) << "pipe_id" << " "
				<< setw(16) << "drop_probability" << " "
				<< setw(10) << "service_rate" << endl;
#endif
			for(interfaceMap::iterator ii = pid_interfaces.begin(); ii != pid_interfaces.end(); ii ++){
				string pipe_id = (*ii).first;
				double drop_probability = 0;
				double service_rate = 0;
				interfaceStats((*ii).second, drop_probability, service_rate);
#if RONG_DEBUG
				std::cout << setiosflags(ios::left);
				std::cout << setw(10) << pipe_id << " "
						<< setw(16) << drop_probability << " "
						<< setw(10) << service_rate << endl;
#endif
				pfile << setiosflags(ios::left);
				pfile << setw(10) << pipe_id << " "
						<< setw(16) << drop_probability << " "
						<< setw(10) << service_rate << endl;

			}

		}
		pfile.close();
#if RONG_DEBUG
		std::cout<< "SSFNET STATS DEBUG: Statistics end-------------------------------------------"<< endl;
#endif
		if (current_time <= end_time) resched(PROBE_INTERVAL);
	}

