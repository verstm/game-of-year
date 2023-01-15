import pygame
import numpy
from math import sin, cos, asin, acos, hypot
import os
import pickle
from twisted.internet import protocol, reactor
import threading
from socket import socket, AF_INET, SOCK_DGRAM
from net_functions import *
from copy import copy, deepcopy
import time
import random
from server import *
from main_classes import *
from characters import *
from twisted.internet import protocol, reactor

pygame.init()
true_width, true_height = pygame.display.Info().current_w, pygame.display.Info().current_h
WIDTH = int(true_width * 0.8)
HEIGHT = int(true_height * 0.8)
FPS = 60
running = True
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
DEBUG = True

clock = pygame.time.Clock()


class EchoServer(protocol.Protocol):

    def connectionMade(self):
        game.connected = 1

    def dataReceived(self, data):
        recv_pack = eval(data.decode())
        game.pack = recv_pack
        send_pack = game.info
        self.transport.write(str(send_pack).encode())
        #clock.tick(FPS)

    def connectionLost(self, reason):
        game.connected = 0


class EchoClient(protocol.Protocol):

    def connectionMade(self):
        game.connected = 1
        send_pack = game.info
        self.transport.write(str(send_pack).encode())
        clock.tick(FPS)

    def dataReceived(self, data):
        recv_pack = eval(data.decode())
        game.pack = recv_pack
        send_pack = game.info
        self.transport.write(str(send_pack).encode())
        # clock.tick(FPS)

    def connectionLost(self, reason):
        game.connected = 0
        print("connection lost")


class ClientFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()


def client(ip):
    f = ClientFactory()
    reactor.connectTCP(ip, 8080, f)
    reactor.run(installSignalHandlers=False)


def server():
    print('server started')
    factory = protocol.ServerFactory()
    factory.protocol = EchoServer
    reactor.listenTCP(8080, factory)
    reactor.run(installSignalHandlers=False)


class Main:
    def __init__(self, WIDTH, HEIGHT, screen, FPS, host):
        self.map = Map(self, WIDTH, HEIGHT, screen)
        self.menu = Menu(WIDTH, HEIGHT, self, screen, FPS)
        self.camera = Camera(WIDTH, HEIGHT, self)
        self.pers1 = Human(WIDTH, HEIGHT, self, screen, FPS)
        self.pers2 = Human(WIDTH, HEIGHT, self, screen, FPS)
        self.pers2.main_chr = 0
        self.pers2.rect.x, self.pers2.rect.y = self.pers1.truecords
        self.gui = GUI(self.pers1, self.pers2, WIDTH, HEIGHT, screen)
        self.mode = 0
        self.events = []
        self.connected = 0
        self.pack = None
        self.host = host
        self.multiplayer_flg = 0
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.screen = screen
        self.FPS = FPS

    def update(self):
        self.events = []
        if self.mode < 2:
            self.mode, self.pers1 = self.menu.update()
            if self.mode == 2:
                self.gui = GUI(self.pers1, self.pers2, self.WIDTH, self.HEIGHT, self.screen)
                self.mode += 1
            self.set_enemies()
        if self.mode == 2:
            self.map.update()
            self.camera.update()
            self.pers1.update()
            self.pers2.update()
            self.gui.update(self.pers1, self.pers2)
        if self.mode == 3:
            if self.connected and self.pack:
                self.check_pack()
            else:
                ...
            if self.host:
                if not self.multiplayer_flg:
                    self.server_thread = threading.Thread(target=server)
                    self.server_thread.start()
                    self.multiplayer_flg = 1
            else:
                if not self.multiplayer_flg:
                    opn = scan_lan(8080)
                    self.client_thread = threading.Thread(target=client, args=[opn[0]])
                    self.client_thread.start()
                    self.multiplayer_flg = 1
            self.map.update()
            self.camera.update()
            self.pers1.update()
            self.pers2.update()
            self.gui.update(self.pers1, self.pers2)
            if self.pers1.HP <= 0:
                self.mode = 4
            if self.pers2.HP <= 0:
                self.mode = 4
            # self.pers1.HP -= 1
            # self.pers2.HP -= 1
        if self.mode == 4:
            print('GAME OVER!!!')
        self.info = [self.pers1.info]

    def check_pack(self):
        # pack = [self.pers1.info, self.pers2.info]
        # persinfo = [self.HP, self.maxHP, self.name, self.pic, animsforinfo, self.animation_counter]
        pack = deepcopy(self.pack)
        characters = [self.pers2]
        for i in range(len(characters)):
            characters[i].HP = pack[i][0]
            characters[i].maxHP = pack[i][1]
            characters[i].name = pack[i][2]
            characters[i].pic = pack[i][3]
            # characters[i].vertical_speed = pack[i][5]
            # characters[i].horizontal_speed = pack[i][6]
            characters[i].x = pack[i][7]
            characters[i].y = pack[i][8]
            characters[i].keys = pack[i][9]
            characters[i].mouse_arr = pack[i][10]
            characters[i].alpha = pack[i][11]

            # characters[i].rect.x = pack[i][7]
            # characters[i].rect.y = pack[i][8]

    # def information_gathering(self):

    def set_enemies(self):
        self.pers1.enemy = self.pers2
        self.pers2.enemy = self.pers1
        self.pers1_group = pygame.sprite.Group()
        self.pers1_group.add(self.pers1)
        self.pers2_group = pygame.sprite.Group()
        self.pers2_group.add(self.pers2)
        self.pers1.enemygroup = self.pers2_group
        self.pers2.enemygroup = self.pers1_group


game = Main(WIDTH, HEIGHT, screen, FPS, True)

while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.WINDOWCLOSE:
            exit(0)
            running = False

    game.update()
    clock.tick(FPS)
    pygame.display.update()
    pygame.display.flip()
