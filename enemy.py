import pygame
pygame.init()
import time


# Класс врага. Прицепляет врага к платформе и заставляет его ходить по ней туда-сюда
class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, platform, size, image, text, reply, reply_time, speed=1, anim=None):
		pygame.sprite.Sprite.__init__(self)
		self.platform = platform
		if anim:
			self.image = anim[0].images[0]
		else:
			self.image = image
		self.anim = anim
		self.rect = self.image.get_rect()
		self.rect.bottom = platform.rect.top
		self.rect.x = x
		self.xvel = speed # Он двигается только по горизонтали
		self.reply = reply
		self.text = text
		self.reply_time = reply_time

	def update(self):
		self.rect.x += self.xvel
		if self.rect.right >= self.platform.rect.right or self.rect.left <= self.platform.rect.left: # Если враг дошел до края платформы...
			self.xvel = -self.xvel	# ...разворачиваем его

		if self.xvel > 0:
			direction = 'RIGHT'
		elif self.xvel < 0:
			direction = 'LEFT'

		
		self.rect.move_ip(self.xvel, 0)
		if self.anim:
			if direction == 'RIGHT':
				self.anim[0].update()
				self.image = self.anim[0].image
			if direction == 'LEFT':
				self.anim[1].update()
				self.image = self.anim[1].image

		if self.text.sprite:
			if time.time() - self.t > self.reply_time:
				self.text.text = ''
				self.text.render()
			self.text.rect.midbottom = self.rect.midtop
		