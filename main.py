import sys
import pygame

pygame.init()

def Main():
    game = Game((1300, 600))
    while 1:
        game.draw()
        game.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

class Player(pygame.sprite.Sprite):
    def __init__(self, coordinates, image):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = self.coordinates = coordinates
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

    def draw(self):
        pass
    
    def update(self):
        self.rect.move_ip(1, 1)
    
    
class Projectile((pygame.sprite.Sprite)):
    def __init__(self, coordinates):
        pygame.sprite.Sprite().__init__(self)
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
        self.player1 = Player((650, 300), "C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/red tank.png")
        self.player2 = Player((300, 500), "C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/blue tank.png")
        self.playersGroup = pygame.sprite.Group(self.player1, self.player2)

    def draw(self):
        self.playersGroup.draw(self.screen)
        
    def update(self):
        self.playersGroup.update()
        pygame.display.flip()
        
Main()
