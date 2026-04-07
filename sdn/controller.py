from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from collections import defaultdict
import time

class LoadBalancer(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(LoadBalancer, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        
        # Server pool
        self.servers = ['10.0.0.101', '10.0.0.102', '10.0.0.103']
        self.server_index = 0

        # Traffic monitoring
        self.packet_count = defaultdict(int)
        self.last_time = time.time()

    def get_next_server(self):
        server = self.servers[self.server_index]
        self.server_index = (self.server_index + 1) % len(self.servers)
        return server

    def detect_anomaly(self, src_ip):
        self.packet_count[src_ip] += 1
        
        if time.time() - self.last_time > 5:
            for ip, count in self.packet_count.items():
                if count > 50:  # threshold
                    self.logger.info(f"⚠️ Anomaly detected from {ip}")
                    return ip
            self.packet_count.clear()
            self.last_time = time.time()
        return None

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Table-miss flow
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                               match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        ip_pkt = pkt.get_protocol(ipv4.ipv4)

        if ip_pkt:
            src_ip = ip_pkt.src

            # Detect anomaly
            bad_ip = self.detect_anomaly(src_ip)
            if bad_ip:
                match = parser.OFPMatch(ipv4_src=bad_ip)
                actions = []  # drop
                self.add_flow(datapath, 100, match, actions)
                return

            # Load balancing
            dst_ip = ip_pkt.dst
            if dst_ip == "10.0.0.100":  # virtual IP
                selected_server = self.get_next_server()
                self.logger.info(f"Redirecting to {selected_server}")

                actions = [
                    parser.OFPActionSetField(ipv4_dst=selected_server),
                    parser.OFPActionOutput(ofproto.OFPP_FLOOD)
                ]

                match = parser.OFPMatch(ipv4_dst="10.0.0.100")
                self.add_flow(datapath, 10, match, actions)

        # Default flooding
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        out = parser.OFPPacketOut(datapath=datapath,
                                 buffer_id=ofproto.OFP_NO_BUFFER,
                                 in_port=msg.match['in_port'],
                                 actions=actions,
                                 data=msg.data)
        datapath.send_msg(out)
