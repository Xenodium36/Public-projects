#! /usr/bin/env python3
import re
import socket
import sys


def print_err(err_msg):
    print(err_msg)
    exit(-1)


# Function to download file from server
def get_file(f_path, f_hostname, f_agent, f_tcp_ip_adr, f_tcp_ip_port):
    file_name = f_path[f_path.rfind("/") + 1:]
    path_list_tmp = []
    msg = "GET " + f_path + " FSP/1.0\r\n" + f_hostname + "\r\n" + f_agent
    # Create socket and connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect((f_tcp_ip_adr, f_tcp_ip_port))
        soc.settimeout(30)
        soc.send(str.encode(msg))
        # Check header
        try:
            header = soc.recv(1024)
        except ConnectionResetError:
            print_err("Couldn't connect to the file server")
        except socket.timeout:
            print_err("Socket timed out")
        header = header.decode()
        if header.find("FSP/1.0") != -1:
            err_code = header[header.rfind("\n") + 1:]
            if header.find("Bad Request") != -1:
                print_err("Bad request: " + err_code)
            elif header.find("Not Found") != -1:
                print_err("File not found: " + err_code)
            elif header.find("Server Error") != -1:
                print_err("Server error: " + err_code)
        f = open(file_name, "wb")
        # Receive data and write them to file
        while True:
            data = soc.recv(1024)
            if not data:
                break
            # If file is index, then i want to save path to the array
            if file_name == "index":
                ret_msg_tmp = data.decode()
                path_list_tmp = path_list_tmp + ret_msg_tmp.split("\r\n")
                if path_list_tmp[len(path_list_tmp) - 1] == "":
                    path_list_tmp.pop()
            f.write(data)
        soc.settimeout(None)
        soc.close()
    f.close()
    if file_name == "index":
        return path_list_tmp


# Check the number of arguments
if len(sys.argv) != 5:
    print_err("Wrong number of arguments")

# find indexes ip and path
if sys.argv[1] == "-n" and sys.argv[3] == "-f":
    udp_ip = sys.argv[2]
    path = sys.argv[4]
elif sys.argv[1] == "-f" and sys.argv[3] == "-n":
    path = sys.argv[2]
    udp_ip = sys.argv[4]
else:
    print_err("Wrong switch. Expected -n and -f")

# Check protocol
if path[:6] != "fsp://":
    print_err("Error, wrong protocol")
path = path.replace("fsp://", "")

# Process path
server_name = path[:path.find("/")]
if not re.match("^[a-zA-Z0-9_.-]*$", server_name):
    print_err("Invalid server name")

path = path.replace(server_name, "")[1:]

# Process IP address
if not re.match("^[0-9.:]*$", udp_ip):
    print_err("Invalid characters in IP address")
udp_ip_adr = udp_ip[:udp_ip.find(":")]
udp_ip_port = int(udp_ip[udp_ip.rfind(":") + 1:])

# Create server message
message = "WHEREIS " + server_name

# Connect to server using UDP, to get next IP
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect((udp_ip_adr, udp_ip_port))
    s.send(str.encode(message))
    s.settimeout(30)
    try:
        tcp_ip = s.recv(1024)
    except ConnectionResetError:
        print_err("Couldn't connect to the main server")
    except socket.timeout:
        print_err("Socket timed out")
    if not tcp_ip:
        print_err("Didn't receive anything")
    if tcp_ip == b'ERR Syntax':
        print_err("Wrong syntax in message")
    if tcp_ip == b'ERR Not Found':
        print_err("Unknown server")
    s.settimeout(None)
    s.close()

# Process new IP address
tcp_ip = tcp_ip.decode()
tcp_ip = tcp_ip.replace("OK ", "")
tcp_ip_adr = tcp_ip[:tcp_ip.find(":")]
tcp_ip_port = int(tcp_ip[tcp_ip.rfind(":") + 1:])

hostname = "Hostname: " + server_name
agent = "Agent: xharsa01\r\n\r\n"
# Check, if i want every file
if path == "*":
    path = path.replace("*", "index")
    path_list = get_file(path, hostname, agent, tcp_ip_adr, tcp_ip_port)
    for item in path_list:
        get_file(item, hostname, agent, tcp_ip_adr, tcp_ip_port)
else:
    get_file(path, hostname, agent, tcp_ip_adr, tcp_ip_port)
