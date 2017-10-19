#Importing necessary libraries
import socket, sys, struct, time, os,re, random
import binascii,subprocess,commands
from struct import *
from urlparse import urlparse
from collections import OrderedDict

#Get the current working directory
cwd = os.getcwd()

#Accept the URL from the command line
url=sys.argv[1]

if url.startswith("http://")==False:
	url="http://"+url

url_valid = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
if len(url_valid)==0:
    print("The URL is invalid!!!")
    exit()

#Check the number of '/' and append '/' only when count('/') is 2
if url.count('/')==2:
        url=url+'/'
	 #Open a file in the current working directory to write data with "w" mode
	filename='index.html'
	f=open(cwd+'/'+filename, "w")
else:
	#Determining the filename based on the last element in the url if last element is nulll then set the file name as index.html
	a= url.split('/')
	if "." not in a[len(a)-1] and url.endswith("/")==False:
		url=url+'/'
		filename='index.html'
		f=open(cwd+'/'+filename, "w")
	if "." not in a[len(a)-1] and url.endswith("/")==True:
                filename='index.html'
                f=open(cwd+'/'+filename, "w")
	else:
		#Filename picking up from the url path
		filename=a[len(a)-1]
		f=open(cwd+'/'+filename, "w")
	
#using parseurl module to split the URL into host and the path
z=urlparse(url)
host=z.netloc
path=z.path

#Defining the interface as eth0
ifname='eth0'

#Run ifconfig on the command line and get the output
ifconfig= subprocess.check_output('ifconfig')
v=ifconfig.find(ifname)
sp=ifconfig.find("\n\n")

#Pick the ipaddress
loc=ifconfig[ifconfig.find("eth0"):ifconfig.find("\n\n")].find("inet addr")
s_ip= ifconfig[loc+10:ifconfig.find(" ",loc+10)]

#Get the ipaddress of the destination host
try:
	d_ip = socket.gethostbyname(host)
except:
	print "The URL is invalid!!"
	exit()
#Pick an available port from the specified range
port= random.randint(1300,65535)

#Setting window size
wind_size=65500

#Convert source and destination ip to network format
source_address = socket.inet_aton( s_ip )
dest_address = socket.inet_aton(d_ip)

#Placeholder and protocol type to make the pseudo header
placeholder = 0
protocol = socket.IPPROTO_TCP

# function to compute checksum of incoming and outgoing packets
def checksum(x):
    #Set iniitial sum to 0
    sum = 0
    var = 0
	
    #Determine the length to compute checksum based on even and odd input characters
    length = len (x)
    constant = 2

    #For every 16 bits i.e 2 characters add it into a value and compute the whole checksum in the loop
    while length >= constant:
	#Convert the characters to their unicode value using ord() and concatenating both the characters
        w = ord(x[var])+(ord(x[var+1]) << 8 )
        sum = sum + w
        var = var + constant

	#Reduce the length by 2
        length = length - constant
    #When last character is reached then consider only one element
    if length == 1:
        sum = sum + ord(x[var])
    #Add the carry Compute the one's complement of the checksum
    sum = sum + (sum >> 16)
    sum = ~sum & 0xffff
    return sum

#Creating Send and Receive packet with AF_PACKET family for the send socket as Ethernet header, IP header and TCP header has to be built for the packets
try:
    send_s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    recv_s=socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

#Handle exception while socket is being created
except socket.error:
    print 'Send or Receive Socket could not be created. Please Try again'
    exit()
	
#Function to make the ethernet header
def ET_header(d_mac,s_mac):
	#Packing destination mac , spurce mac and Type for IPv4
        eth = pack('!6s6s2s', d_mac , s_mac , '\x08\x00')
        return eth

#Function to make the IP_header
def IP_header(ihl, version, Type_of_service, Total_len, id_packet, frag_off, TTL,Proto_type, checksum, src_addr, dest_addr):
	#Combining the ihl and version field as pack function has minimum of 1 byte data.
        ihl_version = (version << 4) + ihl
	
	#Packing IP header using pack function by packing all the fields of the IP header in the required order 
        IPheader = pack('!BBHHHBBH4s4s' ,ihl_version, Type_of_service, Total_len, id_packet, frag_off, TTL,Proto_type, checksum,  src_addr, dest_addr)
        return IPheader

