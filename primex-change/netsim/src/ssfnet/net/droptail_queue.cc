/**
 * \file droptail_queue.cc
 * \brief Source file for the DropTailQueue class.
 * \author Nathanael Van Vorst
 * \author Jason Liu
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

#include "os/logger.h"
#include "proto/ipv4/icmpv4_message.h"
#include "net/droptail_queue.h"
#include "net/net.h"
#include "net/interface.h"
#include <math.h>

#define MONITOR_IFACE 0

namespace prime {
namespace ssfnet {

LOGGING_COMPONENT(DropTailQueue);

//#define LOG_WARN(X) std::cout<<"[droptail_queue.cc:"<<__LINE__<<"]"<<X;
//#define LOG_DEBUG(X) std::cout<<"[droptail_queue.cc:"<<__LINE__<<"]"<<X;

void DropTailQueue::initStateMap() {
	NicQueue::initStateMap();
	unshared.last_xmit_time=0;
	unshared.queue_delay=0;
}

void DropTailQueue::init()
{
	NicQueue::init();
	// convert the queuing delay in seconds to simulation ticks
	weight = 1.0 - exp(-1.0/(getBitRate()/mean_pkt));

	unshared.max_queue_delay = VirtualTime
			(8.0 * getBufferSize() / getBitRate(), VirtualTime::SECOND);
//	unshared.avgqueue = 0;
#ifdef PACKET_TRAIN_MIX
	u_timer = new QueueUpdateTimer(this->getInterface()->inHost()->getCommunity(), this);
	u_timer->schedule(0);
#endif
	if(getInterface()->getUID()==MONITOR_IFACE){
		char foo[5000];
		char bar[5000];
		char bob[3000];
		sprintf(foo,"queue_%lld",getInterface()->getUID());
		sprintf(bar,"flow_%lld", getInterface()->getUID());
		sprintf(bob,"loss_%lld", getInterface()->getUID());
		queue_file = fopen(foo,"w");
		flow_file = fopen(bar, "w");
		//fprintf(flow_file, "[src, dst]  start  end  delivered  dropped  delivered_ratio \n");
		loss_file=fopen(bob,"w");
		//if(!loss_file) LOG_ERROR("Cannot open loss file to write"<<endl);
	}
}

void DropTailQueue::wrapup(){
	if(queue_file) fclose(queue_file);
	if(flow_file) fclose(flow_file);
	if(loss_file) fclose(loss_file);
}

int DropTailQueue::type(){
	return DROPTAIL_QUEUE_TYPE;
}

int DropTailQueue::getInstantLength()
{
	// calculate/update the queuing delay
	VirtualTime now = inHost()->getNow();
	if(now != unshared.last_xmit_time) {
		unshared.queue_delay -= (now - unshared.last_xmit_time);
		if (unshared.queue_delay < 0) unshared.queue_delay = 0;
		unshared.last_xmit_time = now;
	}
	return int(unshared.queue_delay.second()*getBitRate()/8.0);
}

int DropTailQueue::getAverageLength()
{
	return avgqueue;
}

int DropTailQueue::getQueueSize() {
	return getInstantLength();
}

bool DropTailQueue::enqueue(Packet* pkt, float drop_prob, bool cannot_drop)
{
	int pktlen = pkt->size();
	VirtualTime now = inHost()->getNow();
#ifdef FLUID_TRAIN
	LOG_DEBUG("[0]debug, Enqueue at interface="<<getInterface()->getUID()
			<<", at time="<<now.second()
			<<", cur_index="<<cur_index<<"\n");
#endif
	VirtualTime jitter = calibrate(pktlen);
	VirtualTime testqueue_delay;
#ifdef FLUID_TRAIN
#ifdef USE_STCP
	STCPMessage* stcpmsg = (STCPMessage*)pkt->getMessageByArchetype(SSFNET_PROTOCOL_TYPE_STCP);
#else
	SUDPMessage* sudpmsg = (SUDPMessage*)pkt->getMessageByArchetype(SSFNET_PROTOCOL_TYPE_SUDP);
#endif
	uint64 bytes_delivered = 0;
	uint64 dropped_bytes = 0;
	VirtualTime delay = 0;
	int predict_queue = shadow_queue;
	VirtualTime prev_start = 0;
	VirtualTime prev_end = 0;
	bool prev_loss = 0;
	VirtualTime my_start=now;
	bool is_overlap = false;
	VirtualTime mark =0;
#else
	if(getInterface()->getUID()==MONITOR_IFACE)
	 {
		fprintf(queue_file, "%f %d\n", now.second(), getQueueSize()/1400);
		bytes_total += pktlen;
	 }
#endif
#ifdef FLUID_TRAIN
#ifdef USE_STCP
	if (pkt->isPacketTrain()) {
		assert(stcpmsg);
		uint64 init_bytes = stcpmsg->getDuration()*stcpmsg->getInputRate();
		LOG_DEBUG("[1]At interface ="<<getInterface()->getUID()
				<<", bytes init="<<init_bytes
				<<", bytes delivered="<<bytes_delivered
				<<", bytes dropped="<<dropped_bytes
				<<", duration="<<stcpmsg->getDuration()
				<<", input rate="<<stcpmsg->getInputRate()<<endl);

		//use pkt_arrival_rate and train_rate to adjust the train rate and the size of the train..
		//int pkt_arrival_rate=getPacketArrivalRate();
		float arrival_rate = stcpmsg->getInputRate();
		if (arrival_rate == 0){
			LOG_WARN("ACK"<<endl)
			return false;
		}
		VirtualTime duration = VirtualTime(stcpmsg->getDuration(), VirtualTime::SECOND);
		float delivered_ratio = stcpmsg->getDeliveredRatio();

		//Check if the flow is overlapped before updating the train;
		//Adjust the rate if the flow is overlapped
		IPv4Message* iph = (IPv4Message*) pkt->getMessageByArchetype(SSFNET_PROTOCOL_TYPE_IPV4);
		Flow* f = new Flow(stcpmsg->getSrcPort(),stcpmsg->getDstPort(),iph->getSrc(),iph->getDst(),SSFNET_PROTOCOL_TYPE_STCP);
		if(getInterface()->getUID()==MONITOR_IFACE){
			LOG_DEBUG("debug, **************This is flow from ["<<iph->getSrc()<<"] to ["<<iph->getDst()<<"] "
					<<", arrival rate="<<arrival_rate
					<<", duration="<<duration
					<<", delivered ratio="<<delivered_ratio<<endl);
			LOG_DEBUG("1. Check overlapping."<<endl)
		}

		FlowRateMAP::iterator fe = flow_rate.find(f);
		if (fe != flow_rate.end()) { //The train from this flow has arrived at this interface before
			prev_start = fe->second->start;
			prev_end = fe->second->end;
			prev_loss = fe->second->has_loss;
			if(getInterface()->getUID()==MONITOR_IFACE){
				LOG_DEBUG("debug, This flow has arrived before, prev-start="<<prev_start
						<<", prev_end="<<prev_end<<", prev_loss="<<prev_loss<<endl);
			}
			if (fe->second->end > now) {//The old train overlaps the new train, we need to adjust the start time of the new train
				//subtract the old train's arrival rate from the rate array
				if(getInterface()->getUID()==MONITOR_IFACE){
					LOG_DEBUG("debug, There is overlap."<<endl);
					LOG_DEBUG("debug, cur index="<<cur_index
							<<", end_idx="<<fe->second->end_idx
							<<", now="<<now.second()
							<<", flow end="<<fe->second->end.second()<<"\n");
				}
				for (int i = cur_index; i <= fe->second->end_idx; i++) {
					TrainRate* rv = rate_list->get(i, 0);
					while (rv && fe->second->original_end>=rv->end) {
						if(getInterface()->getUID()==MONITOR_IFACE){
							LOG_DEBUG("debug, adjusting the overlap, i="<<i
									<<", rv start="<<rv->start
									<<", rv end="<<rv->end
									<<", rv rate="<<rv->rate<<endl);
						}
						rv->rate -= fe->second->arrival_rate;
						if(rv->rate==0 && i==fe->second->end_idx) rv->end = now;
						if(getInterface()->getUID()==MONITOR_IFACE){
							LOG_DEBUG("debug, after adjusting the overlap, i="<<i
								<<", rv start="<<rv->start
								<<", rv end="<<rv->end
								<<", rv rate="<<rv->rate<<endl);
						}
						rv = rv->next;

					}
				}
				/*if(fe->second->end.second()<(now.second()+stcpmsg->getDuration())){
					my_start=fe->second->end;
					is_overlap=true;
					return false;
				}else{
					return false;
				}*/
			}
		} else { //This is the first time this flow passes through this interface.
			FlowRateInfo* rate_info=new FlowRateInfo(0,now+duration,0,stcpmsg->getInputRate(), now, false);
			fe=flow_rate.insert(SSFNET_MAKE_PAIR(f, rate_info)).first;
			if(getInterface()->getUID()==MONITOR_IFACE){
				LOG_DEBUG("now="<<now.second()<<", at interface="<<getInterface()->getUID()
					<<", insert a new flow into flow map, original_end="
					<<fe->second->original_end.second()
					<<", rate="<<stcpmsg->getInputRate()<<"\n");
			}
		}
		fe->second->original_end = now+duration;
		fe->second->arrival_rate = stcpmsg->getInputRate();
		fe->second->start = my_start;

		//Update the rate_list and the next input rate & delivered ratio for this train
		//The rate_list maintains the arrival rates of the incoming trains
		VirtualTime start = my_start;
		VirtualTime end = now + duration;
		int end_idx = 0;
		if(getInterface()->getUID()==MONITOR_IFACE){
			LOG_DEBUG("debug, clean to now, now="<<now.second()
					<<", interface="<<getInterface()->getUID()
					<<", current index="<<cur_index<<endl);
			for (int i = cur_index; rate_list->get(i, 0)->valid(); i++) {
				TrainRate* rv = rate_list->get(i, 0);
				while (rv) {
					LOG_DEBUG("\tdebug, interface="<<getInterface()->getUID()
							<<", rv->start="<<rv->start.second()
							<<", rv->end="<<rv->end.second()
							<<", rv->rate="<<rv->rate
							<<", index="<<i<<endl);
					rv = rv->next;
				}
			}
		}
		LOG_DEBUG("debug, At interface "<<getInterface()->getUID()
				<<", clean to now."<<endl);
		rate_list->cleanToNow(cur_index, now);
		for (int i = 0; i<5; i++) {
			TrainRate* rv = rate_list->get(i, 0);
			while (rv) {
				if(rv->valid())
					LOG_DEBUG("\tdebug[TEST], after cleaning, interface="<<getInterface()->getUID()
						<<", rv->start="<<rv->start.second()
						<<", rv->end="<<rv->end.second()
						<<", rv->rate="<<rv->rate
						<<", rv->next="<<rv->next
						<<", index="<<i<<endl);
				rv = rv->next;
			}
		}
		if(getInterface()->getUID()==MONITOR_IFACE){
			int c =0;
			bool die=false;
			LOG_DEBUG("[1]debug, after cleaning, interface="<<getInterface()->getUID()<<", cur_index="<<cur_index<<"\n");
			TrainRate* prev=0;
			for (int i = cur_index; rate_list->get(i, 0)->valid(); i++) {
				c++;
				TrainRate* rv = rate_list->get(i, 0);
				while (rv) {
					LOG_DEBUG("\tdebug, after cleaning, interface="<<getInterface()->getUID()
							<<", rv->start="<<rv->start.second()
						<<", rv->end="<<rv->end.second()
						<<", rv->rate="<<rv->rate
						<<", rv->next="<<rv->next
						<<", index="<<i<<endl);
					if(rv->rate < 0)
						die=true;
					if(prev && prev->end > rv->start)
						die=true;
					prev=rv;
					rv = rv->next;
				}
			}
			if(die)
				LOG_ERROR("wtf\n");
		}
		if(getInterface()->getUID()==MONITOR_IFACE){
			LOG_DEBUG("2. Update the rate list and the train"<<endl);
			LOG_DEBUG("rate_list->get(cur_index, 0)->start="<<rate_list->get(cur_index, 0)->start.second()
				<<", now="<<now.second()
				<<", rate_list->get(i, 0)->end="<<rate_list->get(cur_index, 0)->end.second()
				<<", rate_list->get(i, 0)->rate="<<rate_list->get(cur_index, 0)->rate
				<<", rate_list->get(i, 0)->valid()="<<rate_list->get(cur_index, 0)->valid()<<endl);
		}
		if (!rate_list->get(cur_index,0)->valid()){
			//No existing train in the list
			if(getInterface()->getUID()==MONITOR_IFACE){
				LOG_DEBUG("debug, No existing train in the list, cur index="<<cur_index<<"\n");
				LOG_DEBUG("debug, set rate into rate list, now="<<now.second()
						<<", at interface="<<getInterface()->getUID()
						<<", cur index="<<cur_index<<", set rate to empty list at interface ["<<getInterface()->getUID()
						<<"], ["<<iph->getSrc()
						<<"], [start="<<start.second()<<", end="<<end.second()
						<<"], rate="<<arrival_rate<<endl);
			}
			rate_list->set(cur_index, start, end, arrival_rate);
			end_idx=cur_index;
			//Update the train for the next queue
			this->updateTrain(arrival_rate, 0, duration-(my_start-now), bytes_delivered, dropped_bytes, delay, predict_queue);
		}else{
			//Break the train to multiple trains and cal their rates separately
			if(getInterface()->getUID()==MONITOR_IFACE){
				LOG_DEBUG("Break the train,  cur index="<<cur_index<<"\n");
				LOG_DEBUG("rate_list->get(i, 0)->start="<<rate_list->get(cur_index, 0)->start.second()
					<<", now="<<now.second()
					<<", rate_list->get(i, 0)->valid()="<<rate_list->get(cur_index, 0)->valid()<<endl);
			}
			TrainRate* prev_rv=0;
			int i=0;
			for(i=cur_index;
					(rate_list->get(i, 0)->end > now) && (rate_list->get(i, 0)->start < end ) && (rate_list->get(i, 0)->valid());
					i++){
				TrainRate* rv=rate_list->get(i, 0);
				prev_rv=rv;
				while(rv && rv->valid() && rv->start.second()<end.second() && rv->end.second() > start.second()){
					prev_rv=rv;
					if(getInterface()->getUID()==MONITOR_IFACE)
						LOG_DEBUG("debug, in while loop, [i="<<i<<"]rv->start="<<rv->start.second()
							<<", rv->end="<<rv->end.second()
							<<", now="<<now.second()
							<<", rv->valid()="<<rv->valid()<<endl);
					if(rv->end<=end){
						this->updateTrain(arrival_rate, rv->rate, (rv->end-rv->start), bytes_delivered, dropped_bytes, delay, predict_queue);
						rv->rate += arrival_rate;
						if(getInterface()->getUID()==MONITOR_IFACE)
							LOG_DEBUG("debug, while1, now="<<now.second()<<", at interface="<<getInterface()->getUID()
								<<", cur index="<<cur_index
								<<", update the rate at interface ["<<getInterface()->getUID()
								<<"], ["<<iph->getSrc()
								<<"], [start="<<start.second()<<", end="<<end.second()<<"]\n");
					}else{
						this->updateTrain(arrival_rate, rv->rate, (end-rv->start), bytes_delivered, dropped_bytes, delay, predict_queue);
						if(getInterface()->getUID()==MONITOR_IFACE)
							LOG_DEBUG("debug, while2, now="<<now.second()<<", at interface="<<getInterface()->getUID()
								<<", cur index="<<cur_index
								<<", split the rate list at interface ["<<getInterface()->getUID()
								<<"], ["<<iph->getSrc()
								<<"], [start="<<start.second()<<", end="<<rv->end.second()
								<<", new start="<<end.second()<<"]\n");
						rate_list->split(i, end, rv->rate+arrival_rate);
						break;
					}
					rv=rv->next;
				}
				end_idx=i;
			}
			if(end.second()>prev_rv->end.second()){
					LOG_DEBUG("before, bytes delivered="<<bytes_delivered
							<<", init bytes="<<init_bytes
							<<", end="<<end.second()
							<<", prev end="<<prev_rv->end.second()<<endl);
					if(is_overlap){
						this->updateTrain(arrival_rate, 0, end-mark, bytes_delivered, dropped_bytes, delay, predict_queue);
					}else{
						this->updateTrain(arrival_rate, 0, end-prev_rv->end, bytes_delivered,dropped_bytes, delay, predict_queue);
					}
					rate_list->set(i, prev_rv->end, end, arrival_rate);
					LOG_DEBUG("after, bytes delivered="<<bytes_delivered
							<<", init bytes="<<init_bytes<<endl);
			}
		}

		//init_bytes = stcpmsg->getDuration()*stcpmsg->getInputRate();

		stcpmsg->setDuration(duration.second()+delay.second()+dropped_bytes*8/(float)getBitRate());
		stcpmsg->setInputRate(bytes_delivered/stcpmsg->getDuration());

		if(bytes_delivered == 0){
			stcpmsg->setDeliveredRatio(0);
		}else {
			bytes_delivered += 1;
			stcpmsg->setDeliveredRatio(delivered_ratio*bytes_delivered/(bytes_delivered+dropped_bytes));
		}

		Flow* f1=new Flow(stcpmsg->getSrcPort(), stcpmsg->getDstPort(),iph->getSrc(), iph->getDst(),SSFNET_PROTOCOL_TYPE_STCP );
		FlowRateMAP::iterator fe1 = flow_rate.find(f1);

		//Update the end info of the flow in flow_info map
		fe1->second->end = start+duration+delay;
		fe1->second->end_idx = end_idx;
		bool cur_loss=dropped_bytes>0;
		fe1->second->has_loss = cur_loss;
		if(!prev_loss && !cur_loss && prev_end!=0){
			//go over the flow info map and check all the other flows which overlaps my previous train
			if(getInterface()->getUID()==MONITOR_IFACE)
				LOG_DEBUG("Go over the flow info map and check all other flows which overlaps my previous train "<<endl)
			for(FlowRateMAP::iterator it = flow_rate.begin(); it!=flow_rate.end(); it++){
				if(getInterface()->getUID()==MONITOR_IFACE){
					LOG_DEBUG("["<<it->first->dst_ip<<"] start="<<it->second->start<<", end="<<it->second->end<<
						", loss="<<it->second->has_loss<<endl);
					LOG_DEBUG("prev_start="<<prev_start.second()<<", prev_end="<<prev_end.second()<<endl);
				}
				if(it->second->end>prev_start && it->second->start<prev_end && it->second->has_loss){
					fe1->second->has_loss = true;
					LOG_DEBUG("my rate is "<<fe1->second->arrival_rate<<", aggregate rate is "<<this->getTrainRate()<<endl);
					//stcpmsg->setDeliveredRatio(delivered_ratio*fe1->second->arrival_rate/this->getTrainRate()*0.99);
					stcpmsg->setDeliveredRatio(delivered_ratio*0.5);
					if(getInterface()->getUID()==MONITOR_IFACE){
						LOG_DEBUG("There should be a loss, set the loss to be true."<<endl);
					}
					break;
				}
			}
		}
		if(getInterface()->getUID()==MONITOR_IFACE){
			LOG_DEBUG("4. After updating the train, now="<<now.second()
				<<", original_end="<<fe1->second->original_end.second()
				<<", arrival rate="<<fe1->second->arrival_rate
				<<", end="<<fe1->second->end.second()
				<<", end idx="<<fe1->second->end_idx
				<<", duration="<<stcpmsg->getDuration()
				<<", rate="<<stcpmsg->getInputRate()
				<<", bytes delivered="<<bytes_delivered
				<<", bytes dropped="<<dropped_bytes
				<<", delivered ratio="<<stcpmsg->getDeliveredRatio()
				<<"\n");

			bytes_dropped += dropped_bytes;
			bytes_total += bytes_delivered;
			bytes_total += dropped_bytes;

			fprintf(loss_file, "%lld %lld %f %lld %lld\n",
					getInterface()->getParent()->getUID(),
					getInterface()->getUID(),
					now.second(),
					bytes_total,
					bytes_dropped);
			fprintf(flow_file, "[%s, %s] \t%f \t%f \t%lld \t%lld \t%f \t%f \t%d\n",
					iph->getSrc().toString().c_str(), iph->getDst().toString().c_str(), now.second(),
					(now.second()+stcpmsg->getDuration()),
					bytes_delivered, dropped_bytes, stcpmsg->getDeliveredRatio(),
					delivered_ratio,
					shadow_queue);//*/
		}

		if(getInterface()->getUID()==MONITOR_IFACE){
			bool die=false;
			LOG_DEBUG("[2]debug, after cleaning, interface="<<getInterface()->getUID()<<"\n");
			TrainRate* prev=0;
			for (int i = cur_index; rate_list->get(i, 0)->valid(); i++) {
				TrainRate* rv = rate_list->get(i, 0);
				while (rv) {
					LOG_DEBUG("\tdebug, after cleaning, interface="<<getInterface()->getUID()
							<<", rv->start="<<rv->start.second()
						<<", rv->end="<<rv->end.second()
						<<", rv->rate="<<rv->rate
						<<", rv->next="<<rv->next
						<<", index="<<i<<endl);
					if(rv->rate < 0)
						die=true;
					if(prev && prev->end > rv->start)
						die=true;
					prev=rv;
					rv = rv->next;
				}
			}
			if(die)
				LOG_ERROR("wtf\n");
		}
	}
	testqueue_delay = VirtualTime(shadow_queue/(double)getBitRate(), VirtualTime::SECOND) +
			VirtualTime(8.0*pktlen/getBitRate(), VirtualTime::SECOND);
