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

public class MininetConfluxPollux extends ModelInterface{
	public MininetConfluxPollux(Database db, Experiment exp) {
		super(db, exp, new ArrayList<ModelParam>());
	}
	public INet buildModel(Map<String, ModelParamValue> parameters) {
		//create the top most network
		INet topnet   = exp.createTopNet("topnet");
		topnet.createShortestPath();
		

		//creating hosts
		IHost h1 = topnet.createHost("h1");
		IInterface if1 = h1.createInterface("if0");

		IHost h2 = topnet.createHost("h2");
		IInterface if2 = h2.createInterface("if0");

		IHost h3 = topnet.createHost("h3");
		IInterface if3 = h3.createInterface("if0");

		//creating Routers
		IRouter center_router = topnet.createRouter("center_router");
        IRouter portal_router = topnet.createRouter("portal_router");

		
		//h1 connects to portal_router; h2, h3 connects to r
		ILink l1 = topnet.createLink();
		l1.createInterface(if1);
		l1.createInterface(portal_router.createInterface("if1"));

		ILink l2 = topnet.createLink();
		l2.createInterface(if2);
		l2.createInterface(center_router.createInterface("if2"));
		
		ILink l3 = topnet.createLink();
		l3.createInterface(if3);
		l3.createInterface(center_router.createInterface("if3"));



		//connecting portal_router with r
		ILink lrtor = topnet.createLink();
		lrtor.createInterface(((IRouter)topnet.get("center_router")).createInterface("if0"));
		lrtor.createInterface(((IRouter)topnet.get("portal_router")).createInterface("if0"));
		
		
		//setting portal with an interface of router "portal_router"
        IInterface portal_interface = portal_router.createInterface("portal_if_10_10_2_0"); //connects to the portal netns
		portal_interface.createTrafficPortal();
		portal_interface.setIpAddress("10.10.2.1");
		portal_interface.addReachableNetwork("10.10.2.0/24");
		//setting portal with an interface of router "center_router"
        IInterface portaltoPh_interface = center_router.createInterface("portal_if_10_10_3_0"); //connects to the portal netns
		portaltoPh_interface.createTrafficPortal();
		portaltoPh_interface.setIpAddress("10.10.3.2");
		portaltoPh_interface.addReachableNetwork("10.10.1.0/24");	
		


		//add simulated traffic
		TrafficFactory trafficFactory = new TrafficFactory(topnet);

                trafficFactory.createSimulatedTCP(10, 2, 1000000000, h1, h2);
                trafficFactory.createSimulatedTCP(12, 2, 1000000000, h1, h2);
                trafficFactory.createSimulatedTCP(14, 2, 1000000000, h1, h2);
                trafficFactory.createSimulatedTCP(16, 2, 1000000000, h1, h2);
                trafficFactory.createSimulatedTCP(18, 2, 1000000000, h1, h2);
	
		return topnet;
		
	}
}
//For compiling the model with portal from command line the string name of the net or elements needs to be used instead of the variable name. Compiling:-
	//java -DRUNTIME_ENV=[c_slave1,d_slave1,eth2,10.10.1.1] -DPORTAL_LINKS=c_slave1:eth2,topnet.portal_router.portal_if_10_10_1_0 -jar ../primogeni/netscript/dist/jprime.jar create MininetConfluxCastor MininetConfluxCastor.java 192.168.0.0/16
//Running:
	//../primex/netsim/primex -tp 10.10.1.1 106 1200 MininetConfluxCastor_part_1.tlv
