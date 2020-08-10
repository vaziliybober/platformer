import pygame
pygame.init()


# Класс, нужный для передвижения камеры вслед за героем
class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height) # Смещение всех объектов относительно их настоящего положения
        self.width = width
        self.height = height

    # Возвращает смещенный прямоугольник любого спрайта
    def apply(self, entity):
        return entity.rect.move(self.rect.topleft)

    # Центрирует камеру относительно героя
    def update(self, target, screen_size, level_size):
        x = -target.rect.x + (screen_size[0]/2)
        y = -target.rect.y + (screen_size[1]/2)
        #print(x, y)
        x = min(0, x)
        y = min(0, y)
        x = max(screen_size[0]-level_size[0], x)
        y = max(screen_size[1]-level_size[1], y)
        self.rect = pygame.Rect(x, y, self.width, self.height)

