#include <linux/if_tun.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>

#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <string.h>
#include <pcap.h>
#include <iostream>
using namespace std;

class PortalDevice { 
  public:
    enum ThreadType { READER=0, WRITER=1 };
    
    PortalDevice();
    ~PortalDevice();
    void init();
    void reader_thread();
    void writer_thread();
    inline int getRxFD() { return rx_fd; }
    bool process_pkts(int);
    static void process_pkt(u_char * portal, const struct pcap_pkthdr * pkt_meta, const u_char * pkt);
  protected:
    void handleArp();
    void insertIntoSim(uint32_t len);

    int maxfd;
    int rx_fd, tx_fd;
    pcap_t * pcap_handle;
};
