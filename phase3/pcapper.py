#! /usr/local/bin/python

from scapy.all import *

output = raw_input("enter file path of pcap file: " )


'''
def myhaslayer(p, layer):
    r = p.haslayer(layer)
    if (r == 0):
        return False
    return True


def layerstring(p):
    if (myhaslayer(p, UDP)):
        return "UDP"
    elif (myhaslayer(p, TCP)):
        return "TCP"
    return ""
'''


def write(pkt):
    wrpcap(output, pkt, append = True)  #appends packet to output file 


def onsniff(p):
    write(p)


sniff(iface="eth1", prn = onsniff, count = 100000000)