#else
	if (pkt->isPacketTrain()) {
		assert(sudpmsg);

		float arrival_rate = sudpmsg->getInputRate();
		if (arrival_rate == 0){
			LOG_WARN("ACK"<<endl)
			return false;
		}

		VirtualTime duration = VirtualTime(sudpmsg->getDuration(), VirtualTime::SECOND);
		float delivered_ratio = sudpmsg->getDeliveredRatio();

		//Check if the flow is overlapped before updating the train;
		//Adjust the rate if the flow is overlapped
		IPv4Message* iph = (IPv4Message*) pkt->getMessageByArchetype(SSFNET_PROTOCOL_TYPE_IPV4);

		Flow* f = new Flow(sudpmsg->getSrcPort(),sudpmsg->getDstPort(),iph->getSrc(),iph->getDst(),SSFNET_PROTOCOL_TYPE_SUDP);

		FlowRateMAP::iterator fe = flow_rate.find(f);
		if (fe != flow_rate.end()) { //The train from this flow has arrived at this interface before
			prev_start = fe->second->start;
			prev_end = fe->second->end;
			prev_loss = fe->second->has_loss;

			if (fe->second->end > now) {//The old train overlaps the new train, we need to adjust the start time of the new train
				//subtract the old train's arrival rate from the rate array
				for (int i = cur_index; i <= fe->second->end_idx; i++) {
					TrainRate* rv = rate_list->get(i, 0);
					while (rv && fe->second->original_end>=rv->end) {
						rv->rate -= fe->second->arrival_rate;
						if(rv->rate==0 && i==fe->second->end_idx) rv->end = now;
						rv = rv->next;

					}
				}
			}
		} else { //This is the first time this flow passes through this interface.
			FlowRateInfo* rate_info=new FlowRateInfo(0,now+duration,0,sudpmsg->getInputRate(), now, false);
			fe=flow_rate.insert(SSFNET_MAKE_PAIR(f, rate_info)).first;
		}
		fe->second->original_end = now+duration;
		fe->second->arrival_rate = sudpmsg->getInputRate();
		fe->second->start = my_start;

		//Update the rate_list and the next input rate & delivered ratio for this train
		//The rate_list maintains the arrival rates of the incoming trains
		VirtualTime start = my_start;
		VirtualTime end = now + duration;
		int end_idx = 0;
		rate_list->cleanToNow(cur_index, now);

		if (!rate_list->get(cur_index,0)->valid()){
			//No existing train in the list
			rate_list->set(cur_index, start, end, arrival_rate);
			end_idx=cur_index;
			//Update the train for the next queue
			this->updateTrain(arrival_rate, 0, duration-(my_start-now), bytes_delivered, dropped_bytes, delay, predict_queue);
		}else{
			//Break the train to multiple trains and cal their rates separately
			TrainRate* prev_rv=0;
			int i=0;
			for(i=cur_index;
					(rate_list->get(i, 0)->end > now) && (rate_list->get(i, 0)->start < end ) && (rate_list->get(i, 0)->valid());
					i++){
				TrainRate* rv=rate_list->get(i, 0);
				prev_rv=rv;
				while(rv && rv->valid() && rv->start.second()<end.second() && rv->end.second() > start.second()){
					prev_rv=rv;
					if(rv->end<=end){
						this->updateTrain(arrival_rate, rv->rate, (rv->end-rv->start), bytes_delivered, dropped_bytes, delay, predict_queue);
						rv->rate += arrival_rate;
					}else{
						this->updateTrain(arrival_rate, rv->rate, (end-rv->start), bytes_delivered, dropped_bytes, delay, predict_queue);
						rate_list->split(i, end, rv->rate+arrival_rate);
						break;
					}
					rv=rv->next;
				}
				end_idx=i;
			}
			if(end.second()>prev_rv->end.second()){
				if(is_overlap){
					this->updateTrain(arrival_rate, 0, end-mark, bytes_delivered, dropped_bytes, delay, predict_queue);
				}else{
					this->updateTrain(arrival_rate, 0, end-prev_rv->end, bytes_delivered,dropped_bytes, delay, predict_queue);
				}
				rate_list->set(i, prev_rv->end, end, arrival_rate);
			}
		}

		sudpmsg->setDuration(duration.second()+delay.second()+dropped_bytes*8/(float)getBitRate());
		sudpmsg->setInputRate(bytes_delivered/sudpmsg->getDuration());

		if(bytes_delivered == 0){
			sudpmsg->setDeliveredRatio(0);
		}else {
			bytes_delivered += 1;
			sudpmsg->setDeliveredRatio(delivered_ratio*bytes_delivered/(bytes_delivered+dropped_bytes));
		}

		Flow* f1=new Flow(sudpmsg->getSrcPort(), sudpmsg->getDstPort(),iph->getSrc(), iph->getDst(),SSFNET_PROTOCOL_TYPE_SUDP );
		FlowRateMAP::iterator fe1 = flow_rate.find(f1);

		//Update the end info of the flow in flow_info map
		fe1->second->end = start+duration+delay;
		fe1->second->end_idx = end_idx;
		bool cur_loss=dropped_bytes>0;
		fe1->second->has_loss = cur_loss;
		if(!prev_loss && !cur_loss && prev_end!=0){
			//go over the flow info map and check all the other flows which overlaps my previous train
			for(FlowRateMAP::iterator it = flow_rate.begin(); it!=flow_rate.end(); it++){
				if(it->second->end>prev_start && it->second->start<prev_end && it->second->has_loss){
					fe1->second->has_loss = true;
					LOG_DEBUG("my rate is "<<fe1->second->arrival_rate<<", aggregate rate is "<<this->getTrainRate()<<endl);
					//sudpmsg->setDeliveredRatio(delivered_ratio*fe1->second->arrival_rate/this->getTrainRate()*0.99);
					sudpmsg->setDeliveredRatio(delivered_ratio*0.5);
					break;
				}
			}
		}
	}
	testqueue_delay = VirtualTime(shadow_queue/(double)getBitRate(), VirtualTime::SECOND) +
			VirtualTime(8.0*pktlen/getBitRate(), VirtualTime::SECOND);
