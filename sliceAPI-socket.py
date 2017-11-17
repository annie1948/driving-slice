#!/usr/bin/python
#coding:utf8
from threading import Lock
from flask_socketio import SocketIO, emit
from flask import *
import paramiko
import re
import time
import eventlet

async_mode = None
eventlet.monkey_patch()
app = Flask(__name__)
socketio = SocketIO(app,async_mode=async_mode)
thread = None
thread_lock = Lock()

HOST_CORE = '127.0.0.1'
PORT_CORE = 22
USER_CORE = 'root'
PASSWORD_CORE = '123'
HOST_REMOTE = '127.0.0.1'
PASSWORD_REMOTE = '123'

def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(1)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST_CORE, PORT_CORE, USER_CORE, PASSWORD_CORE)
        stdin, stdout, stderr = ssh.exec_command("ping 127.0.0.1 -c 1 | awk {'print $7'} | sed -e 1d -e 3,6d -e 's/time=//g'")
        delay = stdout.read()
        if delay:
            delay = float(delay.strip('\n'))
        else:
            delay = 0
        print delay
        stdin, stdout, stderr = ssh.exec_command("bash status.sh ")
        cpu = stdout.read()
        cpu = float(cpu.strip('\n'))
        stdin, stdout, stderr = ssh.exec_command("cat /proc/meminfo ")
        mem_array = re.findall(r'(\d+)', stdout.read())
        memory = (float(mem_array[0]) - float(mem_array[2])) / float(mem_array[0])
        memory = int(round(memory, 2) * 100)
        stdin, stdout, stderr = ssh.exec_command("df -ah ")
        disk_arr = re.findall(r'(\d+%)', stdout.read())
        disk = int(disk_arr[2].strip('%'))
        print cpu, memory, disk
        stdin, stdout, stderr = ssh.exec_command("/sbin/ifconfig enp4s0  | grep 字节 ")
        band_arr1 = re.findall(r'(\d+.\d+)', stdout.read())
        time.sleep(0.5)
        stdin, stdout, stderr = ssh.exec_command("/sbin/ifconfig enp4s0  | grep 字节 ")
        band_arr2 = re.findall(r'(\d+.\d+)', stdout.read())
        down_bw = (float(band_arr2[0]) - float(band_arr1[0])) * 8*2
        up_bw = (float(band_arr2[2]) - float(band_arr1[2])) * 8*2
        print down_bw,up_bw
        ssh.close()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST_REMOTE, PORT_CORE, USER_CORE, PASSWORD_REMOTE)
        stdin, stdout, stderr = ssh.exec_command("ping 127.0.0.1553 -c 1 | awk {'print $7'} | sed -e 1d -e 3,6d -e 's/time=//g'")
        delay2 = stdout.read()
        if delay2:
            delay2 = float(delay2.strip('\n'))
        else:
            delay2 = 0
        print delay2
        stdin, stdout, stderr = ssh.exec_command("bash status.sh ")
        cpu2 = stdout.read()
        cpu2 = float(cpu2.strip('\n'))
        stdin, stdout, stderr = ssh.exec_command("cat /proc/meminfo ")
        mem_array = re.findall(r'(\d+)', stdout.read())
        memory2 = (float(mem_array[0]) - float(mem_array[2])) / float(mem_array[0])
        memory2 = int(round(memory2, 2) * 100)
        stdin, stdout, stderr = ssh.exec_command("df -ah ")
        disk_arr = re.findall(r'(\d+%)', stdout.read())
        disk2 = int(disk_arr[2].strip('%'))
        print cpu2, memory2, disk2
        stdin, stdout, stderr = ssh.exec_command("/sbin/ifconfig enp4s0  | grep 字节 ")
        band_arr1 = re.findall(r'(\d+.\d+)', stdout.read())
        time.sleep(0.5)
        stdin, stdout, stderr = ssh.exec_command("/sbin/ifconfig enp4s0  | grep 字节 ")
        band_arr2 = re.findall(r'(\d+.\d+)', stdout.read())
        down_bw2 = (float(band_arr2[0]) - float(band_arr1[0])) * 8*2
        up_bw2 = (float(band_arr2[2]) - float(band_arr1[2])) * 8*2
        print down_bw2, up_bw2
        ssh.close()

        socketio.emit('event1', {'delay': delay})
        socketio.emit('gauge1', {'cpu': cpu, 'memory': memory, 'disk':disk})
        socketio.emit('event1_bw', {'down_bw': down_bw, 'up_bw': up_bw})
        socketio.emit('event2', {'delay': delay2})
        socketio.emit('gauge2', {'cpu': cpu2, 'memory': memory2, 'disk': disk2})
        socketio.emit('event2_bw', {'down_bw': down_bw2, 'up_bw': up_bw2})

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('connect')
def socketio_connect():
    print('Client has connected to the backend')
    global thread
    with thread_lock:
        print 'jinglail'
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port= 5000)

