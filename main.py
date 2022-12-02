import pygame as pg
import pygame.event

pg.init()
true_width, true_height = pygame.display.Info().current_w, pygame.display.Info().current_h
print(true_width, true_height)
WIDTH = true_width*0.8
HEIGHT = true_height*0.8
FPS = 60
running = True
clock = pg.time.Clock()

screen = pg.display.set_mode((WIDTH, HEIGHT))
while running:
    for event in pg.event.get():
        if event.type == pg.WINDOWCLOSE:
            running = False
    clock.tick(FPS)
    pg.display.update()
    pg.display.flip()
