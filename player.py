import pygame

class Player():
    def __init__(self, x, color):
        self.x = x
        self.y = 500
        self.color = color
        self.rect = pygame.Rect(x, self.y, 50, 50)
        self.velocity = 5
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 50, 50))

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.velocity
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.velocity
        self.update()
            
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, 50, 50)
