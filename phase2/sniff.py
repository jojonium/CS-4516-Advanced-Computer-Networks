from scapy.all import *
import time
import threading
import sys
import pprint

flowdict = {}
begintime = time.time()

def threadtest():
    print('--------------------------------------')
    print(time.ctime())
    print(len(flowdict))
    print('--------------------------------------')
    threading.Timer(0.2, threadtest).start()
    for k, v in flowdict.iteritems():
        timediff = begintime - time.time() - v['endtime']
        print("TIMEDIFF: " + str(timediff))

def flowstring(p):
    return "sport:" + str(p.sport) + "dport:" + str(p.dport) + "src:" + p.src + "dst:" + p.dst + layerstring(p)

def hasUDP(p):
    r = p.haslayer(UDP)
    if (r == 0):
        return False
    return True

def layerstring(p):
    if (hasUDP(p)):
        return "UDP"
    return "TCP"

def onsniff(p):
    print("---THE FLOWSTRING---")
    print(flowstring(p))
    fstring = flowstring(p) 
    if fstring not in flowdict:
        flowdict[fstring] = {
            'sport': p.sport,
            'dport': p.dport,
            'src': p.src,
            'dst': p.dst,
            'starttime': begintime - time.time(),
            'bytessent': 0,
            'packetsreceived': 0
        }
        flowdict[fstring]['endtime'] = flowdict[fstring]['starttime']


    currflow = flowdict[fstring]
    currflow['endtime'] = time.time() - begintime
    currflow['bytessent'] += len(p)
    currflow['packetsreceived'] += 1

    print("---THE FLOW LIST---")
    printflowdict()

def printflowdict():
    i = 0
    for k, v in flowdict.iteritems():
        print("flow " + str(i))
        pprint.pprint(v)
        i += 1

threadtest()
sniff(iface="eth1", prn = onsniff, count = 20)



