from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from GaugePanel import GaugePanel
import sys, os
import psutil
import random
import time
import re

value_input_byte = 0
value_output_byte = 0
value_audio_frame = 0
value_video_frame = 0

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


class WorkThread(QThread):
    # Initalize the Thread
    def __int__(self):
        super(WorkThread, self).__init__()
    # Thread operating
    def run(self):
        fname = '../ffreport.log'
        # In a loop we want to read all of the data
        while True:
            global value_input_byte
            global value_output_byte
            global value_audio_frame
            global value_video_frame
            
            try:
                key_info, net_in, net_out = get_rate(get_key)
                key_data_input = 0
                key_data_output = 0
                size_audio_frame = 0
                size_video_frame = 0

                for key in key_info:
                    # en0 is the name of the NIC for macOS
                    if key == 'en0':
                        print('%s\nInput:\t %-5sKB/s\nOutput:\t %-5sKB/s\n' % (key, net_in.get(key), net_out.get(key)))
                        key_data_input = net_in.get(key)
                        key_data_output = net_out.get(key)
            
                with open(fname, 'r') as f:
                    lines = f.readlines()
                    if len(lines) != 0:
                        last_line = lines[-1]
                        print('File' + fname + 'Last Line'+ last_line)
                        time_counter, bias_A_V, frame_drop, audio_frame_size, video_frame_size, _, _ = extract_ffplay_data(last_line)
                        
                        if audio_frame_size.find('KB'):
                            size_audio_frame = int(audio_frame_size.strip('KB'))
                        else:
                            size_audio_frame = 0

                        if video_frame_size.find('KB'):
                            size_video_frame = int(video_frame_size.strip('KB'))
                        else:
                            size_video_frame = 0

                value_input_byte = key_data_input
                value_output_byte = key_data_output
                value_audio_frame = size_audio_frame
                value_video_frame = size_video_frame
                
                print("[Generate]{}, {}, {}, {}".format(value_input_byte, value_output_byte, value_audio_frame, value_video_frame))

                time.sleep(0.5)         

            except KeyboardInterrupt:
                exit()


class MyQMainWindow(QMainWindow):
    def __init__ (self):
        super(MyQMainWindow, self).__init__()

        # MainWindow.setObjectName('MainWindow')
        # MainWindow.resize(600, 600)
        # self.centralWidget = QtWidgets.QWidget(MainWindow)
        # self.centralWidget.setObjectName('centralWidget')
        # self.retranslateUi(MainWindow)
        # MainWindow.setWindowTitle('Data Visualize')
        self.resize(600,600)
        wid = QWidget(self)
        self.setCentralWidget(wid)
        gridLayout = QGridLayout()
        wid.setLayout(gridLayout)
        # self.layout = QtWidgets.QHBoxLayout()
        # gridLayout = QGridLayout()

        # Create QListWidget
        # self.myQListWidget = QtWidgets.QListWidget(self)

        self.gaugePanel_1 = GaugePanel(self)
        self.label_1 = QLabel(self)
        self.label_1.setText('Input(KB)')
        self.label_1.setAlignment(Qt.AlignCenter)
        self.vlayout_1 =  QVBoxLayout()
        self.vlayout_1.addWidget(self.gaugePanel_1)
        self.vlayout_1.addWidget(self.label_1)

        self.gaugePanel_2 = GaugePanel(self)
        self.label_2 = QLabel(self)
        self.label_2.setText('Output(KB)')
        self.label_2.setAlignment(Qt.AlignCenter)
        self.vlayout_2 =  QVBoxLayout()
        self.vlayout_2.addWidget(self.gaugePanel_2)
        self.vlayout_2.addWidget(self.label_2)
        
        self.gaugePanel_3 = GaugePanel(self)
        self.label_3 = QLabel(self)
        self.label_3.setText('size of audio frame (aq)')
        self.label_3.setAlignment(Qt.AlignCenter)
        self.vlayout_3 =  QVBoxLayout()
        self.vlayout_3.addWidget(self.gaugePanel_3)
        self.vlayout_3.addWidget(self.label_3)
        
        self.gaugePanel_4 = GaugePanel(self)
        self.label_4 = QLabel(self)
        self.label_4.setText('size of vedio frame (vq)')
        self.label_4.setAlignment(Qt.AlignCenter)
        self.vlayout_4 =  QVBoxLayout()
        self.vlayout_4.addWidget(self.gaugePanel_4)
        self.vlayout_4.addWidget(self.label_4)

        self.wg_1 = QWidget()
        self.wg_2 = QWidget()
        self.wg_3 = QWidget()
        self.wg_4 = QWidget()

        self.wg_1.setLayout(self.vlayout_1)
        self.wg_2.setLayout(self.vlayout_2)
        self.wg_3.setLayout(self.vlayout_3)
        self.wg_4.setLayout(self.vlayout_4)

        gridLayout.addWidget(self.wg_1,0,0)
        gridLayout.addWidget(self.wg_2,0,1)
        gridLayout.addWidget(self.wg_3,1,0)
        gridLayout.addWidget(self.wg_4,1,1)

        self.Mytimer()
        
        # self.setLayout(gridLayout)
        self.setWindowTitle('Data Visualization')

        # self.setCentralWidget(self.myQListWidget)
    
    def Mytimer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_gauge_value)
        timer.start(50)

    def update_gauge_value(self):
        print("[Update]{}, {}, {}, {}".format(value_input_byte, value_output_byte, value_audio_frame, value_video_frame))

        self.gaugePanel_1.setValue(value_input_byte)
        self.gaugePanel_2.setValue(value_output_byte)
        self.gaugePanel_3.setValue(value_audio_frame)
        self.gaugePanel_4.setValue(value_video_frame)
        
if __name__ == "__main__":
    workThread = WorkThread()
    workThread.start()
    sys_argv = sys.argv
    app = QApplication(sys_argv)
    window = MyQMainWindow()
    window.show()
    sys.exit(app.exec_())