#endif
#else

	testqueue_delay = unshared.queue_delay +
			VirtualTime(8.0*pktlen/getBitRate(), VirtualTime::SECOND);
#endif

	bool should_drop = testqueue_delay > unshared.max_queue_delay;
	if(!pkt->isPacketTrain()){
		if(!cannot_drop && should_drop) {
			// drop the entire packet if the queue full.https://accounts.google.com/ServiceLogin?service=mail&passive=true&rm=false&continue=https://mail.google.com/mail/&ss=1&scc=1&ltmpl=default&ltmplcache=2&hl=en
			LOG_INFO("interface (ip=" << getInterface()->getIP() << ") queue over flown; drop packet\n");
	#if TEST_ROUTING == 1
			saveRouteDebug(pkt,this);
	#endif
			/*if(getInterface()->getUID()==MONITOR_IFACE){
				bytes_dropped += pktlen;
				fprintf(loss_file, "%f %lld %lld\n",
								now.second(), bytes_total, bytes_dropped);
			}*/
			pkt->erase();
			return false;
		}
		/*if(getInterface()->getUID()==MONITOR_IFACE){
			fprintf(loss_file, "%f %lld %lld\n",
				now.second(), bytes_total, bytes_dropped);
		}*/
		double prob=inHost()->getRandom()->uniform(0.0,1.0);
		if((!cannot_drop) && (prob<(double) drop_prob)){
			// drop the entire packet if the queue full.
			LOG_DEBUG("interface (ip=" << getInterface()->getIP() << ") drops packet due to drop probability which is "
					<<drop_prob<<", sampled drop prob="<<prob<<endl);
			if(!pkt->isPacketTrain()){
				pkt->erase();
	#ifdef  PACKET_TRAIN_MIX
				bytes_dropped += pktlen;
	#endif
			}
			return false;
		}else if(cannot_drop && (prob<(double) drop_prob)){
			should_drop=true;
		}
	}

