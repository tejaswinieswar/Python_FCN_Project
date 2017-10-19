from socket import socket, AF_INET, SOCK_STREAM
import sys
import ssl
#for arg in sys.argv[0:5]:     
#print sys.argv[4] + sys.argv[5] + sys.argv[2]
if( len(sys.argv) == 6):
    servername =sys.argv[4]
    NEU_ID= sys.argv[5]
    serverport = int(sys.argv[2])
else:
    servername = sys.argv[2]
    NEU_ID= sys.argv[3]
    serverport = 27994    
clientsocket = socket(AF_INET,SOCK_STREAM)
clientsocket2 = ssl.wrap_socket(clientsocket,cert_reqs=ssl.CERT_NONE)
clientsocket2.connect((servername,serverport))
clientsocket2.send("cs5700spring2017 HELLO "+ NEU_ID + "\n")
while True:
    data1 = clientsocket2.recv(10000)


    if(data1[0:23] == "cs5700spring2017 STATUS"):
        a,b,c,d,e = data1.split(" ")
        answer = eval(c + d + e)
        clientsocket2.send("cs5700spring2017 "+ str(answer)+"\n")

    else :
        print data1[17:81]
        break
clientsocket2.close()
clientsocket.close()
