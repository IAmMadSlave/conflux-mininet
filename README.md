conflux-mininet Project
=======================

Steps to run the conflux emulation / simulation

1. Download the Mininet lastest version
   * https://github.com/mininet/mininet/wiki/Mininet-VM-Images

2. Download conflux-mininet code
   * git clone xxxx

3. Create a python script to run mininet, fnss and conflux
```python
import networkx as nx
import fnss
import conflux

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController

# load the initial topology from fnss
mn_topo = fnss.to_mininet(fnss_topo,
                          switches=switches, 
                          hosts=hosts,
                          relabel_nodes=True)

# conflux API, add simulator, assign emulated nodes, add traffic matrix
mn_topo = conflux.simulator(simulatorpath, driver-name)
mn_topo = conflux.emunodes_assignment(assignnodes, mn_topo)
mn_topo = conflux.trafficmatrix(trafficfile, mn_topo)

# pass that topology directly to mininet, maybe TCLink could be TCLinkMixed
net = Mininet(topo=mn_topo, link=TCLinkMixed, controller=OVSController)
net.start()

# Test bandwidth between nodes
h1, h8 = net.get('h1', 'h8')
net.iperf((h1, h8))
```

4. Check the real performance of iperf and the simulated performance 
