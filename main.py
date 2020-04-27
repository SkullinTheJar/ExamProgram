import sys
import pygame

pygame.init()

def Main():
    game = Game((1300, 600))
    while 1:
        game.draw()
        game.update()

class Player(pygame.sprite.Sprite):
    def __init__(self, coordinates):
        super().__init__(self)
        self.x, self.y = self.coordinates = coordinates
        self.image = pygame.Surface((10, 10))
        self.image.fill(255, 0, 255)
        self.rect = self.image.get_rect

    def draw(self):
        pass
    
    def update(self):
        pass
    
    
class Projectile((pygame.sprite.Sprite)):
    def __init__(self, coordinates):
        super().__init__(self)
        self.x, self.y = self.coordinates = coordinates
        
    def draw(self):
        pass

    def update(self):
        pass

class Wall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(self)
        
    
class Game:
    def __init__(self, size):
        self.size = size
        self.screen = pygame.display.set_mode(size)
        self.playersGroup = pygame.sprite.Group()
        self.player1 = Player((0, 0))
        self.player2 = Player((0, 0))
        self.playersGroup.add(self.player1, self.player2)

    def draw(self):
        pass
        
    def update(self):
        
        pygame.display.flip()
        
Main()
