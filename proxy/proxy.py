#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python
# library. If you want to make a suggestion or fix something you can contact-me
# at voorloop_at_gmail.com
# Distributed over IDC(I Don't Care) license
import select
import socket
import sys
import time

import redis

from circuitbreaker import CircuitBreaker

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 0.0001
forward_to = 'localhost'


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
        # except Exception as e:
        #     print(e)
        #     return False


class TheServer:
    input_list = []
    channel = {}

    def registerPorts(self):
        print('registerPorts')
        self.ports = self.redis_db.get('routeports')
        if self.ports:
            self.ports = self.ports.decode('utf-8').split(',')
        else:
            self.ports = []
        print(self.ports)
        self.pq = []
        for p in self.ports:
            self.pq.append(int(p))
        print(self.pq)

    def deregisterPort(self, port):
        print('deregisterPorts')
        self.ports.remove(str(port))
        self.redis_db.set('routeports', ','.join(self.ports))
        self.registerPorts()

    def __init__(self, host, port):
        self.redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)
        self.registerPorts()

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            #self.registerPorts()
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
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
            pport = self.pq[0]
            self.pq = self.pq[1:]
            self.pq.append(pport)
            retry = False
            try:
                forward = Forward().start(host = forward_to, port = pport)
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
                    self.deregisterPort(pport)
                    retry = True

    def on_close(self):
        print(self.s.getpeername(), "has disconnected")
        # remove objects from input_list
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
        print(data)
        self.channel[self.s].send(data)

if __name__ == '__main__':
    server = TheServer('', 9090)
    try:
        server.main_loop()
    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        sys.exit(1)
