default : main.py login.py requestresult.py settings.json IPGW.svg
	mkdir ~/.ipgw-py-manager -p
	cp settings.json ~/.ipgw-py-manager
install :
	mkdir /usr/local/lib/ipgw-py-manager -p
	cp *.py /usr/local/lib/ipgw-py-manager
	ln -s /usr/local/lib/ipgw-py-manager/main.py /usr/local/bin/ipgw
	echo "Install finished. Please run ipgw --config vim and input your own account."