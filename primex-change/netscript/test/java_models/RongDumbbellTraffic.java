import java.util.ArrayList;
import java.util.Map;

import jprime.Experiment;
import jprime.TrafficFactory;
import jprime.Host.IHost;
import jprime.Interface.IInterface;
import jprime.Link.ILink;
import jprime.Net.INet;
import jprime.Net.Net;
import jprime.Router.IRouter;
import jprime.TCPMaster.ITCPMaster;
import jprime.TCPTraffic.ITCPTraffic;
import jprime.Traffic.ITraffic;
import jprime.Sender.ISender;
import jprime.Receiver.IReceiver;
import jprime.database.Database;
import jprime.util.ModelInterface;
import jprime.MyNewAppTraffic.IMyNewAppTraffic;

/**
 * @author Nathanael Van Vorst
 */
public class RongDumbbellTraffic extends ModelInterface{

	/**
	 * @param db
	 * @param exp
	 */
	public RongDumbbellTraffic(Database db, Experiment exp) {
		super(db, exp, new ArrayList<ModelInterface.ModelParam>());
	}

	/**
	 * @param db
	 * @param expName
	 */
	public RongDumbbellTraffic(Database db, String expName) {
		super(db, expName, new ArrayList<ModelInterface.ModelParam>());
	}

