#include "portalsimulation.h"
#include <cstdlib>
#include <netinet/in.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <netinet/if_ether.h> 
#include <net/ethernet.h>
#include <netinet/ether.h> 
#include <netinet/ip.h>
#define LOG_DEBUG(X) std::cout<<"["<<__LINE__<<"]"<<X;

// Global variable
//pcap_t * pcap_handle;
//int rx_fd, tx_fd;
bool stop = false;

/* tcpdump header (ether.h) defines ETHER_HDRLEN) */
#ifndef ETHER_HDRLEN 
#define ETHER_HDRLEN 14
#endif

u_int16_t handle_ethernet
        (u_char *args,const struct pcap_pkthdr* pkthdr,const u_char*
        packet);

u_char* handle_IP
        (u_char *args,const struct pcap_pkthdr* pkthdr,const u_char*
        packet);

/*
 * Structure of an internet header, naked of options.
 *
 * Stolen from tcpdump source (thanks tcpdump people)
 *
 * We declare ip_len and ip_off to be short, rather than u_short
 * pragmatically since otherwise unsigned comparisons can result
 * against negative integers quite easily, and fail in subtle ways.
 */
struct my_ip {
  u_int8_t  ip_vhl;   /* header length, version */
#define IP_V(ip)  (((ip)->ip_vhl & 0xf0) >> 4)
#define IP_HL(ip) ((ip)->ip_vhl & 0x0f)
  u_int8_t  ip_tos;   /* type of service */
  u_int16_t ip_len;   /* total length */
  u_int16_t ip_id;    /* identification */
  u_int16_t ip_off;   /* fragment offset field */
#define IP_DF 0x4000      /* dont fragment flag */
#define IP_MF 0x2000      /* more fragments flag */
#define IP_OFFMASK 0x1fff   /* mask for fragmenting bits */
  u_int8_t  ip_ttl;   /* time to live */
  u_int8_t  ip_p;   /* protocol */
  u_int16_t ip_sum;   /* checksum */
  struct  in_addr ip_src,ip_dst;  /* source and dest address */
};

u_char* handle_IP
        (u_char *args,const struct pcap_pkthdr* pkthdr,const u_char*
        packet)
{
    const struct my_ip* ip;
    u_int length = pkthdr->len;
    u_int hlen,off,version;
    int i;

    int len;

    /* jump pass the ethernet header */
    ip = (struct my_ip*)(packet + sizeof(struct ether_header));
    length -= sizeof(struct ether_header); 

    /* check to see we have a packet of valid length */
    if (length < sizeof(struct my_ip))
    {
        printf("truncated ip %d",length);
        return NULL;
    }

    len     = ntohs(ip->ip_len);
    hlen    = IP_HL(ip); /* header length */
    version = IP_V(ip);/* ip version */

    /* check version */
    if(version != 4)
    {
      fprintf(stdout,"Unknown version %d\n",version);
      return NULL;
    }

    /* check header length */
    if(hlen < 5 )
    {
        fprintf(stdout,"bad-hlen %d \n",hlen);
    }

    /* see if we have as much packet as we should */
    if(length < len)
        printf("\ntruncated IP - %d bytes missing\n",len - length);

    /* Check to see if we have the first fragment */
    off = ntohs(ip->ip_off);
    if((off & 0x1fff) == 0 )/* aka no 1's in first 13 bits */
    {/* print SOURCE DESTINATION hlen version len offset */
        fprintf(stdout,"IP: ");
        fprintf(stdout,"%s ",
                inet_ntoa(ip->ip_src));
        fprintf(stdout,"%s %d %d %d %d\n",
                inet_ntoa(ip->ip_dst),
                hlen,version,len,off);
    }

    return NULL;
}

/* handle ethernet packets, much of this code gleaned from
 * print-ether.c from tcpdump source
 */
u_int16_t handle_ethernet
        (u_char *args,const struct pcap_pkthdr* pkthdr,const u_char*
        packet)
{
    u_int caplen = pkthdr->caplen;
    u_int length = pkthdr->len;
    struct ether_header *eptr;  /* net/ethernet.h */
    u_short ether_type;

    if (caplen < ETHER_HDRLEN)
    {
        fprintf(stdout,"Packet length less than ethernet header length\n");
        return -1;
    }

    /* lets start with the ether header... */
    eptr = (struct ether_header *) packet;
    ether_type = ntohs(eptr->ether_type);

    /* Lets print SOURCE DEST TYPE LENGTH */
    fprintf(stdout,"ETH: ");
    fprintf(stdout,"%s "
            ,ether_ntoa((struct ether_addr*)eptr->ether_shost));
    fprintf(stdout,"%s "
            ,ether_ntoa((struct ether_addr*)eptr->ether_dhost));

    /* check to see if we have an ip packet */
    if (ether_type == ETHERTYPE_IP)
    {
        fprintf(stdout,"(IP)");
    }else  if (ether_type == ETHERTYPE_ARP)
    {
        fprintf(stdout,"(ARP)");
    }else  if (eptr->ether_type == ETHERTYPE_REVARP)
    {
        fprintf(stdout,"(RARP)");
    }else {
        fprintf(stdout,"(?)");
    }
    fprintf(stdout," %d\n",length);

    return ether_type;
}