#ifdef  PACKET_TRAIN_MIX
	if(!pkt->isPacketTrain()){
		bytes_received += pktlen;
		if(should_drop){
			bytes_dropped += pktlen;
		}
	}


	float curr_loss = 0;
	if((bytes_received-prev_bytes_received)>0){
		curr_loss=(float)(bytes_dropped-prev_bytes_dropped)/(bytes_received-prev_bytes_received);
	}
	LOG_DEBUG("The current loss is "<<curr_loss<<endl);

	//if this is stcp probe, update the loss probability.
	if(stcpmsg){
		float loss_prob;
		if(!stcpmsg->isForward()){ //backward
			loss_prob=1-(1-stcpmsg->getACKLossProbability())*(1-curr_loss);
			stcpmsg->setACKLossProbability(loss_prob);
			LOG_DEBUG("ACK loss="<<loss_prob<<endl);
		}
	}
#endif

#ifdef FLUID_TRAIN
#ifdef USE_STCP
	if(stcpmsg){
		if(stcpmsg->getDeliveredRatio()<1 || stcpmsg->getACKLossProbability()>0){
			should_drop=true;
		}else{
			should_drop=false;
		}
	}
#else
	if(sudpmsg){
			if(sudpmsg->getDeliveredRatio()<1){
				should_drop=true;
			}else{
				should_drop=false;
			}
		}
