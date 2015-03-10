#ifndef _HELLOWORLD_H_
#define _HELLOWORLD_H_

#include "os/ssfnet.h"
#include "os/ssfnet_types.h"
#include "os/protocol_session.h"
#include "proto/application_session.h"
#include "proto/simple_socket.h"
#include "proto/tcp/agent/tcp_session.h"
#include "proto/tcp/tcp_master.h"
#include "os/virtual_time.h"
#include "os/timer.h"

namespace prime {
    namespace ssfnet {
        
        class Receiver : public ConfigurableEntity<Receiver,
        ApplicationSession,
        convert_protonum_to_typeid(SSFNET_PROTOCOL_TYPE_MY_NEW_APP)> {
        public:
            typedef SSFNET_PAIR(SimpleSocket*, uint32_t) SocketByte;
             typedef SSFNET_MAP(int, SocketByte) IdSocketByte;
            typedef SSFNET_MAP(IPAddress, SimpleSocket*) IptoSocketMap;
            
            state_configuration {
                shared configurable int flow_id {
                    type=INT;
                    default_value="0";
                    doc_string="ID of this flow";
                };
            };

            
            Receiver();
            
            virtual ~Receiver();
            
            // Called after config() to initialize this protocol session
            virtual void init();
            
            // Called before the protocol session is reclaimed upon the end of simulation
            virtual void wrapup();

            
            //Called by the application session when new traffic is ready to be started
            virtual void startTraffic(StartTrafficEvent* evt, IPAddress ipaddr, MACAddress mac);
            
            //Return flow_id
            int getFlowId();

        protected:
            // Called by the protocol session above to push a protocol message down the stack
            virtual int push(ProtocolMessage* msg, ProtocolSession* hi_sess,
                             void* extinfo = 0, size_t extinfo_size = 0);
            
            // Called by the lower protocol session to pop a protocol message up the statck
            virtual int pop(ProtocolMessage* msg, ProtocolSession* losess, void* extra = 0);
        private:
            TCPMaster* tcp_master;
            IptoSocketMap dst_socket;
            IdSocketByte id_socket_bytes; // sock_session_id, <socket, bytes>
            SimpleSocket* simplesock;
            uint32_t received_bytes;
         };

    }
    
    
}
#endif