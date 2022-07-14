#!/usr/bin/env python
from datetime import datetime
from pdb import Pdb
from select import select
import pickle
import pygame
import socket
import sys

from cytolk import tolk

tolk.load()


class MyClient:
    def __init__(self, size=[1024, 768]):
        pygame.init()
        pygame.display.set_mode(size)
        pygame.display.set_caption("Client")
        
        self.timer_alive = 0
        self.host = "127.0.0.1"
        self.port = 8050
    def _run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.cli:
            self.cli.bind(("127.0.0.2", self.port))
            self.cli.connect((self.host, self.port))
            self.cli.setblocking(0)
            while True:
                pygame.time.Clock().tick(30)
                #self.received_events()
                self.get_pressed_keys()
                self.key_events()
    def get_pressed_keys(self):
        self.key_pressed = pygame.key.get_pressed()
        self.alt = self.key_pressed[pygame.K_LALT]
        self.ctrl = self.key_pressed[pygame.K_LCTRL]
        self.ctrl = self.key_pressed[pygame.K_RCTRL]
        self.shift = self.key_pressed[pygame.K_LSHIFT]
        self.shift += self.key_pressed[pygame.K_RSHIFT]
    def key_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    self.cli.sendall(self.pre_send("Up"))
                if ev.key == pygame.K_DOWN:
                    self.cli.sendall(self.pre_send("Down")) 
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
        items = ["Start.",
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
                        if x == 0: self._run()
                        elif x == 1: return
 
    def pre_send(self, item):
        data = pickle.dumps(item)
        return data
    def received_events(self):
        rlist, wlist, xlist = select([self.cli], [], [], 0.1)
        if rlist or wlist or xlist:
            Pdb().set_trace()



MyClient().start_menu()()