from subprocess import Popen
import networkx as nx
from mininet.log import info
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from topology import Topology


class Net:
    def __init__(self, gml_file : str, check_for_lat_long = True, open_cli = True):
        self.G = nx.read_gml(gml_file)

        """ If check_for lat_long is true, remove the nodes whose latitude and longitude is not available"""
        if check_for_lat_long:
            removal = []
            for (i, v) in self.G.nodes(data=True):
                if v.get("Latitude") is None or v.get("Longitude") is None:
                    removal.append(i)

            self.G.remove_nodes_from(removal)


        self.topology = Topology(self.G)
        self.open_cli = open_cli

    def run(self):
        self.clean_net()
        self.start_net()
        if self.open_cli:
            CLI(self.net)
        else:
            self.stop_net()
 

    def clean_net(self):
        """Clean mininet to allow to create new topology"""
        info('*** Clean net\n')
        cmd = "mn -c"
        Popen(cmd, shell=True).wait()

    def start_net(self):
        """Build the topology and initialize the network"""
        self.net = Mininet(self.topology)
        self.net.start()
        for i in range(len(self.G.nodes)):
            s = self.net.get(f's{i}')
            s.cmd(f'ovs-vsctl set bridge s{i} stp-enable=true')
        print("Dumping host connections")
        dumpNodeConnections(self.net.hosts)
        print("Testing network connectivity")
        self.net.pingAll()
        """Since it is not always the case that the network will be setup during 1st run of pingall"""
        self.net.pingAll()


    def stop_net(self):
        """Stop mininet with current network"""
        self.net.stop()


    def stop_all(self):
        try:
            self.stop_net()
        except Exception as _:
            pass


