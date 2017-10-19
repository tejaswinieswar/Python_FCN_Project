from socket import socket, AF_INET, SOCK_STREAM  
import sys
#for arg in sys.argv[1:4]:
if( len(sys.argv) == 5):        
    #print sys.argv[3] + sys.argv[4] + sys.argv[2]
    servername =sys.argv[3]
    NEU_ID= sys.argv[4]
    serverport = int(sys.argv[2])
else:
    servername = sys.argv[1]
    NEU_ID= sys.argv[2]
    serverport = 27993
clientsocket = socket(AF_INET,SOCK_STREAM)
clientsocket.connect((servername,serverport))
clientsocket.send("cs5700spring2017 HELLO "+ NEU_ID + "\n")

while True:
    data1 = clientsocket.recv(10000)
   
    
    if(data1[0:23] == "cs5700spring2017 STATUS"):   
        a,b,c,d,e = data1.split(" ")
        answer = eval(c + d + e)
        clientsocket.send("cs5700spring2017 "+ str(answer)+"\n")

    else :
	print data1[17:81]
        break
        
clientsocket.close()
