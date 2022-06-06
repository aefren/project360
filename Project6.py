''  # !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
#from glob import glob
#from math import ceil, floor
#from statistics import mean, median
from pdb import Pdb
from random import choice, randint, uniform, shuffle
#import os
#import pickle
#import sys
import time

from cytolk import tolk
#import natsort
import pygame


tolk.load()

mixer = pygame.mixer
pygame.mixer.pre_init(frequency=44100, size=32, channels=2, buffer=500)
pygame.init()
pygame.mixer.set_num_channels(16)
wav = '.wav'
path = os.getcwd() + str('/data/sounds/')


CHT0 = pygame.mixer.Channel(0)

def loadsound(soundfile, channel=CHT0, path=path, extention=wav, vol=1):
    channel.stop()
    if isinstance(vol, tuple): channel.set_volume(vol[0], vol[1])
    else: channel.set_volume(vol)
    channel.play(mixer.Sound(path + soundfile + extention))
    return mixer.Sound(path + soundfile + extention).get_length()



mixer = pygame.mixer
pygame.mixer.pre_init(frequency=44100, size=32, channels=2, buffer=500)
pygame.init()


class Player:
    def __init__(self, name):
        self.name = name
        self.heading = 1
        self.countdown = 900
        self._countdown = 0
        self.foot = [
            "foot-giant01", 
            "foot-giant02", 
            "foot-giant03", 
            "foot-giant04"]
    def can_walk(self):
        if self.ctime > self._countdown: return 1
    def update(self):
        self.ctime = self.game.ctime


class Tile:
    def __init__(self):
        self.name = ""
        self.type = "Ocean"
        self.steps = []
        self.ambients = []


class Main:
    def __init__(self, size=[1024, 768]):
        pygame.init()
        pygame.display.set_mode(size)
        pygame.display.set_caption("Project 6")
        
        self.head = [
            "Norte", 
            "Noreste", 
            "Este", 
            "Sureste", 
            "Sur", 
            "Suroeste", 
            "Oeste", 
            "Noroeste"]
        self.head_index = 0
    def Move_unit(self, unit):
        if unit.can_walk():
            unit._countdown = self.ctime + unit.countdown
            loadsound(choice(unit.foot))
    def global_keys(self):
        pass
    def run(self):
        tolk.output(f"Starting.")
        self.players = [Player("Player 1")]
        for it in self.players:
            it.game = self
        while True:
            pygame.time.Clock().tick(60)
            unit = self.players[0]
            self.ctime = pygame.time.get_ticks()
            [it.update() for it in self.players]
            self.key_pressed = pygame.key.get_pressed()
            self.alt = self.key_pressed[226]
            self.ctrl = self.key_pressed[224] or self.key_pressed[228]
            self.shift = self.key_pressed[225] or self.key_pressed[229]
            
            if self.key_pressed[pygame.K_UP]:
                self.Move_unit(unit)
            if self.key_pressed[pygame.K_DOWN]:
                self.Move_unit(unit)
            for evt in pygame.event.get():            
                if evt.type == pygame.KEYDOWN and evt.key == pygame.K_LEFT: 
                    if self.key_pressed[pygame.K_RCTRL]:
                        if self.head_index == 0: self.head_index = 4
                        elif self.head_index == 1: self.head_index = 5
                        elif self.head_index == 2: self.head_index = 6
                        elif self.head_index == 3: self.head_index = 7
                        elif self.head_index == 4: self.head_index = 0
                        elif self.head_index == 5: self.head_index = 1
                        elif self.head_index == 6: self.head_index = 2
                        elif self.head_index == 7: self.head_index = 3
                        if unit._countdown < unit.ctime:
                            unit._countdown = (self.ctime + unit.countdown)
                        else:
                            unit._countdown += (unit.countdown)
                    else: 
                        self.head_index -= 1
                        if self.head_index < 0: self.head_index = 7
                        if unit._countdown < unit.ctime:
                            unit._countdown = (self.ctime + 
                                                unit.countdown*0.25)
                        else:
                            unit._countdown += (unit.countdown * 0.25)
                    tolk.output(f"{self.head[self.head_index]}.")
                if evt.type == pygame.KEYDOWN and evt.key == pygame.K_RIGHT:
                    if self.key_pressed[pygame.K_RCTRL]:
                        if self.head_index == 0: self.head_index = 4
                        elif self.head_index == 1: self.head_index = 5
                        elif self.head_index == 2: self.head_index = 6
                        elif self.head_index == 3: self.head_index = 7
                        elif self.head_index == 4: self.head_index = 0
                        elif self.head_index == 5: self.head_index = 1
                        elif self.head_index == 6: self.head_index = 2
                        elif self.head_index == 7: self.head_index = 3
                        if unit._countdown < unit.ctime:
                            unit._countdown = (self.ctime + unit.countdown)
                        else:
                            unit._countdown += (unit.countdown)
                    else: 
                        self.head_index += 1
                        if self.head_index > 7: self.head_index = 0
                        if unit._countdown < unit.ctime:
                            unit._countdown = (self.ctime 
                                                + unit.countdown * 0.25)
                        else:
                            unit._countdown += (unit.countdown * 0.25) 
                    tolk.output(f"{self.head[self.head_index]}.") 
                if self.key_pressed[pygame.K_F12]:
                    Pdb().set_trace()
                    tolk.output(f"Debug On.")
                if self.key_pressed[pygame.K_ESCAPE]:
                    return


Main().run()
