

#include "net/host.h"
#include "os/ssfnet.h"
#include "os/logger.h"
#include "os/protocol_session.h"
#include "proto/tcp/test/hellome.h"
#include "proto/tcp/test/helloworld_traffic.h"
#include "proto/cnf/cnf_message.h"


namespace prime {
namespace ssfnet {
LOGGING_COMPONENT(MyNewSender);
Sender::Sender(): tcp_master(0), simplesock(0), received_bytes(0){}

Sender::~Sender() {
	if(tcp_master)
			delete tcp_master;
}

void Sender::init() {
	if(tcp_master == NULL)
		tcp_master = (TCPMaster*) inHost()->sessionForNumber(SSFNET_PROTOCOL_TYPE_TCP);
	if(!tcp_master) std::cout << "ERROR: can't find the Transport layer; impossible!" << endl;
	startPassiveListening();
}

void Sender::wrapup() {if(simplesock) delete simplesock;}

int Sender::push(ProtocolMessage* msg, ProtocolSession* hi_sess,
                      void* extinfo, size_t extinfo_size) {

	std::cout << "Sender ERROR: a message is pushed down to the MyNewAppSender session"
				" from protocol layer above; it's impossible" << endl;
		return 0;
}

int Sender::pop(ProtocolMessage* msg, ProtocolSession* losess, void* extra) {
	//((Host*)this->getParent())->getCommunity()->host_ips<<((Host*)this->getParent())->getDefaultIP().toString()<<", s, \n";
		SimpleSocket* sock = SSFNET_STATIC_CAST(SimpleSocket*,extra);
//		std::cout << "Sender DEBUG: socket: " << sock->getSessionId() <<
//				" in Sender::pop status: " << sock->getStatus() << endl;
		uint32 status_ = sock->getStatus();

		if(status_ & SimpleSocket::SOCKET_CONNECTED) {
			// This event is used by this HTTP server to start a new socket so that it always keep listening
//		std::cout << "Sender DEBUG: in MyNewAppSender::pop SOCKET_BUSY" << endl;
			startPassiveListening();
			// Another passive socket has been created
		}
		if(status_ & SimpleSocket::SOCKET_UPDATE_BYTES_RECEIVED) {

//			std::cout << "Sender DEBUG: in MyNewAppSender::pop SOCKET_UPDATE" << endl;
			DataMessage* dm = SSFNET_DYNAMIC_CAST(DataMessage*,msg);
			if(dm){
				// This event is to keep track of the bytes received so far by this applications
				assert(sizeof(CNFMessage) == dm->size());
				received_bytes = received_bytes + dm->size();
//				std::cout << "Sender DEBUG: BYTES RECEIVED SO FAR IN MyNewAppSender: " << received_bytes << endl;
			}
			// Already updated the received bytes

		}
		if(status_ & SimpleSocket::SOCKET_ALL_BYTES_RECEIVED){
			//XXX, dont need??
		}

		if(status_ & SimpleSocket::SOCKET_PSH_FLAG) {
//			std::cout << "Sender DEBUG: in MyNewAppSender::pop SOCKET_PSH" << endl;
			DataMessage* dm = SSFNET_DYNAMIC_CAST(DataMessage*,msg);
			if(dm){
//				std::cout << "Sender DEBUG: in MyNewAppSender:: has message" << endl;
				// There exists a payload that must be conveyed to this application, let's get it
				byte* message = dm->getRawData();
				uint64_t bytes_to_deliver = 0;
				int traffic_id = 0;
				if(message && (sizeof(CNFMessage) == dm->size())) { //there is the request size in the message
					CNFMessage* request = (CNFMessage*) message;
					bytes_to_deliver = request->getContentSize();
					traffic_id = request->getContentID();
#if RONG_DEBUG
					std::cout<<"Sender DEBUG: at sender sub flow: " << traffic_id << " sending "<< bytes_to_deliver
							<< " at time: " << inHost()->getNow().second() << " back to receiver."<<endl;
#endif
					CNFMessage* response = new CNFMessage(0,0,0,0,0,0);
					if(bytes_to_deliver>0 && traffic_id != 0){
						response->setContentID(traffic_id);
						response->setContentSize(bytes_to_deliver);
						sock->send(bytes_to_deliver+sizeof(CNFMessage), (byte*)response);
					}
					else{
						sock->send(sizeof(CNFMessage), (byte*)response);
					}
//					std::cout<<"Sender DEBUG: message traffic id: " << response->getContentID() << endl;

				}else{
//					//this is virtual data
					std::cout << "Sender DEBUG: sender received "<<dm->size()<<" virtual data."<<endl;
				}
			} else {
				std::cout << "Sender ERROR: This should never happen!" << endl;
			}
		}
		return 0;
	return 0;
}

void Sender::startPassiveListening(){
	//Create a socket that will listen for incoming connections
//		std::cout << "Sender DEBUG: creating a new socket because the previous is used!" << endl;
//		std::cout << "Sender DEBUG: Sender tcpMaster="<<tcp_master->getUName()<<endl;
		SimpleSocket* sock = new SimpleSocket(tcp_master, this, shared.listening_port.read());
}

int Sender::getFlowId(){
//	std::cout << "\nSender DEBUG: flow_id: " << shared.flow_id.read() << endl;
	return shared.flow_id.read();
}


SSFNET_REGISTER_APPLICATION_SERVER(9000, Sender);

}
}

