import pygame
pygame.init()
from sprite import Sprite
from functions import load_image
import sys
from text import Text
from levels import color

data_dir = 'data'

class MyGame(Exception): pass
class NewGame(MyGame): pass
class Exit(MyGame): pass
class Continue(MyGame): pass
class Restart(MyGame): pass
class Next(MyGame): pass
class Back(MyGame): pass



class Button(pygame.sprite.Sprite):
	def __init__(self, pos, text, exc, background):
		pygame.sprite.Sprite.__init__(self)
		self.text = text
		self.exc = exc
		self.image = background
		self.normal_image = background
		self.selected_image = load_image(data_dir, 'selected_button.png', (300, 70))
		self.rect = self.image.get_rect()
		self.rect.topleft = pos

class Mouse(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.rect = pygame.Rect((0, 0), (1, 1))


	def update(self):
		self.rect.topleft = pygame.mouse.get_pos()


class Menu:
	def __init__(self, screen_size, esc=True):
		self.background = load_image(data_dir, 'menu.jpg', screen_size)
		self.mouse = Mouse()
		self.buttons = pygame.sprite.Group()
		y = 10
		buttons = (('Новая игра', NewGame), ('Продолжить', Continue), ('Заново', Restart), ('Следующий уровень', Next), ('Предыдущий уровень', Back), ('Выход', Exit))
		if not esc:
			buttons = buttons[:2] + buttons[-1:]
		for text, exc in buttons:
			self.buttons.add(Button((10, y), Text(text, (10, 10), size=25), exc, load_image(data_dir, 'button.png', (300, 70))))
			y += 70 + 10

	def update(self, button_down):
		self.mouse.update()
		for button in self.buttons:
			if pygame.sprite.collide_rect(self.mouse, button):
				button.image = button.selected_image
				if button_down:
					raise button.exc
			else:
				button.image = button.normal_image

		

	def loop(self, screen, timer, FPS):
		while True:
			button_down = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					button_down = True
			f = self.update(button_down)
			if f:
				f()

			screen.blit(self.background, (0, 0))
			for button in self.buttons:
				screen.blit(button.image, button.rect)
				button.text.rect.center = button.rect.center
				screen.blit(button.text.image, button.text.rect)

			timer.tick(FPS)
			pygame.display.flip()


