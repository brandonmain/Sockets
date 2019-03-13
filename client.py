"""
Client side program for communicating with a server
over UDP port.

by: Brandon Main

date: March 4, 2019
"""

import socket
import sys

# Assign device-id
device_ID = sys.argv[1]

# Assign server ip and port nums
server = (sys.argv[2], int(sys.argv[3]))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setblocking(False)


# Function that sends user input to server
def operate(arg, count):
    data = ""

    if count < 3:

        # Send to server
        client_socket.sendto(arg, server)

        # Set timeout for 10 seconds
        client_socket.settimeout(10)

        # Wait for ack
        try:
            data, addr = client_socket.recvfrom(1024)
        except socket.timeout:
            print("\nRequest timed out, retrying...")
            count(arg, count + 1)

        if data:
            print("\nACK " + data)

    elif count >= 3:
        # Log registration error
        print("Error contacting server. Logging error.")
        error_file = open("error.log", "a+")
        error_file.write(arg)
        error_file.close()


### Main function ###
def main():
    while True:
        # Get user input
        arg = raw_input("Enter a command:\n")
        operate(arg, 0)


# Program start
if __name__ == "__main__":
    main()
