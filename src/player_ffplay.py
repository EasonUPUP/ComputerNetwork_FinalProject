import subprocess
import time
import os
from multiprocessing import Process, Pool

def ffplayer():
    # ffplay_stat = subprocess.Popen('FFREPORT=file=ffreport.log:level=32 ffplay rtmp://202.69.69.180:443/webcast/bshdlive-pc', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    ffplay_stat = subprocess.Popen('FFREPORT=file=ffreport.log:level=32 ffplay rtmp://35.236.192.63/live/livestream', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in ffplay_stat.stdout:
        print(line)

def read_log(logging_filename):
    with open(fname, 'r') as f:
        lines = f.readlines()
        if len(lines) != 0:
            last_line = lines[-1]    
            print ('File' + fname + 'Last Line'+ last_line)
# nowtime = subprocess.Popen('date', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# subprocess.call('FFREPORT=file=ffreport.log:level=32 ffplay rtmp://202.69.69.180:443/webcast/bshdlive-pc', shell=True)
# ffplay_stat = subprocess.Popen('FFREPORT=file=ffreport.log:level=32 ffplay rtmp://202.69.69.180:443/webcast/bshdlive-pc', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# print("MY PRINT: "+ffplay_stat.stdout.read())
# read_log = subprocess.Popen('tail -f ffreport.log', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# print(read_log.stdout.read())
# filename = 'ffreport.log'
# proc1 = subprocess.Popen(['tac', filename], stdout=subprocess.PIPE, preexec_fn = lambda: signal(SIGPIPE, SIG_DFL))
# proc2 = subprocess.Popen(['grep', '-m', '1', "url.*sauth.*%s" % channel], stdin=proc1.stdout, stdout=subprocess.PIPE)
# proc1.stdout.close() # allow p1 to receive a SIGPIPE if p2 exists.
# content, err = proc2.communicate()

if __name__ == "__main__":
    ffplayer()