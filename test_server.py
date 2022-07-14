#!/usr/bin/env python
from cytolk import tolk
from select import select
import _thread
import pygame
import pickle
import requests
import socket
import sys
import time

tolk.load()
from pdb import Pdb


class MyServer:
    def __init__(self, size=[1024, 768]):
        pygame.init()
        pygame.display.set_mode(size)
        pygame.display.set_caption("Server")
        
        self.HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
        self.PORT = 8050
        self.clients = []
        self.l = 0
        self.received_events = []
    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.ser:
            #Puerto y servidor que debe escuchar
            #ip = requests.get('https://api.ipify.org').content.decode("utf8")
            ip = "192.168.243.1"
            ip2 = "192.168.1.10"
            print(f"Server ip {ip}.") 
            self.ser.bind((ip, self.PORT))
            #self.ser.settimeout(0.5)
            self.ser.listen(5)
            #self.ser.setblocking(0)
            tolk.output(f"Waiting for connection.")
            while True:
                pygame.time.Clock().tick(30)
                ready = select([self.ser], [self.ser], [self.ser], 0.1)
                if ready[0] or ready[1] or ready[2]:
                    cli, addr = ready[0][0].accept()
                    tolk.output(f"Server connected with {addr}.")
                    self.clients += [[cli, addr]]
                    _thread.start_new_thread(self.multi_treaded_server, (cli,))
                self.run_events()
    def run_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.cli:
            #self.cli.bind(("127.0.0.2", self.PORT))
            self.cli.connect(("192.168.243.1", self.PORT))
            self.cli.setblocking(0)
            while True:
                pygame.time.Clock().tick(30)
                #self.received_events()
                self.get_pressed_keys()
                self.client_key_events()
    def get_pressed_keys(self):
        self.key_pressed = pygame.key.get_pressed()
        self.alt = self.key_pressed[pygame.K_LALT]
        self.ctrl = self.key_pressed[pygame.K_LCTRL]
        self.ctrl = self.key_pressed[pygame.K_RCTRL]
        self.shift = self.key_pressed[pygame.K_LSHIFT]
        self.shift += self.key_pressed[pygame.K_RSHIFT]
    def incoming_event(self, item):
        recibido = item[0].recv(4000)
        recibido = pickle.loads(recibido)
        self.received_events += [recibido]
        print(recibido)
    def client_key_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    self.cli.sendall(self.pre_send("Up"))
                if ev.key == pygame.K_DOWN:
                    self.cli.sendall(self.pre_send("Down")) 
    def server_key_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    self.l = self.selector(self.received_events, self.l, go="up")
                    self.say_received()
                if ev.key == pygame.K_DOWN:
                    self.l = self.selector(self.received_events, self.l, go="down")
                    self.say_received()
                if ev.key == pygame.K_c:
                    tolk.output(f"Connections: {len(self.clients)}.")
                if ev.key == pygame.K_ESCAPE:
                    self.ser.close()
    def run_events(self):
            pygame.time.Clock().tick(30)
            self.get_pressed_keys()
            self.server_key_events()
    def multi_treaded_server(self, client):
        #client.send("Connected.".encode())
        rn = 1
        while True:
            print(f"multi {rn}.")
            rn += 1
            try:
                ready = select([client], [client], [client], 0.1)
            except Exception as err:
                print(f"error {err}.") 
            if ready[1]:
                tolk.output(f"Incoming message..")
                self.incoming_event(ready[1])
            else:
                continue
    def pre_send(self, item):
        data = pickle.dumps(item)
        return data
    def say_received(self):
        if len(self.received_events):
            tolk.output(f"{self.received_events[self.l]}",1)
        else: tolk.output(f"No messages.")
    def selector(self, item, x, go='', wrap=0):
        tolk.silence()
        if len(item) == 0:
            return x
        if go == 'up':
            if x == 0 and wrap == 1:
                x = len(item) - 1
                return x

            if x == 0 and wrap == 0:
                tolk.output(f"End", 1)
                return x
            else:
                x -= 1
                return x

        if go == 'down':
            if x == len(item) - 1 and wrap:
                x = 0
                return x

            if x == len(item) - 1 and wrap == 0:
                tolk.output(f"End", 1)
                return x
            else:
                x += 1
                return x
    def start_menu(self):
        say = 1
        x = 0
        items = ["Host.",
                 "Connect.",
                 "Exit."
                 ]
        while True: 
            pygame.time.Clock().tick(60)
            if say:
                tolk.output(f"{items[x]}")
                say = 0
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        x = self.selector(items, x, go="up")
                        say = 1
                    if event.key == pygame.K_DOWN:
                        x = self.selector(items, x, go="down")
                        say = 1
                    if event.key == pygame.K_RETURN:
                        if x == 0: self.run_server()
                        if x == 1: self.run_client()
                        elif x == 2: return
 



MyServer().start_menu()()