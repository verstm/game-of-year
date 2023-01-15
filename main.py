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

pygame.init()
true_width, true_height = pygame.display.Info().current_w, pygame.display.Info().current_h
WIDTH = int(true_width * 0.8)
HEIGHT = int(true_height * 0.8)
FPS = 60
running = True
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
DEBUG = True


# xd



game = Main(WIDTH, HEIGHT, screen, FPS)

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
