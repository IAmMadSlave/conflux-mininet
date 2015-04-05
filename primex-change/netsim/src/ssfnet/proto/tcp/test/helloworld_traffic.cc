


#include "os/ssfnet.h"
#include "os/logger.h"
#include "os/config_type.h"
#include "os/config_entity.h"
#include "os/traffic.h"
#include "proto/tcp/test/helloworld_traffic.h"
#include "os/protocol_session.h"
#include <string>


namespace prime {
namespace ssfnet {
LOGGING_COMPONENT(MyNewAppTraffic);
//#define DEMAND_FILE "/Users/rong/Documents/workspace/primex/netsim/demand_file"

MyNewAppStartTrafficEvent::MyNewAppStartTrafficEvent():
		StartTrafficEvent(SSFNetEvent::SSFNET_TRAFFIC_MYNEWAPP_START_EVT), bytes_to_send_per_interval(1000000),
        interval(1){}

MyNewAppStartTrafficEvent::MyNewAppStartTrafficEvent(UID_t traffic_type_uid, uint32_t id, UID_t h_uid, UID_t d_uid, uint32_t d_ip, VirtualTime st) :
        StartTrafficEvent(SSFNetEvent::SSFNET_TRAFFIC_MYNEWAPP_START_EVT, traffic_type_uid, id, h_uid, d_uid, d_ip, st), bytes_to_send_per_interval(1000000),
        interval(1){
}

MyNewAppStartTrafficEvent::MyNewAppStartTrafficEvent(TrafficType* traffic_type, uint32_t id, UID_t h_uid, UID_t d_uid, uint32_t d_ip, VirtualTime st) :
        StartTrafficEvent(SSFNetEvent::SSFNET_TRAFFIC_MYNEWAPP_START_EVT, traffic_type, id, h_uid, d_uid, d_ip, st), bytes_to_send_per_interval(1000000),
        interval(1) {
}

MyNewAppStartTrafficEvent::MyNewAppStartTrafficEvent(MyNewAppStartTrafficEvent* evt) :
        StartTrafficEvent(evt), bytes_to_send_per_interval(evt->bytes_to_send_per_interval), interval(evt->interval){
}

MyNewAppStartTrafficEvent::MyNewAppStartTrafficEvent(const MyNewAppStartTrafficEvent& evt) :
		StartTrafficEvent(evt), bytes_to_send_per_interval(evt.bytes_to_send_per_interval), interval(evt.interval){
}

MyNewAppStartTrafficEvent::~MyNewAppStartTrafficEvent(){

}
prime::ssf::ssf_compact* MyNewAppStartTrafficEvent::pack(){
	prime::ssf::ssf_compact* dp = StartTrafficEvent::pack();
	dp->add_unsigned_int(bytes_to_send_per_interval);
	dp->add_float(interval);
	return dp;
}

void MyNewAppStartTrafficEvent::unpack(prime::ssf::ssf_compact* dp){
	StartTrafficEvent::unpack(dp);
	dp->get_unsigned_int(&bytes_to_send_per_interval,1);
	dp->get_float(&interval,1);
}


void MyNewAppStartTrafficEvent::setBytesToSendPerIntv(uint32_t bytes_per_intv){

	bytes_to_send_per_interval = bytes_per_intv;
}

uint32_t MyNewAppStartTrafficEvent::getBytesToSendPerIntv(){
    return bytes_to_send_per_interval;
}

void MyNewAppStartTrafficEvent::setInterval(float intv){
	interval = intv;
}

float MyNewAppStartTrafficEvent::getInterval(){
    return interval;
}

prime::ssf::Event* MyNewAppStartTrafficEvent::createMyNewAppStartTrafficEvent(prime::ssf::ssf_compact* dp){
	MyNewAppStartTrafficEvent* t_evt = new MyNewAppStartTrafficEvent();
    t_evt->unpack(dp);
    return t_evt;
}



MyNewAppTraffic::MyNewAppTraffic():traffic_id(0){}


MyNewAppTraffic::~MyNewAppTraffic() {

}

ConfigType* MyNewAppTraffic::getProtocolType(){return Receiver::getClassConfigType(); }

bool MyNewAppTraffic::shouldBeIncludedInCommunity(Community* com){
	return StaticTrafficType::shouldBeIncludedInCommunity(com);
}

void MyNewAppTraffic::init(){
		StaticTrafficType::init();
		if(unshared.traffic_flows->empty()) printf("MYNEWAPPTRAFFIC DEBUG: No symbiotic traffic flows!\n");
		else{
			host_bytes.insert(SSFNET_MAKE_PAIR(unshared.traffic_flows->front().first,0));
			}
		ifstream uidfile(shared.host_uid.read().c_str());
		string line;
		if (uidfile.is_open()){
			while (uidfile.good()){
				SSFNET_VECTOR(string) elems;
				getline(uidfile, line);
				stringstream ss(line);
				string item;
				while (getline(ss, item, ',')) {
				elems.push_back(item); //elems: index, uid, ip, name
				}
				if (!elems.empty()) {
				UID_t myuid = atol(elems[0].c_str());
				SSFNET_STRING myuname = elems[2].c_str();
//				std::cout << "MYNEWAPPTRAFFIC DEBUG: UName is: " << myuname << " UID: " << myuid << endl;
				host_id.insert(SSFNET_MAKE_PAIR(myuname, myuid));
				}
			}
		}
		else{std::cout << "MYNEWAPPTRAFFIC ERROR: unable to open file: " << shared.host_uid.read() << endl;}
		uidfile.close();
#if RONG_DEBUG
		for(TrafficFlowList::iterator ti = unshared.traffic_flows->begin(); ti!= unshared.traffic_flows->end(); ti++){
					std::cout << "MyNewAppTraffic DEBUG: src: " << (*ti).first << " dst: " << (*ti).second << endl;
				}
#endif
/*
		std::cout << "MYNEWAPPTRAFFIC DEBUG: stop time: " << shared.stop.read()
				<< " check bytes interval: " << shared.update_interval.read()
				<<" demand file: " << shared.demand_file.read()
				<< " node_uid_ip file: " << shared.host_uid.read() << endl;
*/
}

bool MyNewAppTraffic::checkBytesFromPhy(SSFNET_STRING filename){
//	std::cout << "MYNEWAPPTRAFFIC DEBUG: time to check the file: "<< filename << " for bytes at " << VirtualTime(prime::ssf::now()).second() << endl;
#if 0
	bool file_exist;
			ifstream myfile(filename.c_str());
			if (myfile.is_open()) {
					while (myfile.good()) {
						SSFNET_VECTOR(string) elems;
						getline(myfile, line);
						stringstream ss(line);
						string item;
						while (getline(ss, item, ' ')) {
							elems.push_back(item); //elems: src_name,dst_name, bytes
						}
						if (!elems.empty()) {
							SSFNET_STRING name = elems[1].c_str();
							uint32_t bytes = atoi(elems[2].c_str());
							host_bytes[host_id[name]] = bytes;
//							std::cout << "MYNEWAPPTRAFFIC DEBUG: UID is: " << host_id[name] << " send_bytes: " << bytes << endl;


						}
					}
					file_exist = 1;
					myfile.close();

								std::string str = "rm ";
								FILE* fp = popen((str.append(std::string(filename)).c_str()), "r");
										if (fp == 0) {
											// Could not open file
											fprintf(stderr, "MYNEWAPPTRAFFIC DEBUG: Could not erase file\n");
										} else {
											printf("MYNEWAPPTRAFFIC DEBUG: file erase successfully\n");
										}

				} else {
					LOG_ERROR("MYNEWAPPTRAFFIC ERROR: Unable to open file!"<<endl);
					printf("MYNEWAPPTRAFFIC ERROR: no more data to send\n");
					file_exist = 0;
				}
			return file_exist;
#endif
	for(UIDByteMap::iterator hi = host_bytes.begin(); hi != host_bytes.end(); hi++){
			(*hi).second = 100;
//			std::cout << "MYNEWAPPTRAFFIC DEBUG: Retrieve sender: " << (*hi).first << " bytes: " << (*hi).second << endl;
		}
	return 1;
}

void MyNewAppTraffic::getNextEvent(
        StartTrafficEvent*& traffics_to_start, //if traffic needs to be started now, create a start traffic event and set this
        UpdateTrafficTypeEvent*& update_evt, //if there needs to be an update event the traffic manager will deliver it to all concerned traffic types on remote traffic managers
        bool& wrap_up, //if this traffic is finished set to true and the traffic mgr will clean this up.
        VirtualTime& recall_at //when should this be recalled to start more traffic; set to zero recall immediately
        ){

	VirtualTime now = prime::ssf::now();
		VirtualTime next;
		traffics_to_start=new MyNewAppStartTrafficEvent();
			if(shared.dst_ips.read().size()>0){
				LOG_ERROR("MyNewAppTraffic doesn't support hybrid traffic yet!"<<endl)
			}
			if(traffic_id==0){
				if(unshared.traffic_flows->empty()){
					LOG_WARN("src and dst are set to be the same, no traffic flows, wrap_up, traffic_id="<<traffic_id<<endl)
					wrap_up = true;
					delete traffics_to_start;
					traffics_to_start= 0;
				}
			    else{
			    traffics_to_start->setHostUID(unshared.traffic_flows->front().first);
				traffics_to_start->setDstUID(unshared.traffic_flows->front().second);
				traffics_to_start->setTrafficId(traffic_id++);
				traffics_to_start->setTrafficType(this);
				traffics_to_start->setTrafficTypeUID(getUID());
				SSFNET_DYNAMIC_CAST(MyNewAppStartTrafficEvent*, traffics_to_start)->setBytesToSendPerIntv(0);
				SSFNET_DYNAMIC_CAST(MyNewAppStartTrafficEvent*, traffics_to_start)->setInterval(shared.update_interval.read());
				traffics_to_start->setStartTime(VirtualTime(shared.start_time.read(), VirtualTime::SECOND));
				next = (VirtualTime(shared.start_time.read(), VirtualTime::SECOND));
				}
			}else{
				if(!unshared.traffic_flows->empty()){
				traffics_to_start->setStartTime(VirtualTime(prime::ssf::now()));
				traffics_to_start->setHostUID(unshared.traffic_flows->front().first);
				traffics_to_start->setDstUID(unshared.traffic_flows->front().second);
				traffics_to_start->setTrafficId(traffic_id++);
				traffics_to_start->setTrafficType(this);
				traffics_to_start->setTrafficTypeUID(getUID());

				//set the additional parameters in SYMBIO start traffic event: bytes_to_send_per_intv, interval
				uint32_t bytes_to_send = 0;
				if(checkBytesFromPhy(shared.demand_file.read().c_str())){
#if RONG_DEBUG
					std::cout << "MYNEWAPPTRAFFIC DEBUG:There is demand in the file!" << shared.demand_file.read().c_str() << endl;
#endif
					UIDByteMap::iterator biter = host_bytes.find(unshared.traffic_flows->front().first);
					if(biter != host_bytes.end()) {
						bytes_to_send = (*biter).second;
						host_bytes[(*biter).first] = 0;
#if RONG_DEBUG
						std::cout << "MYNEWAPPTRAFFIC DEBUG:check sender: " << (*biter).first << " bytes: " <<
								bytes_to_send << endl;
#endif
					}
				}
				SSFNET_DYNAMIC_CAST(MyNewAppStartTrafficEvent*, traffics_to_start)->setBytesToSendPerIntv(bytes_to_send);
				SSFNET_DYNAMIC_CAST(MyNewAppStartTrafficEvent*, traffics_to_start)->setInterval(shared.update_interval.read());
				next=VirtualTime(shared.update_interval.read(), VirtualTime::SECOND);
				}
			}
			if(now >= VirtualTime(shared.stop.read(), VirtualTime::SECOND)){
							wrap_up=true;
#if RONG_DEBUG
							std::cout <<"MYNEWAPPTRAFFIC DEBUG: now="<<VirtualTime(prime::ssf::now())<<", stop="<<stop<<" stop starting new flows."<<endl;
#endif
			}else{
				recall_at = next;
			}
#if RONG_DEBUG
			std::cout <<"MYNEWAPPTRAFFIC DEBUG: mynewapptraffic id: " << traffics_to_start->getTrafficId()
					 <<", start time: " << traffics_to_start->getStartTime()
					 <<", source host: " << traffics_to_start->getHostUID()
					 <<", dst host: " << traffics_to_start->getDstUID()
					 <<", traffic demand: " << SSFNET_DYNAMIC_CAST(MyNewAppStartTrafficEvent*, traffics_to_start)->getBytesToSendPerIntv()
					 <<", next recall: " << recall_at << ", wrap up or not:" << wrap_up
					<< endl;
#endif
}


int MyNewAppTraffic::getDstPort(){
	return shared.dst_port.read();
}

float MyNewAppTraffic::getStop(){
	return shared.stop.read();
}

SSF_REGISTER_EVENT(MyNewAppStartTrafficEvent, MyNewAppStartTrafficEvent::createMyNewAppStartTrafficEvent);
}
}

