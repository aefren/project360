# -*- coding: utf-8 -*-
import gc
import math
import numpy
import os
import pickle
import psutil
import pygame
import sys
import natsort
import synthizer as syn
import time

from collections import deque
from cytolk import tolk
from glob import glob
from pdb import Pdb
from random import choice, randint, uniform, shuffle

tolk.load()

wav = '.wav'
soundpath = os.getcwd() + str('/data/sounds/')



class EmptyClass:
    def __init__(self):
        pass


class Block:
    def __init__(self):
        pass
    def set_to_rock(self):
        self.name = "Rock"
        self.sounds = [
            ]


class Floor:
    def __init__(self):
        pass
    def set_to_concrete(self):
        self.name = "Concrete"
        self.sounds = [
            "ft-concrete01",
            "ft-concrete02",
            "ft-concrete03",
            "ft-concrete04",
            "ft-concrete05",
            ]
        
    def set_to_grass(self):
        self.name = "Grass"
        self.sounds = [
            "ft-grass01",
            "ft-grass02",
            "ft-grass03",
            "ft-grass04",
            "ft-grass05",
            ]
    def set_to_forest(self):
        self.name = "Forest"
        self.sounds = [
            "ft-forest01",
            "ft-forest02",
            "ft-forest03",
            "ft-forest04",
            "ft-forest05",
            "ft-forest06",
            "ft-forest07",
            ]
    def set_to_rustwood(self):
        self.name = "Rust Wood"
        self.sounds = [
            "ft-rustwood01",
            "ft-rustwood02",
            "ft-rustwood03",
            "ft-rustwood04",
            "ft-rustwood05",
            "ft-rustwood06",
            "ft-rustwood07",
            ]
    def set_to_sand(self):
        self.name = "Sand"
        self.sounds = [
            "ft-sand01",
            "ft-sand02",
            "ft-sand03",
            "ft-sand04",
            "ft-sand05",
            ]
    def set_to_water(self):
        self.name = "Water"
        self.sounds = [
            "ft-water01",
            "ft-water02",
            "ft-water03",
            "ft-water04",
            "ft-water05",
            "ft-water06",
            "ft-water07",
            "ft-water08",
            "ft-water09",
            ]
    def set_to_wood(self):
        self.name = "Wood"
        self.sounds = [
            "ft-wood01",
            "ft-wood02",
            "ft-wood03",
            "ft-wood04",
            "ft-wood05",
            ]


class SoundEvent:
    def __init__(self, position):
        self.y = position[0]
        self.x = position[1]
        self.z = position[2]
        self.position = position
        self.sounds = []
        self.source = None
        
        self.distance_ref = 1
        self.distance_max = 10
        self.gain = 1
        self.loop = 0
        self.pitch_bend = 1
        self.ratio = 0
        self.rolloff = 1
    def add_sound(self):
        sound = main.get_sound(path=soundpath, filext="/*.wav")
        self.sounds += [sound]
    def check_complete(self):
        if self.source == None: return
        position = self.generator.playback_position.value
        length = self.buffer.get_length_in_seconds()
        if position >= length:
            self.clean() 
    def clean(self):
        if self.source:
            self.source.remove_generator(self.generator)
            self.source.dec_ref()
            self.source = None
            self.generator.dec_ref()
            del(self.generator)
            del(self.buffer)
    def update(self):
        self.check_complete()
        if self.source:
            self.generator.looping.value = self.loop
            self.generator.pitch_bend.value = self.pitch_bend
            
            self.source.gain.value = self.gain
            self.source.position.value = self._position
            self.source.distance_ref.value = self.distance_ref
            self.source.distance_max.value = self.distance_max
            self.source.rolloff.value = self.rolloff


class Player:
    def __init__(self):
        self.name = ""
        self.editor = 0
        self.generator = None
        
        self.running = 0
        self.walk_countdown = 500
        self.run_countdown_factor = 0.7
        self._countdown = 0
        self.step_length = 0.07
        self.run_step_factor = 2
        self.locations = []
        self.sensor_timers = [0, 0, 0, 0, 0]
        self.foot = [
            ]
        self.passable_floor = ["Grass", "Sand"]
        self.passable_wall = [None]
        self.source = None
    def can_pass(self, destination):
        if self.editor: return True
        floor = None 
        if destination.floor not in self.passable_floor:
            floor = f"Can not pass {destination.floor} floor.."
        if floor:
            #if floor: tolk.output(floor)
            return False
        else: return True
    def can_walk(self):
        if self.ctime > self._countdown: return 1
    def clean(self):
        if self.source: 
            self.source.dec_ref()
            self.source = None
        if self.generator: 
            self.generator.dec_ref()
            self.generator = None
    def check_location(self):
        locations = main.get_location(self.position)
        if locations != self.locations:
            for it in locations:
                if it not in self.locations: tolk.output(f"{it}")
            self.locations = locations 
    def say_degrees(self):
        tolk.output(f"{self.degrees}.",1)
    def say_cdt(self):
        x = str(self.position[1])
        y = str(self.position[0])
        if "." in x: x = x[:x.rfind(".")+3]
        if "." in y: y = y[:y.rfind(".")+3]
        x = float(x)
        y = float(y)
        tolk.output(f"y {y}, x {x}.",1)
    def say_location(self):
        locations = main.get_location(self.position)
        if locations:
            for it in locations:
                tolk.output(f"{it}")
    def set_editor(self):
        self.editor = 1
        self.walk_countdown = 0
    def set_name(self, name):
        self.name = name
    def set_degrees(self, degrees):
        if degrees < 0: degrees += 360
        elif degrees > 360: degrees -= 360
        self.degrees = degrees
    def set_position(self, position=[]):
        self.position = position
    def set_run(self):
        if self.running == 0:
            self.running = 1
            tolk.output(f"Running On.",1)
        elif self.running:
            self.running = 0
            tolk.output(f"Running Off.",1)
    def update(self):
        self.ctime = main.ctime


