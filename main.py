import pygame
pygame.init()
import sys
from b import b
from levels import levels
from camera import Camera
import time
from copy import deepcopy
from menu import Menu, NewGame, Exit, Continue, Next, Back, Restart
import shelve
from text import Text


FPS = 60
screen_size = (1200, 640)
screen = pygame.display.set_mode(screen_size)
timer = pygame.time.Clock()
camera = Camera(*screen_size)
from levels import levels


i = 0
menu = Menu(screen_size, False)



try:
	menu.loop(screen, timer, FPS)
except NewGame:
	pass
except Exit:
	pygame.quit()
	sys.exit()
except Continue:
	save = shelve.open('save')
	try:
		i = save['save']
	except KeyError:
		i = 0
	finally:
		save.close()


menu = Menu(screen_size, True)

lvl = levels[i]()
lvl.create_sprites(screen_size)
music = lvl.music
channel = pygame.mixer.Channel(1)
if music:
	channel.play(music)




while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			save = shelve.open('save')
			save['save'] = i
			save.close()
			pygame.quit()
			sys.exit()
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		try:
			menu.loop(screen, timer, FPS)
		except NewGame:
			t = time.time()
			i = 0
			lvl = levels[i]()
			#print(time.time() - t)
			lvl.create_sprites(screen_size)
			channel.fadeout(1000)
			channel.queue(lvl.music)
			#print(time.time() - t)
			continue
		except Restart:
			lvl = levels[i]()
			lvl.create_sprites(screen_size)
		except Next:
			try:
				lvl = levels[i+1]()
				i += 1
				lvl.create_sprites(screen_size)
				channel.fadeout(1000)
				if lvl.music:
					channel.queue(lvl.music)
				save = shelve.open('save')
				save['save'] = i
				save.close()
			except IndexError:
				print('You win')
				save = shelve.open('save')
				#save['save'] = 0
				save.close()
				screen.fill((255, 255, 255))
				text = Text('YOU WIN', (0, 0), size = 40)
				screen.blit(text.image, (screen_size[0]//2, screen_size[1]//2))
				pygame.display.update()
				time.sleep(3)
				menu = Menu(screen_size, False)
				i = 0
				try:
					menu.loop(screen, timer, FPS)
				except NewGame:
					i = 0
					lvl = levels[i]()
					#print(time.time() - t)
					lvl.create_sprites(screen_size)
					channel.fadeout(1000)
					channel.queue(lvl.music)
					menu = Menu(screen_size)
				except Exit:
					pygame.quit()
					sys.exit()
				except Continue:
					save = shelve.open('save')
					try:
						i = save['save']
					except KeyError:
						i = 0
					finally:
						save.close()


		except Back:
			if i >= 1:
				lvl = levels[i-1]()
				i -= 1
				lvl.create_sprites(screen_size)
				channel.fadeout(1000)
				if lvl.music:
					channel.queue(lvl.music)
				save = shelve.open('save')
				save['save'] = i
				save.close()

		except Exit:
			pygame.quit()
			sys.exit()
		except Continue:
			save = shelve.open('save')
			try:
				i = save['save']
			except KeyError:
				i = 0
			finally:
				save.close()


	do = lvl.update_sprites()
	if do == 'next':
		try:
			lvl = levels[i+1]()
			i += 1
			lvl.create_sprites(screen_size)
			channel.fadeout(1000)
			if lvl.music:
				channel.queue(lvl.music)
			save = shelve.open('save')
			save['save'] = i
			save.close()
		except IndexError:
			print('You win')
			save = shelve.open('save')
			save['save'] = 0
			save.close()
			screen.fill((255, 255, 255))
			text = Text('YOU WIN', (0, 0), size = 40)
			screen.blit(text.image, (screen_size[0]//2, screen_size[1]//2))
			pygame.display.update()
			time.sleep(3)
			menu = Menu(screen_size, False)
			i = 0
			try:
				menu.loop(screen, timer, FPS)
			except NewGame:
				i = 0
				lvl = levels[i]()
				#print(time.time() - t)
				lvl.create_sprites(screen_size)
				channel.fadeout(1000)
				channel.queue(lvl.music)
				menu = Menu(screen_size)
			except Exit:
				pygame.quit()
				sys.exit()
			except Continue:
				save = shelve.open('save')
				try:
					i = save['save']
				except KeyError:
					i = 0
				finally:
					save.close()


	elif do == 'restart' or not lvl.remaining_hearts:
		print(do)
		lvl = levels[i]()
		lvl.create_sprites(screen_size)

	screen.blit(lvl.background, (0, 0))
	camera.update(lvl.hero, screen_size, lvl.map_size)


	screen.blit(lvl.hero.image, camera.apply(lvl.hero))
	screen.blit(lvl.portal.image, camera.apply(lvl.portal))
	for wb in lvl.wall_blocks:
		screen.blit(wb.image, camera.apply(wb))
	for block in lvl.platform_blocks:
		screen.blit(block.image, camera.apply(block))
	for enemy in lvl.enemies:
		screen.blit(enemy.image, camera.apply(enemy))
		screen.blit(enemy.text.image, camera.apply(enemy.text))

	for heal in lvl.heals:
		screen.blit(heal.image, camera.apply(heal))
	for heart in lvl.remaining_hearts:
		screen.blit(*heart)


	timer.tick(FPS)
	pygame.display.flip()
