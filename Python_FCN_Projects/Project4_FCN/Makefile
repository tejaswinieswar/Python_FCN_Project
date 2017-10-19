run:
	chmod 777 rawhttpget
	chmod 777 arp.py
	sudo ethtool --offload eth0 rx off
	sudo ethtool -K eth0 gso off
	sudo ethtool -K eth0 gro off
	sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