#Function to build TCP_header
def TCP_header(source_port,dest_port,seq, ack_number, doff, fin_flag, syn_flag, rst_flag, psh_flag, ack_flag, urg_flag, window_size, checksum_tcp, urg_pointer):
	#Shifting the offset value by 4 places
        offset_RES = (doff << 4) + 0
	#Shifting the flags to the correct position
        flags = fin_flag + (syn_flag << 1) + (rst_flag << 2) + (psh_flag <<3) + (ack_flag << 4) + (urg_flag << 5)
	#Pack the data based on the checksum value
        if checksum_tcp==0:
                TCPheader = pack('!HHLLBBHHH' ,source_port,dest_port,seq, ack_number,offset_RES, flags, window_size, checksum_tcp, urg_pointer)
        else:
                TCPheader = pack('!HHLLBBH' ,source_port,dest_port,seq, ack_number,offset_RES, flags, window_size) + pack('H' , checksum_tcp) + pack('!H' , urg_pointer)
        return TCPheader

#Function to compute the final checksum of the TCP header along with pseudo header
def final_pack(tcp_initial,user_data):
	#Total length initial header(with checksum 0) and the data
        tcp_total_length = len(tcp_initial) + len(user_data)

	#Packing of the pseudo header
        psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol ,tcp_total_length);
        psh = psh + tcp_initial + user_data;
	
	#Compute the final checksum
        check = checksum(psh)
        return check

#Unpacking the IP header
def extract_IP_header(dat):
	#Pick the first element in the tuple which is the actual packet
        pac=dat[0]

	#Unpack 20 bytes of the packet to obtain the IP header in the same format it was packed and extract the necessary fields
        ipheader = struct.unpack("!BBHHHBBH4s4s", pac[0:20])
        xyz=pac[0:20]
        ihl_version = ipheader[0]
        IHL = ihl_version & 0xF

        ipheader_length = IHL * 4
        s_addr = socket.inet_ntoa(ipheader[8]);
        d_addr = socket.inet_ntoa(ipheader[9]);

	#Compute the IP checksum of the incoming packet and check its validity
        cal_ip_check=checksum(xyz)
        if cal_ip_check!=0:
                ip_check_flag=1
        else:
                ip_check_flag=0

        return ipheader_length,ip_check_flag, s_addr

#Unpacking the TCP header
def extract_TCP_header(dat,iph_length):
        #Pick the first element in the tuple which is the actual packet
	pac=dat[0]
	#Unpack tcp header bytes of the packet to obtain the TCP header in the same format it was packed and extract the necessary fields
        TCPheader1 = pac[iph_length:iph_length+20]
        t = unpack('!HHLLBBHHH' ,TCPheader1)
        source_port = t[0]
        dest_port = t[1]
        sequence = t[2]
        acknowledgement = t[3]
        doff_res = t[4]
        checksum_tcp= t[7]
        t_length = doff_res >> 2

        window=t[6]
        tcp_urg_ptr=t[8]
	#convert the flags to binary format to pick the fin flag
        flags=bin(t[5])
	
	#Calculate the length of the data
        headers_size = iph_length + t_length
        data= pac[headers_size:]
	
	#Calculate the length of the tcp header and data 
        le=len(pac[iph_length:])
	#Make the pseudo header again to verify the tcp checksum
        pseudoh1 = pack('!4s4sBBH',dest_address,source_address,placeholder,protocol,le);
	fina=pseudoh1+pac[iph_length:]
	#Initialize the value of the checksum
        cal_tcp_check=11
        cal_tcp_check=checksum(fina)

	#Verify if checksum is valid
        if cal_tcp_check!=0:
                tcp_check_flag=1
        else:
                tcp_check_flag=0

        return sequence, acknowledgement, data, flags[6],tcp_check_flag,source_port, dest_port

