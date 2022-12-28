import socket
import time
from socket import socket, AF_INET, SOCK_DGRAM


def local_ipv4():
    st = socket(AF_INET, SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        ip_l = st.getsockname()[0]
    except Exception:
        ip_l = '127.0.0.1'
    finally:
        st.close()
    return ip_l


def is_port_open(host, port):
    s = socket()
    s.settimeout(0.01)
    try:
        s.connect((host, port))
    except:
        return False
    else:
        return True


def scan_lan(port):
    xd = time.time()
    ip = local_ipv4()
    found = []
    samp = '.'.join(ip.split('.')[:-1]) + '.'
    for i in range(1, 256):
        ip = samp + str(i)
        op = is_port_open(ip, port)
        if op:
            found.append(ip)
    t = time.time() - xd
    return found



