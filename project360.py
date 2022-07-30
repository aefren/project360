# -*- coding: utf-8 -*-
import decimal
import gc
import math
import numpy
import os
import pickle
import pygame
import sys
import natsort
import synthizer as syn
#import sys
import time

from cytolk import tolk
from glob import glob
from pdb import Pdb
from random import choice, randint, uniform, shuffle

tolk.load()

wav = '.wav'
soundpath = os.getcwd() + str('/data/sounds/')


class Source:
    def __init__(self, tile):
        self.tile = tile
        self.position = self.tile.x, self.tile.y 


class Player:
    def __init__(self):
        self.name = ""
        self.editor = 0
        self.countdown = 500
        self._countdown = 0
        self.foot = [
            ]
        self.passable_floor = ["Grass", "Sand"]
        self.passable_wall = [None]
    def can_pass(self, destination):
        if self.editor: return True
        floor = None 
        wall = None
        if destination.floor not in self.passable_floor:
            floor = f"Can not pass {destination.floor} floor.."
        if destination.wall not in self.passable_wall:
            wall = f"Can not pass {destination.wall} wall.." 
        if floor or wall:
            if floor: tolk.output(floor)
            if wall: tolk.output(wall)
            return False
        else: return True
    def can_walk(self):
        if self.ctime > self._countdown: return 1
    def say_degrees(self):
        tolk.output(f"{self.degrees}.",1)
    def say_cdt(self):
        x = str(self.position[0])
        #x = x[:x.rfind(".")+3]
        y = str(self.position[1])
        #y = y[:y.rfind(".")+3]
        tolk.output(f"x {x}, y {y}.",1)
    def set_editor(self):
        self.editor = 1
        self.countdown = 0
    def set_name(self, name):
        self.name = name
    def set_degrees(self, degrees):
        self.degrees = degrees
    def set_position(self, position=[]):
        self.position = position
    def update(self):
        self.ctime = main.ctime


class World:
    def __init__(self):
        self.name = None
        self.jumppoints = []
        self.players = []
        self.sources = []
    
    def add_player(self, degrees, name, position=[]):
        player = Player()
        player.set_degrees(degrees)
        player.set_name(name)
        player.set_position(position)
        self.players += [player]
    def add_tileattr(self):
        for y in self.map:
            for it in y:
                it.generator = None
                it.source = None
    def new_world(self):
        
        tolk.output(f"creating world.", 1)
        self.name = "map1"
        self.ext = ".map"
        self.height = 500
        self.width = 500
        self.map = []
        for y in range(0, self.height, 1):
            self.map.append([])
            for x in range(0, self.width, 1):
                tile = Tile()
                tile.x, tile.y = x, y
                self.map[y].append(tile)
    def restart_tiles(self):
        for ls in self.map:
            for it in ls:
                it.restart_attr()
    def set_savingmap_settings(self):
        for src in self.sources:
            if src.tile.source:
                src.tile.source.pause()
                src.tile.source.remove_generator(src.tile.generator)
                src.tile.source = None
                src.tile.generator = None
    def update(self):
        self.sources = [src for src in self.sources if src.tile.ambient]

class Tile:
    def __init__(self):
        self.name = ""
        self.ambient = []
        self.blocked = 0
        #self.generator = None
        self.items = []
        self.jname = None
        self.map = None
        self.set_to_rock()
        self.sonar = None
        self.source = None
        
    
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
    def restart_attr(self):
        if self.floor == "Grass": self.set_to_grass()
        elif self.floor == "Sand": self.set_to_sand()
        elif self.floor == "wall": self.set_to_rock()
    def set_to_grass(self):
        self.floor = "Grass"
        self.wall = None
        self.foot_floor = [
            "grass01",
            "grass02",
            "grass03",
            "grass04",
            ]
        self.foot_wall = []
    def set_to_sand(self):
        self.floor = "Sand"
        self.wall = None
        self.foot_floor = [
            "sand01",
            "sand02",
            "sand03",
            "sand04",
            "sand05",
            ]
        self.foot_wall = []    
    def set_to_rock(self):
        self.floor = "Rock"
        self.wall = "Wall"
        self.foot_floor = []
        self.foot_wall = []
    def set_tiletype(self, value):
        if value == "Grass": self.set_to_grass()
        if value == "Sand": self.set_to_sand()
        if value == "Wall": self.set_to_rock() 
    def say_type(self):
        tolk.output(f"{self.floor}.")
        if self.wall: tolk.output(f"{self.wall}.")
    def update(self):
        pass


