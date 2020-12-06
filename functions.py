import pygame
pygame.init()
import os

def load_image(dir, name, size):
	image = pygame.image.load(os.path.join(dir, name))
	return pygame.transform.scale(image, list(map(int, size)))

def load_sound(dir, name):
	if not name:
		return None
	music = pygame.mixer.Sound(os.path.join(dir, name))
	return music
