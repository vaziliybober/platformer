import pygame
pygame.init()
from sprite import Sprite
from functions import load_image, load_sound
from b import b
from hero import Hero
from enemy import Enemy
from animation import Animation
from text import Text
from heal import Heal
import time
import sys
import copy
import shelve
from random import randint


def color(r, g, b, size=(100, 100)):
	s = pygame.Surface(size)
	s.fill((r, g, b))
	return s

data_dir = 'data'

class Level:
	def get_map_size(self):
		w = (len(self.map[0])+1)*self.block_size[0]
		h = (len(self.map))*self.block_size[1]
		return [w, h]

	def __setattr__(self, name, value):
		self.__dict__[name] = value
		if name == 'map':
			self.map_size = self.get_map_size()
			for i, _ in enumerate(self.map):
				self.map[i] += ' '
		if name.endswith('_size'):
			try:
				self.__dict__[name[:-5] + '_image'] = pygame.transform.scale(self.__dict__[name[:-5] + '_image'], list(map(int, value)))
			except KeyError:
				pass
		if name.endswith('_image'):
			try:
				self.__dict__[name[:-6] + '_size'] = self.__dict__[name[:-6] + '_image'].get_rect().size
			except KeyError:
				pass
		if name == 'hero_image':
			self.hero_anim = None
		if name == 'enemy_image':
			self.enemy_anim = None























	def create_sprites(self, screen_size):
		self.screen_size = screen_size

		if type(self.background) == str:
			self.background = load_image(data_dir, self.background, screen_size)
		else:
			self.background = pygame.transform.scale(self.background, screen_size)

		self.platform_blocks = pygame.sprite.Group()
		self.platforms = pygame.sprite.Group()
		self.wall_blocks = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.heals = pygame.sprite.Group()



		self.wall = Sprite((0, 0), size=(self.block_size[0], self.map_size[1]))

		self.hearts = []
		x = 5
		y = 5
		for i in range(self.hearts_number):
			self.hearts.append((self.heart_image, (x, y)))
			x += self.heart_size[0] + self.heart_gap
		self.remaining_hearts = self.hearts.copy()

		x = 0
		y = self.map_size[1] - self.block_size[1]
		p = 0
		rmap = self.map[::-1]
		for i, row in enumerate(rmap):
			wb = Sprite((x, y), self.wall_block_image)
			b = Sprite((x, y), self.block_image)
			self.wall_blocks.add(wb)
			self.platforms.add(wb)
			self.platform_blocks.add(b)
			x += self.block_size[0]
			for j, cell in enumerate(row):
				if cell == '-':
					self.platform_blocks.add(Sprite((x, y), self.block_image))
					p += 1
				elif cell == 's':
					self.hero = Hero((x, y), self.hero_size, self.hero_image, self.hero_speed, self.gravity, self.hero_jump_power, anim=self.hero_anim)
					self.hero.rect.bottom = y + self.block_size[1]
				elif cell == 'h':
					heal = Sprite((x, y), self.heal_image)
					heal.rect.center = pygame.Rect((x, y), self.block_size).center
					self.heals.add(heal)

				elif cell == 'p':
					self.portal = Sprite((x, y), self.portal_image)
				elif p != 0:
					platform = Sprite((x - p*self.block_size[0], y), size=(p*self.block_size[0], self.block_size[1]), image=self.block_image)
					self.platforms.add(platform)
					if i < len(rmap)-1: # Если платформа не самая верхняя...
						ex = x - p*self.block_size[0]
						for c in rmap[i+1][j-p: j]: # ...проверяем, нужен ли краб на платформе. Костыль!
							if c == 'e':
								self.enemies.add(Enemy(ex, platform, self.enemy_size, self.enemy_image, self.enemy_text.copy(), self.enemy_reply, self.enemy_reply_time, speed=1, anim=self.enemy_anim))
							ex += self.block_size[0]

					p = 0
				x += self.block_size[0]
			x = 0
			p = 0
			y -= self.block_size[1]

























	def update_sprites(self):
		if time.time() - self._wbt > self.wall_delay:
			self._wbx += self.wall_speed
			for wb in self.wall_blocks:
				wb.rect.x += self._wbx
			if self._wbx >= 1: self._wbx -= int(self._wbx)
		self.hero.update()
		self.hero.onGround = False
		self.hero.yvel += self.hero.yaccel
		self.hero.rect.y += self.hero.yvel

		self._hero_and_platforms(0, self.hero.yvel)
		self.hero.xvel += self.hero.xaccel
		self.hero.rect.x += self.hero.xvel
		self._hero_and_platforms(self.hero.xvel, 0)
		#self.hero.xvel = 0

		self._hero_and_enemies()
		if self.hero.xaccel < 0 and self.hero.xvel <= 0:
			self.hero.xaccel = 0
		if self.hero.xaccel > 0 and self.hero.xvel >= 0:
			self.hero.xaccel = 0
		if self.hero.xaccel == 0:
			self.hero.xvel = 0 # Если кнопку не жмем, герой не должен двигаться по OX.


		self.enemies.update()

		self._enemies_and_platforms()
		self._enemies_and_enemies()
		h_w = self._hero_and_wall()
		if h_w:
			return h_w
		if self.hero.rect.top > self.map_size[1]:
			return 'restart'

		self._hero_and_heals()
		h_p = self._hero_and_portal()
		if h_p:
			return h_p



	def _hero_and_platforms(self, xvel, yvel):
		for p in self.platform_blocks:

			if pygame.sprite.collide_rect(self.hero, p):  # Если столкновение вообще есть...
				if yvel > 0:  # ... и герой пытается провалиться вниз сквозь платформу...
					self.hero.rect.bottom = p.rect.top # ...не даём ему это сделать
					self.hero.onGround = True
					self.hero.yvel = 0

				if yvel < 0: # Так же, если он пытается пробить платформу головой
					self.hero.rect.top = p.rect.bottom
					self.hero.yvel = 0

				if xvel > 0:  # Упирается в платформу, идя вправо
					self.hero.rect.right = p.rect.left

				if xvel < 0:  # влево
					self.hero.rect.left = p.rect.right

	def _hero_and_enemies(self):
		for e in self.enemies:

			if pygame.sprite.collide_rect(self.hero, e):

				if self.hero.yvel >= 1:
					if self.enemy_kill_sound:
						self.enemy_kill_sound.play()
					self.hero.rect.bottom = e.rect.top
					self.enemies.remove(e)
					self.hero._jump(self.enemy_head_jump_power)
				else:
					if self.enemy_bump_sound:
						self.enemy_bump_sound.play()

					e.t = time.time()
					e.text.text = e.reply
					e.text.follow(e)
					e.text.render()
					self.remaining_hearts.pop(-1)
					if self.hero.xvel < 0:
						self.hero.xvel = self.enemy_bump_power
						self.hero.xaccel = -self.enemy_bump_accel
					elif self.hero.xvel > 0:
						self.hero.xvel = -self.enemy_bump_power
						self.hero.xaccel = self.enemy_bump_accel
					else:
						if e.xvel > 0:
							self.hero.xvel = self.enemy_bump_power
							self.hero.xaccel = -self.enemy_bump_accel
						if e.xvel < 0:
							self.hero.xvel = -self.enemy_bump_power
							self.hero.xaccel = self.enemy_bump_accel


	def _enemies_and_platforms(self):
		for e in self.enemies:
			for p in self.platforms:
				if pygame.sprite.collide_rect(e, p) and p not in self.wall_blocks:
					if e.xvel > 0:  # Упирается в платформу, идя вправо
						e.rect.right = p.rect.left
						e.xvel = -e.xvel

					elif e.xvel < 0:  # влево
						e.rect.left = p.rect.right
						e.xvel = -e.xvel

	def _enemies_and_enemies(self):
		for e1 in self.enemies:
			for e2 in self.enemies:
				if pygame.sprite.collide_rect(e1, e2) and not e1 is e2:
					if e1.xvel < 0:
						temp = e2
						e2 = e1
						e1 = temp
					d = e1.rect.right - e2.rect.left
					e1.rect.x -= d/2
					e2.rect.x += d/2
					e1.xvel = -e1.xvel
					e2.xvel = -e2.xvel



	def _hero_and_wall(self):
		for wb in self.wall_blocks:
			if pygame.sprite.collide_rect(self.hero, wb):
				if self.wall_touch_sound:
					self.wall_touch_sound.play()
				return 'restart'


	def _hero_and_heals(self):
		for heal in self.heals:
			if pygame.sprite.collide_rect(self.hero, heal) and len(self.remaining_hearts) < self.hearts_number:
				if self.chewing_sound:
					self.chewing_sound.play()
				self.remaining_hearts.append(self.hearts[len(self.remaining_hearts)])
				self.heals.remove(heal)

	def _hero_and_portal(self):
		if pygame.sprite.collide_rect(self.hero, self.portal):
			if self.next_level_sound:
				self.next_level_sound.play()
			return 'next'







































	def __init__(self):
		self.block_size = (4*b, 4*b)
		self.map = [
		'--------------------------------',
		'                               -',
		'                              s-',
		'                               -',
		'                              --',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                     -         -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'             --                -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                        -      -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                        --     -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                        --     -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                               -',
		'                         p     -',
		'                               -']

		self.background = '1189.png'
		self.music = None
		self.next_level_sound = None

		self.hero_size = (4*b, 6*b)
		hero_images = [[load_image(data_dir, 'max' + str(i) + direction, self.hero_size)
		for i in range(1, 10)] for direction in ('right.png', 'left.png')]
		self.__dict__['hero_image'] = hero_images[0][0]
		self.hero_anim = [Animation(hero_images[i], 9, 8) for i in range(2)]
		self.hero_speed = b/2
		self.gravity = b/100*3
		self.hero_jump_power = b


		self.block_image = load_image(data_dir, 'parta.png', self.block_size)

		self.wall_block_size = (b, self.block_size[1])
		self.wall_block_image = load_image(data_dir, 'laser.png', self.wall_block_size)
		self.wall_speed = b/10*3
		self._wbx = 0 # Не менять
		self._wbt = time.time() # не менять
		self.wall_delay = 0
		self.wall_touch_sound = None

		self.portal_size = (4*b, 4*b)
		self.portal_image = load_image(data_dir, 'portal.png', self.portal_size)

		self.enemy_size = (6*b, 4*b)
		enemy_images = [load_image(data_dir, 'krab_danya' + str(i) + '.png', self.enemy_size) for i in range(1, 4)]
		self.enemy_image = enemy_images[0]
		self.enemy_anim = [Animation(enemy_images, 3, 40)] * 2
		self.enemy_text = Text('', (100, 600), 'Georgia', 25, (200, 0, 0))
		self.enemy_reply = 'Тыы чтоле'
		self.enemy_head_jump_power = b
		self.enemy_bump_accel = b/100*3
		self.enemy_bump_power = b
		self.enemy_reply_time = 2.5
		self.enemy_bump_sound = None
		self.enemy_kill_sound = None

		self.heart_size = (4*b, 4*b)
		self.heart_image = load_image(data_dir, 'heart.png', self.heart_size)
		self.hearts_number = 3
		self.heart_gap = b/2

		self.heal_size = (b*3, b*3)
		self.heal_image = load_image(data_dir, 'snack.png', self.heal_size)
		self.chewing_sound = None#load_sound(data_dir, 'chewing.ogg')







