#Function for creating the packet
def Make_ack(random,seq,ack,tcp_fin, tcp_syn, tcp_rst, tcp_psh, tcp_ack, tcp_urg,user_data,ethernet):
	#Form the initial TCP header with checksum 0
        ack_tcp= TCP_header(port,80,seq,ack,5,tcp_fin,tcp_syn,tcp_rst,tcp_psh,tcp_ack,tcp_urg,socket.htons (wind_size),0,0)
        ack_data=user_data

	#Form the pseudo header and calculate final checksum and the final TCP header
        ack_checksum=final_pack(ack_tcp, ack_data)
        ack_tcp_header = TCP_header(port,80,seq,ack,5,tcp_fin,tcp_syn,tcp_rst,tcp_psh,tcp_ack,tcp_urg,socket.htons (wind_size),ack_checksum,0)
	
	#Make the initial IP header with checksum 0
        ack_ip=IP_header(5,4,0,20+len(ack_tcp_header)+len(user_data),random,0,255,socket.IPPROTO_TCP, 0, socket.inet_aton ( s_ip ), socket.inet_aton ( d_ip ))
        ip_c=checksum(ack_ip)

	#Final IP header with computed checksum
        ack_ip_new=IP_header(5,4,0,20+len(ack_tcp_header)+len(user_data),random,0,255,socket.IPPROTO_TCP, ip_c, socket.inet_aton ( s_ip ), socket.inet_aton ( d_ip ))
        ack_packet = ack_ip_new + ack_tcp_header + ack_data
	#Return the packet with the ethernet header
        return ethernet+ack_packet

#Function to compute the Mac address of the gateway
def arp_mac_gateway(source_ip, dest_ip):
	#Determine the local macaddress
        var= send_s.getsockname()
	mac_local = var[4]
        ip_local = source_ip

	#Ethernet header with broadcast address and type code for arp protocol
        ethernet_header= struct.pack("!6s6s2s",'\xff\xff\xff\xff\xff\xff',mac_local,'\x08\x06')

	#ARP header parameters- hardware type Ethernet, specifiying IPv4 version being used, length of the mac address, length of the IP address,Code of ARP request, setting all 0 mac address for target
        arp_header = struct.pack("!2s2s1s1s2s6s4s6s4s",'\x00\x01','\x08\x00','\x06','\x04','\x00\x01',mac_local, socket.inet_aton(ip_local),'\x00\x00\x00\x00\x00\x00', socket.inet_aton(dest_ip))
	
	try:
		#Create send and receive sockets for arp message
		arp_s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806))
		#Bind to the eth0 interface
		arp_s.bind((ifname, socket.htons(0x0806)))
		arp_r = socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(0x0806))
		
	except socket.error:
		print 'ARP Send of receive Socket could not be created. Please Try again'
		exit()
		
		
        while True:
                try:
			#Send the arp query along with the ethernet header
                        arp_s.send(ethernet_header+arp_header)
                        receive = arp_r.recvfrom(2048)

			#Verify if the arp response is from the ip of the gateway
                        if dest_ip==socket.inet_ntoa(receive[0][28:32]):
				#Unpack the values to pick the mac address of the gateway
                                val= struct.unpack("!6s6s2s",receive[0][0:14])
                                val1= struct.unpack("!2s2s1s1s2s6s4s6s4s",receive[0][14:42])
                                gate_mac=val1[5]
                                return mac_local,gate_mac
                        continue
                except socket.timeout:
                        print "ARP failed.Try again"
                        exit()

#Function to check validity of the packets and to discard packets which do not belong to the current stream
def packet_validity(incoming_ip,s_port,d_port):
	if incoming_ip!= d_ip or s_port!= 80 or d_port != port:
		return 1
	else:
		return 0
	

#####################################################################################################################
#Implementation starts here

#List to store the sequence number of the acked packets
acked_pacs=[]

#Random number for packet id
rando=12345

#Bind the socket to the interface
send_s.bind(('eth0',0))

#Obtain the IP address for the gateway to send the ARP query
target= commands.getoutput('route -n').split('\n')[2].split()[0x01]

#Call the function to obtain local and gateway address and compute the ethernet header
sorc_mac,gate_mac=arp_mac_gateway(s_ip,target)
eth_fin= ET_header(gate_mac,sorc_mac)

#######################################################################################################################
#TCP Handshake phase

#SYN packet with syn flag being set and send it along with the ethernet header
packet=Make_ack(rando,895638,0,0,1,0,0,0,0,'',eth_fin)
send_s.send(packet)
dat = recv_s.recvfrom(4096)

#Extract the IP header and the TCP header from the data
iph_length,ip_flag, ip_incoming_pac= extract_IP_header(dat)
s, a ,d,fin,tcp_flag, s_port, d_port = extract_TCP_header(dat,iph_length)
acked_pacs.append(int(s))

#Send the ack for the received SYNACK
packet1 = Make_ack(rando+1,a,s+1,0,0,0,0,1,0,'',eth_fin)
send_s.send(packet1)

#########################################################################################################################

