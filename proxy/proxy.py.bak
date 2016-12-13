#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python
# library. If you want to make a suggestion or fix something you can contact-me
# at voorloop_at_gmail.com
# Distributed over IDC(I Don't Care) license
import socket
import select
import time
import sys
import redis
import queue
from circuitbreaker import CircuitBreaker
# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 1
# forward_to = ('www.google.com', 80)
forwardto = 'localhost'
ports = []
pq = queue.Queue()
redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)

def registerPorts():    
    print('registerPorts')
    ports = redis_db.get('routeports')
    if ports:
        ports = ports.decode('utf-8').split(',')
    else:
        ports = []
    print(ports)
    pq = queue.Queue()
    for p in ports:
        pq.put(int(p))

def deregisterPort(port):
    print('deregisterPorts')
    ports.remove(str(port))
    redis_db.set('routeports', ','.join(ports))
    registerPorts()

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @CircuitBreaker(max_failure_to_open=3, reset_timeout=10)
    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            e.port = port
            print(e)
            raise e

class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            registerPorts()
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            print('1')
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        retry = True
        while retry:
            p = pq.get()
            pq.put(p)
            print(p)
            retry = False
            try:
                print("Forwading request to port: ", p)
                forward = Forward().start(forwardto, p)

                clientsock, clientaddr = self.server.accept()
                if forward:
                    print(clientaddr, "has connected")
                    self.input_list.append(clientsock)
                    self.input_list.append(forward)
                    self.channel[clientsock] = forward
                    self.channel[forward] = clientsock
                else:
                    print("Can't establish connection with remote server.")
                    print("Closing connection with client side", clientaddr)
                    clientsock.close()

            except Exception as e:
                print(e.args)
                if e.args[0].startswith("Port Failure"):
                    deregisterPort(p)
                    retry = True



    def on_close(self):
        print(self.s.getpeername(), "has disconnected")
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        print (data)
        self.channel[self.s].send(data)

if __name__ == '__main__':
        server = TheServer('localhost', 9090)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print ("Ctrl C - Stopping server")
            sys.exit(1)