import pygame as pg
import pygame.event
import numpy
from pygame import gfxdraw

pg.init()
true_width, true_height = pygame.display.Info().current_w, pygame.display.Info().current_h
print(true_width, true_height)
WIDTH = int(true_width * 0.8)
HEIGHT = int(true_height * 0.8)
FPS = 60
running = True
clock = pg.time.Clock()
screen = pg.display.set_mode((WIDTH, HEIGHT))
ASSETS_PATH = 'Assets/'
controls = [[pg.K_w, pg.K_d, pg.K_s, pg.K_a, pg.K_SPACE, pg.KMOD_SHIFT]]
G = 1


class Main:
    def __init__(self):
        self.map = Map()
        self.menu = Menu()
        self.gui = GUI()
        self.camera = Camera()
        self.pers = Human()
        self.mode = 0
        self.info = []

    def update(self):
        if self.mode == 0:
            self.mode = self.menu.update()
        if self.mode == 1:
            self.map.update()
            self.camera.update()
            self.pers.update()
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
        # game.camera.move(1, 1)

    def render(self):
        camerax, cameray = game.camera.cam_x, game.camera.cam_y
        self.visible_area = self.hitboxes[camerax:camerax + int(WIDTH), cameray:cameray + int(HEIGHT)]
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
        # self.cam_x = int(len(game.map.hitboxes) - WIDTH)
        # self.cam_y = int(len(game.map.hitboxes[0]) - HEIGHT)
        # print(self.cam_x, self.cam_y)
        ...

    def set(self, x, y):
        ans = [0, 0]
        if x >= game.map.size[0] - WIDTH:
            print('horizontal border ->')
            ans[0] = 1
        if x < 0:
            print('horizontal border <-')
            ans[0] = -1
        if ans[0] == 0:
            self.cam_x = x
        if y >= game.map.size[1] - HEIGHT:
            print('vertical border ->')
            ans[1] = 1
        if y < 0:
            print('vertical border <-')
            ans[1] = -1
        if ans[1] == 0:
            self.cam_y = y
        return ans

    def move(self, x, y):
        '''ans = [0, 0]
        if x >= game.map.size[0] - WIDTH:
            print('horizontal border')
            ans[0] = 1
        else:
            self.cam_x += x
        if y >= game.map.size[1] - HEIGHT:
            print('vertical border')
            ans[1] = 1
        else:
            self.cam_y += y

        return ans'''
        ...


class Object:
    def __init__(self):
        pass


class Pawn:
    def __init__(self):
        self.truecords = (WIDTH // 2, HEIGHT // 2)
        self.x, self.y = 0, 0
        pygame.sprite.Sprite.__init__(self)
        self.group = pygame.sprite.Group()
        self.group.add(self)
        self.controls_num = 0
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.jump_power = 3
        self.grav_accel = G
        self.onfloor = 0
        # self.jump_cooldown =
        self.jumpflg = 0
        self.lascoords = (None, None)
        self.cam_xlock, self.cam_ylock = 0, 0
        self.xcamflg, self.ycamflg = 0, 0
        self.left, self.right, self.top, self.bottom = 0, 0, 0, 0

    def move(self, x, y):
        # print(x, y)
        x2 = self.rect.x
        y2 = self.rect.y
        w = self.rect.w
        h = self.rect.h
        b = self.rect.bottom
        t = self.rect.top
        lastx, lasty = 0, 0
        flg = 0
        visible_area = game.map.visible_area
        # print(visible_area[self.rect.x, self.rect.y]) if visible_area[self.rect.x, self.rect.y] else 0
        for j in range(1, abs(x) + 1):
            if x2 - j <= 0:
                self.left = True
            elif x2 + w + j >= WIDTH:
                self.right = True
            else:
                self.left = all([visible_area[x2 - j, i] for i in range(y2, y2 + h)])
                self.right = all([visible_area[x2 + w + j, i] for i in range(y2, y2 + h)])

            if self.left:
                lastx = -j + 1
                break
            if self.right:
                lastx = j - 1
                break
        for j in range(1, abs(y) + 1):
            if y2 - j <= 0:
                self.top = True
            if y2 + h + j >= HEIGHT:
                self.bottom = True
            else:
                self.top = all([visible_area[i, y2 - j] for i in range(x2, x2 + w)])
                self.bottom = all([visible_area[i, y2 + h + j] for i in range(x2, x2 + w)])
                flg = 1
            if self.top:
                lasty = -j + 1
                break
            if self.bottom:
                lasty = j - 1
                break

        if ((x < 0 and not self.left) or (x >= 0 and not self.right)) and WIDTH > self.rect.x + x > 0:
            self.x += x
        else:
            self.x += lastx
            print('blet', lastx)

        if ((y < 0 and not self.top) or (y >= 0 and not self.bottom)) and HEIGHT > self.rect.y + y > 0:
            self.y += y
        else:
            self.y += lasty

    def cam_targeting(self):
        tx, ty = self.truecords
        r1, r2 = game.camera.cam_x if self.xcamflg else self.x, game.camera.cam_y if self.ycamflg else self.y
        x = game.camera.set(r1, r2)
        camx, camy = game.camera.cam_x, game.camera.cam_y
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
        print(self.xcamflg, self.ycamflg)
    def events_check(self):
        keyboard = pygame.key.get_pressed()
        keys = []
        for i in range(len(controls[self.controls_num])):
            x = controls[self.controls_num][i]
            if keyboard[x]:
                keys.append(i)
        self.control(keys)

    def physics(self):
        self.move(int(self.horizontal_speed), int(self.vertical_speed))
        self.onfloor = self.bottom
        if self.onfloor:
            self.grav_accel = G
            self.vertical_speed = 0
            self.horizontal_speed += (-self.horizontal_speed) / 5
        else:
            # self.grav_accel += G
            self.vertical_speed += self.grav_accel


class Human(Pawn, pygame.sprite.Sprite):
    def __init__(self):
        super(Human, self).__init__()
        animpath = ASSETS_PATH + 'Sprites/Animations/running_1/'
        self.image = pg.image.load(ASSETS_PATH + 'Sprites/Static/Human/idle1.png')
        self.rect = self.image.get_rect()
        self.runanimation = [animpath + f'{i}.png' for i in range(1, 7)]
        self.moves = []
        print(self.rect.bottom)

    def update(self):
        self.cam_targeting()
        self.events_check()
        self.physics()
        # self.rect.x, self.rect.y = self.x, self.y
        self.group.draw(screen)

    def control(self, keys):
        speed = 1
        if 0 in keys:
            ...
            # self.move(0, -speed)
        if 2 in keys:
            ...
            # self.move(0, speed)
        if 1 in keys:
            self.horizontal_speed += speed
            # self.move(speed, 0)
        if 3 in keys:
            self.horizontal_speed -= speed
            # self.move(-speed, 0)
        if 4 in keys and (self.jumpflg or self.bottom) and self.vertical_speed > -15:
            self.jumpflg = 1
            self.vertical_speed += -self.jump_power
        else:
            self.jumpflg = 0


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
