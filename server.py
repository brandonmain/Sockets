"""
Server side program for communicating with client devices
via a UDP port.

by: Brandon Main

date: March 4, 2019
"""

import socket
import sys
import time
import hashlib

# Use loopback address.
SERVER_IP = "127.0.0.1"
# Get UDP port entered from command line.
UDP_PORT = int(sys.argv[1])

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = ""
addr = ""


# Function that returns an ack code to a client.
#
# ack format: ACK code device-ID time hash parameter(s)
#
# codes:
#       00 - Successful device registration
#       01 - Device already registered
#       02 - Updated IP registration
#       12 - Reused IP address
#       13 - Reused MAC address
#       20 - Successful deregister
#       21 - Unsuccessful deregister (bad MAC or IP)
#       30 - Device was never registered
#       31 - Unsuccessful login/logoff
#       50 - Successful data transmission from client
#       51 - Data transmitted but client device-ID not in system
#       70 - Successful login
#       80 - Successful logoff
#
def ack(code):
    server_socket.sendto(code, addr)


# Function to register device
def register(arg):

    device = arg.split(" ", 1)[1]
    found = False

    # check database of devices
    with open('devices.db') as device_file:
        lines = device_file.readlines()

    for line in lines:
        # Device id found
        if line.split(" ")[0] == device.split(" ")[0]:
            found = True
            ack("01 " + device.split(" ", 1)[0] + " " + str(time.ctime())
                + " " + hashlib.sha256(arg).hexdigest() + " " + "This device is already registered.")

    if not found:
        # Device not found, create new device
        device_file = open("devices.db", "a+")
        device_file.write("\n" + arg.split(" ", 1)[1])
        device_file.close()
        ack("00 " + device.split(" ", 1)[0] + " " + str(time.ctime())
            + " " + hashlib.sha256(arg).hexdigest() + " " + "New device added.")


# Function that lets a client deregister from server
def deregister(arg):

    device = arg.split(" ", 1)[1]
    found = False

    # check database of devices
    with open('devices.db') as device_file:
        lines = device_file.readlines()

    for line in lines:
        # Device id found
        if line.split(" ")[0] == device.split(" ")[0]:
            found = True
            # Check if device registered to another mac
            if line.split(" ")[2] == device.split(" ")[2]:
                lines.remove(line)
                open("devices.db", "w").close()
                device_file = open("devices.db", "w")
                for l in lines:
                    device_file.write(l + "\n")
                device_file.close()
                ack("20 " + device.split(" ", 1)[0] + " " + str(time.ctime())
                    + " " + hashlib.sha256(arg).hexdigest() + " " + "Device removed from server.")
                break
            # mac doesn't match, don't deregister and send ack 30
            else:
                ack("30 " + device.split(" ", 1)[0] + " " + str(time.ctime())
                    + " " + hashlib.sha256(arg).hexdigest() + " " + "Device registered with different MAC address.")
                break

    # Device not found
    if not found:
        ack("21 " + device.split(" ", 1)[0] + " " + str(time.ctime())
            + " " + hashlib.sha256(arg).hexdigest() + " " + "Device was never registered.")


# Function to handle login from client
def login(arg):

    device = arg.split(" ", 1)[1]
    found = False

    # check database of devices
    with open('devices.db') as device_file:
        lines = device_file.readlines()

    for line in lines:
        # Device id found & phrases match
        if line.split(" ")[0] == device.split(" ")[0] & line.split(" ")[1] == device.split(" ")[1]:
            ack("70 " + device.split(" ", 1)[0] + " " + str(time.ctime())
                + " " + hashlib.sha256(arg).hexdigest() + " " + "Login successful.")

    if not found:
        # Device not found
        ack("31 " + device.split(" ", 1)[0] + " " + str(time.ctime())
            + " " + hashlib.sha256(arg).hexdigest() + " " + "Login unsuccessful.")


# Function to handle login from client
def logoff(arg):

    device = arg.split(" ", 1)[1]
    found = False

    # check database of devices
    with open('devices.db') as device_file:
        lines = device_file.readlines()

    for line in lines:
        # Device id found
        if line.split(" ")[0] == device.split(" ")[0] & line.split(" ")[3] == device.split(" ")[1]:
            ack("80 " + device.split(" ", 1)[0] + " " + str(time.ctime())
                + " " + hashlib.sha256(arg).hexdigest() + " " + "Logoff successful.")

    if not found:
        # Device not found
        ack("31 " + device.split(" ", 1)[0] + " " + str(time.ctime())
            + " " + hashlib.sha256(arg).hexdigest() + " " + "Logoff unsuccessful.")


# Function to receive data messages from client
def rcv_data(arg):

    device = arg.split(" ", 1)[1]
    found = False

    # check database of devices
    with open('devices.db') as device_file:
        lines = device_file.readlines()

    for line in lines:
        # Device id found
        if line.split(" ")[0] == device.split(" ")[0]:
            ack("50 " + device.split(" ", 1)[0] + " " + str(time.ctime())
                + " " + hashlib.sha256(arg).hexdigest() + " " + "Data received.")

    if not found:
        # Device not found
        ack("51 " + device.split(" ", 1)[0] + " " + str(time.ctime())
            + " " + hashlib.sha256(arg).hexdigest() + " " + "Device not in system.")


# Function that determines what to do from client input
def operate(arg):

    if arg.split(' ', 1)[0] == "REGISTER":
        register(arg)
    elif arg.split(' ', 1)[0] == "DEREGISTER":
        deregister(arg)
    elif arg.split(' ', 1)[0] == "LOGIN":
        login(arg)
    elif arg.split(' ', 1)[0] == "LOGOFF":
        logoff(arg)
    elif arg.split(' ', 1)[0] == "DATA":
        rcv_data(arg)


# Function to check for proper port input
def check_port_num():

    global UDP_PORT

    if UDP_PORT < 0:
        print("\n\n\tError: non-existent port number, please enter a new one.\n")
        UDP_PORT = input()

    elif UDP_PORT > 65535:
        print("\n\n\tError: non-existent port number, please enter a new one.\n")
        UDP_PORT = input()

    else:
        print("Starting server on port " + str(UDP_PORT) + "...")


# Server loops until given an exit command of "quit".
def run():

    global data
    global addr

    while True:
        data, addr = server_socket.recvfrom(1024)
        arg = data + " " + str(addr[0]) + " " + str(addr[1])
        operate(arg)


### Main function ###
def main():

    global server_socket

    # Check for correct UDP port input
    check_port_num()

    # Bind server ip to port after checking for good port
    server_socket.bind((SERVER_IP, UDP_PORT))

    # Stay Alive
    run()


# Program start
if __name__ == "__main__":
    main()
