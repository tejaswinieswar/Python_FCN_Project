import operator
#Open the trace file and stor it in an variable
F = open("exp3_out.tr","r")
G = open("exp3_out.tr","r")
#print F
dictionary={}
cbr_d={}
lst = []
data = 0

#Reading the data in the trace file
for i in F:
    #Splitting the record based on dot
    t = i.split()
    x= t[1].split(".")
    interval= x[0]
    #Pick the packet received at node 0 which is an acknowledgement
    if (t[0]=='r' and t[3]=='0' and t[4]=='ack'):
        if interval in dictionary:
            #Segregate all the packets based on the time interval i.e all packets within 1 second, 2 second
            pac_count= dictionary[interval]
            #Increment the packet count when found
            dictionary.update({interval : pac_count+1})
        else:
            #Initialization for the first packet found in that interval
            dictionary.update({interval : 1})
    #Packets received at node 5 to get the packets of the cbr
    if (t[0]=='r' and t[3]=='5' and t[4]=='cbr'):
        if interval in cbr_d:
            p_c= cbr_d[interval]
            cbr_d.update({interval : p_c+1})
        else:
            cbr_d.update({interval : 1})
#print dictionary
#print cbr_d


datadict={}
lat=[]
#to calculate latency
def calc_lat(intr): 
    totaltime=0
    packcount=0
    #G = open("exp3_out.tr","r")
    for j in G:
        r= j.split()
        if float(r[1]) > (intr+1):
            latency = (totaltime/packcount)*1000
            #print "lat",intr,latency
            lat.append(latency)
            break 
        #To pick all the packets that have been enqueued in node 0
        if (r[0]=='+' and r[2]=='0'):
            #s_c = s_c+1
            datadict[r[10]]= float(r[1])
        # To pick ACK received at node 0
        if (r[3] == '0' and r[4] == 'ack'):
            if r[10] in datadict:
                starttime = datadict[r[10]]
                endtime =  float(r[1])
                totaltime += (endtime - starttime)
                packcount += 1

t_tcp=[]
t_cbr=[]
#To calculate the Throughput within the time interval
for i in xrange(0, len(dictionary)):
   # key=operator.ittemgetter(i);
    i1 = str(i)
    data = dictionary[i1]
    lst.append(data)
    #print dictionary[i1]
    a= dictionary[i1]*1000.0*8.0
    b= 1024.0*1024.0
    if i>4 and i<26:
        c= cbr_d[i1]*500.0*8.0
        thr_cbr =float(c/b)
        #print i,thr_cbr
        t_cbr.append(thr_cbr) 
    #print a , b
    thr= float(a/b)
    #thr = float((dictionary[i]*1000*8)/(1024*1024))
    #print i,thr
    t_tcp.append(thr)
    calc_lat(i)
#print data_dict
print " latency"
print lat
print "troughput"
print t_tcp
print "throughput_cbr"
print t_cbr

