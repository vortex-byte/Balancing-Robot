import os
from flask import Flask, request
from flask_socketio import SocketIO
import serial
from serial.tools import list_ports
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

serialDevice = None
serialBaudRate = 115200
clientIp = None # Connected WS client IP
clientSid = None # Connected WS client SID

@app.route('/')
def index():
    return "Flask-SocketIO server running on Raspberry Pi"

"""Sends serial data over WS to client."""
def sendSerialData():
    global serialDevice, clientIp

    while True:
        if serialDevice is not None:
            try:
                if serialDevice.in_waiting > 0: # Message from arduino
                    serialData = serialDevice.readline().decode('utf-8', errors="ignore").strip()
                    socketio.emit('message', serialData, to=clientSid) # send to GUI
            except serial.SerialException:
                print("Serial port disconnected")
                serialDevice.close()
                serialDevice = None
                scanPort()
            except Exception as e:
                print("Failed to send data. Error: ", e)
                serialDevice.close()
                serialDevice = None
                exit(1)

        time.sleep(0.1)

"""Scans for available serial ports and connects if found."""
def scanPort():
    global serialDevice

    print("Scanning port...")
    while serialDevice is None:
        # For Direct Serial Port
        port = "/dev/ttyAMA0" # Raspberry Pi RXTX port
        if os.path.exists(port):
            try:
                serialDevice = serial.Serial(port, serialBaudRate, timeout=1)
                print("Connected to serial:", port)
                return
            except (OSError, serial.SerialException):
                print("Failed to connect to serial:", port)
                time.sleep(2)

        # For USB Serial Port
        # ports = list(serial.tools.list_ports.comports())
        # for port in ports:
        #     try:
        #         serialDevice = serial.Serial(port.device, serialBaudRate, timeout=1)
        #         print("Connected to serial:", port.device)
        #         return
        #     except (OSError, serial.SerialException):
        #         continue
        # print("No serial port found, retrying...")
        # time.sleep(2)

"""Handles new WebSocket client connections."""
@socketio.on('connect')
def handle_connect():
    global clientIp

    clientIp = request.remote_addr
    clientSid = request.sid
    if clientIp is not None:
        print("Client connected IP:", clientIp)

"""Handles when WS client disconnected."""
@socketio.on('disconnect')
def handle_disconnect():
    global clientIp

    print("Client disconnected IP:", clientIp)
    clientIp = None
    clientSid = None

"""Handles receiving message from client """
@socketio.on('message')
def handle_message(msg):
    serialDevice.write(msg.encode())
    print('Message from client:', msg)

thread = threading.Thread(target=sendSerialData)
thread.daemon = True
thread.start()
scanPort()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
