#!/usr/bin/python
import sys
print "TCP Protocol:"+sys.argv[1]+ " TCP Protocol 2:"+ sys.argv[2] + " CBR_rate:"+ sys.argv[3]
#Open the trace file 
F = open("exp2_out_"+sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]+".tr",'r')
G = open("exp2_out_"+sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]+".tr",'r')

#Variables required for calculating Throuhput, Latency, Packet Drop Rate from the generated trace file.
req=[]
s_c=0
r_c=0
d_size=0.0
d_c=0
#latency=[]
#timediff=[]
datadict ={}
datadict2 ={}
totaltime =0
packcount = 0
s_c2=0
r_c2=0
d_c2=0
totaltime2 =0
packetcount2 =0
#Iterate throught the tracefile
for i in F:
    #split each record based on space
    t = i.split()
    #Pick the packet that it is enqueued at node 0
    if (t[0]=='+' and t[2]=='0'):
        s_c = s_c+1
        #Initially saving the starttime of the packet in the dictionary with key as sequence number
	datadict[t[10]]= float(t[1])
        #O_F.write(i)
    #Pick the tcp packets that were received at node 3
    if (t[0]=='r' and t[3]=='3'and t[4]=='tcp'):
        #print "iiii",i
        r_c = r_c+1
#        d_size= d_size+int(t[5])
    if (t[4] == 'tcp'):
        req.append(t[1])
    #Number of packets dropped
    if (t[0] == 'd' and t[4] == 'tcp' and t[7] == '1'):
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
for i in G:
    #split each record based on space
    t = i.split()
    #Pick the packet that it is enqueued at node 0
    if (t[0]=='+' and t[2]=='4'):
        s_c2 = s_c2+1
        #Initially saving the starttime of the packet in the dictionary with key as sequence number
        datadict2[t[10]]= float(t[1])
        #O_F.write(i)
    #Pick the tcp packets that were received at node 5
    if (t[0]=='r' and t[3]=='5'and t[4]=='tcp'):
        #print "iiii",i
        r_c2 = r_c2+1
#        d_size= d_size+int(t[5])
    if (t[4] == 'tcp'):
        req.append(t[1])
    #Number of packets dropped
    if (t[0] == 'd' and t[4] == 'tcp' and t[7] == '3'):
        d_c2= d_c2 + 1
    # Pick the tcp acknowledgement packets received to calculate latency
    if (t[3] == '4' and t[4] == 'ack'):
        if t[10] in datadict2:
                starttime2 = datadict2[t[10]]
                endtime2 =  float(t[1])
                #Subtract the endtime and starttime to get the latency
                totaltime2 += (endtime2 - starttime2)
                packetcount2 += 1
#print sum(timediff)
#print latency[0:10]
print "sent",s_c,r_c,d_c, s_c2, r_c2, d_c2
#print sum(latency),len(latency)

#Calculate latency
latency = (totaltime/packcount)*1000
latency2 = (totaltime2/packetcount2)*1000
#time =float(req[len(req)-1]) - float(req[0])
#print time
#t = (d_size/9.0)*(8.0/1024*1024)

#Calculate Throughput
thr = (r_c*1000*8.0/9.0)/(1024*1024)
thr2 = (r_c2*1000*8.0/9.0)/(1024*1024)

#Calculate Drop Rate
drop_rate = (float(d_c)/float(s_c))*100
drop_rate2 = (float(d_c2)/float(s_c2))*100
print "------------------------------------------"
#print "Total packet size=",d_size
#print "Total time for tcp packets=",time
print thr
#print "No of packets dropped=", d_c
#print "Drop_rate", drop_rate
print latency
print drop_rate

print "--------case 2---------"
print thr2
print latency2
print drop_rate2
#f.write("Throughput"+"\t"+"Latency"+"\t"+"Drop Rate" )
#f.write(str(thr) + "\t" + str(latency) + "\t" + str(drop_rate))												)
#f.close()