sounds = {}
for name in ('duet1', 'duet2', 'duet3', 'pantera', 'bump', 'tii_chtole', 'bzz', 'molodec', 'chewing', 'crown_sound', 'vzhuh', 'r2d2', 'kosmos', 'kosmos_portal'):
	sounds[name] = load_sound(data_dir, name+'.wav')

levels = []
#----------------------LVL1---------------------------------------














def create_level():
	t = time.time()
	lvl = Level()

	lvl.music = sounds['duet1']
	lvl.hero_size = (4*b, 4*b)
	lvl.hero_image = color(255, 150, 150, (4*b, 4*b))
	lvl.enemy_image = color(50, 50, 50, (4*b, 4*b))
	lvl.background = color(0, 0, 255)
	lvl.block_image.fill((0, 0, 0))
	lvl.heal_image = color(150, 150, 0, (2*b, 2*b))
	lvl.wall_block_image.fill((0, 0, 100))
	lvl.enemy_reply = ''
	lvl.hearts_number = 2
	lvl.heart_image = color(150, 0, 0, (3*b, 3*b))
	lvl.portal_image.fill((0, 200, 200))
	lvl.hero_jump_power = b*11/10
	lvl.wall_speed = b/6
	lvl.enemy_head_jump_power = b*13/10
	lvl.map = [
	 '------------------------------------------------------------------------------------------------------',
	 '                                                  e                                                  -',
	 '                                ----------------------------                                         -',
	 '                              -                                                                      -',
	 '       --------                                e        e  -                                         -',
	 '                                        --------------------                                         -',
	 '                            ---------                      -------   -----------                     -',
	 '                    ---                                          -   -         -                     -',
	 '                                                        p      ---   --        -      e              -',
	 '                                                        --     - e  e -        -------- -            -',
	 '                              --                               --------        -        -            -',
	 '                       -                                                       -  e  e  -            -',
	 '                                                                               ------ ---            -',
	 '             e                                                                      - -              -',
	 '            ---                                             e   e             eh    - -              -',
	 '                                                   ------------------  -------------- ----           -',
	 '                         ----                      -                                     -           -',
	 '                                                   -                                     -           -',
	 '       --                                          -    eh                     e         -           -',
	 '                   ----                            -----------   -------------------------           -',
	 '                                                                                                     -',
	 '    s                                                                                                -',
	 '  -----                                                                                              -',
	 'e h                   ------                                                                         -',
	 '-----------    -----------------------                                                              --']
	print(time.time() - t)
	return lvl