class World:
    def __init__(self):
        self.name = None
        self.jumppoints = []
        self.locations = []
        self.players = []
        self.sources = []
    
    def add_player(self, degrees, name, position=[]):
        player = Player()
        player.set_degrees(degrees)
        player.set_name(name)
        player.set_position(position)
        self.players += [player]
    def new_world(self, info=0):        
        inicio = pygame.time.get_ticks()
        tolk.output(f"creating world.", 1)
        self.name = main.set_attr(attrtype="str")
        if self.name == None: return
        self.ext = ".map"
        self.width = 1000
        self.length = 1000
        self.map = []
        for y in range(0, self.length, 1):
            self.map.append([])
            for x in range(0, self.width, 1):
                tile = Tile()
                tile.y, tile.x = y, x
                #tile.set_to_sand()
                self.map[y].append(tile)
        if info:
            pworld = pickle.dumps(self)
            mem = psutil.Process(os.getpid()).memory_info().rss/1024
            print(f"pickle: {sys.getsizeof(pworld)/1024}.")
            ctime = pygame.time.get_ticks()
            print(f"{mem=:}.")
            print(f"{ctime-inicio}.")
            tolk.output(f"Done.")
            Pdb().set_trace()
    def set_savingmap_settings(self):
        self.players = []
        for y in self.map:
            for it in y: 
                if hasattr(it, "pos"): del(it.pos)
        for pl in self.players:
            pl.clean()
        for src in self.sources:
            if src.source:
                src.clean()
    def update(self):
        [src.update() for src in self.sources]


class Tile:
    def __init__(self):
        self.floors = []
        self.items = []
    
    def hasfloor(self, position):
        if hasattr(self, "floors") == False: return
        for fl in self.floors:
            if fl.position == position: return True
    def set_floor(self, floor_type):
        y = self.y
        x = self.x
        self.positions = []
        for r in range(10):
            x = self.x
            for i in range(10):
                floor = Floor()
                if floor_type == "Concrete": floor.set_to_concrete()
                if floor_type == "Grass": floor.set_to_grass()
                if floor_type == "Forest": floor.set_to_forest()
                if floor_type == "Sand": floor.set_to_sand()
                if floor_type == "Rust Wood": floor.set_to_rustwood()
                if floor_type == "Water": floor.set_to_water()
                if floor_type == "Wood": floor.set_to_wood()
                floor.position = (y, x)
                self.floors += [floor]
                x = round(x + 0.1, 1)
                if i == 9: y = round(y + 0.1, 1)
    def say_floor(self):
        if hasattr(self, "floors") == False: return
        position = main.player.position
        for fl in self.floors:
            if (position[0], position[1]) == fl.position:
                tolk.output(f"{fl.name}.")
    def update(self):
        pass


