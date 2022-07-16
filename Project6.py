''  # !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from glob import glob
import math
#from statistics import mean, median
from pdb import Pdb
from random import choice, randint, uniform, shuffle
import os
import pickle
#import sys
import time

from cytolk import tolk
import natsort
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
        self.ctime = self.main.ctime


class World:
    def __init__(self):
        self.name = None
        self.tiles = []
    def create_map(self):
        tolk.output(f"creating world.", 1)
        self.name = "Map 1"
        #self.ext = ".map"
        self.height = 50
        self.width = 50
        self.map = []
        for y in range(0, self.height, 1):
            self.map.append([])
            for x in range(0, self.width, 1):
                self.map[y].append(Tile())
        main.pos = self.map[0][0]
        main.x = 0
        main.y = 0
    def update(self):
        pass



class Tile:
    def __init__(self):
        self.name = ""
        self.type = "Grass"
        self.steps = []
    def get_type(self):
        say = 1
        x = 0
        types = [
            ["Grass", getattr(Tile, "set_to_grass")],
            ["Sand", getattr(Tile, "set_to_sand")],
            ["Wall",getattr(Tile, "set_to_wall")],
            ]
        while True:
            time.sleep(0.1)
            if say:
                try:
                    tolk.output(f"{types[x]}.")
                except Exception: Pdb().set_trace()
                say = 0

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        x = game.selector(types, x, go="up")
                        say = 1
                    if event.key == pygame.K_DOWN:
                        x = game.selector(types, x, go="down")
                        say = 1
                    if event.key == pygame.K_RETURN:
                        tolk.output(f"set to {types[x][0]}.")
                        return types[x]
                    if event.key == pygame.K_ESCAPE:
                        return