levels.append(create_level)


#---------------------LVL2-------------------------------------
def create_level():
	lvl = levels[0]()
	lvl.music = sounds['duet2']
	lvl.hearts_number = 2
	lvl.hero_jump_power = b/2
	lvl.enemy_head_jump_power = b/2*5
	lvl.map = [
 '-----------------------------------------------------------------------------------------------------',
 '                                                                                     -              -',
 '                                                                 -                    -          e p-',
 '                                                                -                      -  -----------',
 '                                                               -                        -           -',
 '                                                              -                          -          -',
 '                                                             -          --------          -         -',
 '                                                            -           -      -           -        -',
 '                  ------------------                       -            -      -            -       -',
 '                  -                -                      -             --------             -      -',
 '                  -                -                     -                                    -  -  -',
 '                  -                                     -                                       -   -',
 '                  -                          e   e     ------------------------------------------   -',
 '                   -------    --------------------------                                        -   -',
 '                                                       -                                        -   -',
 '                                                       -                   ------               -   -',
 '                                                       -                   -    -               -   -',
 '                                                       -                   -   --               -   -',
 '                                                       ------------------------------------------   -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '       ----------------       ---------------                                                       -',
 '       -                                    -                                                       -',
 '       -                                    -                                                       -',
 '       -                                    -                                                       -',
 '       -s                e                  -                                                       -',
 '       --------------------------------------                                                       -']
	return lvl
