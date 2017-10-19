from  HTMLParser import  HTMLParser
import socket,re,sys
#Defining socket
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#Input parameters from command line
username=sys.argv[1]
password=sys.argv[2]

#Defining lists. frontier list is the main list. url_visited is the urls which are crawled already. se_fl is the list of secret falgs. 
frontier=[]
url_visited=[]
se_fl=[]
CRLF = "\r\n"

#HTMLParser sub-class for parsing the html data
class htmlparser_url(HTMLParser):
    def handle_starttag(self,tag,attrs):

        #Handle data inside anchor tags
        if (tag=='a'):
            x=str(attrs[0]).split("'")
            if(x[1]=='href'):

                #Pick links only that belong to fakebook
                if(x[3].startswith('/')):
                    frontier.append(x[3])

#Create instance for HTMLParser subclass
p1=htmlparser_url()

#Connecting the socket to the server and establishing the TCP connection.
try:
    s.connect(('cs5700sp17.ccs.neu.edu',80))
except:
        print "Connection time out!! please check the domain and port number"
        s.close()
        quit()            
#HTTP request to get the login page
get = ["GET /accounts/login/?next=/fakebook/ HTTP/1.1",  "Host: cs5700sp17.ccs.neu.edu ","Connection: keep-alive", "", "",]
s.send(CRLF.join(get))
buff=s.recv(4096)

#If the 1st get message recieves "0" data or Internal server error data from the server
while len(buff)==5 or buff.startswith('HTTP/1.1 500')==True:
    if(buff.startswith('HTTP/1.1 500')==True):
            s.close()
            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.connect(('cs5700sp17.ccs.neu.edu',80))
            except:
                print "Socket Error"
                s.close()
                quit()
    s.send(get)
    buff=s.recv(4096)

#Find csrftoken in HTTP Response message
c_pos= buff.find("csrftoken")
csrf= buff[c_pos+10:c_pos+42]
#Find session_id in HTTP Response message
s_pos= buff.find("sessionid")
sess= buff[s_pos+10:s_pos+42]

#HTTP POST message to login to Fakebook using the credentials
post="POST /accounts/login/ HTTP/1.1\r\nHost: cs5700sp17.ccs.neu.edu\r\nConnection: keep-alive\r\nContent-Length: 109\r\nContent-Type: application/x-www-form-urlencoded\r\nCookie: csrftoken="+csrf+"; sessionid="+sess+"\r\n\r\nusername="+username+"&password="+password+"&csrfmiddlewaretoken="+csrf+"&next=%2Ffakebook%2F"
s.send(post)
b=s.recv(4096)

#Handling if the post message recieves 0
while len(b)==5:
    s.send(post)
    b=s.recv(4096)
#Checking is the login credentials are correct
if(b.find('Please enter a correct username and password.') != -1 or len(sys.argv[2]) != 8) or len(sys.argv[1])!= 9:
        print "Invalid credentials"
        s.close()
        exit()
#Handling if the server throws an Internal server error while sending the post message
while ( b.find('500') != -1 ):
            s.close()
            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.connect(('cs5700sp17.ccs.neu.edu',80))
            except:
                print "Socket Error"
                s.close()
                quit()
#Once login is successful then find the temporarily redirected Location
loc_pos= b.find("Location: ")
sp=b.find(CRLF,loc_pos+12)
loc= b[loc_pos+8:sp]
loc1= loc[31:]
frontier.append(loc1)

#Find the Cookie for further requests
fin_sess_pos= b.find("sessionid")
fin_sess= b[fin_sess_pos+10:fin_sess_pos+42]
i=0
global st_code
global current_url

#Function to send get message to the server and to find secret flags
def feedurl(current_url,fin_sess):
            get = ["GET "+current_url+" HTTP/1.1",  "Host: cs5700sp17.ccs.neu.edu ","Connection: keep-alive","Cookie: sessionid="+fin_sess ,"", "",]
            #Append the visited urls to a list
            url_visited.append(current_url)
            s.send(CRLF.join(get))
            buff1=s.recv(4096)
            #If server returns 0 then retry with the same url
            if(len(buff1)==5):
                get = ["GET "+current_url+" HTTP/1.1",  "Host: cs5700sp17.ccs.neu.edu ","Connection: keep-alive","Cookie: sessionid="+fin_sess ,"", "",]
                url_visited.append(current_url)
                s.send(CRLF.join(get))
                buff1=s.recv(4096)
            #Pick up the HTTP status code 
            st_code_pos=buff1.find("HTTP/1.1")
            st_code=buff1[st_code_pos+9:st_code_pos+12]
            #Passing data to the HTMLParser
            p1.feed(buff1)
            #Find the secret flag in every page with the specified format
            secret=re.findall('<h2 class=\'secret_flag\' style="color:red">FLAG: (\w+)',buff1)
            if(secret!= []):
                #if secret flag flound then append it to a list and print
                se_fl.append(secret)
                print secret[0]
            return st_code

try:
    #Break out of the loop when you find 5 secret flags
    while (len(se_fl)<5):
        url_check=False

        #create a socket for every request
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect(('cs5700sp17.ccs.neu.edu',80))    
        current_url = frontier[i]

        #Check if the url has been already traversed
        for n in url_visited:
            if(n==current_url):
                url_check=True
                break

        #If already traversed then continue with the loop
        if(url_check==True):
            i=i+1
            continue

        #Call the feedurl function to send HTTP request
        st_code=feedurl(current_url, fin_sess)  

        #When server returns 500 HTTP status code then continusly try till you get the html page      
        while ( st_code == '500' ):
            s.close()
            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.connect(('cs5700sp17.ccs.neu.edu',80))
            except:
                print "Socket Error"
                s.close()
                quit()  
            st_code=feedurl(current_url, fin_sess)
            continue

        #For 301,302 case retry again and request with the new Location
        if(st_code=='301' or st_code=='302'):
            loc_pos=buff1.find("Location: ")
            sp_loc=buff1.find(CLRF,loc_pos+12)
            loc=buff1[loc_pos+8:sp_loc]
            loc1 = loc[31:]
            st_code = feedurl(loc1, fin_sess)
            #If the server throws an Internal server error while handling 301 or 302 case
            if(st_code == '500'):
                continue
        #For 403, 404 case, abandon the url list which is being crawled currently.
        if(st_code == '403' or st_code=='404'):
            i = i+1
            url_visited.append(current_url)
            continue
        i = i+1

except IndexError:
    print "Program terminated abruptly. Please try again"
except KeyboardInterrupt:
    print "Keyboard Interrupt!! Was still crawling"
except:
    print "Socket Error"
    s.close()
    quit()
s.close()