class Main:
    def __init__(self, size=[1024, 768]):
        self.name = 1
        self.making_map = 0
        self.world = None
    
    
    def get_radians(self, degrees):
        return (
            math.cos(math.radians(degrees)), 
            math.sin(math.radians(degrees))
            )
    
    def global_keys(self, event):
        if event.key == pygame.K_x:
            self.player.say_cdt()
    def movement_keys(self, evt):
        if self.key_pressed[pygame.K_UP] and self.key_pressed[pygame.K_RSHIFT] == 0:
            self.Move_unit(self.player)
        if self.key_pressed[pygame.K_DOWN]:
            self.Move_unit(self.player, 1)
        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_LEFT: 
                if self.key_pressed[pygame.K_RCTRL]: self.player.degrees -= 90
                elif self.key_pressed[pygame.K_RSHIFT]: self.player.degrees -= 45
                else: self.player.degrees -= 1
                if self.player.degrees < 0: self.player.degrees += 361
                self.player.say_degrees()
            if evt.key == pygame.K_RIGHT:
                if self.key_pressed[pygame.K_RCTRL]: self.player.degrees += 90
                elif self.key_pressed[pygame.K_RSHIFT]: 
                    self.player.degrees += 45
                else: self.player.degrees += 1
                if self.player.degrees > 360: self.player.degrees -= 361
                self.player.say_degrees()
            if evt.key == pygame.K_UP:
                if self.key_pressed[pygame.K_RSHIFT]: 
                    self.player.degrees += 180
                    if self.player.degrees > 360: self.player.degrees -= 360
                    self.player.say_degrees()
    def load_map(self, location, filext, saved=0):
        x = 0
        say = 1
        maps = glob(os.path.join(location + filext))
        maps = natsort.natsorted(maps)
        while True:
            pygame.time.Clock().tick(60)
            if say:
                say = 0
                if maps:
                    file = open(maps[x], "rb")
                    world = pickle.loads(file.read())
                    world.update()
                    if saved == 0:
                        tolk.output(f"{world.name}.", 1)
                    elif saved: tolk.output(f"{maps[x][6:-5]}")
                else:
                    tolk.output(f"no maps.", 1)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        maps = natsort.natsorted(maps)
                        tolk.output(f"Sort by name.", 1)
                        say = 1
                    if event.key == pygame.K_2:
                        maps.sort(
                            key=lambda t: os.stat(t).st_mtime, reverse=True)
                        tolk.output(f"Sort by newest date.", 1)
                        say = 1
                    if event.key == pygame.K_3:
                        maps.sort(key=lambda t: os.stat(t).st_mtime)
                        tolk.output(f"Sort by oldest date.", 1)
                        say = 1
                    if event.key == pygame.K_UP:
                        x = self.selector(maps, x, go="up")
                        say = 1
                    if event.key == pygame.K_DOWN:
                        x = self.selector(maps, x, go="down")
                        say = 1
                    if event.key == pygame.K_HOME:
                        x = 0
                        say = 1
                    if event.key == pygame.K_END:
                        x = len(maps) - 1
                        say = 1
                    if event.key == pygame.K_PAGEUP:
                        x -= 10
                        if x < 0: x = 0
                        say = 1
                    if event.key == pygame.K_PAGEDOWN:
                        x += 10
                        if x >= len(maps): x = len(maps) - 1
                        say = 1
                    if event.key == pygame.K_RETURN:
                        if maps:
                            file = open(maps[x], "rb")
                            self.world = World()
                            world = pickle.loads(file.read())
                            self.world.name = world.name
                            self.world.ext = world.ext
                            self.world.height = world.height
                            self.world.width = world.width
                            self.world.map = world.map
                            self.world.update()
                            return
                        else: tolk.output(f"no maps.", 1)
                    if event.key == pygame.K_F12:
                        tolk.output(f"debug on.", 1)
                        Pdb().set_trace()
                        tolk.output(f"debug off.", 1)
                    if event.key == pygame.K_ESCAPE:
                        return
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
    def run(self):
        tolk.output(f"Starting.")
        self.player = self.world.players[0]
        while True:
            pygame.time.Clock().tick(60)
            self.ctime = pygame.time.get_ticks()
            [it.update() for it in self.players]
            self.key_pressed = pygame.key.get_pressed()
            self.alt = self.key_pressed[226]
            self.ctrl = self.key_pressed[224] or self.key_pressed[228]
            self.shift = self.key_pressed[225] or self.key_pressed[229]
            for event in pygame.event.get():
                self.global_keys(event
                self.movement_keys(event)
                if evt.type == pygame.KEYDOWN:
                    if self.key_pressed[pygame.K_F12]:
                        Pdb().set_trace()
                        tolk.output(f"Debug On.")
                    if self.key_pressed[pygame.K_ESCAPE]:
                        return


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

    def set_tiles(self, event):
        if event.key == pygame.K_F1:
            pass
        if event.key == pygame.K_c:
            pass
        if event.key == pygame.K_g:
            pass
        if self.shift and event.key == pygame.K_s:
            tolk.output(f"{len(self.tiles)} tiles selected.")
            return
        if event.key == pygame.K_t:
            tiletype = Tile .get_type()
            for it in self.tiles:
                it.tiletype()
        if event.key == pygame.K_z:
            tolk.output(f"{len(self.tiles)} tiles selected.")        
        if event.key == pygame.K_PAGEUP:
            self.xrange -= 1
            tolk.output(f"X range: {self.xrange}.")
        if event.key == pygame.K_PAGEDOWN:
            self.xrange += 1
            tolk.output(f"X range: {self.xrange}.")
        if event.key == pygame.K_HOME:
            self.yrange -= 1
            tolk.output(f"Y range: {self.yrange}.")
        if event.key == pygame.K_END:
            self.yrange += 1
            tolk.output(f"Y range: {self.yrange}.")
        if event.key == pygame.K_DELETE:
            self.yrange =0
            self.xrange = 0
            tolk.output(f"Ranges reseted.")
        if event.key == pygame.K_F1:
            self.world.debug()
        if event.key == pygame.K_BACKSPACE:
            self.tiles = []
            self.capital = []
            tolk.output(f"Cleaned.", 1)
        if self.shift and event.key == pygame.K_SPACE:
            xrange = [self.x, self.x + self.xrange]
            xrange = range(min(xrange), max(xrange) + 1)
            yrange = [self.y, self.y + self.yrange]
            yrange = range(min(yrange), max(yrange) + 1)
            wmap = self.world.map
            for y in range(len(wmap)):
                for x in range(len(wmap[y])):
                    if wmap[y][x].tiles: continue
                    if wmap[y][x].capital: continue
                    if wmap[y][x] in self.tiles: continue
                    if y in yrange and x in xrange:
                        self.tiles += [wmap[y][x]]
            tolk.output(f"{len(self.tiles)}tiles selected.")
            return
        if event.key == pygame.K_SPACE:
            tolk.silence()
            if self.pos in self.tiles:
                self.tiles.remove(self.pos)
                tolk.output(f"removed.", 1)
                return
            elif self.pos not in self.tiles and self.pos.tiles == [] and self.pos.capital is None:
                self.tiles += [self.pos]
                tolk.output(f"added.", 1)
            elif self.pos not in self.tiles and self.pos.tiles:
                tolk.output(f"Expanding.")
                self.tiles = self.pos.tiles + [self.pos]
                self.capital = self.pos
        if event.key == pygame.K_DELETE:
            self.pos.name = None
            self.pos.type = None
            for tl in self.pos.tiles:
                tl.capital = None
                tl.name = None
                tl.type = None
            self.pos.tiles = []
            self.pos.capital = None
        if event.key == pygame.K_RETURN:
            if self.capital is None:
                tolk.output(f"capital need.", 1)
                return
            if len(self.tiles) < 4:
                tolk.output(f"Needs 2 or more tiles to create a province.")
                return
            tolk.output(f"seting.", 1)
            self.capital.tiles = [it for it in self.tiles]
            self.capital.set_name()
            tolk.output(f"{self.pos.name}.")
            for it in self.tiles:
                if it != self.capital: it.capital = self.capital
                it.size = len(self.tiles)
            self.capital = None
            self.tiles = []
            self.world.update()

    def start_menu(self):
        say = 1
        x = 0
        options = [
            "Explore",
            "map editor.",
            "Map creator."]
        while True:
            pygame.time.Clock().tick(60)
            if say:
                tolk.output(f"{options[x]}")
                say = 0

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        x = self.selector(options, x, go="up")
                        say = 1
                    if event.key == pygame.K_DOWN:
                        x = self.selector(options, x, go="down")
                        say = 1
                    if event.key == pygame.K_HOME:
                        x = 0
                        say = 1
                    if event.key == pygame.K_END:
                        x = len(options) - 1
                        say = 1
                    if event.key == pygame.K_RETURN:
                        if x == 0:                       
                            say = 1
                            self.load_map("maps//", "/*.map")
                        if x == 1:
                            self.multiplayer_menu()
                        if x == 2:
                            say = 1
                            self.making_regions = 1
                            self.loading_map("maps//", "/*.map")
                            if self.world:
                                self.pos = self.world.map[0][0]
                                self.run()
                        if x == 3:
                            self.making_regions = 1
                            self.world = World()
                            self.world.game = self
                            self.world.create()
                            
                            self.run()
                    if event.key == pygame.K_ESCAPE:
                        exit()
    def tile_editor(self):
        self.wmap = self.world.map
        self.pos = self.wmap[0][0]]
        self.y, self.x = 0, 0
        while  True:
            pygame.time.Clock().tick(60)
            self.key_pressed = pygame.key.get_pressed()
            for event in pygame.event.get():
                self.tile_editor_keys(event)
                if evt.type == pygame.KEYDOWN:
                    if self.key_pressed[pygame.K_F12]:
                        Pdb().set_trace()
                        tolk.output(f"Debug On.")
                    if self.key_pressed[pygame.K_ESCAPE]:
                        return
    def (self):
        pass

    
if __name__ == "__main__":
    
    main = Main().start_menu()