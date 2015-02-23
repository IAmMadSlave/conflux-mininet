/**
 * \file portal_device.cc
 */

#define EMU_BUFSIZ 300000 // buffer up to 200 pkts of 1500 bytes

#include "os/emu/portal_device.h"
#include "os/io_mgr.h"
#include "os/logger.h"
#include "proto/emu/emulation_protocol.h"
#include "os/partition.h"

#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <sys/select.h>
#include <sys/types.h>
#include <unistd.h>
#include <iomanip>
#include <errno.h>
#include <net/ethernet.h>
#include <sys/poll.h>



#include <netdb.h>
#include <netinet/in_systm.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <string.h>
#include <arpa/inet.h>

#include <linux/if_ether.h>
#include <linux/if_packet.h>

//#define LOG_WARN(X) std::cout<<"["<<__LINE__<<"]"<<X;
#define LOG_DEBUG(X) std::cout<<"["<<__LINE__<<"]"<<X;

namespace prime {
namespace ssfnet {

int Portal::c_mtu         = 0;
int Portal::mode_loss     = 1;
bool Portal::sconfiged = false;
int server_port = 9000;

LOGGING_COMPONENT(PortalDevice);
#define BUFFSIZE 300000 // buffer up to 200 pkts of 1500 bytes


void TrafficPortal::init() {
	EmulationProtocol::init();
	getInterface()->inHost()->registerTrafficPortal(this);
}

IPPrefix::List& TrafficPortal::getNetworks() {
	return unshared.networks.read();
}

void TrafficPortal::transmit(Packet* pkt, VirtualTime deficit) {
	getInterface()->receiveEmuPkt(pkt);
}

bool TrafficPortal::receive(Packet* pkt, bool pkt_was_targeted_at_iface) {
	LOG_DEBUG(getUName()<<
	" emu proto pkt_was_targeted_at_iface="
	<<(pkt_was_targeted_at_iface?"true":"false")<<
	", ipForwardingEnabled()="<<(ipForwardingEnabled()?"true":"false")
	<<", isActive()="<<(isActive()?"true":"false")<<endl);

	if(isActive()) {
		LOG_DEBUG("exporting packet from iface "<<getInterface()->getUName()<<endl);
		//LOG_DEBUG("pkt->size()="<<pkt->size()<<endl);
		emuDevice->exportPacket(getInterface(),pkt);
		return true;
	}
	LOG_DEBUG(getUName()<<" emu proto did not take packet! "<<endl);
	return false;
}

PortalDevice::PortalDevice():maxfd(0) {
}

PortalDevice::~PortalDevice(){
	for(Portal::Map::iterator i = uid2portal.begin(); i!=uid2portal.end();i++) {
		delete i->second;
	}
}

void PortalDevice::init(){
	BlockingEmulationDevice::init();
	LOG_DEBUG("PortalDevice::init() input_channel="<<input_channel<<", output_channel="<<output_channel<<endl);
	LOG_DEBUG("Portal Table:\n"<<ip2portal<<endl);

	for(Portal::Map::iterator i = uid2portal.begin(); i!=uid2portal.end();i++) {
		i->second->init();
		if(maxfd < i->second->getRxFD()) {
			maxfd = i->second->getRxFD();
		}
		ip2mac.insert(SSFNET_MAKE_PAIR(i->second->getIP(),i->second->getMAC()));
		LOG_DEBUG("IP->"<<i->second->getIP()<<endl);
		LOG_DEBUG("MAC->"<<i->second->getMAC()<<endl);
	}
	sim_net=getCommunity()->getPartition()->getTopnet()->getIPPrefix();
	//ip2portal.setupRoutes(sim_net);
	LOG_DEBUG("Simulated network prefix is "<<sim_net<<endl);
}

void PortalDevice::wrapup() {
	BlockingEmulationDevice::wrapup();
}

void PortalDevice::registerProxiedEmulationProtocol(EmulationDeviceProxy* dev, EmulationProtocol* emu_proto) {
	ssfnet_throw_exception(SSFNetException::other_exception,"Cannot call registerProxiedEmulationProtocol() on an TAPDevice!");
}

void PortalDevice::registerEmulationProtocol(EmulationProtocol* emu_proto) {
	if(!TrafficPortal::getClassConfigType()->isSubtype(emu_proto->getTypeId())) {
		LOG_ERROR("The Portal device only supports emulation protocols of type TrafficPortal! Found "<<emu_proto->getTypeName()<<endl);
	}
	TrafficPortal* portal_proto = (TrafficPortal*) emu_proto;
	Portal* portal= new Portal(emu_proto, this);
	uid2portal.insert(SSFNET_MAKE_PAIR(emu_proto->getInterface()->getUID(),portal));
	for(IPPrefix::List::iterator i=portal_proto->getNetworks().begin(); i!=portal_proto->getNetworks().end(); i++) {
		ip2portal.addPortal(*i, portal, portal_proto);
	}
	emu_proto->setEmulationDevice(this);
}

void PortalDevice::exportPacket(Interface* iface, Packet* pkt) {
	//LOG_DEBUG("exporting packet from "<<iface->getUName()<<", ip="<<iface->getIP()<<endl);
	EmulationEvent* evt= new EmulationEvent(iface, pkt, false);
	output_channel->write(evt);
}

void PortalDevice::handleProxiedEvent(EmulationEvent* evt) {
	LOG_WARN("Portal devices cannot proxy evts!"<<endl);
	evt->free();
}

EmulationProtocol* PortalDevice::ip2EmulationProtocol(IPAddress& ip) {
	TrafficPortalPair * portal = ip2portal.getPortal((uint32)ip);

	if(!portal) {
		LOG_WARN("asked to handle the departure to an unknown network "<<ip);
		return 0;
	}

	return portal->trafficPortal;
}

void PortalDevice::reader_thread() {
	int result, sock;
	char buffer[65536];
	maxfd++;
//it should be 1 greater than the max fd...
	LOG_DEBUG("Starting portal read thread"<<endl);

	// we assume all Portal Receive Sockets are opened
	Portal::Map::iterator portal_it;
	fd_set base_fds, fds;

	// Zero out file descriptors and setup all file descriptor return 
	FD_ZERO(&base_fds);
	for(portal_it = uid2portal.begin();portal_it!=uid2portal.end();portal_it++) {
		FD_SET(portal_it->second->getRxFD(),&base_fds);
	}

	//int max_loops=500;
	//bool more_packets=false;

	for(;!stop;) {
		fds=base_fds;
		result = select(maxfd, &fds, NULL, NULL, NULL);
		if (result == -1) {
			LOG_DEBUG("select error - exit"<<endl);		
			break;
		} else {
			for(portal_it = uid2portal.begin();
				portal_it!=uid2portal.end();portal_it++) {
				sock = portal_it->second->getRxFD();
				if (FD_ISSET(sock, &fds)) {
         				// myfds[j] is readable
					LOG_DEBUG("receive packet from portal"<<endl);
      					rc = recvfrom(sock, buffer, sizeof(buffer), 0, cliadd, &len);
					if (rc < 0) LOG_DEBUG("error"<<endl);
					// verify the vector of sizes of events
					memcpy(&numberevents, buffer+8, 4);
					numberofevents = ntohl(numberofevents);
					// loop over number of events
					for (i=1;i<=numberofevents;i++){
						memcpy(&eventsize, buffer+(i*4), 4);
						eventsize = ntohl(eventsize);
						EventSizes.push_back(size);
					}
					// iterate over rest of buffer parse event sizes
					for (iterate:EventSizes)
						buffer = buffer+(numberofevents*4);
						memcpy(&WaitingEvent, buffer+EventSize, EventSize);
						// type cast to WaitingEvent
						// put back to simulator side
				}
			}
		}
	}
}

void PortalDevice::writer_thread() {
	LOG_DEBUG("Starting portal write thread"<<endl)
	double delay;
	VirtualTime last_arp_check=getCommunity()->now();
	for(;!stop;) {
	SSFNetEvent* evt_ = (SSFNetEvent*)output_channel->getRealEvent(delay, 10);
 	if (evt_ != NULL) {
		VirtualTime now=this->getCommunity()->now();
		switch(evt_->getSSFNetEventType()) {
		case SSFNetEvent::SSFNET_EMU_NORMAL_EVT: 
		{
			EmulationEvent* evt = (EmulationEvent*)evt_;
			LOG_DEBUG("This is an SSFNet Normal Event"<<endl);
			if(evt->pkt) {
				LOG_DEBUG("Got a evt to write out! iface="<<evt->iface->getUName()<<", ip="<<evt->iface->getIP()<<endl);
				// check which portal that belong to
				Portal::Map::iterator portal_it = uid2portal.find(evt->iface->getUID());		
				if(portal_it == uid2portal.end()) {
				LOG_WARN("interface not registered! Dropping packet."<<endl);
				evt->free();
				} else {
					IPAddress tgt = ((IPv4Message*)(evt->pkt->getMessageByArchetype(SSFNET_PROTOCOL_TYPE_IPV4)))->getDst();
	              			TrafficPortalPair* tp =ip2portal.getPortal(tgt);
                            		if(tp) watingForArps.push_back(new WaitingArpEvt(portal_it->second,evt,this->getCommunity()->now(), tgt));
                            		else {
                                		LOG_WARN("Tried to export an emulation event from an interface which ("<< evt->iface->getUName()<<") to and ip ("<<tgt<<") but I dont know where to arp for the mac!"<<endl);
                                // the event needs to be reclaimed
                                	evt->free();
                            		}
				} // else - YES -there is a portal
			} // if evt is a packet
		evt_=0;	
		} // SSFNET_EMU_NORMAL_EVT
		default:
				LOG_DEBUG("Unexpected evt type - like ARP!"<<endl);
		}
   	} else {
		LOG_DEBUG("Timeout!"<<endl);
		if(watingForArps.size()>0) {
                    for(WaitingArpEvt::List::iterator arp_it=watingForArps.begin();arp_it!=watingForArps.end();) {
			LOG_DEBUG("*arp_it="<<(*arp_it)<<endl);
			//MACAddress* mac = lookupMAC((*arp_it)->tgt);
			MACAddress* mac;
			TrafficPortalPair* tp =ip2portal.getPortal((*arp_it)->tgt);
			if(tp) {
				LOG_DEBUG("Sending mac that was waiting for arp response...."<<endl);
				assert((*arp_it)->portal && (*arp_it)->evt);
				(*arp_it)->portal->sendPacket((*arp_it)->evt,*mac);
				// the event needs to be reclaimed
				delete (*arp_it);
				arp_it=watingForArps.erase(arp_it);
			} else LOG_ERROR("How did this happen?");
                    } // end-loop FOR WAITING ARP EVT
		} // IF WAITING > 0	
	} 
	} //end-infinite loop
	LOG_DEBUG("End of Writer Thread"<<endl); 
}

void PortalDevice::insertIntoSim(EthernetHeader* eth, IPv4RawHeader* ip, uint32_t len) {
	LOG_DEBUG("insertIntoSim, len="<<len<<endl)

	// we need to copy the message to a new buffer (the receive
	// buffer will be reused for next message)
	char* buf = new char[len];
	assert(buf);
	memcpy(buf, (char*)eth, len);
	eth = (EthernetHeader*)buf; // update the eth header pointer
	ip = (IPv4RawHeader*)(buf+sizeof(EthernetHeader)); // update the ip header pointer


	//find the iface in the sim which corresponds to the src mac
	TrafficPortalPair* p = ip2portal.getPortal(ip->getSrc());
	if(!p) {
		LOG_WARN("Tried to import a packet from an unknown network, ip=\n"<<*ip<<endl);
		return;
	}

	// create the event (the new buffer is handed off to the event
	// as the payload) and pass it subsequently to the simulator
	UID_t dst_uid=getCommunity()->synchronousNameResolution(IPAddress(ip->getDst()));
	Packet* pkt=new Packet(SSFNET_PROTOCOL_TYPE_IPV4, (prime::ssfnet::byte*)buf, len, sizeof(EthernetHeader), dst_uid);

	EmulationEvent* evt=0;
	if(!dst_uid) {
		evt = new EmulationEvent(p->trafficPortal->getInterface(), pkt,true);
		LOG_DEBUG("created emu evt with a need for async name res"<<endl)
	}
	else {
		evt = new EmulationEvent(p->trafficPortal->getInterface(), pkt,false);
		LOG_DEBUG("created emu evt withOUT a need for async name res"<<endl)
	}

	assert(evt);
	//std::cout << "**** get event at " << getCommunity()->now() << ", dst_uid=" << dst_uid << ", dest ip=" << IPAddress(ip->getDst()) << std::endl;
	input_channel->putRealEvent(evt);
	// no need to reclaim buf or evt!
}

bool PortalDevice::isActive() {
	return !stop;
}

bool PortalDevice::requiresSingleInstancePerHost() {
	return false;
}

int PortalDevice::getDeviceType() {
	return EMU_TRAFFIC_PORTAL;
}

SSFNET_REGISTER_EMU_DEVICE(PortalDevice, EMU_TRAFFIC_PORTAL);

Portal::Portal(EmulationProtocol* emuproto_, PortalDevice* dev_) :
					dev(dev_),
					emuproto(emuproto_),
					rx_fd(-1),
					tx_fd(-1),
					pcap_handle(0),
					sendbuf(new byte[BUFFSIZE])
					{

	if(!sconfiged) {
		sconfiged=true;
		char* env_var=0;
		env_var = getenv("c_mtu");
		if(env_var && strlen(env_var)>0) {
			c_mtu   = (int)atol(env_var);
		}
		env_var = getenv("mode_loss");
		if(env_var && strlen(env_var)>0) {
			mode_loss   = (int)atol(env_var);
		}
	}
}

Portal::~Portal() {
	/* cleanup */
	if(pcap_handle) {
		pcap_close(pcap_handle);
		pcap_handle=0;
	}
	if(tx_fd!=-1)
		close(tx_fd);
	delete sendbuf;
}

void Portal::init() {

	int rc;
	char service[7];	
	struct addrinfo hints, *res;

	//setup the pcap rx channel
	bpf_u_int32 mask;
	bpf_u_int32 net;
	char errbuf[PCAP_ERRBUF_SIZE];
	SSFNET_STRING* nic=Partition::getPortalNic(emuproto->getInterface()->getUID());
	if(!nic) 
		LOG_ERROR("Unable find net interface attached to the traffic portal '"
		<<emuproto->getInterface()->getUName()<<"'"<<endl);

	iface_name.clear();
	iface_name.append(nic->c_str());
	char dev_str[nic->length() + 1];
	sprintf(dev_str,"%s", nic->c_str());

	// Receiver socket configuration 
	memset(&hints, 0, sizeof(struct addrinfo));
	hints.ai_flags = AI_PASSIVE;
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_DGRAM;

	// Every new portal will get a new server port assignment
	server_port++; 
	snprintf(service, sizeof(service), "%d", server_port);
 	if ((rc = getaddrinfo(NULL, service, &hints, &res)) != 0) {
		LOG_ERROR("getaddrinfo(): failed" <<endl);
 	}
	
	LOG_DEBUG("Creating rx_fd for "<<nic<<"\n");
	rx_fd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
	if(rx_fd == -1) LOG_ERROR("Unable open (rx) UDP socket for "<<nic<<endl);

	LOG_DEBUG("Binding rx_fd on "<<nic<<"\n");
	rc = bind(rx_fd, res->ai_addr, res->ai_addrlen);
	if (rc == -1) LOG_ERROR("Unable to bind the tx socket for "<<nic<<"!"<<endl);

	/* points to one interface returned from ioctl */
	struct ifreq tx_ifr; 

	// Sender socket configuration 	
	LOG_DEBUG("Creating tx_fd for "<<nic<<"\n");
	tx_fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (tx_fd == -1) LOG_ERROR("Unable open (tx) raw socket for "<<nic<<endl);

	/* initialize interface struct */
	strncpy (tx_ifr.ifr_name, dev_str, sizeof(tx_ifr.ifr_name));
	if (c_mtu) { // set MTU
		tx_ifr.ifr_mtu = c_mtu;
		if (ioctl(tx_fd, SIOCSIFMTU, &tx_ifr) < 0) 
			LOG_ERROR("Unable to ioctl the tx socket for "<<nic<<"!"<<endl);
	}

	if (ioctl(tx_fd, SIOCGIFINDEX, &tx_ifr) < 0)  // get iface index
		LOG_ERROR("Unable to ioctl the tx socket for "<<nic<<"!"<<endl);
		
	LOG_DEBUG("Ready to send/recv on "<<nic<<"!"<<endl);
}

void Portal::sendPacket(EmulationEvent* evt, MACAddress& dstmac) {
	//prepare the buffer to put the real bytes in
	LOG_DEBUG("###sendPacket initiated"<<endl);

	int buffer_size, reserved_size;
	byte* pbuf = evt->pkt->getRawBuffer(&buffer_size, &reserved_size);//getRawBuffer is declared in packet.h
	//pbuf is now pointing to rawbuf, which is the real packet created by the simulator. (rawbuf->packet.h )
	int temp_size = buffer_size - reserved_size;
	byte* temp_buf = pbuf+reserved_size;//zzz

	if(!pbuf) {
		LOG_DEBUG("###!pbuf"<<endl);
		//the packet does not have a buffer... we need to serialize into a local buf
		if(evt->pkt->size() > (int)(BUFFSIZE-sizeof(EthernetHeader))) {
			LOG_ERROR("Do not support pkts over "<< (BUFFSIZE-sizeof(EthernetHeader))<<" bytes!"<<endl);
		}
		temp_size=evt->pkt->size();
		pbuf=(byte*)sendbuf;
		reserved_size=sizeof(EthernetHeader);
		temp_buf=(byte*)(sendbuf+reserved_size);
		buffer_size=reserved_size+temp_size;
	}
	else {
		//If pbuf is not empty we will go here
		if(reserved_size < (int)sizeof(EthernetHeader)) {
			//we don't have enough space for the ethernet header...
			LOG_DEBUG("Found a packet with a raw buffer but not enough reserved space!"<<endl);
			temp_size=evt->pkt->size();
			pbuf=(byte*)sendbuf;
			reserved_size=sizeof(EthernetHeader);
			temp_buf=(byte*)(sendbuf+reserved_size);
			buffer_size=reserved_size+temp_size;
		}
		else if(reserved_size>(int)sizeof(EthernetHeader)) {

			//we need the ethernet header to be contigous with the ip payload...
			LOG_DEBUG("##Reserved size larger"<<endl);
			pbuf+=(reserved_size-sizeof(EthernetHeader));
			buffer_size-=(reserved_size-sizeof(EthernetHeader));
			reserved_size-=(reserved_size-sizeof(EthernetHeader));
		}
		//else its the perfect size!
	}
	assert(pbuf);
	if(evt->pkt->size() != temp_size) {
		LOG_ERROR("ACK! evt->pkt->size()("<< evt->pkt->size()<<") != temp_size("<<temp_size<<")"<<endl);
	}	
	//XXX assert(evt->pkt->size() == temp_size);
	EthernetHeader* eth_h = (EthernetHeader*)pbuf;//zzz

	//make the pkt real and put it in temp_buf
	evt->pkt->getMessage()->toRawBytes(temp_buf, temp_size);

	LOG_DEBUG("Packet Content= "<<evt->pkt->getMessage()<<endl);
	assert(temp_size==0);

		LOG_DEBUG("##**Looks like packet failed to send. Trying raw Ip socket mechanism."<<endl);
		IPAddress tgt = ((IPv4Message*)(evt->pkt->getMessageByArchetype(SSFNET_PROTOCOL_TYPE_IPV4)))->getDst();		
		//((IPv4Message*)(evt->pkt->getMessageByArchetype(SSFNET_PROTOCOL_TYPE_IPV4)))->getSrc();

                reserved_size=sizeof(EthernetHeader);
	        temp_buf=(byte*)(pbuf+reserved_size);


		int my_size=buffer_size-reserved_size;
		LOG_DEBUG("buffer size="<<buffer_size<<" reserved size="<<reserved_size<<"  my_size="<<my_size<<"  pbuf content:"<<endl);
	//	for (int il =0; il<buffer_size;il++)
	//	LOG_DEBUG(std::hex<<std::setw(2)<<(int)temp_buf[il]<<endl);
	//	for (int il =0; il<buffer_size;il++)
	//	LOG_DEBUG(std::hex<<std::setw(2)<<(int)pbuf[il]<<endl);

		LOG_DEBUG("Dst IP is="<<tgt<<"Src="<<((IPv4Message*)(evt->pkt->getMessageByArchetype(SSFNET_PROTOCOL_TYPE_IPV4)))->getSrc()<<" Dst Mac= "<<std::hex<<(uint32) * eth_h->getDst() << " Src Mac= "<<std::hex<<(uint32) * eth_h->getSrc()<<endl);
		//IP is=10.10.1.2  
		//now need to convert it to htonl()
		struct sockaddr_in DestAddr;
		DestAddr.sin_family = AF_INET;
		DestAddr.sin_addr.s_addr = htonl(tgt);
//		DestAddr.sin_addr.s_addr = inet_addr(tgt);
		//if( sendto(tx_fd_ip, temp_buf, sizeof(temp_buf), 0, (struct sockaddr *)&DestAddr, sizeof(DestAddr))<0)//sends wrong data(packet content incorrect) to the receiver, thats why the receiver is failing to understand the reply packet even though its receiving it.
		if( sendto(tx_fd_udp, temp_buf, my_size, 0, (struct sockaddr *)&DestAddr, sizeof(DestAddr))<0)
		{
			LOG_DEBUG("*****************Raw Ip packed failed to write. buffer size="<<buffer_size<<endl);
		}
		else
			LOG_DEBUG("Packet successfully sent. Buffer size="<<buffer_size<<endl);
	//}
}

bool Portal::process_pkts(int max_pkts) {
	int rv=0;
	while(max_pkts>0) {
		rv=pcap_dispatch(pcap_handle, -1, process_pkt, (u_char*)this);
		if(rv <= 0)
			return false;
		max_pkts-=rv;
	}
	return true;
}

void Portal::process_pkt(u_char * portal_, const struct pcap_pkthdr * pkt_meta, const u_char * pkt) {
	Portal* portal = (Portal*) portal_;
	EthernetHeader* eth=(EthernetHeader*)pkt;
	uint16_t frame_type;
	IPv4RawHeader* ip=0;
	if(eth->isVLAN()) {
		LOG_WARN("We don't handle vlans for portals!\n");
		VLANHeader* vlan=(VLANHeader*)(pkt+sizeof(EthernetHeader));
		frame_type=vlan->getFrameType();
		ip=(IPv4RawHeader*)(pkt+sizeof(EthernetHeader)+sizeof(VLANHeader));
	}
	else {
		frame_type=eth->getFrameType();
		ip=(IPv4RawHeader*)(pkt+sizeof(EthernetHeader));
	}

	if(pkt_meta->caplen != pkt_meta->len) {
		LOG_WARN("Unable to import packet because the capture length was less the than packet length["<<pkt_meta->caplen<<"!="<<pkt_meta->len<<"]!\n"<<*eth<<"\n"<<*ip<<endl);
		return;
	}
	
	if(EthernetHeader::isIPv4(frame_type)) {
		LOG_DEBUG(" Got IPv4 pkt [size="<<(ip->getLen()-ip->getHdrLen())<<"]\n\t"<<*ip<<"\n");
		//std::cout<<"["<<__LINE__<<"]"<<" Got IPv4 pkt [size="<<(ip->getLen()-ip->getHdrLen())<<"]\n\t"<<*ip<<"\n";
 		portal->dev->insertIntoSim(eth,ip,pkt_meta->caplen);
	}
	else if(EthernetHeader::isIPv6(frame_type)) {
		LOG_WARN("Received an IPv6 Message... dropping it."<<endl)
	}
	else {
		LOG_WARN("Unknown protocol following Ethernet header!"<<endl << *eth <<endl);
	}
}


PRIME_OSTREAM& operator<< (PRIME_OSTREAM& os, Portal const& portal) {
	return os << "["<<portal.emuproto->getInterface()->getName()<<" tx_fd="<<portal.tx_fd<<", rx_fd="<<portal.rx_fd<<"]";
}

void PortalTable::addPortal(IPPrefix& network, Portal* portal, TrafficPortal* proto, bool replace) {
	TrafficPortalPair* conflict = (TrafficPortalPair*) insert((uint32)network.getAddress(), network.getLength(), new TrafficPortalPair(network,proto,portal), replace);
	if(conflict) {
		if(replace) {
			delete conflict; // this is the old route
		} else {
			delete conflict;  // this is the new route
		}
	}
}

TrafficPortalPair* PortalTable::getPortal(uint32 ipaddr) {
	TrafficPortalPair* rv = NULL;
	// find out the route for the given ip address
	lookup(ipaddr, (TrieData**)&rv);
	return rv;
}


PRIME_OSTREAM& operator<<(PRIME_OSTREAM &os, const TrafficPortalPair& x) {
	return os <<"["<<x.prefix<<" --> "<<x.trafficPortal->getInterface()->getUName()<<","<< *(x.portal) <<"]";
}

PRIME_OSTREAM& operator<<(PRIME_OSTREAM &os, const PortalTable& x) {
	PortalTable::dump_helper(x.root, 0, 0, os);
	return os;
}

void PortalTable::dump_helper(TrieNode* root, uint32 sofar,
		int n, PRIME_OSTREAM &os) {
	// Recurse on children, if any.
	for (int i=0; i < TRIE_KEY_SPAN; i++) {
		if(root->children[i]) {
			dump_helper(root->children[i], (sofar << 1) | i, n+1, os);
		}
	}
	if(root->data) {
		os << "\t" << *((TrafficPortalPair*)root->data)<<"\n";
	}
}

// used to register an event class.
SSF_REGISTER_EVENT(ArpEvent, ArpEvent::createArpEvent);
} //namespace ssfnet
} //namespace prime
