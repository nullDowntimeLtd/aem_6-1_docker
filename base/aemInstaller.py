import subprocess
import signal
import os
import sys
import psutil
from optparse import OptionParser

# Argument definition
usage = "usage: %prog [options] arg"
parser = OptionParser(usage)
parser.add_option("-i", "--install_file", dest="filename",help="AEM install file")
parser.add_option("-r", "--runmode",dest="runmode",help="Run mode for the installation")
parser.add_option("-p", "--port", dest="port",help="Port for instance")

options, args = parser.parse_args()
optDic = vars(options)

# Copy out parameters
print optDic
print optDic['filename']
fileName = optDic.setdefault('filename','cq-publish-4503.jar')
runmode = optDic.setdefault('runmode','publish')
port = optDic.setdefault('port','4503')

#
# Waits for connection on 5007, and then checks that the returned
# success message has been recieved.
#
# Starts AEM installer
installProcess = subprocess.Popen(['java', '-jar', fileName, '-listener-port','50007','-r',runmode,'nosample','-p',port])

# Starting listener
import socket
HOST = ''
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()

successfulStart = False
while 1:
    data = conn.recv(1024)
    if not data:
      break
    else:
      print str(data)
      if str(data).strip() == 'started':
        successfulStart = True
      break
    # conn.sendall(data)
conn.close()

#Post install hook
postInstallHook = "postInstallHook.py"
if os.path.isfile(postInstallHook):
    print "Executing post install hook"
    returncode = subprocess.call(["python", postInstallHook])
    print returncode
else:
    print "No post install hook found"

print "Successful Start %s" % successfulStart
print "Stopping instance"
#
# If the success message was recieved, attempt to close all associated
# processes.
#
if successfulStart == True:
  parentAEMprocess= psutil.Process(installProcess.pid)
  for childProcess in parentAEMprocess.get_children():
    os.kill(childProcess.pid,signal.SIGINT)

  os.kill(parentAEMprocess.pid, signal.SIGINT)

  installProcess.wait()
  sys.exit(0)
else:
  installProcess.kill()
  sys.exit(1)
