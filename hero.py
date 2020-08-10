import pygame
import time
import sys
pygame.init()


# Класс героя игры. Определяет движение, управление, столкновения и анимацию, относящиеся к герою
#-------------------------------------------------------
class Hero(pygame.sprite.Sprite):
    def __init__(self, topleft, size, image, speed=2, gravity=0.15, jump_power=6, anim=None):
        pygame.sprite.Sprite.__init__(self)
        if anim:
            self.image = anim[0].images[0] # Изначально первый кадр анимации
        else:
            self.image = image
        self.anim = anim # Тут список из двух анимаций: направо - 0, налево - 1
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.speed = speed
        self.xaccel, self.yaccel = 0, gravity # Ускорения
        self.xvel, self.yvel = 0, 0
        self.jump_power = jump_power
        self.onGround = False
        self.direction = 'RIGHT'

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_UP] and self.onGround:
            self._jump(self.jump_power)
        elif self.xaccel == 0:
            if keys_pressed[pygame.K_RIGHT]:
                self.xvel = self.speed
                if self.anim: self.anim[0].update()
                self.direction = 'RIGHT'
            elif keys_pressed[pygame.K_LEFT]:
                self.xvel = -self.speed
                if self.anim: self.anim[1].update()
                self.direction = 'LEFT'
            elif self.anim:
                self.anim[0].reset(), self.anim[1].reset()

        if self.anim:
            if self.direction == 'RIGHT':
                self.image = self.anim[0].image
            if self.direction == 'LEFT':
                self.image = self.anim[1].image

    def _jump(self, jump_power):
        self.yvel = -jump_power