#endif
#endif
	// calculate queuing delay
	unshared.queue_delay = testqueue_delay+jitter+VirtualTime(getLatency(), VirtualTime::SECOND);

	// timestamp icmp timestamp packet
	ICMPv4Message* icmph = (ICMPv4Message*)pkt->getMessageByArchetype(SSFNET_PROTOCOL_TYPE_ICMPV4);
	if(icmph) {
		if(icmph->getType() == ICMPv4Message::ICMP_TYPE_TIMESTAMP) {
			icmph->setTimeMsgOriginateTimestamp((uint32)inHost()->getNow().millisecond());
			icmph->setTimeMsgReceiveTimestamp((uint32)(inHost()->getNow()+unshared.queue_delay).millisecond());
		} else if(icmph->getType() == ICMPv4Message::ICMP_TYPE_TIMESTAMP_REPLY) {
			icmph->setTimeMsgTransmitTimestamp((uint32)inHost()->getNow().millisecond());
		}
	}

	// call the interface to send the packet.
	getInterface()->transmit(pkt, unshared.queue_delay);

	return !should_drop;
}

#ifdef FLUID_TRAIN
void DropTailQueue::updateTrain(uint64 arrival_rate, uint64 existing_rate, VirtualTime duration, uint64& bytes_delivered, uint64& dropped_bytes, VirtualTime& delay, int& predict_queue){
	float bit_rate=this->getBitRate(); //in bits
	int buffer_size=this->getBufferSize(); //in bytes
	int prev_queue=predict_queue;
	if(getInterface()->getUID()==MONITOR_IFACE){
		LOG_DEBUG("3, Update the train."<<endl);
		LOG_DEBUG("time="<<inHost()->getNow().second()
			<<", my rate="<<arrival_rate
			<<", existing rate="<<existing_rate
			<<", duration="<<duration
			<<", shadow_queue="<<shadow_queue
			<<", delay="<<duration
			<<", buffer size="<<buffer_size<<endl);
	}
	if((arrival_rate+existing_rate)*8 > bit_rate){
		//Suppose the buffer size is infinity
		predict_queue += (arrival_rate+existing_rate-bit_rate/8)*duration.second();
		if(getInterface()->getUID()==MONITOR_IFACE){
			LOG_DEBUG("Aggregate rate is greater than the bit rate. predict queue="<<predict_queue<<endl);
		}
	}else{
		//The train does not accumulate in the buffer, its rate and duration keep the same.
		predict_queue -= (bit_rate/8 - arrival_rate - existing_rate)*duration.second();
		if(predict_queue<0) predict_queue=0;
		if(getInterface()->getUID()==MONITOR_IFACE){
			LOG_DEBUG("Aggregate rate is less than the bit rate. predict queue="<<predict_queue<<endl);
		}
	}
	if(predict_queue<=buffer_size){ //There is no loss
		bytes_delivered += arrival_rate*duration.second();
		if(getInterface()->getUID()==MONITOR_IFACE){
			LOG_DEBUG("There is no loss, bytes_delivered="<<bytes_delivered<<endl);
		}
	}else{
		//Drop the bytes that exceed the buffer size
		//uint64 dropped = (predict_queue-buffer_size);
		uint64 dropped = (predict_queue-buffer_size)*(arrival_rate/double(arrival_rate+existing_rate));
		dropped_bytes += dropped;
		bytes_delivered += arrival_rate*duration.second() - dropped;
		if(getInterface()->getUID()==MONITOR_IFACE){
			LOG_DEBUG("There is loss, bytes_delivered="<<bytes_delivered
					<<", dropped="<<dropped<<endl);
		}
		predict_queue=buffer_size;
	}
	if(prev_queue < predict_queue)
		delay += VirtualTime((predict_queue-prev_queue)/bit_rate, VirtualTime::SECOND);
	if(getInterface()->getUID()==MONITOR_IFACE){
		LOG_DEBUG("\tUpdate the train"
				<<", at interface="<<getInterface()->getUID()
				<<", existing_rate="<<existing_rate
				<<", duration="<<duration.second()
				<<", arrival rate="<<arrival_rate
				<<", bytes delivered="<<bytes_delivered
				<<", bytes dropped="<<dropped_bytes
				<<", arrive ratio="<< (arrival_rate/double(arrival_rate+existing_rate))
				<<", delay="<<delay.second()
				<<", predict queue="<<predict_queue<<"\n");
	}

}
#endif
VirtualTime DropTailQueue::calibrate(int pktlen)
{
	VirtualTime jitter(0);
	VirtualTime now = inHost()->getNow();

#ifdef FLUID_TRAIN
	float now_s = (float)(inHost()->getNow().second());
	float bit_rate=this->getBitRate(); //in bits
	int buffer_size=this->getBufferSize(); //in bytes
	int i;
	LOG_DEBUG("debug, ~~~~~~~start calibrate, now="<<now_s
		<<", interface="<<getInterface()->getUID()
		<<", current index="<<cur_index<<endl);
	TrainRate* rv = rate_list->get(cur_index,0);
	TrainRate* prev=0;
	for(i=cur_index; rate_list->get(i,0)->valid() && rate_list->get(i,0)->start<now;i++){
		rv = rate_list->get(i,0);
		prev = rv;
		while(rv && rv->start<now){
			VirtualTime end_time = (rv->end > now ? now : rv->end);
			float period = (end_time - rv->start).second();
			//LOG_DEBUG("The end time = "<<end_time.second()<<", period="<<period<<", rate="<<rv->rate<<endl);
			if((rv->rate*8) <= bit_rate){
				//LOG_DEBUG("Arrival rate is less than the bit rate."<<endl);
				shadow_queue -= ((bit_rate/8)-rv->rate)*period;
				if(shadow_queue<0) shadow_queue=0;
			}else{
				//LOG_DEBUG("Arrival rate is greater than the bit rate."<<endl);
				shadow_queue += (rv->rate - bit_rate/8)*period;
				if(shadow_queue > buffer_size){
					shadow_queue = buffer_size;
				}
			}
#ifdef USE_STCP
			if(getInterface()->getUID()==MONITOR_IFACE){
				if(rv->rate<0) LOG_ERROR("WTF"<<endl)
			}
			if(getInterface()->getUID()==MONITOR_IFACE)
			{
				fprintf(queue_file, "%f %d %d %f [%f, %f]\n", now_s, shadow_queue/1400, rv->rate, period, rv->start.second(), rv->end.second());
			 }
#endif
			rv=rv->next;
		}
	}

	//keep track of the index of the current time, and the last_update_time (now)
	if(prev)
		LOG_DEBUG("debug, in calibrate, before clean to now, now="<<now.second()
			<<", current index="<<cur_index
			<<", i="<<i
			<<", rv="<<rv
			<<", prev->start="<<prev->start.second()
			<<", prev->end="<<prev->end.second()
			<<", prev->rate="<<prev->rate<<endl);
	LOG_DEBUG("debug, in calibrate, At interface "<<getInterface()->getUID()
			<<", clean to now."<<endl);

	for(;cur_index<i;cur_index++) {
		rate_list->cleanToNow(cur_index, now);
	}

	if(prev&&now.second()<prev->end.second()){
		cur_index--;
	}

	if(getInterface()->getUID()==MONITOR_IFACE){
		LOG_DEBUG("debug, in calibrate, after cleaning, read rate list, cur index="<<cur_index
				<<", interface="<<getInterface()->getUID()<<"\n");
		for (int i = cur_index; rate_list->get(i, 0)->valid(); i++) {
			TrainRate* rv = rate_list->get(i, 0);
			while (rv) {
				LOG_DEBUG("\tdebug, in calibrate, rv->start="<<rv->start.second()
						<<", rv->end="<<rv->end.second()
						<<", rv->rate="<<rv->rate
						<<", index="<<i<<endl);
				rv = rv->next;
			}
		}
	}

#endif

	if(getJitterRange() > 0) { // if jitter is enabled
		jitter = VirtualTime(inHost()->getRandom()->uniform(-1, 1) *
				8 * getJitterRange() * pktlen / getBitRate(),
				VirtualTime::SECOND);
		now += jitter;
	}
	if(now > unshared.last_xmit_time) { // it's possible jitter makes now < last_xmit_time
		unshared.queue_delay -= (now - unshared.last_xmit_time);
		if (unshared.queue_delay < 0) unshared.queue_delay = 0;
		unshared.last_xmit_time = now;
	}
	int m = 0;
	if(now > unshared.last_xmit_time) // queue is idle?
	    m = int((now-unshared.last_xmit_time).second()*getBitRate()/mean_pkt);
	  avgqueue *= pow (1-weight, m+1);
	  avgqueue += weight*(unshared.queue_delay.second()*getBitRate()/8.0);
	return jitter;
}

} // namespace ssfnet
} // namespace prime