PortalDevice::PortalDevice():rx_fd(-1),
  tx_fd(-1),
  pcap_handle(0),
  maxfd(0) {
}

PortalDevice::~PortalDevice(){
}

void PortalDevice::init(){

//setup the pcap rx channel
  bpf_u_int32 maskp;
  bpf_u_int32 netp;
  char *dev; /* name of the device to use */ 
  char *net; /* dot notation of the network address */
  char *mask;/* dot notation of the network mask    */
  char errbuf[PCAP_ERRBUF_SIZE];
  struct in_addr addr;

  std::string nic("eth2");
  char dev_str[nic.length() + 1];
  sprintf(dev_str,"%s", nic.c_str());

  LOG_DEBUG("Creating pcap handle for "<<nic<<"\n");
  if (pcap_lookupnet(dev_str, &netp, &maskp, errbuf) == -1) {
    LOG_DEBUG("Couldn't get netmask for device "<<nic<<", err:"<<errbuf<<endl);
  }

  // check the interface
  /* get the network address in a human readable form */
  addr.s_addr = netp;
  net = inet_ntoa(addr);

  if(net == NULL)/* thanks Scott :-P */
  {
    perror("inet_ntoa");
    exit(1);
  }

  LOG_DEBUG("NET: "<< net << endl);
  /* do the same as above for the device's mask */
  addr.s_addr = maskp;
  mask = inet_ntoa(addr);
  
  if(mask == NULL)
  {
    perror("inet_ntoa");
    exit(1);
  }
  LOG_DEBUG("MASK: "<<mask<<endl);
 
  pcap_handle = pcap_open_live(dev_str, 65535, 0, -1, errbuf); 

  if(!pcap_handle) {
    LOG_DEBUG("Couldn't open device "<<nic<<", err:"<<errbuf<<endl);
  }

  if (pcap_setnonblock(pcap_handle,1,errbuf) == -1) {
    LOG_DEBUG("Couldn't change "<<nic<<" to non-blocking! err:"<<errbuf<<endl);
  }

  if (pcap_getnonblock(pcap_handle,errbuf)==0) {
    LOG_DEBUG("Couldn't change "<<nic<<" to non-blocking! err:"<<errbuf<<endl);
  }

  rx_fd = pcap_get_selectable_fd(pcap_handle);
  LOG_DEBUG("rx_fd:"<<rx_fd<<"!"<<endl);
  if(rx_fd == -1) {
    LOG_DEBUG("Libpcap couldn't get a selectable FD for "<<nic<<endl);
  }

  if(pcap_setdirection(pcap_handle,PCAP_D_IN)==-1) {
    LOG_DEBUG("Libpcap couldn't set the capture direction for "<<nic<<endl);
  }

//setup the tx channel
  tx_fd = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
  if(tx_fd == -1) {
    LOG_DEBUG("Unable to open (tx) raw socket for "<<nic<<"!"<<endl);
  }
  
  LOG_DEBUG("Ready to send/recv on "<<nic<<"!"<<endl);
}

void PortalDevice::reader_thread() {
  maxfd++;
  LOG_DEBUG("Starting portal read thread!  maxfd="<<maxfd<<endl);

  fd_set base_fds, fds;
  FD_ZERO(&base_fds);
  FD_SET(this->getRxFD(),&base_fds);

  int max_loops=500;
  bool more_packets=false;
  int retval; 
  struct timeval tv; 
  LOG_DEBUG("FD setup done"<<endl);

  for(;!stop;) {
//FD_COPY isn't standard... a simple assignment should work though....
//FD_ZERO(&fds);
    fds=base_fds;
    LOG_DEBUG("before select"<<endl);
    tv.tv_sec = 5;
    tv.tv_usec = 0;
    retval = select(maxfd, &fds, NULL, NULL, NULL);

    if (retval == -1)
        perror("select()");
    else if (retval) {
        LOG_DEBUG("Data is available now"<<endl);
    } else {
        LOG_DEBUG("No data within five seconds"<<endl);
    } 
    LOG_DEBUG("after select"<<endl);

    max_loops=500;
    more_packets=false;
    do {
      more_packets=more_packets || this->process_pkts(100);
      max_loops--;
    } while(more_packets && max_loops>0);
  }
}

bool PortalDevice::process_pkts(int max_pkts) {
  int rv=0;
  while(max_pkts>0) {
    rv=pcap_dispatch(pcap_handle, -1, process_pkt, (u_char*)this);
    if(rv <= 0)
      return false;
    max_pkts-=rv;
  }
  return true;
}

void PortalDevice::process_pkt(u_char * portal_, const struct pcap_pkthdr * pkt_meta, const u_char * pkt) {

  u_int16_t type = handle_ethernet(portal_,pkt_meta,pkt);

  if(type == ETHERTYPE_IP)  {/* handle IP packet */
    handle_IP(portal_,pkt_meta,pkt);
  } else if(type == ETHERTYPE_ARP) {/* handle arp packet */
  } else if(type == ETHERTYPE_REVARP) {/* handle reverse arp packet */
  }
}

int main ()
{
    PortalDevice *mypd;

    if (geteuid() != 0) {
      cout << "error: you must be root to run this\n";
      return -1;
    }

    mypd = new PortalDevice();
    mypd->init();
    mypd->reader_thread();
    LOG_DEBUG("End of program\n");
}
