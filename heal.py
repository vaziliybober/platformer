import pygame
pygame.init()
from sprite import Sprite


class Heal(Sprite):

	def update(self, hero, heals, hearts, rem_hearts):
		for heal in heals:
			if pygame.sprite.collide_rect(hero, heal) and len(rem_hearts) < 3:
				rem_hearts.append(hearts[len(rem_hearts)])
				heals.remove(heal)