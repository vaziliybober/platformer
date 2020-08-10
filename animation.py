import pygame
pygame.init()


# Класс анимации. Производит смену кадров и позволяет настраивать частоту смены кадров
#------------------------------------------------------------
class Animation:
    # Инициализация кол-ва кадров анимации - frames и кол-ва кадров realframes, которое будет проходить между двумя кадрами анимации
    def __init__(self, images, frames, realframes):
        self.images = images
        self.image = images[0]
        self.frame = 0
        self.maxframe = frames - 1
        self.realframe = 0
        self.maxrealframe = realframes - 1

    # Изменяет, если настало время, значение текущего кадра анимации image
    def update(self):
        self.image = self.images[self.frame]
        if self.realframe == self.maxrealframe:
            self.frame += 1
            self.realframe = 0
        self.realframe += 1
        if self.frame == self.maxframe:
            self.frame = 0

    # Сбрасывает анимацию на первый кадр
    def reset(self):
        self.image = self.images[0]
        self.frame = self.realframe = 0