#!/usr/bin/python
import sys

#Open the trace file and stor it in an variable
F = open("exp1_out_"+sys.argv[1]+"_"+sys.argv[2]+".tr",'r')
G = open("exp1_out_"+sys.argv[1]+"_"+sys.argv[2]+".tr",'r')

#Variables required for calculating Throuhput, Latency, Packet Drop Rate from the generated trace file.
req=[]
s_c=0
r_c=0
d_size=0.0
d_c=0
latency=[]
timediff=[]
datadict ={}
totaltime =0
packcount = 0
#Reading the data in the trace file
for i in F:
    #Splitting the record based on space
    t = i.split()
    #Pick the packets which were enqueued at node 0 
    if (t[0]=='+' and t[2]=='0'):
        s_c = s_c+1
        #Initially saving the starttime of the packet in the dictionary with key as sequence number
	datadict[t[10]]= float(t[1])
    #Pick the tcp packets that were received at node 3
    if (t[0]=='r' and t[3]=='3'and t[4]=='tcp'):
        r_c = r_c+1
    #Number of packets dropped
    if (t[0] == 'd' and t[4] == 'tcp'):
        d_c= d_c + 1
    # Pick the tcp acknowledgement packets received to calculate latency
    if (t[3] == '0' and t[4] == 'ack'):
        #Search the starttime
	if t[10] in datadict:
		starttime = datadict[t[10]]
		endtime =  float(t[1])
                #Subtract the endtime and starttime to get the latency
		totaltime += (endtime - starttime)
		packcount += 1 	
print sum(timediff)
print "sent",s_c,r_c,d_c
#Calculating latency
latency = (totaltime/packcount)*1000
#Calculating throughput
thr = (r_c*1000*8.0/9.0)/(1024*1024)
#Calculating Droprate
drop_rate = (float(d_c)/float(s_c))*100
print "------------------------------------------"
#print "Total packet size=",d_size
#print "Total time for tcp packets=",time
print thr
#print "No of packets dropped=", d_c
#print "Drop_rate", drop_rate
print latency
print drop_rate

