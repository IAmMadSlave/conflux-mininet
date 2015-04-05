#ifndef __HELLOWORLD_TRAFFIC_H__
#define __HELLOWORLD_TRAFFIC_H__


#include "os/ssfnet.h"
#include "os/traffic.h"
#include "os/config_type.h"
#include "os/config_entity.h"
#include "os/virtual_time.h"
#include "ssf.h"
#include "os/ssfnet_types.h"
#include "proto/tcp/test/helloworld.h"

namespace prime {
    namespace ssfnet {
#define MYNEWAPP_TRAFFIC 5020
        
//        extern string node_uid_file;
        class MyNewAppStartTrafficEvent: public StartTrafficEvent {
        public:
            /** The default constructor. */
            MyNewAppStartTrafficEvent();
            
            /** The constructor. */
            MyNewAppStartTrafficEvent(UID_t trafficTypeUID, uint32_t id, UID_t h_uid, UID_t d_uid, uint32_t d_ip, VirtualTime st);
            
            /** The constructor. */
            MyNewAppStartTrafficEvent(TrafficType* trafficType, uint32_t id, UID_t h_uid, UID_t d_uid, uint32_t d_ip, VirtualTime st);
            
            /** The ssf clone constructor. */
            MyNewAppStartTrafficEvent(MyNewAppStartTrafficEvent* evt);
            
            /** The copy constructor. */
            MyNewAppStartTrafficEvent(const MyNewAppStartTrafficEvent& evt);
            
            /** The destructor. */
            virtual ~MyNewAppStartTrafficEvent();
            
            virtual Event* clone() {
                return new MyNewAppStartTrafficEvent(*this);
            }
            
            virtual prime::ssf::ssf_compact* pack();
            
            virtual void unpack(prime::ssf::ssf_compact* dp);
            
            /* The number of bytes to send per interval. */
            void setBytesToSendPerIntv(uint32_t bytes_per_intervals);
            
            /* Called by the client to get the bytes to send per interval. */
            uint32_t getBytesToSendPerIntv();
            
            void setInterval(float interval);
            
            float getInterval();
            
        private:
            uint32_t bytes_to_send_per_interval; //The unique session id.
            float interval;
        public:
            /**
             * This method is the factory method for deserializing the event
             * object. A new traffic event object is created.
             */
            static prime::ssf::Event* createMyNewAppStartTrafficEvent(prime::ssf::ssf_compact* dp);
            
            /* This macros is used by SSF to declare an event class. */
            SSF_DECLARE_EVENT(MyNewAppStartTrafficEvent);
        };
        
        
        class MyNewAppTraffic : public ConfigurableEntity <MyNewAppTraffic,
        StaticTrafficType, MYNEWAPP_TRAFFIC> {
            friend class MyNewAppStartTrafficEvent;
        public:
            typedef SSFNET_MAP(UID_t, uint32_t) UIDByteMap;
            typedef SSFNET_MAP(SSFNET_STRING, UID_t)NameUIDMap;
//            typedef SSFNET_MAP(UID_t, UID_t)ReceiverSenderMap;
            
            state_configuration {
                shared configurable uint32_t dst_port {
                    type=INT;
                    default_value="9000";
                    doc_string="The destination port for an MyNewAPP connection.";
                };
                shared configurable float stop {
                    type=FLOAT;
                    default_value="100";
                    doc_string="Time to stop the traffic (default: 100).";
                };
                shared configurable float update_interval {
                    type=FLOAT;
                    default_value="1";
                    doc_string="Time interval to check demand file (default: 1).";
                };
                shared configurable SSFNET_STRING host_uid {
                    type=STRING;
                    default_value=" ";
                    doc_string="The file that indicates the all hosts of the network";
                };
                shared configurable SSFNET_STRING demand_file {
                    type=STRING;
                    default_value=" ";
                    doc_string="The file that indicates the empirical delays between clusters";
                };
            };

            MyNewAppTraffic();
            
            virtual ~MyNewAppTraffic();
            
            //return the protocol this traffic is intended for
            virtual ConfigType* getProtocolType();
            
            /*
             * called when the traffic type is initially created
             */
            virtual void init();
            
            /*
             * the traffic manager will call this to find out if this traffic type should be included
             */
            virtual bool shouldBeIncludedInCommunity(Community* com);
            
            //called by the traffic manager to if this traffic needs to start traffic
            virtual void getNextEvent(
                                      StartTrafficEvent*& traffics_to_start, //if traffic needs to be started now, create a start traffic event and set this
                                      UpdateTrafficTypeEvent*& update_evt, //if there needs to be an update event the traffic manager will deliver it to all concerned traffic types on remote traffic managers
                                      bool& wrap_up, //if this traffic is finished set to true and the traffic mgr will clean this up.
                                      VirtualTime& recall_at //when should this be recalled to start more traffic; set to zero recall immediately
                                      );
            bool checkBytesFromPhy(SSFNET_STRING demand_file);
            int getDstPort();
            float getInterval();
            float getStop();

        private:
//            float interval;
//            float stop;
//            int dst_port;
            uint32_t traffic_id;
            UIDByteMap host_bytes;
            NameUIDMap host_id;
//            ReceiverSenderMap recv_send;
            
                   };
    }
}
#endif