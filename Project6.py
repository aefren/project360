''  # !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
#from glob import glob
import math
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
        self.y = 10
        self.x = 10
        self.degrees = 0
        self.countdown = 500
        self._countdown = 0
        self.foot = [
            "foot01", 
            "foot02", 
            "foot03", 
            "foot04"]
    def can_walk(self):
        if self.ctime > self._countdown: return 1
    def say_degrees(self):
        tolk.output(f"{self.degrees}.",1)
    def say_cdt(self):
        tolk.output(f"y {round(self.y, 3)}, x {round(self.x, 3)}.",1)
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
    def get_radians(self, degrees):
        return (
            math.cos(math.radians(degrees)), 
            math.sin(math.radians(degrees))
            )
    def Move_unit(self, unit, backward=0):
        if unit.can_walk():
            unit._countdown = self.ctime + unit.countdown
            degrees = unit.degrees
            if backward:
                degrees += 180
                if degrees > 360: degrees -= 361
            radians = self.get_radians(degrees)
            self.player.y += radians[0]
            self.player.x += radians[1]
            loadsound(choice(unit.foot))
    def global_keys(self, event):
        if event.key == pygame.K_x:
            self.player.say_cdt()
    def run(self):
        tolk.output(f"Starting.")
        self.players = [Player("Player 1")]
        self.player = self.players[0]
        for it in self.players:
            it.game = self
        while True:
            pygame.time.Clock().tick(60)
            self.ctime = pygame.time.get_ticks()
            [it.update() for it in self.players]
            self.key_pressed = pygame.key.get_pressed()
            self.alt = self.key_pressed[226]
            self.ctrl = self.key_pressed[224] or self.key_pressed[228]
            self.shift = self.key_pressed[225] or self.key_pressed[229]
            
            if self.key_pressed[pygame.K_UP] and self.key_pressed[pygame.K_RSHIFT] == 0:
                self.Move_unit(self.player)
            if self.key_pressed[pygame.K_DOWN]:
                self.Move_unit(self.player, 1)
            for evt in pygame.event.get():
                #self.global_keys(evt)
                if evt.type == pygame.KEYDOWN:
                    if evt.key == pygame.K_x:
                        self.player.say_cdt()             
                    if evt.key == pygame.K_LEFT: 
                        if self.key_pressed[pygame.K_RCTRL]: self.player.degrees -= 90
                        elif self.key_pressed[pygame.K_RSHIFT]: self.player.degrees -= 45
                        else: self.player.degrees -= 1
                        if self.player.degrees < 0: self.player.degrees += 361
                        self.player.say_degrees()
                    if evt.key == pygame.K_RIGHT:
                        if self.key_pressed[pygame.K_RCTRL]: 
                            self.player.degrees += 90
                        elif self.key_pressed[pygame.K_RSHIFT]: self.player.degrees += 45
                        else: self.player.degrees += 1
                        if self.player.degrees > 360: self.player.degrees -= 361
                        self.player.say_degrees()
                    if evt.key == pygame.K_UP:
                        if self.key_pressed[pygame.K_RSHIFT]: 
                            self.player.degrees += 180
                            if self.player.degrees > 360: self.player.degrees -= 360
                            self.player.say_degrees()
                    if self.key_pressed[pygame.K_F12]:
                        Pdb().set_trace()
                        tolk.output(f"Debug On.")
                    if self.key_pressed[pygame.K_ESCAPE]:
                        return


Main().run()
