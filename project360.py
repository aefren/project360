
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
    def new_world(self):
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
        main.y = 0
        main.x = 0
        pass
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
            "Grass",
            "Sand",
            "Wall",
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
                        x = main.selector(types, x, go="up")
                        say = 1
                    if event.key == pygame.K_DOWN:
                        x = main.selector(types, x, go="down")
                        say = 1
                    if event.key == pygame.K_RETURN:
                        tolk.output(f"set to {types[x]}.")
                        return types[x]
                    if event.key == pygame.K_ESCAPE:
                        return
    def set_to_grass(self):
        self.type = "Grass"
    def set_to_sand(self):
        self.type = "Sand"
    def set_to_wall(self):
        self.type = "Wall"
    def set_tiletype(self, value):
        if value == "Grass": self.set_to_grass()
        if value == "Sand": self.set_to_sand()
        if value == "Wall": self.set_to_wall() 
    def say_type(self):
        tolk.output(f"{self.type}.")
    def update(self):
        pass


class Main:
    def __init__(self, size=[1024, 768]):
        pygame.init()
        pygame.display.set_mode(size)
        pygame.display.set_caption("Project360")
        self.making_map = 0
        self.world = None
    
    
    def _walk(self):
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
            self.keys_object_movement()
            for event in pygame.event.get():
                self.keys_set_degree(event)
                if event.type == pygame.KEYDOWN:
                    self.keys_global(event)
                    if self.key_pressed[pygame.K_F12]:
                        Pdb().set_trace()
                        tolk.output(f"Debug On.")
                    if self.key_pressed[pygame.K_ESCAPE]:
                        return
    def _edit_map(self):
        self.wmap = self.world.map
        self.pos = self.wmap[0][0]
        self.y, self.x = 0, 0
        self.xrange = 0
        self.yrange = 0
        self.tiles = []
        while  True:
            pygame.time.Clock().tick(60)
            self.key_pressed = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.keys_map_editor(event)
                    if self.key_pressed[pygame.K_F12]:
                        Pdb().set_trace()
                        tolk.output(f"Debug On.")
                    if self.key_pressed[pygame.K_ESCAPE]:
                        return



    def get_radians(self, degrees):
        return (
            math.cos(math.radians(degrees)), 
            math.sin(math.radians(degrees))
            )
    
    def keys_global(self, event):
        if event.key == pygame.K_x:
            self.player.say_cdt()
    def keys_map_editor(self, event):
        self.set_tile(event)        
        # Map movement.
        if event.key == pygame.K_UP:
            if self.y > 0: 
                self.y -= 1
                self.set_map_move()
            else:
                tolk.output("End.")
        if event.key == pygame.K_DOWN:
            if self.y < len(self.world.map) - 1: 
                self.y += 1
                self.set_map_move()
            else:
                tolk.output("End.")
        if event.key == pygame.K_LEFT:
            if self.x > 0: 
                self.x -= 1
                self.set_map_move()
            else:
                tolk.output("End.")
        if event.key == pygame.K_RIGHT:
            if self.x < len(self.world.map[0]) - 1: 
                self.x += 1
                self.set_map_move()
            else:
                tolk.output("End.")
    def keys_object_movement(self):
        if self.key_pressed[pygame.K_UP] and self.key_pressed[pygame.K_RSHIFT] == 0:
            self.Move_unit(self.player)
        if self.key_pressed[pygame.K_DOWN]:
            self.Move_unit(self.player, 1)
    def keys_set_degree(self, event):
        if event.key == pygame.K_LEFT: 
            if self.key_pressed[pygame.K_RCTRL]: self.player.degrees -= 90
            elif self.key_pressed[pygame.K_RSHIFT]: self.player.degrees -= 45
            else: self.player.degrees -= 1
            if self.player.degrees < 0: self.player.degrees += 361
            self.player.say_degrees()
        if event.key == pygame.K_RIGHT:
            if self.key_pressed[pygame.K_RCTRL]: self.player.degrees += 90
            elif self.key_pressed[pygame.K_RSHIFT]: 
                self.player.degrees += 45
            else: self.player.degrees += 1
            if self.player.degrees > 360: self.player.degrees -= 361
            self.player.say_degrees()
        if event.key == pygame.K_UP:
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
    def map_info(self):
        self.pos.update()
        self.pos.say_type()
        if self.pos in self.tiles: tolk.output(f"Selected.")
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
    def set_map_move(self):
        self.pos = self.world.map[self.y][self.x]
        self.map_info()

    def set_tile(self, event):
        try:
            if event.key == pygame.K_F1:
                pass
        except Exception: Pdb().set_trace()
        if event.key == pygame.K_c:
            pass
        if event.key == pygame.K_g:
            pass
        if event.key == pygame.K_s:
            tolk.output(f"{len(self.tiles)} tiles selected.")
            return
        if event.key == pygame.K_t:
            if len(self.tiles) == 0:
                tolk.output(f"No tiles selected.")
                return
            tiletype = self.pos.get_type()
            [it.set_tiletype(tiletype) for it in self.tiles]
        if event.key == pygame.K_x:
            tolk.output(f"Y {self.y}, X {self.x}.")
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
        if event.key == pygame.K_BACKSPACE:
            self.tiles = []
            tolk.output(f"Cleaned.", 1)
        if event.key == pygame.K_SPACE:
            tolk.silence()
            xrange = [self.x, self.x + self.xrange]
            xrange = range(min(xrange), max(xrange) + 1)
            yrange = [self.y, self.y + self.yrange]
            yrange = range(min(yrange), max(yrange) + 1)
            wmap = self.world.map
            for y in range(len(wmap)):
                for x in range(len(wmap[y])):
                    if wmap[y][x] in self.tiles: continue
                    if y in yrange and x in xrange:
                        self.tiles += [wmap[y][x]]
            tolk.output(f"{len(self.tiles)}tiles selected.")
            return
    def start_menu(self):
        say = 1
        x = 0
        options = [
            "Explore.",
            "map editor.",
            "Map creator."
            ]
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
                            if self.world:
                                self._walk()
                        if x == 1:
                            say = 1
                            self.loading_map("maps//", "/*.map")
                            if self.world:
                                self._edit_map()
                        if x == 2:
                            say = 1
                            self.world = World()
                            self.world.new_world()
                            self._edit_map()
                    if event.key == pygame.K_ESCAPE:
                        exit()
    
if __name__ == "__main__":
    main = Main()    
    main.start_menu()