	/* (non-Javadoc)
	 * @see jprime.ModelInterface#buildModel()
	 */
	@Override
	public INet buildModel(Map<String, ModelParamValue> parameters) {
	    ArrayList<IRouter> routers_list=new ArrayList<IRouter>();
        ArrayList<IHost> hosts_list=new ArrayList<IHost>();
        
		Net top = exp.createTopNet("topnet");
		top.createShortestPath();
		//top.createAlgorithmicRouting();
		
		IRouter r0 = top.createRouter("router0");
		routers_list.add(r0);
		IInterface r0_h1= r0.createInterface("ifh1");
		IInterface r0_h3= r0.createInterface("ifh3");
		IInterface r0_r1= r0.createInterface("ifr1");
		r0_r1.setBitRate("1000000000"); //1G
        r0_r1.setLatency("0.0");
        r0_r1.setBufferSize("65535");
        r0_r1.setQueueType("RedQueue");
        r0_h1.setBitRate("1000000000"); //1G
        r0_h1.setLatency("0.0");
        r0_h1.setBufferSize("65535");
        r0_h3.setBitRate("1000000000"); //1G
        r0_h3.setLatency("0.0");
        r0_h3.setBufferSize("65535");
       		
		IRouter r1 = top.createRouter("router1");
		routers_list.add(r1);
		IInterface r1_r0= r1.createInterface("ifr0");
		IInterface r1_h2= r1.createInterface("ifh2");
		IInterface r1_h4= r1.createInterface("ifh4");
		r1_r0.setBitRate("1000000000"); //1G
        r1_r0.setLatency("0.0");
        r1_r0.setBufferSize("65535");
        r1_r0.setQueueType("RedQueue");
        r1_h2.setBitRate("1000000000"); //1G
        r1_h2.setLatency("0.0");
        r1_h2.setBufferSize("65535");
        r1_h4.setBitRate("1000000000"); //1G
        r1_h4.setLatency("0.0");
        r1_h4.setBufferSize("65535");
             
		IHost h1 = top.createHost("host1");
		hosts_list.add(h1);
		IInterface h1_if0= h1.createInterface("if0");
		h1_if0.setBitRate("1000000000"); //1G
        h1_if0.setLatency("0.0");
        h1_if0.setBufferSize("65535");
		ITCPMaster tcp1 = h1.createTCPMaster();
		tcp1.setMss("1400");
		tcp1.setTcpCA("reno");
		ISender s = h1.createSender();
		s.setFlowId("1");
//		s.setListeningPort("9000");
		
		IHost h2 = top.createHost("host2");
		hosts_list.add(h2);
		IInterface h2_if0= h2.createInterface("if0");
		h2_if0.setBitRate("1000000000"); //1G
        h2_if0.setLatency("0.0");
        h2_if0.setBufferSize("65535");
		ITCPMaster tcp2 = h2.createTCPMaster();
		tcp2.setMss("1400");
        tcp2.setTcpCA("reno");
        IReceiver r = h2.createReceiver();
        r.setFlowId("1");
        
        
        IHost h3 = top.createHost("host3");
        hosts_list.add(h3);
        IInterface h3_if0= h3.createInterface("if0");
        h3_if0.setBitRate("1000000000"); //1G
        h3_if0.setLatency("0.0");
        h3_if0.setBufferSize("65535");
        ITCPMaster tcp3 = h3.createTCPMaster();
        tcp3.setMss("1400");
        tcp3.setTcpCA("reno");
        h3.createHTTPServer();
        
        IHost h4 = top.createHost("host4");
        hosts_list.add(h4);
        IInterface h4_if0= h4.createInterface("if0");
        h4_if0.setBitRate("1000000000"); //1G
        h4_if0.setLatency("0.0");
        h4_if0.setBufferSize("65535");
        ITCPMaster tcp4 = h4.createTCPMaster();
        tcp4.setMss("1400");
        tcp4.setTcpCA("reno");
        h4.createHTTPClient();
        
        
        ILink l_h1= top.createLink("r0_h1");
		l_h1.createInterface(r0_h1);
		l_h1.createInterface(h1_if0);
		l_h1.setDelay((float)0.001); 
		l_h1.setBandwidth("1000000000");

		ILink l_h2= top.createLink("r1_h2");
		l_h2.createInterface(r1_h2);
		l_h2.createInterface(h2_if0);
		l_h2.setDelay((float)0.0000001); 
		l_h2.setBandwidth("1000000000");
		
		ILink l_h3= top.createLink("r0_h3");
        l_h3.createInterface(r0_h3);
        l_h3.createInterface(h3_if0);
        l_h3.setDelay((float)0.001); 
        l_h3.setBandwidth("1000000000");

        ILink l_h4= top.createLink("r1_h4");
        l_h4.createInterface(r1_h4);
        l_h4.createInterface(h4_if0);
        l_h4.setDelay((float)0.0000001); 
        l_h4.setBandwidth("1000000000");
		
		ILink l_r0_r1= top.createLink("l_r0_r1");
		l_r0_r1.createInterface(r1_r0);
		l_r0_r1.createInterface(r0_r1);
        l_r0_r1.setDelay((float)0.015); 
//        l_r0_r1.setBandwidth("64000000");
//		int b = Integer.parseInt(System.getProperty("MbS","64"))*1000000;
        l_r0_r1.setBandwidth("1000000000");
        int b = Integer.parseInt(System.getProperty("MbS","1000"))*1000000;
		System.out.println("Bandwidth="+b+" Mb/s");
		l_r0_r1.setBandwidth(Integer.toString(b));
		exp.setHostsList(hosts_list);
		exp.setRoutersList(routers_list);
		
		ITraffic t = top.createTraffic();
		float start = 1;
		float stop = 10;
		float interval = 1;
		String node_uid = "/Users/rong/Documents/workspace/primex/netscript/exp/" + exp.getName() + "/" +  exp.getName() + "_node_uid.txt";
		String demand = "/Users/rong/Documents/workspace/primex/netsim/" + "demand_file";
		IMyNewAppTraffic g1 = t.createMyNewAppTraffic();
		g1.setSrcs(".:host2");
		g1.setDsts(".:host1");
		g1.setStartTime(start);
		g1.setStop(stop);
		g1.setUpdateInterval(interval);
		g1.setDemandFile(demand);
		g1.setHostUid(node_uid);
		
        float start2 = 0;
        ITCPTraffic g2 = t.createTCPTraffic();
        g2.setSrcs(".:host4");
        g2.setDsts(".:host3");
        g2.setStartTime(start2);
        g2.setFileSize(10000000);
        g2.setConnectionsPerSession(1);
        g2.setNumberOfSessions("1");
        
		return top;
	}

}
