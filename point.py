import pygame

class Rect:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, 50, 50)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 50, 50))

    def update(self):
        self.rect = pygame.Rect(self.x, self.y, 50, 50)
