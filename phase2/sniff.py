from scapy.all import *
import time
import threading
import sys
import pprint

flowdict = {}
begintime = time.time()
burstdaemon = None

def threadtest():
    print('--------------------------------------')
    print(time.ctime())
    print(len(flowdict))
    print('--------------------------------------')
    for k, v in flowdict.iteritems():
        timediff = begintime - time.time() - v['endtime']
        print("TIMEDIFF: " + str(timediff))
    burstdaemon = threading.Timer(0.2, threadtest)
    burstdaemon.daemon = True
    burstdaemon.start()

def flowstring(p):
    return "sport:" + str(p.sport) + "dport:" + str(p.dport) + "src:" + p.src + "dst:" + p.dst + layerstring(p)

def myhaslayer(p, layer):
    r = p.haslayer(layer)
    if (r == 0):
        return False
    return True

'''
def hasUDP(p):
    r = p.haslayer(UDP)
    if (r == 0):
        return False
    return True
'''

def layerstring(p):
    if (myhaslayer(p, UDP)):
        return "UDP"
    elif (myhaslayer(p, TCP)):
        return "TCP"
    return ""

def onsniff(p):
    p.show()
    if (layerstring(p) == ""):
        print ("non TCP or UPD packet, so ignoring it")
    else:
        print("---THE FLOWSTRING---")
        #p.show()
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
sniff(iface="eth1", prn = onsniff, count = 1000000)
'''
try:
    sniff(iface="eth1", prn = onsniff, count = 20)
except KeyboardInterrupt:
    print "attempting to close threads"
    run_event.clear()
    burstdaemon.join()
    print "threads successfully closed"

'''


