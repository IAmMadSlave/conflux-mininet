

#include "net/host.h"
#include "os/ssfnet.h"
#include "os/logger.h"
#include "os/protocol_session.h"
#include "proto/tcp/test/helloworld.h"
#include "proto/tcp/test/helloworld_traffic.h"
#include "proto/cnf/cnf_message.h"


namespace prime {
namespace ssfnet {

LOGGING_COMPONENT(Receiver);

Receiver::Receiver(): tcp_master(0), simplesock(0), received_bytes(0){}

Receiver::~Receiver() {}

void Receiver::init() {}

void Receiver::wrapup() {

	for(IdSocketByte::iterator bi = id_socket_bytes.begin(); bi!= id_socket_bytes.end(); bi ++){

					SimpleSocket* sock = (*bi).second.first;
					std::cout << "Receiver DEBUG: Disconnect socket: " << sock
							<< "from = "<< inHost()->getName()<< endl;
					std::cout<<"complete[uid="<<getUID()<<","<<getUName()<<"] tcp_session_id="<<(*bi).first
																			<<"; throughput="<< ((double)sock->getInstantaneousRecvThroughput())/((double)1e6) << " MB/s"
																			<<", totol download time="<< sock->getLastRecv().second()-sock->getFirstRecv().second()
																			<<", flow length="<< sock->getLastRecv().second()-sock->getFirstSend().second() << "s"
																			<<"; start="<<sock->getFirstRecv().second()<<", end="<<sock->getLastRecv().second()
																			<<", total bytes recv="<< ((double)sock->getBytesRecv())/((double)1e6)<<" MB\n";
					}

	if(simplesock) delete simplesock;}

int Receiver::push(ProtocolMessage* msg, ProtocolSession* hi_sess,
                      void* extinfo, size_t extinfo_size) {

	std::cout << "Receiver ERROR: a message is pushed down to the Receiver session"
				" from protocol layer above; it's impossible\n";
		return 0;
}

int Receiver::pop(ProtocolMessage* msg, ProtocolSession* losess, void* extra) {

	SimpleSocket* sock = SSFNET_STATIC_CAST(SimpleSocket*,extra);
		uint32 status_ = sock->getStatus();
		int session_id = sock->getSessionId();
//		std::cout << "Receiver DEBUG: Receiver: socket: " << sock
//				<< " pop status:" << status_ << endl;

		if(status_ & SimpleSocket::SOCKET_CONNECTED) {
			//This event is not implemented here because this is not a server application
			std::cout << "Receiver ERROR: Got a SOCKET_BUSY signal in Receiver!"<< endl;
		}
		if(status_ & SimpleSocket::SOCKET_UPDATE_BYTES_RECEIVED) {
			// This event is to keep track of the bytes received so far by this applications
			DataMessage* dm = SSFNET_DYNAMIC_CAST(DataMessage*,msg);
//			std::cout << "Receiver DEBUG: BYTES RECEIVED SO FAR IN this message:" << dm->size() <<endl;
			received_bytes = received_bytes + dm->size();
#if RONG_DEBUG
			std::cout << "Receiver DEBUG: now="<<inHost()->getNow().second()<<", BYTES RECEIVED SO FAR IN Receiver:" << received_bytes <<endl;
#endif
/*
			IntervaltoBytes& id_bytes_ = session_id_bytes.find(session_id)->second;
			assert(!id_bytes_.empty());
			IntervaltoBytes::iterator idpair= id_bytes_.find(cm->getContentID());
						if(idpair==id_bytes_.end()){
							std::cout << "Receiver ERROR: Invalid sub flow id, shouldn't happen!"<< endl;
						}else{
							uint32_t& p= (*idpair).second;
							p=p-vsize;
							std::cout << "Receiver DEBUG: sub flow id="<<cm->getContentID()<<", remaining bytes = "<<p<<endl;
							if(p<=0){
								std::cout << "Receiver DEBUG: complete sub flow="<<cm->getContentID()<<", socket="<<sock<<" at time="<<inHost()->getNow().second()<<endl;
								id_bytes_.erase(idpair);
							}
						}
*/

		}

		if(status_ & SimpleSocket::SOCKET_ALL_BYTES_RECEIVED){
		}

		if(status_ & SimpleSocket::SOCKET_PSH_FLAG) {
				// We do not implement here this case
			}

		return 0;

}
void Receiver::startTraffic(StartTrafficEvent* evt, IPAddress ipaddr, MACAddress mac) {

//std::cout << "Receiver DEBUG: starting MyNewApp traffic "<<getUID()<<", at: "<<inHost()->getNow().second()<<", myip: "<<this->inHost()->getDefaultIP().toString()<<
//				" dstip: "<<ipaddr<<", traffictype: "<< evt->getTrafficType()<<endl;
if(!evt->getTrafficType()) std::cout << "Receiver ERROR: SIGH!"<<endl;
switch(evt->getTrafficType()->getConfigType()->type_id){
	case MYNEWAPP_TRAFFIC:
	{
		//std::cout << "Receiver DEBUG: Receiver START TRAFFIC at " << inHost()->getNow().second() << endl;
					Host* host = inHost();
					assert(host);
					int dst_port_ = 0;
					uint32_t request_bytes_ = 0;
					float interval_ = 0;
					MyNewAppTraffic* tt = SSFNET_STATIC_CAST(MyNewAppTraffic*,evt->getTrafficType());
					int target_comm_id = evt->getSrcCommunityID();
					uint32_t traffic_id = evt->getTrafficId();
					UID_t traffic_type_uid = evt->getTrafficTypeUID();
					uint32_t total_request_bytes = 0;

					if(!tcp_master) {
						// Get a pointer to the protocol session below
						tcp_master = (TCPMaster*)inHost()->sessionForNumber(SSFNET_PROTOCOL_TYPE_TCP);
						if(!tcp_master) LOG_ERROR("missing TCP session.");
					}
//					std::cout << "!!!Receiver DEBUG: Receiver tcpMaster="<<tcp_master->getUName()<<endl;

					// Get the destination port to connect to
					dst_port_ = tt->getDstPort();

					// Get the file size from the event
					request_bytes_ = SSFNET_DYNAMIC_CAST(MyNewAppStartTrafficEvent*,evt)->getBytesToSendPerIntv();
					interval_ = SSFNET_DYNAMIC_CAST(MyNewAppStartTrafficEvent*, evt)->getInterval();
#if RONG_DEBUG
					std::cout<<"Receiver DEBUG: host: " <<getUName()<<"["<<getParent()->getUID()<<"] asking for: "
												<<request_bytes_<<" bytes to host: "<<evt->getDstUID()
												<< " at port: " << dst_port_
												<<" in time: "<<inHost()->getNow().second()
												<<endl;
#endif
					SimpleSocket* simple_sock = 0;
					CNFMessage* request = new CNFMessage(0,0,0,0,0,0);
					//cout << "---> creating a new socket for ip" << ipaddr << endl;

					if(traffic_id == 0){
						simple_sock = new SimpleSocket(tcp_master, this, ipaddr, dst_port_);
						if(dst_socket.find(ipaddr) == dst_socket.end()){
						dst_socket.insert(SSFNET_MAKE_PAIR(ipaddr, simple_sock));
						id_socket_bytes.insert(SSFNET_MAKE_PAIR(simple_sock->getSessionId(), SSFNET_MAKE_PAIR(simple_sock,total_request_bytes)));
		//				id_socket_bytes.insert(SSFNET_MAKE_PAIR(traffic_id,SSFNET_MAKE_PAIR(simple_sock, request_bytes_)));
//						std::cout << "Receiver DEBUG: sub flow: " << request->getContentID() << " starting at: " << inHost()->getNow().second() << endl;
						simple_sock->send(sizeof(CNFMessage), (byte*)request);
						}
					else std::cout << "Receiver ERROR: First start a traffic, shouldn't be found in the map!" << endl;
					}
					else {
							if (request_bytes_ > 0){
							simple_sock = (*dst_socket.find(ipaddr)).second;
							assert(id_socket_bytes.find(simple_sock->getSessionId()) != id_socket_bytes.end());
							SocketByte &b = id_socket_bytes.find(simple_sock->getSessionId())->second;
							b.second += request_bytes_;
							request->setContentSize(request_bytes_);
							request->setContentID(traffic_id);
//							std::cout << "Receiver DEBUG: sub flow: " << request->getContentID() << " requesting: " << request->getContentSize() << endl;
							simple_sock->send(sizeof(CNFMessage), (byte*)request);
							}
						}
/*
					std::cout << "Receiver DEBUG: dst_socket map:-------------" << endl;
					for(IptoSocketMap::iterator si = dst_socket.begin(); si != dst_socket.end(); si ++){
						std::cout << "Dest: " << (*si).first << " Socket:" << (*si).second->getSessionId() << endl;
					}
					std::cout << "Receiver DEBUG: session_socket_bytes map:-----------" << endl;
										for(IdSocketByte::iterator si = id_socket_bytes.begin(); si != id_socket_bytes.end(); si++){
											std::cout << "socket_id: " << (*si).first
													<< " socket: " << (*si).second.first
													<< " total_request_bytes : " << (*si).second.second << endl;

										}
*/


					break;
}
	default:
		std::cout << "ERROR: Invalid traffic type...."<<endl;
evt->free();
}
}

int Receiver::getFlowId(){
	return shared.flow_id.read();
}
//register the application to run on port 9999
//SSFNET_REGISTER_APPLICATION_SERVER(9000, MyNewApp);

}
}

