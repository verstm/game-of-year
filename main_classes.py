import pygame
import os
import numpy
import threading
from net_functions import *
from copy import copy, deepcopy
from characters import *





class GUI:
    # если будем менять настройки разрешения во время работы игры надо будет заинитить гуи заново
    # 1536 864
    def __init__(self, chr1, chr2, WIDTH, HEIGHT, screen):
        self.chr1 = chr1
        self.chr2 = chr2

        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.screen = screen

        path = os.path.join(os.path.dirname(__file__), 'Assets')
        path = os.path.join(path, 'Sprites')

        self.chr_font = pygame.font.Font(None, 40)
        self.chr1_font_color = (63, 72, 204)
        self.chr2_font_color = (255, 0, 0)

        self.text_chr1 = self.chr_font.render(chr1.name, True, self.chr1_font_color)
        self.text_chr2 = self.chr_font.render(chr2.name, True, self.chr2_font_color)

        self.text_chr1_rect = self.text_chr1.get_rect()
        self.text_chr1_rect.left = self.HEIGHT // 40
        self.text_chr1_rect.top = self.HEIGHT // 40

        self.text_chr2_rect = self.text_chr2.get_rect()
        self.text_chr2_rect.right = self.WIDTH - self.HEIGHT // 40
        self.text_chr2_rect.top = self.HEIGHT // 40

        self.pic1 = chr1.pic
        self.image_chr1 = pygame.image.load(os.path.join(path, self.pic1)).convert()
        self.image_chr1 = pygame.transform.scale(self.image_chr1, (self.HEIGHT // 5, self.HEIGHT // 5))
        self.image_chr1_rect = self.image_chr1.get_rect()
        self.image_chr1_rect.left = self.text_chr1_rect.left
        self.image_chr1_rect.top = self.text_chr1_rect.bottom + self.HEIGHT // 54

        self.pic2 = chr2.pic
        self.image_chr2 = pygame.image.load(os.path.join(path, self.pic2)).convert()
        self.image_chr2 = pygame.transform.scale(self.image_chr2, (self.HEIGHT // 5, self.HEIGHT // 5))
        self.image_chr2_rect = self.image_chr2.get_rect()
        self.image_chr2_rect.right = self.WIDTH - self.HEIGHT // 40
        self.image_chr2_rect.top = self.text_chr2_rect.bottom + self.HEIGHT // 54

        self.image_hp1 = pygame.image.load(os.path.join(path, 'hp_bar.png'))
        self.image_hp1 = pygame.transform.scale(self.image_hp1, (self.HEIGHT // 5, self.HEIGHT // 21))
        self.image_hp1_rect = self.image_hp1.get_rect()
        self.image_hp1_rect.left = self.text_chr1_rect.left
        self.image_hp1_rect.top = self.image_chr1_rect.bottom + self.HEIGHT // 54

        self.image_hp2 = pygame.image.load(os.path.join(path, 'hp_bar.png'))
        self.image_hp2 = pygame.transform.scale(self.image_hp2, (self.HEIGHT // 5, self.HEIGHT // 21))
        self.image_hp2_rect = self.image_hp2.get_rect()
        self.image_hp2_rect.right = self.text_chr2_rect.right
        self.image_hp2_rect.top = self.image_chr2_rect.bottom + self.HEIGHT // 54

        self.green_hp1 = pygame.Surface(
            (self.HEIGHT // 5 - self.image_hp1_rect.width // 6, self.HEIGHT // 21 // 3 * 2 - self.HEIGHT // 21 // 3 * 2 * 0.1))
        self.green_hp1_rect = self.green_hp1.get_rect()
        self.green_hp1_rect.left = self.image_hp1_rect.left + self.image_hp1_rect.width // 6
        self.green_hp1_rect.centery = self.image_hp1_rect.centery

        self.red_hp1 = pygame.Surface((0, self.HEIGHT // 21 // 3 * 2 - self.HEIGHT // 21 // 3 * 2 * 0.1))
        self.red_hp1_rect = self.red_hp1.get_rect()
        self.red_hp1_rect.height = self.green_hp1_rect.height

        self.green_hp2 = pygame.Surface(
            (self.HEIGHT // 5 - self.image_hp2_rect.width // 6, self.HEIGHT // 21 // 3 * 2 - self.HEIGHT // 21 // 3 * 2 * 0.1))
        self.green_hp2_rect = self.green_hp2.get_rect()
        self.green_hp2_rect.left = self.image_hp2_rect.left + self.image_hp2_rect.width // 6
        self.green_hp2_rect.centery = self.image_hp2_rect.centery

        self.red_hp2 = pygame.Surface((0, self.HEIGHT // 21 // 3 * 2 - self.HEIGHT // 21 // 3 * 2 * 0.1))
        self.red_hp2_rect = self.red_hp1.get_rect()
        self.red_hp2_rect.height = self.green_hp2_rect.height

        self.to_blit = [[self.text_chr1, self.text_chr1_rect], [self.text_chr2, self.text_chr2_rect],
                        [self.image_chr1, self.image_chr1_rect], [self.image_chr2, self.image_chr2_rect],
                        [self.green_hp1, self.green_hp1_rect], [self.green_hp2, self.green_hp2_rect],
                        [self.red_hp1, self.red_hp1_rect], [self.red_hp2, self.red_hp2_rect],
                        [self.image_hp1, self.image_hp1_rect], [self.image_hp2, self.image_hp2_rect]]

    def update(self, chr1, chr2):
        self.to_blit = [[self.text_chr1, self.text_chr1_rect], [self.text_chr2, self.text_chr2_rect],
                        [self.image_chr1, self.image_chr1_rect], [self.image_chr2, self.image_chr2_rect],
                        [self.green_hp1, self.green_hp1_rect], [self.green_hp2, self.green_hp2_rect],
                        [self.red_hp1, self.red_hp1_rect], [self.red_hp2, self.red_hp2_rect],
                        [self.image_hp1, self.image_hp1_rect], [self.image_hp2, self.image_hp2_rect]]

        self.chr1 = chr1
        self.chr2 = chr2

        self.green_hp1.fill((0, 255, 0))
        self.red_hp1 = pygame.Surface(
            (self.green_hp1_rect.width * (1 - self.chr1.HP / self.chr1.maxHP), self.green_hp1_rect.height))
        self.red_hp1_rect = self.red_hp1.get_rect()
        self.red_hp1_rect.right = self.green_hp1_rect.right
        self.red_hp1_rect.top = self.green_hp1_rect.top
        self.red_hp1.fill((255, 0, 0))

        self.green_hp2.fill((0, 255, 0))
        self.red_hp2 = pygame.Surface(
            (self.green_hp2_rect.width * (1 - self.chr2.HP / self.chr2.maxHP), self.green_hp2_rect.height))
        self.red_hp2_rect = self.red_hp2.get_rect()
        self.red_hp2_rect.right = self.green_hp2_rect.right
        self.red_hp2_rect.top = self.green_hp2_rect.top
        self.red_hp2.fill((255, 0, 0))

        self.blit_gui()

    def blit_gui(self):
        for el in self.to_blit:
            self.screen.blit(el[0], el[1])


class Map:
    # self.map = Map(self, WIDTH, HEIGHT, screen)
    def __init__(self, game, WIDTH, HEIGHT, screen):
        self.hitboxes = numpy.loadtxt('xd.txt')
        self.size = (len(self.hitboxes), len(self.hitboxes[0]))

        self.mapimage = pygame.image.load('map.png')
        self.mapsprite = pygame.sprite.Sprite()
        self.mapsprite.image = self.mapimage
        self.mapsprite.rect = self.mapsprite.image.get_rect()
        print('map initialized')
        self.screen = screen
        self.game = game
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def update(self):
        self.render()
        # game.camera.move(1, 1)

    def render(self):
        camerax, cameray = self.game.camera.cam_x, self.game.camera.cam_y
        self.visible_area = self.hitboxes[camerax:camerax + int(self.WIDTH), cameray:cameray + int(self.HEIGHT)]
        self.mapsprite.rect.x = -camerax
        self.mapsprite.rect.y = -cameray
        self.screen.blit(self.mapsprite.image, self.mapsprite.rect)


class Menu:
    def __init__(self, WIDTH, HEIGHT, game, screen, FPS):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.game = game
        self.screen = screen
        self.FPS = FPS
        self.characters = [Human(WIDTH, HEIGHT, game, screen, FPS), Not_Gaster(WIDTH, HEIGHT, game, screen, FPS)]
        self.pers = 1
        print('menu initialized')
        self.screen_rect = self.screen.get_rect()

        self.pers_menu = Human(WIDTH, HEIGHT, game, screen, FPS)
        self.pers_menu.rect.x = self.WIDTH + 1
        self.pers_menu.rect.centery = self.screen_rect.centery

        self.pers_tmp = Human(WIDTH, HEIGHT, game, screen, FPS)
        self.pers_tmp.rect.x = self.WIDTH + 1
        self.pers_tmp.rect.centery = self.screen_rect.centery

        self.mode = 0
        self.font_btns = pygame.font.Font(None, 30)
        self.t_play = self.font_btns.render('Играть с друзьями', False, (255, 255, 255))
        screen_rect = screen.get_rect()

        self.t_play_rect = self.t_play.get_rect()
        self.t_play_rect.center = screen_rect.center
        self.t_play_rect.y -= screen_rect.height // 5
        
        self.t_exit = self.font_btns.render('У меня нет друзей', False, (255, 255, 255))
        self.t_exit_rect = self.t_exit.get_rect()
        self.t_exit_rect.center = screen_rect.center
        self.t_exit_rect.y += screen_rect.height // 5

        self.t_start = self.font_btns.render('ИГРАТЬ', False, (0, 0, 255))
        self.t_start_rect = self.t_start.get_rect()
        self.t_start_rect.center = screen_rect.center
        self.t_start_rect.y += screen_rect.height // 5

        self.btn_flg = 0
        self.update_pers()

        self.thrown_flag = False

    def update(self):
        if not self.mode:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.t_play, self.t_play_rect)
            self.screen.blit(self.t_exit, self.t_exit_rect)
        else:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.image_pers, self.image_pers_rect)
            self.screen.blit(self.pers_name, self.pers_name_rect)
            self.screen.blit(self.arrow_left, self.arrow_left_rect)
            self.screen.blit(self.arrow_right, self.arrow_right_rect)
            self.screen.blit(self.pers_menu.image, self.pers_menu.rect)
            self.screen.blit(self.pers_tmp.image, self.pers_tmp.rect)
            if self.pers_menu.rect.centerx > self.WIDTH // 2:
                self.pers_menu.rect.centerx -= 10
            if self.thrown_flag:
                self.pers_menu.rect.y -= 50
                if self.pers_tmp.rect.centerx > self.WIDTH // 2:
                    self.pers_tmp.rect.centerx -= 10
                else:
                    self.thrown_flag = False
                    self.pers_menu.rect.x = self.pers_tmp.rect.x
                    self.pers_menu.rect.centery = self.screen_rect.centery
                    self.pers_tmp.rect.x = self.WIDTH + 1
        
        return self.check_buttons(), self.pers_menu


    def check_buttons(self):
        mouse = pygame.mouse.get_pos()
        pressed_mouse = pygame.mouse.get_pressed()[0]
        if pressed_mouse:
            if self.btn_flg:
                pressed_mouse = 0
            else:
                self.btn_flg = 1
        else:
            self.btn_flg = 0
        if not self.mode:
            if self.t_play_rect.x < mouse[0] < self.t_play_rect.right and self.t_play_rect.y < mouse[1] < self.t_play_rect.bottom:
                self.t_play = self.font_btns.render('ИГРАТЬ C ДРУЗЬЯМИ', False, (255, 0, 0))
                if pressed_mouse:
                    self.mode += 1
                return self.mode
            elif self.t_exit_rect.x < mouse[0] < self.t_exit_rect.right and self.t_exit_rect.y < mouse[1] < self.t_exit_rect.bottom:
                self.t_exit = self.font_btns.render('У МЕНЯ НЕТ ДРУЗЕЙ', False, (255, 0, 0))
                if pressed_mouse:
                    exit(0)
            else:
                self.t_play = self.font_btns.render('ИГРАТЬ С ДРУЗЬЯМИ', False, (255, 255, 255))
                self.t_exit = self.font_btns.render('У МЕНЯ НЕТ ДРУЗЕЙ', False, (255, 255, 255))
        elif self.mode == 1:
            if self.arrow_left_rect.x < mouse[0] < self.arrow_left_rect.right and self.arrow_left_rect.y < mouse[1] < self.arrow_left_rect.bottom:
                self.arrow_left = self.font_btns.render('<', False, (255, 0, 0))
                if pressed_mouse:
                    self.change_pers(-1)
                    
            elif self.arrow_right_rect.x < mouse[0] < self.arrow_right_rect.right and self.arrow_right_rect.y < mouse[1] < self.arrow_right_rect.bottom:
                self.arrow_right = self.font_btns.render('>', False, (255, 0, 0))
                if pressed_mouse:
                    self.change_pers(1)
            elif self.pers_name_rect.x < mouse[0] < self.pers_name_rect.right and self.pers_name_rect.y < mouse[1] < self.pers_name_rect.bottom:
                self.pers_name = self.font_btns.render(self.characters[self.pers].name, False, (255, 0, 0))
                if pressed_mouse:
                    self.mode = 3
            else:
                self.arrow_left = self.font_btns.render('<', False, (255, 255, 255))
                self.arrow_right = self.font_btns.render('>', False, (255, 255, 255))
                self.pers_name = self.font_btns.render(self.characters[self.pers].name, False, (255, 255, 255))
        return self.mode
    
    def change_pers(self, n):
        self.thrown_flag = True
        self.pers += n
        self.pers %= len(self.characters)
        self.update_pers()

    def update_pers(self):
        path = os.path.join(os.path.dirname(__file__), 'Assets')
        path = os.path.join(path, 'Sprites')
        
        self.pers_menu = self.characters[self.pers]
        self.pers_menu.rect.x = self.WIDTH + 1
        self.pers_menu.rect.centery = self.screen_rect.centery

        self.image_pers = pygame.image.load(os.path.join(path, self.pers_menu.pic)).convert()
        self.image_pers = pygame.transform.scale(self.image_pers, (self.HEIGHT // 5, self.HEIGHT // 5))
        self.image_pers_rect = self.image_pers.get_rect()
        self.image_pers_rect.centerx = self.screen_rect.centerx
        self.image_pers_rect.centery = self.screen_rect.centery - self.WIDTH // 6

        self.pers_name = self.font_btns.render(self.characters[self.pers].name, False, (255, 255, 255))
        self.pers_name_rect = self.pers_name.get_rect()
        self.pers_name_rect.centerx = self.image_pers_rect.centerx
        self.pers_name_bottomy = self.image_pers_rect.y - self.WIDTH // 20

        self.arrow_left = self.font_btns.render('<', False, (255, 255, 255))
        self.arrow_left_rect = self.arrow_left.get_rect()
        self.arrow_left_rect.right = self.pers_name_rect.x - self.WIDTH // 25
        self.arrow_left_rect.centery = self.pers_name_rect.centery

        self.arrow_right = self.font_btns.render('>', False, (255, 255, 255))
        self.arrow_right_rect = self.arrow_right.get_rect()
        self.arrow_right_rect.x = self.pers_name_rect.right + self.WIDTH // 25
        self.arrow_right_rect.centery = self.pers_name_rect.centery


class Camera:
    def __init__(self, WIDTH, HEIGHT, game):
        self.cam_x = 0
        self.cam_y = 0
        self.game = game
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

        print('camera initialized')

    def update(self):
        # self.cam_x = int(len(game.map.hitboxes) - self.WIDTH)
        # self.cam_y = int(len(game.map.hitboxes[0]) - self.HEIGHT)
        # print(self.cam_x, self.cam_y)
        ...

    def set(self, x, y):
        ans = [0, 0]
        if x >= self.game.map.size[0] - self.WIDTH:
            print('horizontal border ->')
            ans[0] = 1
        if x < 0:
            print('horizontal border <-')
            ans[0] = -1
        if ans[0] == 0:
            self.cam_x = x
        if y >= self.game.map.size[1] - self.HEIGHT:
            print('vertical border ->')
            ans[1] = 1
        if y < 0:
            print('vertical border <-')
            ans[1] = -1
        if ans[1] == 0:
            self.cam_y = y
        return ans

    def move(self, x, y):
        ans = [0, 0]
        if x >= self.game.map.size[0] - self.WIDTH:
            print('horizontal border')
            ans[0] = 1
        else:
            self.cam_x += x
        if y >= self.game.map.size[1] - self.HEIGHT:
            print('vertical border')
            ans[1] = 1
        else:
            self.cam_y += y

        return ans
        ...