levels.append(create_level)


#---------------------LVL3-------------------------------
def create_level():
	lvl = levels[0]()
	lvl.music = sounds['duet3']
	lvl.hero_speed = b/3
	lvl.hero_jump_power = b/10*9
	lvl.enemy_head_jump_power = b/5*3
	lvl.map = [
 '-----------------------------------------------------------------------------------------------------',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                s   -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                   p                                                -',
 '                                                  --                                                -',
 '                                                 -                                                  -',
 '                                          -   --                                       e           e-',
 '                                             -                                         --------------',
 '                                            -                                                       -',
 '                                       - ------                                                     -',
 '                                      -                                                             -',
 '                                     -                                                              -',
 '                                                                                                    -',
 '    e    e    e   e   e    e    e   e  e    e    e    e   e   e   e   e   e    e   e   e   e    e   -',
 '-----------------------------------------------------------------------------------------------------']

	return lvl
levels.append(create_level)






























def create_level():
	lvl = Level()
	lvl.enemy_bump_sound = sounds['tii_chtole']
	lvl.enemy_kill_sound = sounds['bump']
	lvl.wall_touch_sound = sounds['bzz']
	lvl.chewing_sound = sounds['chewing']
	return lvl
levels.append(create_level)


#-----------------------LVL5-------------------------------------------------
def create_level():
	lvl = Level()
	lvl.enemy_bump_sound = sounds['tii_chtole']
	lvl.enemy_kill_sound = sounds['bump']
	lvl.block_size = (4*b, 4*b)
	lvl.wall_touch_sound = sounds['bzz']
	lvl.chewing_sound = sounds['chewing']
	lvl.map = [
		'--------------------------------------------------------------------------------------------------------------------------------',
		'                                                                                                                               -',
		'                                                                                                                              s-',
		'                                                                                                                               -',
		'                                                                                                                              --',
		'                                                                    p                                                          -',
		'                                                                    ----                          ---------                    -',
		'                                                                                                                    e          -',
		'                                                                                                                   -----       -',
		'                                                                           e                                                   -',
		'                                                                          -----                                                -',
		'                                                                                       e                                       -',
		'                                                                                      -------                                  -',
		'                                                                                                                               -',
		'                                                                                                                               -',
		'                                                                                                                               -',
		'                                                                                                                               -',
		'                                                                                                                               -',
		'                                                                                                                               -']
	return lvl