class Main:
    def __init__(self, size=[1024, 768]):
        # Pygame initial settings.
        pygame.init()
        pygame.display.set_mode(size)
        pygame.display.set_caption("Project360")
        
        # Synthizer initial settings
        syn.initialize()
        self.ctx = syn.Context()
        self.ctx.default_panner_strategy.value = syn.PannerStrategy.HRTF
        self.ctx.default_distance_max.value = 40
        
        # Other initial settings.
        self.making_map = 0
        self.world = None
        decimal.getcontext().prec = 3
    def _walk(self):
        self.world.restart_tiles()
        self.world.add_player(0, "player1", [5, 5, 0])
        self.player = self.world.players[0]
        self.wmap = self.world.map
        self.pos = self.wmap[self.player.position[0]][self.player.position[1]]
        self.init_source3d()
        tolk.output(f"Explorer.",1)
        while True:
            pygame.time.Clock().tick(60)
            self.update()
            self.player.update()
            self.get_pressed_keys()
            self.ctx.position.value = self.player.position
            self.keys_object_movement()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.keys_set_degree(event)
                    self.keys_global(event)
                    if event.key == pygame.K_F12:
                        tolk.output(f"Debug On.")
                        Pdb().set_trace()
                        tolk.output(f"Debug Off.")
                    if event.key == pygame.K_ESCAPE:
                        exit()
    def _edit_map(self):
        self.wmap = self.world.map
        self.world.restart_tiles()
        #self.world.add_tileattr()
        self.world.add_player(0, name="Editor", position=[2,2,0])
        self.player = self.world.players[0]
        self.player.set_editor()
        self.pos = self.wmap[0][0]
        self.y, self.x = self.player.position[0], self.player.position[1]
        self.xrange = 0
        self.yrange = 0
        self.tiles = []
        self.set_map_move()
        tolk.output(f"Editor.",1)
        while  True:
            pygame.time.Clock().tick(60)
            self.update(editing=1)
            self.get_pressed_keys()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.keys_map_editor(event)
                    self.keys_set_degree(event)
                    if event.key == pygame.K_F12:
                        tolk.output(f"Debug On.")
                        Pdb().set_trace()
                        tolk.output(f"Debug Off.")
                    if event.key == pygame.K_ESCAPE:
                        exit()



    def add_directsound(self, sound):
        buffer = syn.Buffer.from_file(f"{soundpath+sound}.wav")
        generator = syn.BufferGenerator(self.ctx)
        generator.buffer.value = buffer
        generator.looping.value = 0
        src = syn.DirectSource(self.ctx)
        src.add_generator(generator)
    def add_jumppoint(self):
        jname = self.set_attr(attrtype="str")
        if jname == None: return
        x, y, = self.player.position[0], self.player.position[1],
        x, y = int(x), int(y) 
        tile = self.pos
        tile.jname = jname
        tile.jposition = x, y, 0
        self.world.jumppoints += [tile]
    def add_source3d(self, sound, tile, z=0):
        if ".wav" not in sound: sound += ".wav"
        position = self.get_i2d(self.wmap, tile)
        position[2] = z
        buffer = syn.Buffer.from_file(f"{soundpath+sound}")
        generator = syn.BufferGenerator(self.ctx)
        generator.buffer.value = buffer
        generator.looping.value = 1
        src = syn.Source3D(self.ctx, position=position)
        src.gain.value = 4
        src.distance_ref.value = 20
        src.add_generator(generator)
        tile.generator = generator
        tile.source = src
    def get_distance(self, source, current):
        distx = abs(source[0] - current[0])
        disty = abs(source[1] - current[1])
        #distz = abs(source[2] - current[2])
        distance = max([distx, disty])
        return distance
    def get_i2d(self, lst, obj,timer=0):
        if timer:print(f"index starts at {pygame.time.get_ticks()}.")
        for y in range(len(lst)):
            for x in range(len(lst[y])):
                if lst[y][x] == obj: 
                    location = [x, y, 0]
                    if timer: print(f"ends at {pygame.time.get_ticks()}.") 
                    return location 
    def get_jumppoint(self):
        tolk.output(f"move to a jump point.",1)
        jumppoints = self.world.jumppoints
        say = 1
        x = 0
        while True:
            pygame.time.Clock().tick(60)
            if say:
                say = 0
                if jumppoints == []: 
                    tolk.output(f"No jump points.")
                    continue
                tolk.output(f"{jumppoints[x].jname}.")
                tolk.output(f"at {jumppoints[x].jposition}.") 
            for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            x = self.selector(jumppoints, x, go="up")
                            say = 1
                        if event.key == pygame.K_DOWN:
                            x = self.selector(jumppoints, x, go="down")
                            say = 1
                        if event.key == pygame.K_HOME:
                            x = 0
                            say = 1
                        if event.key == pygame.K_END:
                            x = len(jumppoints) - 1
                            say = 1
                        if event.key == pygame.K_RETURN:
                            if jumppoints == []: return tolk.silence()
                            self.player.position = jumppoints[x].jposition
                            tolk.silence()
                            return self.set_map_move()
                        if event.key == pygame.K_F12:
                            tolk.output(f"Debug On.",1)
                            Pdb().set_trace()
                            tolk.output(f"Debug Off.")
                        if event.key == pygame.K_ESCAPE:
                            return tolk.silence()
                            
    def get_pressed_keys(self):
        self.key_pressed = pygame.key.get_pressed()
        self.alt = self.key_pressed[pygame.K_LALT]
        self.ctrl = self.key_pressed[pygame.K_LCTRL]
        self.ctrl += self.key_pressed[pygame.K_RCTRL]
        self.shift = self.key_pressed[pygame.K_LSHIFT]
        self.shift += self.key_pressed[pygame.K_RSHIFT]
    def get_sound(self, path=soundpath, filext=".wav", islist=0):
        say = 1
        x = 0
        if islist == 0:
            sounds = glob(os.path.join(path + filext))
            sounds = natsort.natsorted(sounds)
        else: sounds = path
        while True:
            pygame.time.Clock().tick(30)
            if say:
                say = 0
                if sounds:
                    if islist == 0:
                        sound = sounds[x][sounds[x].find("sounds")+7:]
                    else: sound = sounds[x]
                    tolk.output(f"{sound}")
                else: tolk.output(f"No sounds.")
            for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            x = self.selector(sounds, x, go="up")
                            say = 1
                        if event.key == pygame.K_DOWN:
                            x = self.selector(sounds, x, go="down")
                            say = 1
                        if event.key == pygame.K_HOME:
                            x = 0
                            say = 1
                        if event.key == pygame.K_END:
                            x = len(sounds) - 1
                            say = 1
                        if event.key == pygame.K_PAGEUP:
                            x -= 10
                            if x < 0: x = 0
                            say = 1
                        if event.key == pygame.K_PAGEDOWN:
                            x += 10
                            if x >= len(sounds): x = len(maps) - 1
                            say = 1
                        if event.key == pygame.K_RETURN:
                            tolk.silence()
                            if sounds:return sound
                            else: return None
                        if event.key == pygame.K_F12:
                            tolk.output(f"Debug Onn.",1)
                            Pdb().set_trace()
                            tolk.output(f"Debug Off.",1)
                        if event.key == pygame.K_ESCAPE:
                            tolk.silence()
                            return 
    def get_radians(self, degrees):
        r = decimal.Decimal(math.radians(degrees))
        sin = decimal.Decimal(math.sin(r))
        cos = decimal.Decimal(math.cos(r))
        return  sin, cos
    
    
    def init_source3d(self):
        for src in self.world.sources:
            if src.tile.source: continue
            distance = self.get_distance(src.position, self.player.position)
            if distance < self.ctx.default_distance_max.value:
                try:
                    sound = choice(src.tile.ambient)
                except Exception: Pdb().set_trace()
                self.add_source3d(sound, src.tile, 20)
        
    def keys_edit_tile(self, event):
        if event.key == pygame.K_F9:
            self.save_map()
        if event.key == pygame.K_a and self.ctrl:
            tolk.output(f"Add.",1)
            sound = self.get_sound(path=soundpath, filext="/*.wav")
            if sound:
                self.pos.ambient += [sound]
                done = 0
                for it in self.world.sources:
                    if it.tile == self.pos: 
                        done = 1
                        break
                if done == 0: self.world.sources += [Source(self.pos)]
                tolk.output(f"Added.",1)
        if event.key == pygame.K_a and self.shift:
            tolk.output(f"Remove.",1)
            sound = self.get_sound(
                path=self.pos.ambient, filext="/*.wav", islist=1)
            if sound:
                self.pos.ambient.remove(sound)
                self.pos.source.remove_generator(self.pos.generator)
                self.pos.source = None
                tolk.output(f"Removed.",1)
        if event.key == pygame.K_b:
            tolk.output(f"Remove.",1)
            if self.tiles:
                if self.tiles[0].blocked:
                    for it in self.tiles: it.blocked = 0
                    tolk.output(f"Not blocked.")
                elif self.tiles[0].blocked == 0:
                    for it in self.tiles: it.blocked = 1
                    tolk.output(f"Blocked.")
        if event.key == pygame.K_c:
            pass
        if event.key == pygame.K_j and self.shift:
            self.remove_jumppoints()
            return
        if event.key == pygame.K_j and self.ctrl:
            self.add_jumppoint()
            return
        if event.key == pygame.K_j:
            self.get_jumppoint()
        if event.key == pygame.K_n:
            name = self.set_attr(attrtype="str")
            if name: self.pos.name = name
        if event.key == pygame.K_s and self.shift:
            self.pos.ambient = ["forest01"]
            return
        if event.key == pygame.K_s:
            tolk.output(f"{len(self.tiles)} tiles selected.")
        if event.key == pygame.K_t:
            if len(self.tiles) == 0:
                tolk.output(f"No tiles selected.")
                return
            tiletype = self.pos.get_type()
            [it.set_tiletype(tiletype) for it in self.tiles]
        if event.key == pygame.K_x:
            self.player.say_cdt()
        if event.key == pygame.K_PAGEUP:
            self.xrange -= 1
            if self.shift: self.xrange -= 9
            tolk.output(f"X range: {self.xrange}.")
        if event.key == pygame.K_PAGEDOWN:
            self.xrange += 1
            if self.shift: self.xrange += 9
            tolk.output(f"X range: {self.xrange}.")
        if event.key == pygame.K_HOME:
            self.yrange += 1
            if self.shift: self.yrange += 9 
            tolk.output(f"Y range: {self.yrange}.")
        if event.key == pygame.K_END:
            self.yrange -= 1
            if self.shift: self.yrange -= 9
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
            xrange = [int(self.x), int(self.x) + self.xrange]
            xrange = range(min(xrange), max(xrange) + 1)
            yrange = [int(self.y), int(self.y) + self.yrange]
            yrange = range(min(yrange), max(yrange) + 1)
            wmap = self.world.map
            print(f"{xrange=:}, {yrange=:}.")
            idy = yrange[0] -1
            for y in wmap[yrange[0]:yrange[-1]+1]:
                idy += 1
                print(f"{idy=:}.")
                if idy not in yrange: continue
                idx = xrange[0] -1
                for x in y[xrange[0]:xrange[-1]+1]:
                    idx += 1
                    print(f"{idx=:}.")
                    if x in self.tiles: continue
                    if x.blocked: continue
                    if idx not in xrange: continue
                    self.tiles += [x]
                    print(f"added.")
            tolk.output(f"{len(self.tiles)}tiles selected.")
            return
    def keys_global(self, event):
        if event.key == pygame.K_x:
            self.player.say_cdt()
    def keys_map_editor(self, event):
        self.keys_edit_tile(event)        
        # Map movement.
        if event.key == pygame.K_DOWN:
            self.Move_object(self.player, degrees=180)
            self.set_map_move()
        if event.key == pygame.K_UP:
            self.Move_object(self.player, degrees=0)
            self.set_map_move()
        if event.key == pygame.K_LEFT and self.ctrl == 0:
            self.Move_object(self.player, degrees=270)
            self.set_map_move()
        if event.key == pygame.K_RIGHT and self.ctrl == 0:
            self.Move_object(self.player, degrees=90)
            self.set_map_move()
    def keys_object_movement(self):
        if self.key_pressed[pygame.K_w]:
            self.Move_object(self.player)
        if self.key_pressed[pygame.K_s]:
            self.Move_object(self.player, 1)
    def keys_set_degree(self, event):
        if self.player.editor:
            if event.key == pygame.K_LEFT and self.ctrl:
                self.player.degrees -= 45
                if self.player.degrees < 0: self.player.degrees += 360
                self.player.say_degrees()
            if event.key == pygame.K_RIGHT and self.ctrl:
                self.player.degrees += 45
                if self.player.degrees > 360: self.player.degrees -= 360
                if self.player.degrees == 360: self.player.degrees = 0
                self.player.say_degrees()
        if self.player.editor == 0:
            if event.key == pygame.K_a: 
                if self.key_pressed[pygame.K_RSHIFT] \
                or self.key_pressed[pygame.K_LSHIFT]: self.player.degrees -= 180
                else: self.player.degrees -= 45
                if self.player.degrees < 0: self.player.degrees += 360
                self.player.say_degrees()
            if event.key == pygame.K_d:
                if self.key_pressed[pygame.K_RSHIFT]\
                or self.key_pressed[pygame.K_LSHIFT]: 
                    self.player.degrees += 180
                else: self.player.degrees += 45
                if self.player.degrees > 360: self.player.degrees -= 360
                if self.player.degrees == 360: self.player.degrees = 0
                self.player.say_degrees()
    def load_map(self, location, filext, saved=0):
        x = 0
        say = 1
        maps = glob(os.path.join(location + filext))
        maps = natsort.natsorted(maps)
        while True:
            pygame.time.Clock().tick(30)
            if say:
                say = 0
                if maps:
                    file = open(maps[x], "rb")
                    name = pickle.load(file)
                    tolk.output(f"{name}.", 1)
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
                            tolk.output(f"LOADING...",1)
                            self.world = World()
                            world = pickle.load(file)
                            self.world.name = world.name
                            self.world.ext = world.ext
                            self.world.jumppoints = world.jumppoints
                            self.world.height = world.height
                            self.world.width = world.width
                            self.world.map = world.map
                            self.world.sources = world.sources
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
        if self.pos.name: tolk.output(f"{self.pos.name}.")
        self.pos.say_type()
        if self.pos.ambient: tolk.output(f"Ambient sounds.")
        if self.pos.jname: tolk.output(f"{self.pos.jname}.")
        if self.pos in self.tiles: tolk.output(f"Selected.")
    def Move_object(self, unit, backward=0, degrees=None):
        if unit.can_walk():
            unit._countdown = self.ctime + unit.countdown
            x = unit.position[0]
            y = unit.position[1]
            if degrees == None: degrees = unit.degrees
            if backward:
                degrees += 180
                if degrees > 360: degrees -= 361
            radians = self.get_radians(degrees)
            x += radians[0]
            y += radians[1]
            destination = self.wmap[int(y)][int(x)]
            if unit.can_pass(destination):
                unit.position = x, y, 0
                if destination.foot_floor:
                    sound = choice(destination.foot_floor)
                    self.add_directsound(sound)
            else: 
                tolk.output(f"Can not move there.",1)
                try:
                    if destination.foot_wall:
                        sound = choice(destination.foot_wall)
                        self.add_directsound(sound)
                except Exception: Pdb().set_trace()
    
    def remove_jumppoints(self):
        tolk.output(f"Remove a jump point.",1)
        jumppoints = self.world.jumppoints
        say = 1
        x = 0
        while True:
            pygame.time.Clock().tick(60)
            if say:
                say = 0
                if jumppoints == []: 
                    tolk.output(f"No jump points.")
                    continue
                tolk.output(f"{jumppoints[x].jname}.")
                tolk.output(f"at {jumppoints[x].jposition}.")
            for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            x = self.selector(jumppoints, x, go="up")
                            say = 1
                        if event.key == pygame.K_DOWN:
                            x = self.selector(jumppoints, x, go="down")
                            say = 1
                        if event.key == pygame.K_HOME:
                            x = 0
                            say = 1
                        if event.key == pygame.K_END:
                            x = len(jumppoints) - 1
                            say = 1
                        if event.key == pygame.K_RETURN:
                            if jumppoints == []: return tolk.silence()
                            tile = jumppoints[x]
                            tile.jname = None
                            self.world.jumppoints.remove(jumppoints[x])
                            tolk.output(f"Removed",1)
                            tolk.silence()
                            return
                        if event.key == pygame.K_F12:
                            tolk.output(f"Debug On.",1)
                            Pdb().set_trace()
                            tolk.output(f"Debug Off.")
                        if event.key == pygame.K_ESCAPE:
                            return tolk.silence()
    def remove_source3d(self):
        for src in self.world.sources:
            if src.tile.source == None: continue
            distance = self.get_distance(src.position, self.player.position)
            if distance > self.ctx.default_distance_max.value + 5:
                src.tile.source.remove_generator(src.tile.generator)
                src.tile.source = None
                src.tile.generator = None
    def save_map(self):
        tolk.output("Saving map.",1)
        self.world.set_savingmap_settings()
        filename = os.path.join("maps//")
        filename += self.world.name
        filename += self.world.ext
        file = open(filename, "wb")
        pickle.dump(self.world.name, file)
        pickle.dump(self.world, file)
        file.close()
        tolk.output(f"map saved.",1)
        time.sleep(1)

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
    def     set_attr(self, attrtype="str"):
        say = 1
        i = 0
        data = str()
        if attrtype == "str": tolk.output(f"type a string.",1)
        if attrtype == "int": tolk.output(f"type a int.",1)
        if attrtype == "float": tolk.output(f"type a float.",1)        
        while True:
            pygame.time.Clock().tick(60)
            if i < 0: i = 0
            if say:
                say = 0
                if data: tolk.output(f"{data[i]}")
                else: tolk.output(f"Blank.")
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if data: 
                            if attrtype == "str":  return str(data)
                            if attrtype == "int":  return int(data)
                        else: return None
                    if event.key == pygame.K_F12:
                        tolk.output(f"Debug On.",1)
                        Pdb().set_trace()
                        tolk.output(f"Debug Off.",1)
                    if event.key == pygame.K_ESCAPE:
                        tolk.silence()
                        return
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        if data: tolk.output(f"{data}",1)
                        else: tolk.output(f"Blank.",1)
                    if event.key == pygame.K_LEFT:
                        i -= 1
                        say = 1
                    if event.key == pygame.K_RIGHT:
                        i += 1
                        say = 1
                        if i == len(data): i = len(data) - 1
                    if event.key == pygame.K_SPACE:
                        item = None
                        if attrtype == "str": 
                            item = event.unicode
                            home = data[:i+1]
                            end = data[i+1:]
                            data = home + item + end
                            i += 1
                            if i == len(data): i = len(data) - 1
                    if event.key != pygame.K_DELETE:
                        item = None
                        if attrtype == "str":
                            if event.unicode.isalnum() == False: continue 
                        if attrtype == "int":
                            if event.unicode.isnumeric() == False: continue
                        if attrtype == "float":
                            if (event.unicode.isnumeric() == False
                                and event.unicode != "."): continue
                        item = event.unicode 
                        home = data[:i+1]
                        end = data[i+1:]
                        data = home + item + end
                        i += 1
                        if i == len(data): i = len(data) - 1
                    if event.key == pygame.K_DELETE:
                        if len(data) > 0:
                            tolk.output(f"{data[i]}.", 1)
                            data = data[:i] + data[i+1:]
                            i -= 1
                            if i < 0: i = 0
                    
    def set_orientation(self):
        degrees = self.player.degrees
        x, y, z = 0, 0, 0
        if degrees > 270 or degrees in range(0, 90): y = 1
        if degrees in range(91, 270): y = -1
        if degrees in range(1, 180): x = 1
        if degrees > 180: x = 1
        at = [x, y, z]
        up = [0, 0, 1]
        self.ctx.orientation.value = at + up
    def set_map_move(self):
        self.x, self.y = self.player.position[0], self.player.position[1]
        self.x, self.y = int(self.x), int(self.y)
        self.pos = self.world.map[int(self.y)][int(self.x)]
        self.map_info()

    
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
                            self.load_map("maps//", "/*.map")
                            if self.world:
                                self._edit_map()
                        if x == 2:
                            say = 1
                            self.world = World()
                            self.world.new_world()
                            self._edit_map()
                    if event.key == pygame.K_ESCAPE:
                        exit()
    def update(self, editing=0):
        self.ctime = pygame.time.get_ticks()
        self.world.update()
        self.init_source3d()
        self.remove_source3d()
        self.player.update()
        self.set_orientation()
        self.ctx.position.value = self.player.position



if __name__ == "__main__":
    main = Main()    
    main.start_menu()