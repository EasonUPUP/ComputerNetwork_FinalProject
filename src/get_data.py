import os, sys
import time
import psutil
import re
from PyQt5 import QtCore, QtGui, QtWidgets

# get network connection statistics
def get_key():
    key_info = psutil.net_io_counters(pernic=True).keys()

    recv = {}
    sent = {}

    for key in key_info:
        recv.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_recv)
        sent.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_sent)

    return key_info, recv, sent

def get_rate(func):
    key_info, old_recv, old_sent = func()
    time.sleep(1)
    key_info, now_recv, now_sent = func()

    net_in = {}
    net_out = {}

    for key in key_info:
        # float('%.2f' % a)
        net_in.setdefault(key, float('%.2f' %((now_recv.get(key) - old_recv.get(key)) / 1024)))
        net_out.setdefault(key, float('%.2f' %((now_sent.get(key) - old_sent.get(key)) / 1024)))

    return key_info, net_in, net_out

def extract_ffplay_data(logging_line):
    # sample_logging_line = '  41.50 A-V: -0.021 fd=  93 aq=   12KB vq=   56KB sq=    0B f=0/0'
    # line_no_space = re.compile(' ').sub('', sample_logging_line)
    line_no_space = re.compile(' ').sub('', logging_line)
    # '41.50A-V:-0.021fd=93aq=12KBvq=56KBsq=0Bf=0/0'

    if line_no_space.find('A-V:'):
        # Extract time from the stream begin (time from start of the stream/video)
        # A-V: have both audio and video
        time_counter = line_no_space.split('A-V:')[0]
        rest = line_no_space.split('A-V:')[1]
    elif line_no_space.find('M-V:'):
        # Extract time from the stream begin (time from start of the stream/video)
        # M-V: only has video
        time_counter = line_no_space.split('M-V:')[0]
        rest = line_no_space.split('M-V:')[1]
    elif line_no_space.find('M-A:'):
        # Extract time from the stream begin (time from start of the stream/video)
        # M-A: only has audio
        time_counter = line_no_space.split('M-A:')[0]
        rest = line_no_space.split('M-A:')[1]

    # Extract bias of the audio and video (Difference between audio and video timestamps)
    bias_A_V = rest.split('fd=')[0]
    rest = rest.split('fd=')[1]
    # Extract Number of frames dropped
    frame_drop = rest.split('aq=')[0]
    rest = rest.split('aq=')[1]
    # Extract size of audio frame (aq)
    audio_frame_size = rest.split('vq=')[0]
    rest = rest.split('vq=')[1]
    # Extract size of video frame (vq)
    video_frame_size = rest.split('sq=')[0]
    rest = rest.split('sq=')[1]
    # Extract size of subtitle frame (sq)
    subtitle_frame_size = rest.split('f=')[0]
    rest = rest.split('f=')[1]
    # Extract timestamp error correction rate (f)
    timestamp_error_rate = rest

    # print(time_counter + '  ' + bias_A_V + '  ' + frame_drop + '  ' + 
    #         audio_frame_size + '  ' + video_frame_size + '  ' + 
    #         subtitle_frame_size + '  ' + timestamp_error_rate)

    return time_counter, bias_A_V, frame_drop, audio_frame_size, video_frame_size, subtitle_frame_size, timestamp_error_rate

if __name__ == "__main__":
    ## Filename of the logging file for local client ffplay
    fname = '../ffreport.log'

    # In a loop we want to read all of the data
    while True:
        try:
            key_info, net_in, net_out = get_rate(get_key)

            for key in key_info:
                # en0 is the name of the NIC for macOS
                if key == 'en0':
                    print('%s\nInput:\t %-5sKB/s\nOutput:\t %-5sKB/s\n' % (key, net_in.get(key), net_out.get(key)))
        
            with open(fname, 'r') as f:
                lines = f.readlines()
                if len(lines) != 0:
                    last_line = line[-1]
                    print('File' + fname + 'Last Line'+ last_line)


        except KeyboardInterrupt:
            exit()