levels.append(create_level)


#---------------------LVL6-------------------------------------------------------

def create_level():
	lvl = Level()
	lvl.enemy_bump_sound = sounds['tii_chtole']
	lvl.enemy_kill_sound = sounds['bump']
	lvl.wall_touch_sound = sounds['bzz']
	lvl.chewing_sound = sounds['chewing']
	lvl.block_size = (4*b, 4*b)
	lvl.wall_speed = 4

	lvl.map = [
  	'--------------------------------------------------',
  	'                                                 -',
  	'                                               p -',
  	'                                         -- ---- -',
  	'                                      - -        -',
  	'                                     -           -',
  	'                                   -             -',
  	'                                 -               -',
  	'                               -                 -',
  	'                             -                   -',
  	'                            -                    -',
  	'                           -                     -',
  	'                         -                       -',
  	'                        -                        -',
  	'                      -                          -',
  	'                    -                            -',
  	'                  -                              -',
  	'                -                                -',
  	'              --                                 -',
  	'            -                                    -',
  	'           -                                     -',
  	'          -                                      -',
  	'         -                                       -',
  	'        -                                        -',
  	'      --                                         -',
  	'   s--     e                                     -',
  	'--------------------------------------------------']
	return lvl
levels.append(create_level)



#---------------------LVL7-------------------------------

def create_level():
	lvl = Level()
	lvl.music = sounds['pantera']
	lvl.music.set_volume(0.1)
	lvl.block_size = (4*b, 4*b)
	lvl.wall_touch_sound = sounds['bzz']
	lvl.enemy_kill_sound = sounds['bump']
	lvl.enemy_bump_sound = sounds['crown_sound']
	lvl.next_level_sound = sounds['vzhuh']
	lvl.portal_size = (5*b, 5*b)
	lvl.enemy_size = (4*b, 4*b)
	lvl.enemy_reply = ''
	lvl.map =  [

  	'---------------------------------------------------------',
  	'                                                p       -',
  	'                        s      e    h                   -',
  	'---------------------------------------------------------']

	lvl.background = 'pantera_fon.jpg'
	lvl.heal_image = load_image(data_dir, 'heart.png', lvl.heal_size)

	lvl.hero_size = (4*b, 6*b)
	lvl.hero_speed = b
	hero_images = [[load_image(data_dir, 'pantera' + direction, lvl.hero_size)
	for i in range(1, 3)] for direction in ('_right.png', '_left.png')]
	lvl.__dict__['hero_image'] = hero_images[0][0]
	lvl.hero_anim = [Animation(hero_images[i], 1, 1) for i in range(2)]

	lvl.wall_block_image = load_image(data_dir, 'laser_blue.png', lvl.wall_block_size)

	enemy_images = [[load_image(data_dir, 'crown' + direction, lvl.enemy_size)
	for i in range(1, 3)] for direction in ('_right.png', '_left.png')]
	lvl.__dict__['enemy_image'] = hero_images[0][0]
	lvl.enemy_anim = [Animation(enemy_images[i], 1, 1) for i in range(2)]


	lvl.block_image = load_image(data_dir, 'pantera_block.jpg', lvl.block_size)

	return lvl