#Making the get packet for the URL and send the packet
CRLF = "\r\n"
get = ["GET "+path+" HTTP/1.0",  "Host: "+host,"Connection: keep-alive", "", "",]
get1= CRLF.join(get)
packet2 = Make_ack(rando+2,a,s+1,0,0,0,0,1,0,get1,eth_fin)
send_s.send(packet2)
dat1 = recv_s.recvfrom(4096)
get_time=time.time()

#Dictionary for storing the sequnce and its data as key-value pair
s_ack_pacs={}

#Determine the values of the next expected acknowledgement of the incoming packet
next_ack=s+1
ackn=packet2

#Set cwnd to 1
cwnd=1

#If for 60 seconds server doesnt respond then resend packet; if no response for 180 seconds then exit the program
if (time.time()-get_time >60):
	send_s.send(packet2)
if (time.time()-get_time >180):
	print("Server is not responding")
	exit()
#Loop to continuosly receive and send the ack to the packets
while True:
	#Flag to check if the packet starts with the ethernet header
        start_flag=0

	#Random number for the packet id which should be in the packing range
        rando =random.randint(15000,65000)

	#Receive the data packets and extract the headers accordingly
        data = recv_s.recvfrom(4096)
	ack_time=time.time()
        iph_length1,ip_check_flag,ip_incoming_pac=extract_IP_header(data)
        s1, a1 ,d1, fin1,tcp_check_flag, s_port, d_port= extract_TCP_header(data,iph_length1)
	
	valid= packet_validity(ip_incoming_pac,s_port,d_port)
	if valid==1:
		continue

	#Check if the fin flag is set and break out of the while loop
        if fin1 == '1':
                if len(d1)==0:
                        break
	#Verify if the packet received was as expected by verifying the sequence number, if wrong packet received then resend the previous acknowledgement
        if next_ack!=s1:
                send_s.send(ackn)
		#Resetting cwnd to 1 when packet drop occurs
		cwnd=1
                continue

	#If checksum is corrupted for either IP or TCP then drop the packet
        if ip_check_flag==1 or tcp_check_flag==1:
                continue

	#Add the proper packet's sequence number to the list 
        acked_pacs.append(int(s1))

	#For the second packet received verify if the HTTP status code is valid
        if len(acked_pacs)==2:
		#If the code is 200 OK then remove the HTTP headers by identifying 2 consequent carriage return and new line
                if d1.startswith('HTTP/1.1 200 OK'):
                        if d1.find('\r\n\r\n')!=-1:
                                data_start=d1.find('\r\n\r\n')
                                d2=d1[data_start+4:]
				#Enter the data into the dictionary
                                s_ack_pacs[int(s1)]=d2

				#Set the flag to indicate the data is already entered into the dictionary
                                start_flag=1
		#For non 200 code print message to console and exit the program
                else:
                        print "The page is redirected or unavailable"
                        exit()
        #If the data is not entered into the dictionary then add it
        if start_flag==0:
                s_ack_pacs[int(s1)]=d1

	#Make the sequence number and the acknowledgement number for the ack packet
        next_seq= a1
        next_ack= s1+len(d1)

	#Make the packet and send it
        ackn= Make_ack(rando,next_seq,next_ack,0,0,0,0,1,0,'',eth_fin)
        send_s.send(ackn)

	#Check if cwnd is inbetween 0 and 1000, if so the set cwnd as 1 else increment it
        if cwnd>0 and cwnd<1000:
                cwnd=cwnd+1
        else:
                cwnd=1
	#If server doesnt respond for 180 seconds then quit program
	if (time.time()- ack_time >180):
        	print("Server is not responding")
        	exit()

########################################################################################################################
#Teardown phase

#Send acknowledgement for the fin packet
packet3 = Make_ack(rando+1,a1,s1+1,0,0,0,0,1,0,'',eth_fin)
send_s.send(packet3)

#Send fin packet from the client side and receive the final ack
packet4 = Make_ack(rando+2,a1,s1+1,1,0,0,0,1,0,'',eth_fin)
send_s.send(packet4)
dat2 = recv_s.recvfrom(4096)

#Sort the dictionary in order of the sequence number in order to handle in-order sequences
sor= OrderedDict(sorted(s_ack_pacs.items()))

#Loop to read data from the dictionary and writing to the file
for i in sor:
        f.write(str(s_ack_pacs[i]))
f.close()

