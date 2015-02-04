

class MiniSymbio:

# hosts_sim2mn: a map from simulation host ids to mininet vm hosts
# hosts_mn2sim: a map from vm hosts (or vm pids) to simulation host ids
# links_sim2mn: a map from simulation segment/pipe ids to mininet links

    def __init__(modfile)
    # 1. parse the input and take the downscaled (mininet) model
    # 2. create mininet objects (vm nodes and tc links) and populate the data structures above (the maps)
    # 3. set up the communication with the simulator
    #           initially we can simple open a file for input (for commands changing tc links); 
    #           also a file for output (stats collected for the traffic demand at the vm hosts)
    #           Note: we will define the protocol format later

    def async_cmd(cmd) # return a map from mininet host (or pids) to Popen objects
    # iterate through the vm hosts and create popens one for each vm:
    #           Hosts.popen run the commands
    #           use PIPE for stdin, stdout; and STDOUT for stderr
    #           possible usage: may be able to run 'tcpprobe' in the background
    
    def async_terminate/stop/wait(popens):
    # similar to the corresponding host functions
    # also, one should be able to monitor the output from the commands (similar to pmonitor, or host.monitor/waitOutput

    def cmd(cmd): # and return the the collective output
    # iterate through the vm hosts and create popens
    # wait for each vm output (look for hosts.cmd() implementation)


    # this is for running things in background
    def run_cmd_on_hosts_collect_results(h, cmd):
    # iterate through hosts, write the bash command line to popens[h].stdin.fileno
    # then, iterate through the hosts, and read a line (?)
    # actually, we can do exact the same thing as in the Host implementation:
    #   sendCmd() -> write() -> write to popens[h].stdin.fileno
    #   waitOutput() -> monitor() 


[ 'bash', '-ms', 'symbio:'+'host's pid' ]

    def run():
    # in the main function:
        
