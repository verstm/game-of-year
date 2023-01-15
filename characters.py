import pygame
import os
from math import sin, cos, acos, hypot
import time
import random

ASSETS_PATH = 'Assets/'
G = 1
controls = [[pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_a, pygame.K_SPACE, pygame.KMOD_SHIFT, pygame.K_q, pygame.K_w,
             pygame.K_e, pygame.K_r]]
DEBUG = True


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, image, parent, width=None, height=None):
        path = os.path.join(os.path.dirname(__file__), 'Assets')
        path = os.path.join(path, 'Sprites')
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(path, image))
        if width:
            self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.parent = parent

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y


class Pawn:
    def __init__(self, WIDTH, HEIGHT, game, screen, FPS):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.game = game
        self.screen = screen
        self.FPS = FPS
        self.keys = []
        self.mouse_arr = (False, False, False)
        self.alpha = None
        self.truecords = (self.WIDTH // 2, self.HEIGHT // 2)
        self.x, self.y = 0, 0
        pygame.sprite.Sprite.__init__(self)
        self.group = pygame.sprite.Group()
        self.group.add(self)
        self.combo = []
        self.last_combo_time = time.time()
        self.mouse_was_pressed = 0
        self.animation_counter = [0, 1]
        self.default_animation = None
        self.current_animation = None
        self.maxHP = 1000
        self.main_chr = 1
        self.HP = self.maxHP
        self.controls_num = 0
        self.animframes_divisor = 1
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.last_direction = 1
        self.jump_power = 3
        self.grav_accel = G
        self.onfloor = 0
        # self.jump_cooldown =
        self.jumpflg = 0
        self.lascoords = (None, None)
        self.cam_xlock, self.cam_ylock = 0, 0
        self.xcamflg, self.ycamflg = 0, 0
        self.left, self.right, self.top, self.bottom = 0, 0, 0, 0
        self.cd = {self.mouse: 0}
        self.maxcd = {self.mouse: self.FPS // 4}
        self.stun_cnt = 0
        self.hang_cnt = 0
        self.objectgroup = pygame.sprite.Group()

    def init_pers(self):
        animpath_run = ASSETS_PATH + 'Sprites/Animations/running_1/'
        animpath_atk = ASSETS_PATH + 'sprites/Animations/attacking/'
        self.image = pygame.image.load(ASSETS_PATH + 'Sprites/Static/Human/idle1.png')
        self.idle_right = [pygame.image.load(ASSETS_PATH + 'Sprites/Static/Human/idle1.png')]
        self.idle_left = list(map(lambda i: pygame.transform.flip(i, True, False), self.idle_right))
        self.default_animation = lambda: self.idle_right if self.last_direction else self.idle_left
        self.current_animation = self.default_animation()
        self.rect = self.image.get_rect()
        self.runanimation_right = [pygame.image.load(animpath_run + f'{i}.png') for i in range(1, 7)]
        self.runanimation_left = list(map(lambda i: pygame.transform.flip(i, True, False), self.runanimation_right))
        self.stoppinganimation_right = [pygame.image.load(ASSETS_PATH + 'Sprites/stopping.png')]
        self.stoppinganimation_left = list(
            map(lambda i: pygame.transform.flip(i, True, False), self.stoppinganimation_right))
        self.combo1_1_right = [pygame.image.load(ASSETS_PATH + f'Sprites/Animations/combo_1_1/{i}.png') for i in
                               range(1, len(list(os.walk(ASSETS_PATH + f'Sprites/Animations/combo_1_1/'))[0][2]) + 1)]
        self.combo1_2_right = [pygame.image.load(ASSETS_PATH + f'Sprites/Animations/combo_1_2/{i}.png') for i in
                               range(1, len(list(os.walk(ASSETS_PATH + f'Sprites/Animations/combo_1_2/'))[0][2]) + 1)]
        self.combo1_3_right = [pygame.image.load(ASSETS_PATH + f'Sprites/Animations/combo_1_3/{i}.png') for i in
                               range(1, len(list(os.walk(ASSETS_PATH + f'Sprites/Animations/combo_1_3/'))[0][2]) + 1)]
        self.combo1_4_right = [pygame.image.load(ASSETS_PATH + f'Sprites/Animations/combo_1_4/{i}.png') for i in
                               range(1, len(list(os.walk(ASSETS_PATH + f'Sprites/Animations/combo_1_4/'))[0][2]) + 1)]
        self.combo1_1_left = list(map(lambda i: pygame.transform.flip(i, True, False), self.combo1_1_right))
        self.combo1_2_left = list(map(lambda i: pygame.transform.flip(i, True, False), self.combo1_2_right))
        self.combo1_3_left = list(map(lambda i: pygame.transform.flip(i, True, False), self.combo1_3_right))
        self.combo1_4_left = list(map(lambda i: pygame.transform.flip(i, True, False), self.combo1_4_right))
        self.combocd = [0.2]
        self.animation_counter = [0, 0]
        self.moves = []
        self.pic = 'Human.png'
        self.name = 'Human'
        self.combo_expiration = 1
        self.info = [self.HP, self.maxHP, self.name, self.pic, self.animation_counter, self.vertical_speed,
                     self.horizontal_speed, self.x, self.y, self.keys, self.mouse_arr, self.alpha]
        self.enemy = ''
        self.combo_info = {'1': [15, 15, 15, 10], '11': [15, 15, 15, 10], '111': [30, 15, 15, 15],
                           '1111': [15, 15, 0, 20], '-1': [15, 15, 15, 10], '-1-1': [15, 15, 15, 10],
                           '-1-1-1': [30, 15, 15, 15],
                           '-1-1-1-1': [15, 15, 0, 20]}
        self.enemygroup = ''

    def move(self, x, y):
        # print(x, y)
        camerax, cameray = self.game.camera.cam_x, self.game.camera.cam_y
        x2 = self.rect.x
        y2 = self.rect.y
        w = self.rect.w
        h = self.rect.h
        b = self.rect.bottom
        t = self.rect.top
        lastx, lasty = 0, 0
        area = self.game.map.hitboxes
        # print(area[self.rect.x, self.rect.y]) if area[self.rect.x, self.rect.y] else 0
        self.left, self.right, self.top, self.bottom = False, False, False, False
        for j in range(1, abs(x) + 1):
            if x2 - j <= 0:
                self.left = True
            elif x2 + w + j >= self.WIDTH:
                self.right = True
            else:
                if not self.left:
                    self.left = all([area[camerax + x2 - j, cameray + i] for i in range(y2, y2 + h)])
                if not self.right:
                    self.right = all([area[camerax + x2 + w + j, cameray + i] for i in range(y2, y2 + h)])

            if self.left:
                lastx = -j + 1
                break
            if self.right:
                lastx = j - 1
                break

        for j in range(1, abs(y) + 1):
            if y2 - j <= 0:
                self.top = True
            if y2 + h + j >= self.HEIGHT:
                self.bottom = True
            else:
                if not self.top:
                    self.top = all([area[camerax + i, cameray + y2 - j] for i in range(x2, x2 + w)])
                if not self.bottom:
                    self.bottom = all([area[camerax + i, cameray + y2 + h + j] for i in range(x2, x2 + w)])
                flg = 1
            if self.top:
                lasty = -j + 1
                break
            if self.bottom:
                lasty = j - 1
                break

        if ((x < 0 and not self.left) or (x > 0 and not self.right)) and self.WIDTH > self.rect.x + x > 0:
            self.x += x
        else:
            self.x += lastx

        if ((y < 0 and not self.top) or (y > 0 and not self.bottom)) and self.HEIGHT > self.rect.y + y > 0:
            self.y += y
        else:
            self.y += lasty

    def cam_targeting(self, main):
        tx, ty = self.truecords
        if main:
            r1, r2 = self.game.camera.cam_x if self.xcamflg else self.x, self.game.camera.cam_y if self.ycamflg else self.y
            x = self.game.camera.set(r1, r2)
            camx, camy = self.game.camera.cam_x, self.game.camera.cam_y
            if x[0] == 1 or self.rect.x > tx + abs(self.horizontal_speed):
                self.xcamflg = 1
                self.rect.x = self.x - camx + tx
            elif x[0] == -1 or self.rect.x < tx - abs(self.horizontal_speed):
                self.xcamflg = -1
                self.rect.x = self.x - camx + tx
            else:
                self.xcamflg = 0
                # self.rect.x = tx
            if x[1] == 1 or self.rect.y > ty + abs(self.vertical_speed):
                self.ycamflg = 1
                self.rect.y = self.y - camy + ty
            elif x[1] == -1 or self.rect.y < ty - abs(self.vertical_speed):
                self.ycamflg = -1
                self.rect.y = self.y - camy + ty
            else:
                self.ycamflg = 0
                # self.rect.y = ty
        else:
            camx, camy = self.game.camera.cam_x, self.game.camera.cam_y
            self.rect.x = self.x - camx + tx
            self.rect.y = self.y - camy + ty

    def events_check(self):
        keyboard = pygame.key.get_pressed()
        keys = []
        mouse = pygame.mouse.get_pressed()
        if keyboard[pygame.K_g]:
            self.knockback(150, 14)
        for i in range(len(controls[self.controls_num])):
            x = controls[self.controls_num][i]
            if keyboard[x]:
                keys.append(i)
        self.keys = keys
        self.mouse_arr = mouse
        # self.control(keys, mouse)

    def physics(self):
        if self.horizontal_speed < 0:
            self.last_direction = 0
        if self.horizontal_speed > 0:
            self.last_direction = 1
        self.move(int(self.horizontal_speed), int(self.vertical_speed))
        self.onfloor = self.bottom
        if self.onfloor:
            self.grav_accel = G
            self.vertical_speed = 0
            self.horizontal_speed += (-self.horizontal_speed) / 5
        else:
            # self.grav_accel += G
            self.vertical_speed += self.grav_accel
        self.horizontal_speed = 0 if abs(self.horizontal_speed) < 1 else self.horizontal_speed
        self.vertical_speed = 0 if abs(self.vertical_speed) < 1 else self.vertical_speed
        if self.hang_cnt:
            self.vertical_speed = 0
            self.horizontal_speed = 0
            self.hang_cnt -= 1

    def animation_update(self):
        animlen = len(self.current_animation)
        if self.animation_counter[0] / self.animframes_divisor < animlen:
            self.image = self.current_animation[int(self.animation_counter[0] / self.animframes_divisor)]
            self.animation_counter[0] += 1
        else:
            if self.animation_counter[1]:
                self.animation_counter[0] = 0
            else:
                self.current_animation = self.default_animation()
                self.animation_counter[0] = 0
                self.animframes_divisor = 1

    def set_animation(self, animation, loop=True, div=1):
        if self.current_animation != animation:
            self.animframes_divisor = div
            self.current_animation = animation
            self.animation_counter[0] = 0
            if loop:
                self.animation_counter[1] = 1
            else:
                self.animation_counter[1] = 0

    def knockback(self, alpha, velocity):
        if not self.onfloor:
            velocity /= 3
        self.vertical_speed -= velocity * sin(alpha / 57.3)
        self.horizontal_speed += velocity * cos(alpha / 57.3)

    def update_cd(self):

        for key in self.cd.keys():
            if self.cd[key] != 0:
                if self.cd[key] < self.maxcd[key]:
                    self.cd[key] += 1
                else:
                    self.cd[key] = 0

    def mouse(self, alpha):
        self.enemy.stun_cnt = max(30, self.enemy.stun_cnt)
        self.enemy.hang_cnt = max(30, self.enemy.hang_cnt)
        self.cd[self.mouse] = 1
        if alpha > 340 or alpha <= 20:
            self.combo.append(1)
        elif alpha > 20 and alpha <= 90:
            self.combo.append(-3)
        elif alpha > 90 and alpha <= 160:
            self.combo.append(-2)
        elif alpha > 160 and alpha <= 200:
            self.combo.append(-1)
        elif alpha > 200 and alpha <= 270:
            self.combo.append(3)
        elif alpha > 270 and alpha <= 340:
            self.combo.append(2)
        self.attack()

    def attack_hitbox(self, x1, y1, x2, y2):
        self.atk_hitbox = pygame.sprite.Sprite()
        self.atk_hitbox.image = pygame.Surface((max(x1, x2) - min(x1, x2), max(y1, y2) - min(y1, y2)))
        self.atk_hitbox.rect = self.atk_hitbox.image.get_rect()
        self.atk_hitbox.rect.x = x2 if x1 > x2 else x1
        self.atk_hitbox.rect.y = y2 if y1 > y2 else y1
        if DEBUG:
            self.atk_hitbox.image.fill((255, 0, 0))
            self.screen.blit(self.atk_hitbox.image, self.atk_hitbox.rect)
        hits = pygame.sprite.spritecollide(self.atk_hitbox, self.enemygroup, False)
        return hits


class Human(Pawn, pygame.sprite.Sprite):
    def __init__(self, WIDTH, HEIGHT, game, screen, FPS):
        super().__init__(WIDTH, HEIGHT, game, screen, FPS)
        self.init_pers()

    def update(self):
        if self.main_chr:
            self.events_check()
        self.control(self.keys, self.mouse_arr)
        '''if not self.main_chr:
            print(self.alpha)'''
        if self.alpha != None:
            self.mouse(self.alpha)
        self.cam_targeting(self.main_chr)

        self.physics()
        # self.rect.x, self.rect.y = self.x, self.y
        self.animation_update()
        self.group.draw(self.screen)
        self.info = [self.HP, self.maxHP, self.name, self.pic, self.animation_counter, self.vertical_speed,
                     self.horizontal_speed, self.x, self.y, self.keys, self.mouse_arr, self.alpha]

        self.update_cd()

    def control(self, keys, mouse):
        global flg
        speed = 3
        right, left = 1, 3
        if self.current_animation == self.runanimation_right and not right in keys:
            self.set_animation(self.stoppinganimation_right, True)
        if self.current_animation == self.runanimation_left and not left in keys:
            self.set_animation(self.stoppinganimation_left, True)
        if self.horizontal_speed == 0 and (
                self.current_animation == self.stoppinganimation_right or self.current_animation == self.stoppinganimation_left):
            if self.last_direction == 1:
                self.set_animation(self.idle_right, True)
            else:
                self.set_animation(self.idle_left, True)
        if not self.stun_cnt:
            if 0 in keys:
                ...
                # self.move(0, -speed)
            if 2 in keys:
                ...
                # self.move(0, speed)
            if right in keys and self.bottom:
                self.horizontal_speed += speed
                self.set_animation(self.runanimation_right)
                # self.move(speed, 0)
            if left in keys and self.bottom:
                self.horizontal_speed -= speed
                self.set_animation(self.runanimation_left)
                # self.move(-speed, 0)

            if 4 in keys and (self.jumpflg or self.bottom) and self.vertical_speed > -15:
                self.jumpflg = 1
                self.vertical_speed += -self.jump_power
            else:
                self.jumpflg = 0

            if mouse[0] and self.cd[self.mouse] == 0 and not self.mouse_was_pressed:
                self.mouse_was_pressed = 1
                pos = pygame.mouse.get_pos()
                x = pos[0] - int(self.WIDTH // 2)
                y = int(self.HEIGHT // 2) - pos[1]
                sinalpha = y / hypot(x, y)
                cosalpha = x / hypot(x, y)
                if sinalpha < 0:
                    cosalpha = -cosalpha
                alpha = acos(cosalpha) * 57.3
                if sinalpha < 0:
                    alpha += 180
                self.alpha = alpha
            elif not mouse[0]:
                print('none alpha')
                self.alpha = None
                self.mouse_was_pressed = 0
        else:
            self.stun_cnt -= 1

    def debug_stun(self):
        self.stun_cnt = max(30, self.stun_cnt)
        self.hang_cnt = max(30, self.hang_cnt)

    def attack(self):
        rng = 10
        if time.time() - self.last_combo_time >= self.combo_expiration:
            self.combo = [self.combo[-1]]
        if time.time() - self.last_combo_time >= self.combocd[0]:
            if self.combo == [1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x + (self.rect.width) + rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['1'][0]
                    i.hang_cnt = self.combo_info['1'][2]
                    i.HP -= self.combo_info['1'][3]
                self.set_animation(self.combo1_1_right, False, 0.5)
                print(ht)
            elif self.combo == [1, 1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x + (self.rect.width) + rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['11'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['11'][0]
                    i.hang_cnt = self.combo_info['11'][2]
                    i.HP -= self.combo_info['11'][3]

                self.set_animation(self.combo1_2_right, False, 0.5)
            elif self.combo == [1, 1, 1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x + (self.rect.width) + rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['111'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['111'][0]
                    i.hang_cnt = self.combo_info['111'][2]
                    i.HP -= self.combo_info['111'][3]

                self.set_animation(self.combo1_3_right, False, 0.5)
            elif self.combo == [1, 1, 1, 1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x + (self.rect.width) + rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['1111'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['1111'][0]
                    i.hang_cnt = self.combo_info['1111'][2]
                    i.HP -= self.combo_info['1111'][3]
                    i.knockback(45, 150)
                self.set_animation(self.combo1_4_right, False, 0.5)
                self.combo = []
            elif self.combo == [-1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x - rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['-1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['-1'][0]
                    i.hang_cnt = self.combo_info['-1'][2]
                    i.HP -= self.combo_info['-1'][3]
                self.set_animation(self.combo1_1_left, False, 0.5)
                print(ht)
            elif self.combo == [-1, -1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x - rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['-1-1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['-1-1'][0]
                    i.hang_cnt = self.combo_info['-1-1'][2]
                    i.HP -= self.combo_info['-1-1'][3]

                self.set_animation(self.combo1_2_left, False, 0.5)
            elif self.combo == [-1, -1, -1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x - rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['-1-1-1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['-1-1-1'][0]
                    i.hang_cnt = self.combo_info['-1-1-1'][2]
                    i.HP -= self.combo_info['-1-1-1'][3]

                self.set_animation(self.combo1_3_left, False, 0.5)
            elif self.combo == [-1, -1, -1, -1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x - rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['-1-1-1-1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['-1-1-1-1'][0]
                    i.hang_cnt = self.combo_info['-1-1-1-1'][2]
                    i.HP -= self.combo_info['-1-1-1-1'][3]
                    i.knockback(180 - 45, 150)
                self.set_animation(self.combo1_4_left, False, 0.5)
                self.combo = []
            else:
                self.combo = []
            self.last_combo_time = time.time()
        else:
            self.combo.pop(-1)


class Not_Gaster(Pawn, pygame.sprite.Sprite):
    def __init__(self, WIDTH, HEIGHT, game, screen, FPS):
        super().__init__(WIDTH, HEIGHT, game, screen, FPS)
        self.init_pers()
        self.name = 'Gaster'
        self.pic = 'gaster.png'
        self.cd[self.gblaster] = 0
        self.maxcd[self.gblaster] = 90 + self.FPS * 3
        self.flag_restrict_movement = False
        self.cd[self.pellets] = 0
        self.maxcd[self.pellets] = 300
        self.cd[self.explosive_pellets] = 0
        self.maxcd[self.explosive_pellets] = 52 + 180
        self.cd[self.rope] = 0
        self.maxcd[self.rope] = 240
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.game = game
        self.screen = screen
        self.FPS = FPS

    def control(self, keys, mouse):
        global flg
        speed = 3
        right, left = 1, 3
        if self.current_animation == self.runanimation_right and not right in keys:
            self.set_animation(self.stoppinganimation_right, True)
        if self.current_animation == self.runanimation_left and not left in keys:
            self.set_animation(self.stoppinganimation_left, True)
        if self.horizontal_speed == 0 and (
                self.current_animation == self.stoppinganimation_right or self.current_animation == self.stoppinganimation_left):
            if self.last_direction == 1:
                self.set_animation(self.idle_right, True)
            else:
                self.set_animation(self.idle_left, True)
        if not self.stun_cnt:
            if 0 in keys:
                ...
                # self.move(0, -speed)
            if 2 in keys:
                ...
                # self.move(0, speed)
            if right in keys and self.bottom:
                self.horizontal_speed += speed
                self.set_animation(self.runanimation_right)
                # self.move(speed, 0)
            if left in keys and self.bottom:
                self.horizontal_speed -= speed
                self.set_animation(self.runanimation_left)
                # self.move(-speed, 0)

            if 4 in keys and (self.jumpflg or self.bottom) and self.vertical_speed > -15:
                self.jumpflg = 1
                self.vertical_speed += -self.jump_power
            else:
                self.jumpflg = 0

            if mouse[0] and self.cd[self.mouse] == 0 and not self.mouse_was_pressed:
                self.mouse_was_pressed = 1
                pos = pygame.mouse.get_pos()
                x = pos[0] - int(self.WIDTH // 2)
                y = int(self.HEIGHT // 2) - pos[1]
                sinalpha = y / hypot(x, y)
                cosalpha = x / hypot(x, y)
                if sinalpha < 0:
                    cosalpha = -cosalpha
                alpha = acos(cosalpha) * 57.3
                if sinalpha < 0:
                    alpha += 180
                self.alpha = alpha
            elif not mouse[0]:
                print('none alpha')
                self.alpha = None
                self.mouse_was_pressed = 0
        else:
            self.stun_cnt -= 1

    def update(self):
        if self.main_chr:
            self.events_check()
        self.control(self.keys, self.mouse_arr)
        '''if not self.main_chr:
            print(self.alpha)'''
        if self.alpha != None:
            self.mouse(self.alpha)
        self.cam_targeting(self.main_chr)

        self.physics()
        # self.rect.x, self.rect.y = self.x, self.y
        self.animation_update()
        self.group.draw(self.screen)
        self.info = [self.HP, self.maxHP, self.name, self.pic, self.animation_counter, self.vertical_speed,
                     self.horizontal_speed, self.x, self.y, self.keys, self.mouse_arr, self.alpha]

        self.update_cd()

    def attack(self):
        rng = 10
        if time.time() - self.last_combo_time >= self.combo_expiration:
            self.combo = [self.combo[-1]]
        if time.time() - self.last_combo_time >= self.combocd[0]:
            if self.combo == [1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x + (self.rect.width) + rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['1'][0]
                    i.hang_cnt = self.combo_info['1'][2]
                    i.HP -= self.combo_info['1'][3]
                self.set_animation(self.combo1_1_right, False, 0.5)
                print(ht)
            elif self.combo == [1, 1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x + (self.rect.width) + rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['11'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['11'][0]
                    i.hang_cnt = self.combo_info['11'][2]
                    i.HP -= self.combo_info['11'][3]

                self.set_animation(self.combo1_2_right, False, 0.5)
            elif self.combo == [1, 1, 1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x + (self.rect.width) + rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['111'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['111'][0]
                    i.hang_cnt = self.combo_info['111'][2]
                    i.HP -= self.combo_info['111'][3]

                self.set_animation(self.combo1_3_right, False, 0.5)
            elif self.combo == [1, 1, 1, 1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x + (self.rect.width) + rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['1111'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['1111'][0]
                    i.hang_cnt = self.combo_info['1111'][2]
                    i.HP -= self.combo_info['1111'][3]
                    i.knockback(45, 150)
                self.set_animation(self.combo1_4_right, False, 0.5)
                self.combo = []
            elif self.combo == [-1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x - rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['-1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['-1'][0]
                    i.hang_cnt = self.combo_info['-1'][2]
                    i.HP -= self.combo_info['-1'][3]
                self.set_animation(self.combo1_1_left, False, 0.5)
                print(ht)
            elif self.combo == [-1, -1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x - rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['-1-1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['-1-1'][0]
                    i.hang_cnt = self.combo_info['-1-1'][2]
                    i.HP -= self.combo_info['-1-1'][3]

                self.set_animation(self.combo1_2_left, False, 0.5)
            elif self.combo == [-1, -1, -1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x - rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['-1-1-1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['-1-1-1'][0]
                    i.hang_cnt = self.combo_info['-1-1-1'][2]
                    i.HP -= self.combo_info['-1-1-1'][3]

                self.set_animation(self.combo1_3_left, False, 0.5)
            elif self.combo == [-1, -1, -1, -1]:
                ht = self.attack_hitbox(self.rect.x + (self.rect.width // 2), self.rect.y,
                                        self.rect.x - rng,
                                        self.rect.y + self.rect.width)
                self.hang_cnt = self.combo_info['-1-1-1-1'][1]
                for i in ht:
                    i.stun_cnt = self.combo_info['-1-1-1-1'][0]
                    i.hang_cnt = self.combo_info['-1-1-1-1'][2]
                    i.HP -= self.combo_info['-1-1-1-1'][3]
                    i.knockback(180 - 45, 150)
                self.set_animation(self.combo1_4_left, False, 0.5)
                self.combo = []
            else:
                self.combo = []
            self.last_combo_time = time.time()
        else:
            self.combo.pop(-1)

    def gblaster(self):
        self.flag_restrict_movement = True
        if self.last_direction:
            self.blaster = Blaster(self.rect.x + self.rect.width // 3, self.rect.y + self.rect.height // 3, self,
                                   'right', self.screen)
        else:
            self.blaster = Blaster(self.rect.x - self.rect.width // 3 - 41, self.rect.y + self.rect.height // 3, self,
                                   'left', self.screen)
        self.objectgroup.add(self.blaster)
        self.cd[self.gblaster] = 1

    def pellets(self):
        for i in range(15):
            x = random.randint(self.rect.x - self.rect.width * 2, self.rect.x + self.rect.width * 2)
            y = random.randint(self.HEIGHT // 3, self.HEIGHT // 3 * 2)
            self.objectgroup.add(Pellet(x, y, self, self.WIDTH, self.HEIGHT))
        self.cd[self.pellets] = 1

    def explosive_pellets(self):
        for i in range(4):
            x = random.randint(self.rect.x - self.rect.width // 2, self.rect.x)
            y = random.randint(self.rect.y + self.rect.height // 3, self.rect.y + self.rect.height // 1.5)
            self.objectgroup.add(Explosive_Pellet(x, y, self))
        for i in range(4):
            x = random.randint(self.rect.right, self.rect.right + self.rect.width // 2)
            y = random.randint(self.rect.y + self.rect.height // 3, self.rect.y + self.rect.height // 1.5)
            self.objectgroup.add(Explosive_Pellet(x, y, self))
        self.flag_restrict_movement = True
        self.cd[self.explosive_pellets] = 1

    def rope(self):
        if self.last_direction:
            self.objectgroup.add(Rope(self.rect.right, self.rect.y + self.rect.height // 3, self, self.last_direction))
        else:
            self.objectgroup.add(Rope(self.rect.x, self.rect.y + self.rect.height // 3, self, self.last_direction))
        self.cd[self.rope] = 1


class Blaster(Object, pygame.sprite.Sprite):
    def __init__(self, x, y, parent, direction, screen):
        pygame.sprite.Sprite.__init__(self)
        Object.__init__(self, x, y, f'blaster_{direction}.png', parent)
        self.flag_attacking = False
        self.direction = 1 if direction == 'right' else 0
        self.cnt = 0
        self.idle_max = 30
        self.shoot_max = 90
        self.screen = screen

        self.ray = pygame.sprite.Sprite()
        self.ray.image = pygame.Surface((2000, 30))
        self.ray.image.fill((255, 0, 0))
        self.ray.rect = self.ray.image.get_rect()
        if self.direction == 1:
            self.rect.x += self.parent.rect.width
            self.ray.rect.x = self.rect.x + 5
        else:
            self.ray.rect.right = self.rect.x - 5
        self.ray.rect.centery = self.rect.centery

    def update(self):
        if self.cnt < self.shoot_max:
            self.cnt += 1
            if self.cnt >= self.idle_max:
                self.screen.blit(self.ray.image, self.ray.rect)
                for hit in pygame.sprite.spritecollide(self.ray, self.parent.enemygroup, False):
                    try:
                        hit.HP -= 10
                    except Exception as e:
                        pass
        else:
            self.cnt = 0
            self.parent.flag_restrict_movement = False
            self.parent.objectgroup.remove(self)


class Pellet(Object, pygame.sprite.Sprite):
    def __init__(self, x, y, parent, WIDTH, HEIGHT):
        super().__init__(x, y, 'yellow.png', parent, 15, 15)
        rx = self.parent.enemy.rect.centerx - self.rect.centerx
        ry = self.rect.centery - (self.parent.rect.y + self.parent.enemy.rect.centery) / 2
        self.cos = cos(rx / hypot(rx, ry))
        if rx < 0: self.cos = -self.cos
        self.sin = sin(ry / hypot(ry, rx))
        if ry < 0: self.sin = -self.sin
        self.speed = 30
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def update(self):
        self.move(self.speed * self.cos, self.speed * self.sin)
        for hit in pygame.sprite.spritecollide(self, self.parent.enemygroup, False):
            try:
                hit.HP -= 10
                self.parent.objectgroup.remove(self)
            except Exception as e:
                pass
        if not (0 < self.rect.x < self.WIDTH and 0 < self.rect.y < self.HEIGHT):
            self.parent.objectgroup.remove(self)


class Explosive_Pellet(Object, pygame.sprite.Sprite):
    def __init__(self, x, y, parent):
        super().__init__(x, y, 'orange.png', parent, 15, 15)
        self.cnt = 0
        self.cnt_idle = 20
        self.cnt_max = 35
        path = os.path.join(os.path.dirname(__file__), 'Assets')
        path = os.path.join(path, 'Sprites')
        path = os.path.join(path, 'Animations')
        self.path = os.path.join(path, 'explosion')

    def update(self):
        if self.cnt < self.cnt_max:
            self.cnt += 1
            if self.cnt > self.cnt_idle:
                cnt2 = (self.cnt - self.cnt_idle) // 2
                print(cnt2)
                x, y = self.rect.center
                self.image = pygame.image.load(os.path.join(self.path, f'_{cnt2}.png'))
                self.rect = self.image.get_rect()
                self.rect.centerx = x
                self.rect.centery = y
                for hit in pygame.sprite.spritecollide(self, self.parent.enemygroup, False):
                    try:
                        hit.HP -= 10
                        hit.knockback(90, 4)
                    except Exception as e:
                        pass
        else:
            self.cnt = 0
            self.parent.objectgroup.remove(self)
            self.parent.flag_restrict_movement = False

class Rope(Object, pygame.sprite.Sprite):
    def __init__(self, x, y, parent, direction):
        super().__init__(x, y, 'rope.png', parent)
        path = os.path.join(os.path.dirname(__file__), 'Assets')
        self.path = os.path.join(path, 'Sprites')
        self.needed_width = 10
        self.len = 20
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(self.path, 'rope.png')), (self.len, self.needed_width))
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.parent = parent
        self.direction = direction
        if self.direction:
            self.rect.x = x
        else:
            self.rect.right = x
        self.speed = 40
        self.hit = False
        self.max_len = 2 * self.parent.rect.width
    def update(self):
        if self.len < self.max_len:
            if self.direction:
                if not self.hit:
                    x = self.rect.x
                    y = self.rect.y
                    self.image = pygame.transform.scale(pygame.image.load(os.path.join(self.path, 'rope.png')), (self.len, self.needed_width))
                    self.rect = self.image.get_rect()
                    self.len += self.speed
                    self.rect.x = x
                    self.rect.y = y
                    for hit in pygame.sprite.spritecollide(self, self.parent.enemygroup, False):
                        try:
                            hit.HP -= 10
                            self.hit = True
                        except Exception as e:
                            pass
                else:
                    self.max_len = self.parent.rect.width * 5
                    self.parent.enemy.image = pygame.image.load(os.path.join(self.path, 'bdsm_right.png'))
                    self.parent.enemy.move(self.speed, 0)
                    self.len += self.speed
                    self.image = pygame.transform.scale(pygame.image.load(os.path.join(self.path, 'rope.png')), (self.len, self.needed_width))
            else:
                if not self.hit:
                    x = self.rect.right
                    y = self.rect.y
                    self.image = pygame.transform.scale(pygame.image.load(os.path.join(self.path, 'rope.png')), (self.len, self.rect.height))
                    self.rect = self.image.get_rect()
                    self.len += self.speed
                    self.rect.right = x
                    self.rect.y = y
                    for hit in pygame.sprite.spritecollide(self, self.parent.enemygroup, False):
                        try:
                            hit.HP -= 10
                            self.hit = True
                        except Exception as e:
                            pass
                else:
                    x = self.rect.right
                    y = self.rect.y
                    self.max_len = self.parent.rect.width * 5
                    self.parent.enemy.image = pygame.image.load(os.path.join(self.path, 'bdsm_left.png'))
                    self.parent.enemy.move(-self.speed, 0)
                    self.len += self.speed
                    self.image = pygame.transform.scale(pygame.image.load(os.path.join(self.path, 'rope.png')), (self.len, self.needed_width))
                    self.rect = self.image.get_rect()
                    self.rect.right = x
                    self.rect.y = y
        else:
            self.parent.objectgroup.remove(self)
