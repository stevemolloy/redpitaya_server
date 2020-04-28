#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM
from numpy import frombuffer

CONNECTION  = ('127.0.0.1', 65432)

def get_all_data(sock):
    all_data = []
    data = sock.recv(4096)
    while data:
        all_data.append(data)
        data = sock.recv(4096)
    return all_data

def digitiser_acquire(channel, CONNECTION=CONNECTION):
    if not (channel==0 or channel==1):
        raise ValueError('channel must be 0 or 1')
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect(CONNECTION)
        s.sendall(b'digi' + b':' + str(channel).encode())
        all_data = get_all_data(s)

    # Convert binary data in buffer to an array of float32's
    return frombuffer(b''.join(all_data), dtype='float32')
    
def atten_set(val, CONNECTION=CONNECTION):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect(CONNECTION)
        s.sendall(b'atten' + b':' + str(val).encode())
        data = s.recv(1024)
    
    return float(data)