class Main:
    def __init__(self, size=[1024, 768]):
        # Pygame initial settings.
        pygame.init()
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Project360")
        
        # Synthizer initial settings
        syn.initialize()
        self.ctx = syn.Context()
        self.ctx.default_panner_strategy.value = syn.PannerStrategy.HRTF
        self.ctx.default_distance_max.value = 10
        
        # Other initial settings.
        self.locations = []
        self.macro_mode = 1
        self._mouse_timer = 0
        self.mouse_timer = 200
        self.mouse_max_speed = 90
        self.sounds = []
        self.sensor = 0
        self.world = None
    def _walk(self):
        self.world.add_player(
            degrees=0, name="player1", position=[370, 60, 0])
        self.player = self.world.players[0]
        self.wmap = self.world.map
        position = self.player.position
        self.pos = self.wmap[int(position[0])][int(position[1])]
        tolk.output(f"Explorer.",1)
        self.center_mouse()
        while True:
            pygame.time.Clock().tick(30)
            self.update()
            self.player.update()
            self.get_pressed_keys()
            if self.sensor: self.sensor_event()
            self.keys_object_movement()
            for event in pygame.event.get():
                self.mouse_input(event)
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
        self.world.add_player(0, name="Editor", position=[370, 200, 0])
        self.player = self.world.players[0]
        self.player.set_editor()
        self.pos = self.wmap[0][0]
        self.y, self.x = self.player.position[0], self.player.position[1]
        self.xrange = 0
        self.yrange = 0
        self.tiles = []
        self.positions = deque([], 30000)
        self.set_map_move()
        tolk.output(f"Editor.",1)
        while  True:
            pygame.time.Clock().tick(60)
            self.update()
            self.get_pressed_keys()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.keys_map_editor(event)
                    self.keys_global(event)
                    self.keys_set_degree(event)
                    if event.key == pygame.K_F12:
                        tolk.output(f"Debug On.")
                        Pdb().set_trace()
                        tolk.output(f"Debug Off.")
                    if event.key == pygame.K_ESCAPE:
                        exit()



    def add_directsound(self, sound, vol=1):
        buffer = syn.Buffer.from_file(f"{soundpath+sound}.wav")
        generator = syn.BufferGenerator(self.ctx)
        generator.buffer.value = buffer
        generator.looping.value = 0
        if vol: generator.gain.value = vol
        src = syn.DirectSource(self.ctx)
        src.add_generator(generator)
    def add_jumppoint(self):
        name = self.set_attr(attrtype="str")
        if name == None: return
        jumppoint = EmptyClass()
        jumppoint.position = self.player.position
        jumppoint.name = name
        self.world.jumppoints += [jumppoint]
    
    def add_location_event(self):
        name = self.set_attr("str")
        if name == None: return
        location = EmptyClass()
        self.world.locations += [location]
        location.name = name
        location.position = self.player.position
        location.locations = self.positions
    def add_source3d(
            self, sound, gain=None, loop=0, linger=None, position=(), z=0,
            ds_ref=None, ds_max=None, pitch=None, rolloff=None, play=1, 
            info=0):
        if info: print(f"New Buffer {sound}.")
        buffer = None
        if ".wav" not in sound: sound += ".wav"
        for sn in self.sounds:
            if sn[0] == sound: 
                buffer = sn[1]
                break
        if buffer == None:
            buffer = syn.Buffer.from_file(f"{soundpath+sound}")
            self.sounds += [[sound, buffer]]
        generator = syn.BufferGenerator(self.ctx)
        generator.buffer.value = buffer
        if pitch: generator.pitch_bend.value = pitch
        generator.looping.value = loop
        source = syn.Source3D(self.ctx, position=position)
        if ds_max: source.distance_max.value = ds_max
        if ds_ref: source.distance_ref.value = ds_ref
        if gain: source.gain.value = gain
        if rolloff: source.rolloff.value = rolloff
        if linger: 
            generator.config_delete_behavior(linger=True)
            source.config_delete_behavior(linger=True)
        if play: source.add_generator(generator)
        return buffer, generator, source
    def add_sound_event(self):
        name = self.set_attr(attrtype="str")
        if name == None: return
        source = SoundEvent(self.player.position)
        source.name = name
        self.world.sources += [source]
        main.view_sound_events(-1)
    def center_mouse(self):
        sizes = pygame.display.get_desktop_sizes()
        self.screen_size = [sizes[0][0], sizes[0][1]]
        pygame.mouse.set_pos(self.screen_size[0]/2, self.screen_size[0]/2)
    def fix_decimal(self, value, prec=1):
        value = str(value)
        dotindex = value.rfind(".")
        if dotindex < 0: return float(value)
        lng = len(value) - 1
        dec_digits = abs(dotindex - lng)
        if dec_digits > prec:
            value = value[:(dotindex+1)+prec]
        return float(value)
            
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
    def get_options(self, items):
        items.sort()
        say = 1
        x = 0
        while True:
            pygame.time.Clock().tick(60)
            if say:
                say = 0
                tolk.output(f"{items[x]}")
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        x = self.selector(items, x, "up")
                        say = 1
                    if event.key == pygame.K_DOWN:
                        x = self.selector(items, x, "down")
                        say = 1
                    if event.key == pygame.K_RETURN:
                        tolk.silence()
                        return items[x]
                    if event.key == pygame.K_ESCAPE:
                        tolk.silence()
                        return
    def get_pressed_keys(self):
        self.key_pressed = pygame.key.get_pressed()
        self.alt = self.key_pressed[pygame.K_LALT]
        self.ctrl = self.key_pressed[pygame.K_LCTRL]
        self.ctrl += self.key_pressed[pygame.K_RCTRL]
        self.shift = self.key_pressed[pygame.K_LSHIFT]
        self.shift += self.key_pressed[pygame.K_RSHIFT]
    def get_sound(self, path=soundpath, filext=".wav", islist=0):
        src = None
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
                        if event.key == pygame.K_SPACE:
                            if src == None:
                                buffer, generator, src = main.add_source3d(
                                    sound, linger=1, 
                                    position=self.player.position, ds_ref=1,)
                            elif src:
                                src.remove_generator(generator)
                                src.dec_ref()
                                generator.dec_ref()
                                src = None
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
                            if src:
                                src.remove_generator(generator)
                                src.dec_ref()
                                generator.dec_ref()
                            if sounds:return sound
                            else: return None
                        if event.key == pygame.K_F12:
                            tolk.output(f"Debug Onn.",1)
                            Pdb().set_trace()
                            tolk.output(f"Debug Off.",1)
                        if event.key == pygame.K_ESCAPE:
                            tolk.silence()
                            if src:
                                src.remove_generator(generator)
                                src.dec_ref()
                                generator.dec_ref()
                            return 
    def get_radians(self, degrees):
        r = math.radians(degrees)
        sin = math.sin(r)
        cos = math.cos(r)
        return  [round(sin, 4), round(cos, 4)]
    
    
    def get_xrange(self, xrange, dec, extra=0):
        x = self.player.position[1]
        if extra:
            extra = 0
            if int(x + xrange) > int(x): extra = 1
            if int(x + xrange) < int(x): extra = -1
        xrange = xrange + extra
        x = int(x)
        xrange = int(xrange)
        xrange = [x, x + xrange]
        xrange = numpy.arange(min(xrange), max(xrange) + dec, dec)
        xrange = [round(it,1) for it in xrange]
        return xrange
    def get_xrange_dec(self, xrange, dec):
        x = self.player.position[1]
        xrange = [x, x + xrange]
        xrange = numpy.arange(
            round(min(xrange), 1), 
            round(max(xrange) + dec, 1), 
            dec)
        xrange = [round(it,1) for it in xrange]
        return xrange
    def get_yrange(self, yrange, dec, extra=0):
        y = self.player.position[0]
        if extra:
            extra = 0
            if int(y + yrange) > int(y): extra = 1
            if int(y + yrange) < int(y): extra = -1
        yrange = yrange + extra
        y = int(y)
        yrange = int(yrange)
        yrange = [y, y + yrange]
        yrange = numpy.arange(min(yrange),  max(yrange) + dec, dec)
        yrange = [round(it,1) for it in yrange]
        return yrange
    def get_yrange_dec(self, yrange, dec=0.10000):
        y = self.player.position[0]
        yrange = [y, y + yrange]
        yrange = numpy.arange(
            round(min(yrange), 1), 
            round(max(yrange) + dec, 1), 
            dec)
        yrange = [round(it,1) for it in yrange]
        return yrange
    def goto_position(self, y=None, x=None):
        if not y: y = self.player.position[0]
        if not x: x = self.player.position[1]
        self.player.position = y, x, 0
        self.set_map_move()
    def init_source3d(self, info=0):
        for it in self.world.sources:
            if it.sounds == []: continue
            if it.source: continue
            distance = self.get_distance(it.position, self.player.position)
            if distance < self.ctx.default_distance_max.value:
                if info: print(f"Adding sound in {it.position}.")
                sound = choice(it.sounds)
                it._position = list(it.position)
                if hasattr(it, "ratio") == False: it.ratio = 0
                if it.ratio:
                    it._position[0]= uniform(it._position[0]- it.ratio, 
                                         it._position[0] + it.ratio)
                    it._position[1]= uniform(it._position[1]- it.ratio, 
                                         it._position[1] + it.ratio)
                bf, gen, src = self.add_source3d(
                    sound, position=it._position, linger=1, play=0)
                it.buffer = bf
                it.generator = gen
                it.source = src
                it.sound_name = sound
                
                it.generator.looping.value = it.loop
                
                it.source.distance_ref.value = it.distance_ref
                it.source.gain.value = it.gain
                it.source.rolloff.value = it.rolloff
                
                it.source.add_generator(it.generator)
    def keys_edit_tile(self, event):
        if event.key == pygame.K_F3:
            tolk.output(f"View.",1)
            items = ["Sound Events", "Locations", "Jump Points"]
            selected = self.get_options(items)
            if selected == "Sound Events": self.view_sound_events()
            elif selected == "Locations": self.view_location_events()
            elif selected == "Jump Points": self.view_jumppoint()
        if event.key == pygame.K_F9:
            self.save_map()
        if event.key == pygame.K_a and self.ctrl:
            tolk.output(f"Add.",1)
            items = ["Sound Event", "Location", "Jump Point"]
            selected = self.get_options(items)
            if selected == "Jump Point": self.add_jumppoint()
            elif selected == "Location": self.add_location_event()
            if selected == "Sound Event": self.add_sound_event()
        if event.key == pygame.K_b:
            if self.positions == []: return
            items = ["Add", "Remove"]
            selected = self.get_options(items)
            if selected == None: return
            for it in self.positions:
                tile = self.wmap[int(it[0])][int(it[1])]
                #print(f"tile {tile.y}, {tile.x}.")
                if hasattr(tile, "floor") == False: continue
                if selected == "Add":
                    if it not in tile.blocked:
                        print(f"Added {it}.") 
                        tile.blocked += [it]
                elif selected == "Remove":
                    if it in tile.blocked: 
                        tile.blocked.remove(it)
        if event.key == pygame.K_c:
            pass
        if event.key == pygame.K_f:
            if not self.positions: return
            selected = self.select_floor()            
            if selected == None: return
            self.set_floor(selected)
            
        if event.key == pygame.K_m:
            if self.macro_mode:
                self.macro_mode = 0
                tolk.output(f"Macro Off",1)
            elif self.macro_mode == 0:
                self.macro_mode = 1
                tolk.output(f"Macro On",1)
        if event.key == pygame.K_n:
            name = self.set_attr(attrtype="str")
            if name: self.pos.name = name
        if event.key == pygame.K_q:
            self.pos.say_floor()
        if event.key == pygame.K_s and self.shift:
            self.pos.ambient = ["forest01"]
            return
        if event.key == pygame.K_s:
            tolk.output(f"{len(self.tiles)} tiles selected.")
        if event.key == pygame.K_t:
            if not self.tiles:
                tolk.output(f"No tiles selected.")
                return
            selected = self.select_floor()
            if not selected: return
            [it.set_floor (selected) for it in self.tiles]
        if event.key == pygame.K_x:
            self.player.say_cdt()
        if event.key == pygame.K_PAGEUP:
            self.xrange -= 0.1
            if self.ctrl: self.xrange -= 0.9
            self.xrange = round(self.xrange ,1)
            tolk.output(f"X range: {self.xrange}.")
        if event.key == pygame.K_PAGEDOWN:
            self.xrange += 0.1
            if self.ctrl: self.xrange += 0.9
            self.xrange = round(self.xrange, 1)
            tolk.output(f"X range: {self.xrange}.")
        if event.key == pygame.K_HOME:
            self.yrange += 0.1
            if self.ctrl: self.yrange += 0.9 
            self.yrange = round(self.yrange,1)
            tolk.output(f"Y range: {self.yrange}.")
        if event.key == pygame.K_END:
            self.yrange -= 0.1
            if self.ctrl: self.yrange -= 0.9
            self.yrange = round(self.yrange,1)
            tolk.output(f"Y range: {self.yrange}.")
        if event.key == pygame.K_DELETE:
            self.yrange =0
            self.xrange = 0
            tolk.output(f"Ranges reseted.")
        if event.key == pygame.K_BACKSPACE:
            self.tiles = []
            self.positions = []
            tolk.output(f"Cleaned.", 1)
        if event.key == pygame.K_SPACE and self.ctrl:
            tolk.silence()
            if self.macro_mode:
                self.select_square(remove=1)
            else:
                self.select_tile(remove=1)
        elif event.key == pygame.K_SPACE:
            tolk.silence()
            if self.macro_mode:
                self.select_square()
            else:
                self.select_tile()
    def keys_global(self, event):
        if event.key == pygame.K_e:
            if self.sensor == 0:
                self.sensor = 1
                tolk.output(f"Sensor On.")
            elif self.sensor:
                self.sensor = 0
                tolk.output(f"Sensor Off.")
        if event.key == pygame.K_r:
            self.player.set_run()
        if event.key == pygame.K_v:
            self.player.say_location()
        if event.key == pygame.K_x:
            self.player.say_cdt()
        if event.key == pygame.K_F11:
            mem = psutil.Process(os.getpid()).memory_info().rss/1024
            tolk.output(f"{mem}.")
    def keys_map_editor(self, event):
        self.keys_edit_tile(event)        
        # Map movement.
        if event.key == pygame.K_g:
            msg = f"Enter a float value for y."
            tolk.output(msg)
            y = self.set_attr(attrtype="float")
            msg = f"Enter a float value for x."
            tolk.output(msg)
            x = self.set_attr(attrtype="float")
            self.goto_position(y, x)
        if event.key == pygame.K_DOWN:
            if self.ctrl == 0: self.move_editor(self.player, 180)
            elif self.ctrl: self.move_editor(self.player, 180, 1)
            self.set_map_move()
        if event.key == pygame.K_UP:
            if self.ctrl == 0: self.move_editor(self.player, 0)
            elif self.ctrl: self.move_editor(self.player, 0, 1)
            self.set_map_move()
        if event.key == pygame.K_LEFT:
            if self.ctrl == 0: self.move_editor(self.player, 270)
            elif self.ctrl: self.move_editor(self.player, 270, 1)
            self.set_map_move()
        if event.key == pygame.K_RIGHT:
            if self.ctrl == 0: self.move_editor(self.player, 90)
            elif self.ctrl: self.move_editor(self.player, 90, 1)
            self.set_map_move()
    def keys_object_movement(self):
        if self.key_pressed[pygame.K_w]:
            output = self.Move_object(self.player)
            if isinstance(output, str): tolk.output(output)
        if self.key_pressed[pygame.K_s]:
            self.Move_object(self.player, 1)
    def keys_set_degree(self, event):
        if self.player.editor:
            if event.key == pygame.K_LEFT and self.shift:
                degrees = self.player.degrees
                degrees -= 45
                self.player.set_degrees(degrees)
                self.player.say_degrees()
            if event.key == pygame.K_RIGHT and self.shift:
                degrees = self.player.degrees
                degrees += 45
                self.player.set_degrees(degrees)
                self.player.say_degrees()
        if self.player.editor == 0:
            if event.key == pygame.K_a:
                degrees = self.player.degrees 
                if self.shift: degrees -= 180
                else: degrees -= 45
                self.player.set_degrees(degrees)
                self.player.say_degrees()
            if event.key == pygame.K_d:
                degrees = self.player.degrees
                if self.shift: degrees += 180
                else: degrees += 45
                self.player.set_degrees(degrees)
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
                            #self.world = World()
                            self.world = pickle.load(file)
                            #self.world.name = world.name
                            #self.world.ext = world.ext
                            #self.world.jumppoints = world.jumppoints
                            #self.world.length = world.length
                            #self.world.width = world.width
                            #self.world.map = world.map
                            #self.world.sources = world.sources
                            #self.world.initial_settings()
                            file.close()
                            
                            return
                        else: tolk.output(f"no maps.", 1)
                    if event.key == pygame.K_F12:
                        tolk.output(f"debug on.", 1)
                        Pdb().set_trace()
                        tolk.output(f"debug off.", 1)
                    if event.key == pygame.K_ESCAPE:
                        return
    def map_info(self):
        if hasattr(self.pos, "floor"):
            if hasattr(self.pos, "name"): tolk.output(f"{self.name}.")
            self.pos.say_floor()
            if hasattr(self.pos, "ambient"): tolk.output(f"Ambient sounds.")
            if hasattr(self.pos, "jname"): tolk.output(f"{self.pos.jname}.")
        else: tolk.output(f"y {self.pos.y}, x {self.pos.x}.",1)
        if self.macro_mode and self.pos in self.tiles: 
            tolk.output(f"Selected.")
    def mouse_input(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.center_mouse()
            if self._mouse_timer > self.ctime: return
            move = event.rel[0]
            if move < 0 and abs(move) > self.mouse_max_speed: 
                move = -self.mouse_max_speed
            if move > 0 and abs(move) > self.mouse_max_speed: 
                move = self.mouse_max_speed
            if move:
                self.player.set_degrees(self.player.degrees + move)
                self.player.say_degrees()
                self._mouse_timer = self.ctime + self.mouse_timer
        
    def move_editor(self, unit, degrees, lnstep=None):
        x = unit.position[1]
        y = unit.position[0]
        if degrees == None: degrees = unit.degrees
        if lnstep == None: lnstep=unit.step_length
        radians = self.get_radians(degrees)
        radians[0] *= lnstep
        radians[1] *= lnstep
        x = round(x + radians[0], 1)
        y = round(y + radians[1], 1)
        unit.position = y, x, 0
        destination = self.wmap[int(y)][int(x)]
        if hasattr(destination, "floors") == False: return
        for fl in destination.floors:
            if (y, x) == fl.position:
                sound = choice(fl.sounds)
                unit.clean()
                bf, gen, src = self.add_source3d(
                    sound, loop=0, linger=1, position=unit.position)
                unit.generator = gen
                unit.source = src
    def Move_object(self, unit, backward=0, degrees=None, info=1):
        if not unit.can_walk(): return
        if unit.running == 0: 
            unit._countdown = self.ctime + unit.walk_countdown
            step = unit.step_length
        if unit.running: 
            _countdown = self.ctime
            _countdown += unit.walk_countdown *unit.run_countdown_factor
            unit._countdown = _countdown
            step = unit.step_length * unit.run_step_factor 
        
        y = unit.position[0]
        x = unit.position[1]
        if degrees == None: degrees = unit.degrees
        if backward:
            degrees += 180
            if degrees > 360: degrees -= 361
        radians = self.get_radians(degrees)
        radians[0] *= step
        radians[1] *= step
        endy = self.fix_decimal(y + radians[1], prec=2)
        endx = self.fix_decimal(x + radians[0], prec=2)
        print(f"destination: {endy, endx}.")
        print(f"radians0 {radians[0]}, radians1 {radians[1]}.")
        radians = self.get_radians(degrees)
        radians[0] *= 0.01
        radians[1] *= 0.01
        print(f"Reduced radians")
        print(f"radians0 {radians[0]}, radians1 {radians[1]}.")
        count = 0
        while True:
            fixed_y = self.fix_decimal(y, prec=2)
            fixed_x = self.fix_decimal(x, prec=2)
            if (fixed_y, fixed_x) == (endy, endx): break
            count += 1
            y = round(y + radians[1], 4)
            x = round(x + radians[0], 4)
            destination = self.wmap[int(y)][int(x)]
            ypos = self.fix_decimal(y, prec=1)
            xpos = self.fix_decimal(x, prec=1)
            print(f"y {y}, x {x}.")
            if info: print(f"Future pos {ypos, xpos}.")
            if destination.hasfloor((ypos, xpos)) == None:
                tolk.output(f"No floor.")
                break 
            if (hasattr(destination, "blocked") 
            and (ypos, xpos) in destination.blocked): 
                tolk.output(f"Blocked.")
                break
        unit.position = y, x, 0
        print(f"{count=:}.")
        for fl in destination.floors:
            if (ypos, xpos) == fl.position:
                sound = choice(fl.sounds)
                unit.clean()
                bf, gen, src = self.add_source3d(
                    sound, gain=1, loop=0, linger=1, position=unit.position)
                unit.generator = gen
                unit.source = src
                unit.check_location()
    def _Move_object(self, unit, backward=0, degrees=None, info=1):
        if unit.can_walk():
            if unit.running == 0: 
                unit._countdown = self.ctime + unit.walk_countdown
                step = unit.step_length
            if unit.running: 
                _countdown = self.ctime
                _countdown += unit.walk_countdown *unit.run_countdown_factor
                unit._countdown = _countdown
                step = unit.step_length * unit.run_step_factor 
            x = unit.position[1]
            y = unit.position[0]
            if degrees == None: degrees = unit.degrees
            if backward:
                degrees += 180
                if degrees > 360: degrees -= 361
            radians = self.get_radians(degrees)
            radians[0] *= step
            radians[1] *= step
            x += radians[0]
            y += radians[1]
            destination = self.wmap[int(y)][int(x)]
            ypos = str(y)
            xpos = str(x)
            print(f"{ypos, xpos}.")
            if "." in ypos: ypos = ypos[:ypos.rfind(".")+2]
            if "." in xpos: xpos = xpos[:xpos.rfind(".")+2]
            ypos = float(ypos)
            xpos = float(xpos)
            if info: print(f"Future pos {ypos, xpos}.")
            Pdb().set_trace()
            if destination.hasfloor((ypos, xpos)) == None: return f"No floor."
            if (ypos, xpos) in destination.blocked: return f"Blocked."
            unit.position = y, x, 0
            for fl in destination.floors:
                if (ypos, xpos) == fl.position:
                    sound = choice(fl.sounds)
                    unit.clean()
                    bf, gen, src = self.add_source3d(
                        sound, gain=1, loop=0, linger=1, position=unit.position)
                    unit.generator = gen
                    unit.source = src
                    unit.check_location()
    def _Move_object(self, unit, backward=0, degrees=None):
        if unit.can_walk():
            unit._countdown = self.ctime + unit.walk_countdown
            x = unit.position[1]
            y = unit.position[0]
            if degrees == None: degrees = unit.degrees
            if backward:
                degrees += 180
                if degrees > 360: degrees -= 361
            radians = self.get_radians(degrees)
            radians[0] *= unit.step_length
            radians[1] *= unit.step_length
            x += radians[0]
            y += radians[1]
            destination = self.wmap[int(y)][int(x)]
            if hasattr(destination, "floor") == False:
                tolk.output(f"Can not move there.")
                return
            ypos = str(y)
            xpos = str(x)
            if "." in ypos: ypos = ypos[:ypos.rfind(".")+2]
            if "." in xpos: xpos = xpos[:xpos.rfind(".")+2]
            ypos = float(ypos)
            xpos = float(xpos)
            print(f"Future pos {ypos, xpos}.")
            if (ypos, xpos) in destination.blocked:
                tolk.output(f"Can not move there.")
                return  
            unit.position = y, x, 0
            if destination.foot_floor:
                sound = choice(destination.foot_floor)
                unit.clean()
                bf, gen, src = self.add_source3d(
                    sound, gain=1, loop=0, linger=1, position=unit.position)
                unit.generator = gen
                unit.source = src
                unit.check_location()
    
    def remove_source3d(self):
        for src in self.world.sources:
            distance = self.get_distance(src.position, self.player.position)
            if src.sounds == []: continue
            if distance <= self.ctx.default_distance_max.value + 1: continue
            src.clean()
            
    def get_location(self, position):
        msg = []
        y, x = position[:2]
        ypos = str(y)
        xpos = str(x)
        if "." in ypos: ypos = ypos[:ypos.rfind(".")+2]
        if "." in xpos: xpos = xpos[:xpos.rfind(".")+2]
        ypos = float(ypos)
        xpos = float(xpos)
        
        for lc in self.world.locations:
            if (ypos, xpos) in lc.locations:
                msg += [f"{lc.name}"]
        
        return msg 
    def save_map(self):
        tolk.output("Saving map.",1)
        self.world.set_savingmap_settings()
        filename = os.path.join("maps//")
        filename += self.world.name
        filename += self.world.ext
        file = open(filename, "wb")
        try:
            pickle.dump(self.world.name, file)
            pickle.dump(self.world, file)
        except Exception as err:
            print(f"{err}.")
            tolk.output(f"{err}.")
            Pdb().set_trace() 

        file.close()
        tolk.output(f"map saved.",1)
        time.sleep(1)

    def select_floor(self):
        items = [
            "Concrete", "Grass", "Forest", 
            "Rust Wood", "Sand", "Water", "Wood"]
        selected = self.get_options(items)
        return selected
    def select_square(self, remove=0):
        xrng = self.get_xrange(self.xrange, 1)
        yrng = self.get_yrange(self.yrange,1)
        yrng = [int(it) for it in yrng]
        xrng = [int(it) for it in xrng]
        yrange = []
        for it in yrng: 
            if it not in yrange: yrange += [it]
        xrange = []
        for it in xrng: 
            if it not in xrange: xrange += [it]
        wmap = self.world.map
        idy = yrange[0] -1
        for y in wmap[yrange[0]:yrange[-1]+1]:
            idy += 1
            if idy not in yrange: continue
            idx = xrange[0] -1
            for x in y[xrange[0]:xrange[-1]+1]:
                idx += 1
                if idx not in xrange: continue
                if remove == 0:
                    if x in self.tiles: continue
                    self.tiles += [x]
                else:
                    if x in self.tiles: self.tiles.remove(x)
        tolk.output(f"{len(self.tiles)}tiles selected.")
        return
    def select_tile(self, remove=0):
        yrange = self.get_yrange_dec(self.yrange, 0.10001)
        xrange = self.get_xrange_dec(self.xrange, 0.10001)
        for y in yrange:
            for x in xrange:
                if remove:
                    if (y, x) in self.positions:
                        self.positions.remove((y, x))
                if remove == 0:
                    if (y, x) not in self.positions:
                        self.positions += [(y, x)]
        
        tolk.output(f"{len(self.positions)} positions selected.",1)
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
    def sensor_event(self, info=0):
        ldegrees = [self.player.degrees - 90]
        ldegrees += [self.player.degrees -45]
        ldegrees += [self.player.degrees]
        ldegrees += [self.player.degrees + 45]
        ldegrees += [self.player.degrees + 90]
        #ldegrees = [self.player.degrees]
        for r in range(len(ldegrees)):
            if ldegrees[r] < 0: ldegrees[r] += 360
            if ldegrees[r] == 360: ldegrees[r] = 0
            if ldegrees[r] > 360: ldegrees[r] -= 360
        # sonar.
        if info: print(f"{ldegrees=:}.")
        distance = 21
        cdt_value = 150
        idx = -1
        for it in ldegrees:
            idx += 1
            if self.player.sensor_timers[idx] > self.ctime: 
                continue
            if info: print(f"checking {it}.")
            x, y = self.player.position[1], self.player.position[0]
            z = 0
            ctimer = cdt_value * (len(ldegrees) + 2)
            vol = 1
            self.player.sensor_timers[idx] = self.ctime + ctimer
            if idx < len(ldegrees) - 1:
                ctimer = self.ctime + cdt_value
                self.player.sensor_timers[idx+1] = ctimer
            for r in range(distance):
                vol -= vol*0.2
                if vol < 0: vol = 0.05
                radians = self.get_radians(it)
                radians[0] *= self.player.step_length
                radians[1] *= self.player.step_length
                x += radians[0]
                y += radians[1]
                destination = self.wmap[int(y)][int(x)]
                ypos = str(y)
                xpos = str(x)
                if "." in ypos: ypos = ypos[:ypos.rfind(".")+2]
                if "." in xpos: xpos = xpos[:xpos.rfind(".")+2]
                ypos = float(ypos)
                xpos = float(xpos)
                if info: print(f"checking in {ypos, xpos}.")
                can_pass = 1
                if hasattr(destination, "floor") == False: can_pass = 0
                elif (ypos, xpos) in destination.blocked: can_pass = 0
                if can_pass == 0:
                    y = round(y,2)
                    x = round(x, 2)
                    sound = "sensor01"
                    self.player.clean()
                    bf, gen, src = self.add_source3d(
                        sound, linger=1, loop=0, position =[y, x, 0], gain=vol,
                        pitch=0.8)
                    self.player.generator = gen
                    self.player.source = src
                    break
                elif can_pass and r == distance - 1:
                    sound = "sensor01"
                    self.player.clean()
                    bf, gen, src = self.add_source3d(
                        sound, linger=1, loop=0, position =[y, x, z], 
                        gain=0.5, pitch=0.4)
                    self.player.generator = gen
                    self.player.source = src                
                
    def     set_attr(self, attrtype="str"):
        say = 1
        i = 0
        data = str()
        if attrtype == "str": tolk.output(f"type a string.")
        if attrtype == "int": tolk.output(f"type a int.")
        if attrtype == "float": tolk.output(f"type a float.")        
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
                            if attrtype == "float":  return float(data)
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
                    
    
    def set_floor(self, floor_type):
        for pos in self.positions:
            square = self.wmap[int(pos[0])][int(pos[1])]
            if hasattr(square, "floors") == False: square.floors = []
            square.floors = [it for it in square.floors if pos != it.position]
        for pos in self.positions:
            square = self.wmap[int(pos[0])][int(pos[1])]
            floor = Floor()
            if floor_type == "Concrete": floor.set_to_concrete()
            if floor_type == "Grass": floor.set_to_grass()
            if floor_type == "Forest": floor.set_to_forest()
            if floor_type == "Sand": floor.set_to_sand()
            if floor_type == "Rust Wood": floor.set_to_rustwood()
            if floor_type == "Water": floor.set_to_water()
            if floor_type == "Wood": floor.set_to_wood()
            floor.position = pos
            square.floors += [floor]        
    def set_map_move(self):
        self.y, self.x = self.player.position[0], self.player.position[1]
        self.y, self.x = int(self.y), int(self.x)
        if self.macro_mode == 0 and self.player.position[:2] in self.positions:
            tolk.output(f"Position Selected.")
        locations = self.get_location(self.player.position)
        old_pos = self.pos
        self.pos = self.world.map[int(self.y)][int(self.x)]
        if old_pos != self.pos:
            self.map_info()
        if locations != self.locations:
            for it in locations:
                if it not in self.locations: tolk.output(f"{it}")
            self.locations = locations
    def set_orientation(self):
        degrees = self.player.degrees
        x, y, z = 0, 0, 0
        if degrees > 270 or degrees in range(0, 90): y = -1
        if degrees in range(91, 270): y = 1
        if degrees in range(1, 180): x = -1
        if degrees > 180: x = 1
        at = [y, x, z]
        up = [0, 0, 1]
        self.ctx.orientation.value = at + up
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
    def view_jumppoint(self):
        jumppoints = self.world.jumppoints
        say = 1
        x = 0
        while True:
            pygame.time.Clock().tick(60)
            self.update()
            if say:
                if x  >= len(jumppoints): x -= 1
                say = 0
                if jumppoints == []: 
                    tolk.output(f"No jump points.")
                    continue
                tolk.output(f"{jumppoints[x].name}.")
                tolk.output(f"at {jumppoints[x].position}.")
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
                        if event.key == pygame.K_DELETE:
                            self.world.jumppoints.remove(jumppoints[x])
                            tolk.output(f"Removed.",1)
                        if event.key == pygame.K_RETURN:
                            if jumppoints == []: return tolk.silence()
                            self.player.position = jumppoints[x].position
                            tolk.silence()
                            return self.set_map_move()
                        if event.key == pygame.K_F12:
                            tolk.output(f"Debug On.",1)
                            Pdb().set_trace()
                            tolk.output(f"Debug Off.")
                        if event.key == pygame.K_ESCAPE:
                            return tolk.silence()
    def view_location_events(self):
        tolk.output(f"Locations.",1)
        events = self.world.locations
        say = 1
        x = 0
        while True:
            pygame.time.Clock().tick(60)
            self.update()
            if say:
                if x  >= len(events): x = len(events) - 1
                say = 0
                if events == []: 
                    tolk.output(f"No jump points.")
                    continue
                tolk.output(f"{events[x].name}.")
                location = self.get_location(events[x].position)
                if location: 
                    for it in location:
                        if events[x].name != it: tolk.output(f"{it}.")
                tolk.output(f"at {events[x].position}.")
            for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                            events[x].locations += self.positions
                            plus = len(self.positions)
                            tolk.output(f"{plus} Positions Added.")
                        if event.key == pygame.K_UP:
                            x = self.selector(events, x, go="up")
                            say = 1
                        if event.key == pygame.K_DOWN:
                            x = self.selector(events, x, go="down")
                            say = 1
                        if event.key == pygame.K_HOME:
                            x = 0
                            say = 1
                        if event.key == pygame.K_END:
                            x = len(events) - 1
                            say = 1
                        if event.key == pygame.K_DELETE:
                            self.world.locations.remove(events[x])
                        if event.key == pygame.K_RETURN:
                            if events == []: return tolk.silence()
                            self.player.position = events[x].position
                            self.set_map_move()
                            tolk.silence()
                            return
                        if event.key == pygame.K_F12:
                            tolk.output(f"Debug On.",1)
                            Pdb().set_trace()
                            tolk.output(f"Debug Off.")
                        if event.key == pygame.K_ESCAPE:
                            return tolk.silence()
    def view_sound_events(self, x=0):
        events = self.world.sources
        say = 1
        y = 0
        while True:
            pygame.time.Clock().tick(30)
            self.update()            
            if say:
                if x  >= len(events): x -= 1
                say = 0
                if events == []:
                    tolk.output(f"No sound events.")
                    continue
                
                it = events[x]
                params = [
                    [f"Name", it, "name"],
                    [f"Sounds", len(it.sounds)],
                    [f"Position", it, "position"],
                    [f"X", it, "y"],
                    [f"X", it, "x"],
                    [f"Z", it, "z"[0]],
                    [f"Gain", it, "gain"],
                    [f"distance max", it, "distance_max"],
                    [f"distance ref", it, "distance_ref"],
                    [f"Loop", it, "loop"],
                    ["Pitch bend", it, "pitch_bend"],
                    [f"Ratio", it, "ratio" ],
                    [f"RollOff", it, "rolloff" ],
                    ]
                it.position = it.y, it.x, it.z
                it.update()
                tolk.output(f"{params[y][0]} ")
                if len(params[y]) == 3:
                    tolk.output(f"{getattr(params[y][1], params[y][2])}.")
                elif len(params[y]) == 2:
                    tolk.output(f"{params[y][1]}.")
            for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                            events[x].add_sound()
                        if event.key == pygame.K_n:
                            name = self.set_attr(attrtype="str")
                            if name: it.name = name
                        if event.key == pygame.K_s:
                            sound = main.get_sound(events[x].sounds, 
                                                        islist=1)
                            if sound:
                                events[x].sounds.remove(sound)
                                if it.sound_name == sound: it.clean()
                        if event.key == pygame.K_u:
                            attr = getattr(params[y][1], params[y][2])
                            if isinstance(attr, str) == False:
                                attr += 1
                                setattr(params[y][1], params[y][2], attr)
                                say = 1
                        if event.key == pygame.K_j:
                            attr = getattr(params[y][1], params[y][2])
                            if isinstance(attr, str) == False:
                                if attr <= 0: return
                                attr -= 1
                                setattr(params[y][1], params[y][2], attr)
                                say = 1
                        if event.key == pygame.K_i:
                            attr = getattr(params[y][1], params[y][2])
                            if isinstance(attr, str) == False:
                                attr = round(attr + 0.1, 2)
                                setattr(params[y][1], params[y][2], attr)
                                say = 1
                        if event.key == pygame.K_k:
                            attr = getattr(params[y][1], params[y][2])
                            if isinstance(attr, str) == False:
                                if attr <= 0: continue
                                attr = round(attr - 0.1, 2)
                                setattr(params[y][1], params[y][2], attr)
                                say = 1
                        if event.key == pygame.K_LEFT:
                            x = self.selector(events, x, "up")
                            say = 1
                            it = events[x]
                            if y != 0: tolk.output(f"{it.name} ")
                        if event.key == pygame.K_RIGHT:
                            x = self.selector(events, x, "down")
                            say = 1
                            it = events[x]
                            if y != 0: tolk.output(f"{it.name} ")
                        if event.key == pygame.K_UP:
                            y = self.selector(params, y, "up")
                            say = 1
                        if event.key == pygame.K_DOWN:
                            y = self.selector(params, y, "down")
                            say = 1
                        if event.key == pygame.K_HOME:
                            x = 0
                            say = 1
                            it = events[x]
                            if y != 0: tolk.output(f"{it.name} ")
                        if event.key == pygame.K_END:
                            x = len(events) - 1
                            say = 1
                            it = events[x]
                            if y != 0: tolk.output(f"{it.name} ")
                        if event.key == pygame.K_PAGEUP:
                            y = 0
                            say = 1
                        if event.key == pygame.K_PAGEDOWN:
                            y = len(params) - 1
                            say = 1
                        if event.key == pygame.K_DELETE:
                            events[x].clean()
                            self.world.sources.remove(events[x])
                            tolk.output(f"Removed.",1)
                        if event.key == pygame.K_RETURN:
                            if events== []: return tolk.silence()
                            self.player.position = events[x].position
                            tolk.silence()
                            return self.set_map_move()                            
                        if event.key == pygame.K_F12:
                            tolk.output(f"Debug On.",1)
                            Pdb().set_trace()
                            tolk.output(f"Debug Off.")
                        if event.key == pygame.K_ESCAPE:
                            return tolk.silence()
    def update(self):
        self.ctime = pygame.time.get_ticks()
        self.init_source3d()
        self.player.update()
        self.set_orientation()
        self.ctx.position.value = self.player.position
        self.world.update()
        self.remove_source3d()



if __name__ == "__main__":
    main = Main()
    main.start_menu()