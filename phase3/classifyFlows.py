from kamene.all import *
import sys

flowdict = {}
previouslyprinted = True

pcapname = None

if len(sys.argv) > 1:
    pcapname = sys.argv[1]
else:
    pcapname = input("enter the name of pcap file: ")

packets = rdpcap(pcapname)
print(len(packets))


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


def flowstring(p):
    return "sport:" + str(p.sport) + "dport:" + str(p.dport) + "src:" + \
    p[IP].src + "dst:" + p[IP].dst + layerstring(p)


def otherflowstring(p):
    return "sport:" + str(p.dport) + "dport:" + str(p.sport) + "src:" + \
    p[IP].dst + "dst:" + p[IP].src + layerstring(p)


def otherflowstringf(flow):
    return "sport:" + str(flow['dport']) + "dport:" + str(flow['sport']) + \
    "src:" + flow['dst'] + "dst:" + flow['src'] + flow['protocol']


def flowstringf(flow):
    return "sport:" + str(flow['sport']) + "dport:" + str(flow['dport']) + \
    "src:" + flow['src'] + "dst:" + flow['dst'] + flow['protocol']


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


def checktimeout(p):
    global previouslyprinted
    if len(flowdict) > 0:
        currenttime = p.time
        latesttime = None
        # TODO could make this better with python max
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


def newpacket(p):
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
                'starttime': p.time, 
                'bytessent': 0,
                'packetssent': 0
            }
            flowdict[fstring]['endtime'] = flowdict[fstring]['starttime']
        currflow = flowdict[fstring]
        currflow['endtime'] = p.time
        currflow['bytessent'] += len(p)
        currflow['packetssent'] += 1


def printhalfflow(f, bytesreceived, packetsreceived):
    print(str(f['endtime']) + " " + f['src'] + " " + f['dst'] + " " + \
            str(f['sport']) + " " + str(f['dport']) + " " + f['protocol'] + " "\
            + str(f['packetssent']) + " " + str(packetsreceived) + " " + \
            str(f['bytessent']) + " " + str(bytesreceived))


def analyzepackets():
    for p in packets:
        if len(flowdict) != 0:
            checktimeout(p)
        newpacket(p)


analyzepackets()
