from mininet.topo import Topo

class LoadBalancerTopo(Topo):
    def build(self):
        switch = self.addSwitch('s1')

        # Clients
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')

        # Servers
        s1 = self.addHost('srv1', ip='10.0.0.101')
        s2 = self.addHost('srv2', ip='10.0.0.102')
        s3 = self.addHost('srv3', ip='10.0.0.103')

        # Links
        for host in [h1, h2, h3, s1, s2, s3]:
            self.addLink(host, switch)

topos = {'lbtopo': LoadBalancerTopo}
