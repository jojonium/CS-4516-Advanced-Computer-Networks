from kamene.all import *
import time
import threading
import sys

flowdict = {}
begintime = time.time()
burstdaemon = None
previouslyprinted = False

def endburst():
    global flowdict
    doneflowstrings = []
    for k, v in flowdict.items():
        if flowstringf(v) not in doneflowstrings:
            # find the inverse flow
            currflow = v
            otherflow = None
            packetsreceived = 0
            bytesreceived = 0
            if otherflowstringf(v) in flowdict:
                otherflow = flowdict[otherflowstringf(v)]
                packetsreceived = otherflow['packetssent']
                bytesreceived = otherflow['bytessent']
                doneflowstrings.append(otherflowstringf(v))
            printhalfflow(v, packetsreceived, bytesreceived)
    flowdict = {}


def threadtest():
    global previouslyprinted
    if len(flowdict) > 0:
        currenttime = time.time() - begintime
        latesttime = None
        for k, v in flowdict.items():
            if (latesttime == None):
                latesttime = v['endtime']
            if (v['endtime'] > latesttime):
                latesttime = v['endtime']
        if currenttime - latesttime < 1:
            previouslyprinted = False
        else:
            if not previouslyprinted:
                print("BURST ENDED")
                endburst()
                previouslyprinted = True

    burstdaemon = threading.Timer(0.2, threadtest)
    burstdaemon.daemon = True
    burstdaemon.start()


def flowstring(p):
    return "sport:" + str(p.sport) + "dport:" + str(p.dport) + "src:" + p[IP].src + "dst:" + p[IP].dst + layerstring(p)


def otherflowstring(p):
    return "sport:" + str(p.dport) + "dport:" + str(p.sport) + "src:" + p[IP].dst + "dst:" + p[IP].src + layerstring(p)


def otherflowstringf(flow):
    return "sport:" + str(flow['dport']) + "dport:" + str(flow['sport']) + "src:" + flow['dst'] + "dst:" + flow['src'] + flow['protocol']


def flowstringf(flow):
    return "sport:" + str(flow['sport']) + "dport:" + str(flow['dport']) + "src:" + flow['src'] + "dst:" + flow['dst'] + flow['protocol']


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

def onsniff(p):
    #p.show()
    if (layerstring(p) == ""):
        print ("non TCP or UPD packet, so ignoring it")
    else:
        fstring = flowstring(p) 
        if fstring not in flowdict:
            flowdict[fstring] = {
                'protocol': layerstring(p),
                'sport': p.sport,
                'dport': p.dport,
                'src': p[IP].src,
                'dst': p[IP].dst,
                'starttime': begintime - time.time(),
                'bytessent': 0,
                'packetssent': 0
            }
            flowdict[fstring]['endtime'] = flowdict[fstring]['starttime']


        currflow = flowdict[fstring]
        currflow['endtime'] = time.time() - begintime
        currflow['bytessent'] += len(p)
        currflow['packetssent'] += 1


def printhalfflow(f, bytesreceived, packetsreceived):
    print(str(f['endtime']) + " " + f['src'] + " " + f['dst'] + " " + \
            str(f['sport']) + " " + str(f['dport']) + " " + f['protocol'] + " " \
            + str(f['packetssent']) + " " + str(packetsreceived) + " " + \
            str(f['bytessent']) + " " + str(bytesreceived))

def pprinthalfflow(f, bytesreceived, packetsreceived):
    print("timestamp: " + str(f['endtime']))
    print("source IP: " + f['src'])
    print("destination IP: " + f['dst'])
    print("source port: " + str(f['sport']))
    print("destination port: " + str(f['dport']))
    print("protocol: " + f['protocol'])
    print("packets sent: " + str(f['packetssent']))
    print("packets received: " + str(packetsreceived))
    print("bytes sent: " + str(f['bytessent']))
    print("bytes received: " + str(bytesreceived))


print("starting burst demon")
threadtest()
sniff(iface="eth1", prn = onsniff, count = 10000)