levels.append(create_level)

#---------------------LVL8-------------------------------

def create_level():
	lvl = levels[6]()
	lvl.hero_speed = b/2
	lvl.hero_size = (4*b, 4*b)
	hero_images = [[load_image(data_dir, 'pantera' + direction, lvl.hero_size)
	for i in range(1, 3)] for direction in ('_right.png', '_left.png')]
	lvl.__dict__['hero_image'] = hero_images[0][0]
	lvl.hero_anim = [Animation(hero_images[i], 1, 1) for i in range(2)]
	lvl.map =  [
	'---------------------------------------------------------',
  	'                                                       p-',
  	'                     e                        e         -',
  	'---------------------------------------  ----------------',
  	'                    e                 e                 -',
  	'--------------------------------  -----------------------',
  	'                       h        e            he         -',
  	'----------------------------------------  ---------------',
  	'              e                   e                     -',
  	'----------------------------  ---------------------------',
  	'            e          h              e             e   -',
  	'-------------------------  ------------------  -----------',
  	'          e       s          e                          -',
  	'---------------------------------------------------------']


	return lvl
levels.append(create_level)

#---------------------LVL9-------------------------------

def create_level():
	lvl = levels[6]()
	lvl.hero_speed = b/2
	lvl.map =  [
	'---------------------------------------------------------',
  	'              -                                         -',
  	'              -                                        p-',
  	'              -                         e        e      -',
  	'              -              --------------  ------------',
  	'              -                                         -',
  	'              -                    e      e             -',
  	'              ------------------------------------  --- -',
  	'              -                                         -',
  	'              -         e         h                     -',
  	'       -------- -----------------------------------------',
  	'                -                                       -',
  	'       s     e  -           e        e                  -',
  	'---------------------------------------------------------']
	return lvl
levels.append(create_level)









































#---------------------LVL10-------------------------------
def create_level():
    lvl = Level()
    lvl.wall_touch_sound = sounds['bzz']
    lvl.enemy_bump_sound = sounds['r2d2']
    lvl.next_level_sound = sounds['kosmos_portal']
    lvl.block_size = (4*b, 4*b)
    lvl.portal_size = (6*b, 10*b)
    lvl.enemy_size = (4*b, 6*b)
    lvl.enemy_reply = ''
    lvl.portal_image = load_image(data_dir, 'rocket.png', lvl.portal_size)
    enemy_images = [load_image(data_dir, 'inoplanet' + str(i) + '.png', lvl.enemy_size) for i in range(1, 2)]
    lvl.enemy_image = enemy_images[0]
    lvl.map =  [
 '-----------------------------------------------------------------------------------------------------',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                               e-----                               -',
 '                                                             e-----                                 -',
 '                                                           e-----                                   -',
 '                                                         e-----                                     -',
 '                                                       e-----                                       -',
 '                                                     e-----                                         -',
 '                                                   e-----       -                                   -',
 '                                                 e -----                                            -',
 '                                ---------   e  -----                                                -',
 '                                -       -------                           -                         -',
 '                                -                                         -                         -',
 '                                  -                                     ---                         -',
 '                               e  -                                     ---                         -',
 '                          ----------                        ---------------                         -',
 '          s               -        -                                      -                         -',
 '                          -        -                               e      -                         -',
 '                        e -                                 -----------   -                         -',
 '                     -----         -                                  - p -                         -',
 '                     -----    ---------------                         -   -                         -',
 '                                           e                          -   -    e                    -',
 '-------      ------------------------------------              --------------------------------------']

    lvl.background = 'kosmos.png'
    lvl.music = sounds['kosmos']
    lvl.enemy_kill_sound = sounds['bump']
    lvl.block_image = load_image(data_dir, 'kos_block.png', lvl.block_size)
    #lvl.hero_size = (4*b, 6*b)
    hero_images = [[load_image(data_dir, 'kosmonaft' + direction, lvl.hero_size)
    for i in range(1, 3)] for direction in ('_right.png', '_left.png')]
    lvl.__dict__['hero_image'] = hero_images[0][0]
    lvl.hero_anim = [Animation(hero_images[i], 1, 1) for i in range(2)]
    return lvl
