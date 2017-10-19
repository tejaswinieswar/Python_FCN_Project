Read Me:

***Execution Steps***

1-Execute the executable makefile(./makefile) to get the secrete flags for each case. i.e SSL and Non SSL. 
2-The makefile executes a executable file called client which runs two python programs through these commands 
1)./client -p 27993 cs5700sp17.cs.neu.edu 001256309 
2)./client cs5700sp17.cs.neu.edu 001256309 
3)./client -p 27994 -s cs5700sp17.cs.neu.edu 001256309 
4)./client -s cs5700sp17.cs.neu.edu 001256309.
 Client.py for Non SSL and Client1.py for SSL respectively. 

***High Level Approach***

Firstly i made a program(client.py) that makes the non ssl connection and tried my test cases and with successful results.Then i made a similar program(client1.py) with SSL connection and then called either of them based on the user arguments.


List of Files:

README --      This file for user to understand the process of execution.

Makefile---    The initail execution file

Client.py---   Source code for NON SSL case

Client1.py---  Source code for SSL case

secret_flags-- contains the secret flag for each case

