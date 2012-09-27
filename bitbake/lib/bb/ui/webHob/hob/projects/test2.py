from ftplib import FTP

ftp = FTP()
ftp.set_debuglevel(2) # open the debug level 2 to display the message
ftp.connect('10.239.47.176', 30004)
ftp.login('ftpuser', '123456')
print ftp.getwelcome()
ftp.cwd('upload/')
#filename = "1.txt"
#ifhandler = open('/home/an/1.txt', 'wb').write
#ftp.retrbinary('RETR 123.txt', fhandler, 1024)
ftp.set_debuglevel(0)
ftp.quit()