levels.append(create_level)
#---------------------LVL11-------------------------------
def create_level():
    lvl = Level()
    lvl.wall_touch_sound = sounds['bzz']
    lvl.enemy_bump_sound = sounds['r2d2']
    lvl.next_level_sound = sounds['kosmos_portal']
    lvl.block_size = (4*b, 4*b)
    lvl.portal_size = (6*b, 10*b)
    lvl.enemy_reply = ''
    lvl.enemy_size = (4*b, 6*b)
    lvl.portal_image = load_image(data_dir, 'rocket.png', lvl.portal_size)
    enemy_images = [load_image(data_dir, 'inoplanet' + str(i) + '.png', lvl.enemy_size) for i in range(1, 2)]
    lvl.enemy_image = enemy_images[0]
    lvl.map =  [
 '-----------------------------------------------------------------------------------------------------',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                           e        -',
 '                                                                                       -------      -',
 '            s               --                e    e                                        p       -',
 '                                          ----------                                                -',
 '                                                                                  ----              -',
 '     --------------                                        --------                        ---      -',
 '                                  ---------                              e     e                 -  -',
 '                                            e                          ----------                   -',
 '                   ---------               --      ------          -                          ---   -',
 '                                                                                                    -',
 '                                                                ---                -------          -',
 '                                ---                     e                                           -',
 '                                                     --------                                       -',
 '                                      -          -                                                  -',
 '                                             e                                                      -',
 '                                           ---------                                                -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '                                                                                                    -',
 '-----------------------------------------------------------------------------------------------------']

    lvl.background = 'kosmos.png'
    lvl.music = sounds['kosmos']
    lvl.enemy_kill_sound = sounds['bump']
    lvl.block_image = load_image(data_dir, 'kos_block.png', lvl.block_size)
    #lvl.hero_size = (4*b, 6*b)
    hero_images = [[load_image(data_dir, 'kosmonaft' + direction, lvl.hero_size)
    for i in range(1, 3)] for direction in ('_right.png', '_left.png')]
    lvl.__dict__['hero_image'] = hero_images[0][0]
    lvl.hero_anim = [Animation(hero_images[i], 1, 1) for i in range(2)]
    lvl.gravity = b / 100 * randint(2, 6)
    return lvl
levels.append(create_level)

#---------------------LVL12-------------------------------

def create_level():
    lvl = Level()
    lvl.wall_touch_sound = sounds['bzz']
    lvl.enemy_bump_sound = sounds['r2d2']
    lvl.next_level_sound = sounds['kosmos_portal']
    lvl.block_size = (4*b, 4*b)
    lvl.portal_size = (6*b, 10*b)
    lvl.enemy_size = (4*b, 6*b)
    lvl.enemy_reply = ''
    lvl.portal_image = load_image(data_dir, 'rocket.png', lvl.portal_size)
    enemy_images = [load_image(data_dir, 'inoplanet' + str(i) + '.png', lvl.enemy_size) for i in range(1, 2)]
    lvl.enemy_image = enemy_images[0]
    lvl.map =  [
    '----------------------------------------------------------------',
    '                                                               -',
    '                                                               -',
    '                               ---------------                 -',
    '                               -       p     -                 -',
    '                               -             -                 -',
    '                               -              -                -',
    '                      -e       -       -      -                -',
    '                   -------------              -                -',
    '                      -         -             -                -',
    '                      -          --  e -                       -',
    '                      -            -----                       -',
    '         s    e       -                -     e        e        -',
    '----------------------------------------------------------------']

    lvl.background = 'kosmos.png'
    lvl.music = sounds['kosmos']
    lvl.enemy_kill_sound = sounds['bump']
    lvl.block_image = load_image(data_dir, 'kos_block.png', lvl.block_size)
    lvl.hero_size = (4*b, 6*b)
    hero_images = [[load_image(data_dir, 'kosmonaft' + direction, lvl.hero_size)
    for i in range(1, 3)] for direction in ('_right.png', '_left.png')]
    lvl.__dict__['hero_image'] = hero_images[0][0]
    lvl.hero_anim = [Animation(hero_images[i], 1, 1) for i in range(2)]
    return lvl
levels.append(create_level)
