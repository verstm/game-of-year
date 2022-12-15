import pygame as pg
import pygame.event
import numpy
from pygame import gfxdraw

pg.init()
true_width, true_height = pygame.display.Info().current_w, pygame.display.Info().current_h
print(true_width, true_height)
WIDTH = true_width * 0.8
HEIGHT = true_height * 0.8
FPS = 60
running = True
clock = pg.time.Clock()
screen = pg.display.set_mode((WIDTH, HEIGHT))


class Main:
    def __init__(self):
        self.map = Map()
        self.menu = Menu()
        self.gui = GUI()
        self.camera = Camera()
        self.mode = 0
        self.info = []

    def update(self):
        if self.mode == 0:
            self.mode = self.menu.update()
        if self.mode == 1:
            self.map.update()
            self.camera.update()
        # print(self.mode)


class GUI:
    def __init__(self):
        print('gui initialized')


class Map:
    def __init__(self):
        self.hitboxes = numpy.loadtxt('xd.txt')
        self.size = (len(self.hitboxes), len(self.hitboxes[0]))

        self.mapimage = pygame.image.load('ht.png')
        self.mapsprite = pygame.sprite.Sprite()
        self.mapsprite.image = self.mapimage
        self.mapsprite.rect = self.mapsprite.image.get_rect()
        print('map initialized')

    def update(self):
        self.render()
        game.camera.move(1, 1)

    def render(self):
        camerax, cameray = game.camera.cam_x, game.camera.cam_y
        self.visible_area = self.hitboxes[camerax:camerax + int(WIDTH)][cameray:cameray + int(HEIGHT)]
        self.mapsprite.rect.x = -camerax
        self.mapsprite.rect.y = -cameray
        screen.blit(self.mapsprite.image, self.mapsprite.rect)


class Menu:
    def __init__(self):
        print('menu initialized')

    def update(self):
        if self.check_buttons() == 1:
            return 1

    def check_buttons(self):
        return 1


class Camera:
    def __init__(self):
        self.cam_x = 0
        self.cam_y = 0
        print('camera initialized')

    def update(self):
        print(self.cam_x, self.cam_y)

    def move(self, x, y):
        if self.cam_x >= game.map.size[0]-WIDTH or self.cam_y >= game.map.size[1]-HEIGHT:
            print('граница камеры')
        else:
            self.cam_x += x
            self.cam_y += y


class Object:
    def __init__(self):
        pass


class Pawn:
    def __init__(self):
        print('self')


class Human(Pawn, pygame.sprite.Sprite):
    def __init__(self):
        super(Human, self).__init__()


game = Main()

while running:
    screen.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.WINDOWCLOSE:
            running = False
    game.update()
    clock.tick(FPS)
    pg.display.update()
    pg.display.flip()
