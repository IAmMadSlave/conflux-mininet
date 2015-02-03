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

public class Dumbbell8Node2Emulated1Portal extends ModelInterface{
	public Dumbbell8Node2Emulated1Portal(Database db, Experiment exp) {
		super(db, exp, new ArrayList<ModelParam>());
	}
	public INet buildModel(Map<String, ModelParamValue> parameters) {
		//create the top most network
		INet topnet   = exp.createTopNet("topnet");
		topnet.createShortestPath();
		
		//Create the left network
		INet left_net = topnet.createNet("left_net");
		left_net.createShortestPath();
		
		IHost h1 = left_net.createHost("h1");
		IInterface if1 = h1.createInterface("if0");

		IHost h2 = left_net.createHost("h2");
		IInterface if2 = h2.createInterface("if0");

		IHost h3 = left_net.createHost("h3");
		IInterface if3 = h3.createInterface("if0");
		//make h3 in both the left and right nets emulated
		h3.enableEmulation();

		IHost h4 = left_net.createHost("h4");
		IInterface if4 = h4.createInterface("if0");

		IRouter r = left_net.createRouter("r");

		ILink l1 = left_net.createLink();
		l1.createInterface(if1);
		l1.createInterface(r.createInterface("if1"));

		ILink l2 = left_net.createLink();
		l2.createInterface(if2);
		l2.createInterface(r.createInterface("if2"));

		ILink l3 = left_net.createLink();
		l3.createInterface(if3);
		l3.createInterface(r.createInterface("if3"));

		ILink l4 = left_net.createLink();
		l4.createInterface(if4);
		l4.createInterface(r.createInterface("if4"));
		
		//create the right network
		INet right_net = (INet)left_net.copy("right_net",topnet);

		//link the left and right networks
		ILink toplink = topnet.createLink("toplink");
		toplink.createInterface(((IRouter)left_net.get("r")).createInterface("if0"));
		toplink.createInterface(((IRouter)right_net.get("r")).createInterface("if0"));		
		

                IRouter portal_router = left_net.createRouter("portal_router");
                IInterface portal_interface = portal_router.createInterface("portal_if_10_10_9_0"); //connects to the lan
		
		ILink l20 = left_net.createLink();
		l20.createInterface(((IRouter)left_net.get("r")).createInterface("if20"));
		l20.createInterface(((IRouter)left_net.get("portal_router")).createInterface("if0"));

		

		portal_interface.createTrafficPortal();
		portal_interface.setIpAddress("10.10.9.1");
		portal_interface.addReachableNetwork("10.10.9.0/24");

		//add simulated traffic
		IHost right_h2 = (IHost)right_net.get("h1");
		TrafficFactory trafficFactory = new TrafficFactory(topnet);
		trafficFactory.createSimulatedTCP(10, 1000000000, h1, right_h2);
		trafficFactory.createSimulatedTCP(12, 2, 1000000000, h2, right_h2);
	

		//add emulated traffic
		//IHost right_h3 = (IHost)right_net.get("h3");
		//trafficFactory.createEmulatedTCP(5, 100000000, right_h3, h3);
		
		return topnet;
		
	}
}
//For compiling the model with portal from command line the string name of the net or elements needs to0 be used instead of the variable name.
// java -DRUNTIME_ENV=[c_slave1,d_slave1,eth2,10.10.9.1] -DPORTAL_LINKS=c_slave1:eth2,topnet.left_net.portal_router.portal_if_10_10_9_0 -jar ../primogeni/netscript/dist/jprime.jar create Dumbbell8Node2Emulated1Portal Dumbbell8Node2Emulated1Portal.java
