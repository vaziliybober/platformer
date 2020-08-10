import pygame
pygame.init()

class Text:
    def __init__(self, text, topleft, font='Georgia', size=15, color=(0, 0, 0), background=None):
        self.text = text
        self.background = background
        self.font = font
        self.size = size
        self.color = color
        font = pygame.font.SysFont(font, size)
        self.image = font.render(self.text, True, self.color, self.background)
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.sprite = None

    def render(self):
    	font = pygame.font.SysFont(self.font, self.size)
    	self.image = font.render(self.text, True, self.color, self.background)
    	self.rect.size = self.image.get_rect().size


    def follow(self, sprite):
    	self.sprite = sprite

    def copy(self):
    	return Text(self.text, self.rect.topleft, self.font, self.size, self.color)

