import pygame
pygame.init()

class Sprite(pygame.sprite.Sprite):
	def __init__(self, pos, image=None, size=None):
		pygame.sprite.Sprite.__init__(self)
		if image == None and size == None:
			raise Exception

		if image and size:
			image = pygame.transform.scale(image, size)
			self.rect = image.get_rect()
			self.rect.topleft = pos
			self.image = image

		if size and not image:
			self.rect = pygame.Rect(pos, size)

		if image and not size:
			self.rect = image.get_rect()
			self.rect.topleft = pos
			self.image = image

