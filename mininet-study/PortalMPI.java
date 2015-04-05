import java.util.ArrayList;
import java.util.Map;

import jprime.Experiment;
import jprime.TrafficFactory;
import jprime.Host.IHost;
import jprime.Interface.IInterface;
import jprime.Link.ILink;
import jprime.Net.INet;
import jprime.Router.IRouter;
import jprime.database.Database;
import jprime.util.ModelInterface;

public class PortalMPI extends ModelInterface{
	public PortalMPI(Database db, Experiment exp) {
		super(db, exp, new ArrayList<ModelParam>());
	}
	public INet buildModel(Map<String, ModelParamValue> parameters) {
		//create the top most network
		INet topnet   = exp.createTopNet("top");
		topnet.createShortestPath();
		
		//Create the left network
		INet left_net = topnet.createNet("left");
		left_net.createShortestPath();
		
		IHost h1 = left_net.createHost("h1");
		IInterface if1 = h1.createInterface("if0");
          if1.setBufferSize("75000000");
          if1.setBitRate("10000000000"); //10000Mbps

		IHost h2 = left_net.createHost("h2");
		IInterface if2 = h2.createInterface("if0");
          if2.setBufferSize("75000000");
          if2.setBitRate("10000000000"); //10000Mbps


		IHost h3 = left_net.createHost("h3");
		IInterface if3 = h3.createInterface("if0");
          if3.setBufferSize("75000000");
          if3.setBitRate("10000000000"); //10000Mbps


		//Router and its interefaces
		IRouter r1 = left_net.createRouter("r1");
		IInterface if1_r1=r1.createInterface("if1");
          if1_r1.setBufferSize("75000000");
          if1_r1.setBitRate("10000000000"); //10000Mbps
		IInterface  if2_r1=r1.createInterface("if2");
          if2_r1.setBufferSize("75000000");
          if2_r1.setBitRate("10000000000"); //10000Mbps
		IInterface if3_r1=r1.createInterface("if3");
          if3_r1.setBufferSize("75000000");
          if3_r1.setBitRate("10000000000"); //10000Mbps
		IInterface if0_r1=r1.createInterface("if0");
          if0_r1.setBufferSize("75000000");
          if0_r1.setBitRate("10000000000"); //10000Mbps



		//links of left_net
		ILink l1 = left_net.createLink();
		l1.createInterface(if1);
		l1.createInterface(if1_r1);
          l1.setBandwidth("10000000000");
          l1.setDelay((float)0.000001);

		ILink l2 = left_net.createLink();
		l2.createInterface(if2);
		l2.createInterface(if2_r1);
          l2.setBandwidth("10000000000");
          l2.setDelay((float)0.000001);

		ILink l3 = left_net.createLink();
		l3.createInterface(if3);
		l3.createInterface(if3_r1);
          l3.setBandwidth("10000000000");
          l3.setDelay((float)0.000001);



		//Create the right network
		INet right_net = topnet.createNet("right");
		right_net.createShortestPath();

		IHost h4 = right_net.createHost("h4");
		IInterface if4 = h4.createInterface("if0");
          if3.setBufferSize("75000000");
          if4.setBitRate("10000000000"); //10000Mbps

		IHost h5 = right_net.createHost("h5");
		IInterface if5 = h5.createInterface("if0");
          if5.setBufferSize("75000000");
          if5.setBitRate("10000000000"); //10000Mbps

		IHost h6 = right_net.createHost("h6");
		IInterface if6 = h6.createInterface("if0");
          if6.setBufferSize("75000000");
          if6.setBitRate("10000000000"); //10000Mbps

        //      IHost h4 = left_net.createHost("h4");
        //      IInterface if4 = h4.createInterface("if0");

		IRouter r2 = right_net.createRouter("r2");
		IInterface if1_r2=r2.createInterface("if1");
          if1_r2.setBufferSize("75000000");
          if1_r2.setBitRate("10000000000"); //10000Mbps
		IInterface  if2_r2=r2.createInterface("if2");
          if2_r2.setBufferSize("75000000");
          if2_r2.setBitRate("10000000000"); //10000Mbps
		IInterface  if3_r2=r2.createInterface("if3");
          if3_r2.setBufferSize("75000000");
          if3_r2.setBitRate("10000000000"); //10000Mbps
		IInterface if0_r2=r2.createInterface("if0");
          if0_r2.setBufferSize("75000000");
          if0_r2.setBitRate("10000000000"); //10000Mbps


		ILink l4 = right_net.createLink();
		l4.createInterface(if4);
		l4.createInterface(if1_r2);
          l4.setBandwidth("10000000000");
          l4.setDelay((float)0.000001);

		ILink l5 = right_net.createLink();
		l5.createInterface(if5);
		l5.createInterface(if2_r2);
          l5.setBandwidth("10000000000");
          l5.setDelay((float)0.000001);

		ILink l6 = right_net.createLink();
		l6.createInterface(if6);
		l6.createInterface(if3_r2);
          l6.setBandwidth("10000000000");
          l6.setDelay((float)0.000001);


		//link the left and right networks
		ILink toplink = topnet.createLink("toplink");
		toplink.createInterface(if0_r1);
		toplink.createInterface(if0_r2);

          toplink.setBandwidth("10000000000");
          toplink.setDelay((float)0.000001);

//		Creating the portal	
                IInterface portal_if1 = r1.createInterface("portal_if_10_10_1_0"); //connects to the portal netns
                portal_if1.createTrafficPortal();
          portal_if1.setBufferSize("75000000");
          portal_if1.setBitRate("10000000000"); //10000Mbps
                portal_if1.setIpAddress("10.10.1.1");
                portal_if1.addReachableNetwork("10.10.1.0/24");

                IInterface portal_if2 = r2.createInterface("portal_if_10_10_2_0"); //connects to the portal netns
                portal_if2.createTrafficPortal();
          portal_if2.setBufferSize("75000000");
          portal_if2.setBitRate("10000000000"); //10000Mbps
                portal_if2.setIpAddress("10.10.2.1");
                portal_if2.addReachableNetwork("10.10.2.0/24");


	
//		add traffic
//		TrafficFactory trafficFactory = new TrafficFactory(topnet);
//		trafficFactory.createSimulatedTCP(10, 1000000000L, h1, right_h2);
//		trafficFactory.createSimulatedTCP(13, 2, 10000000000L, h2, right_h2);
		return topnet;
	}
}

 
