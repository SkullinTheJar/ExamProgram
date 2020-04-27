import sys
import pygame
import math

pygame.init()

def Main():
    game = Game((1300, 600))
    while 1:
        game.draw()
        game.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

class Player(pygame.sprite.Sprite):
    def __init__(self, n, coords, speed, turnSpeed, image):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        self.turnSpeed = turnSpeed
        self.n = n
        self.originalImage = pygame.transform.scale(pygame.image.load(image).convert(), (30, 30))
        self.image = self.originalImage
        self.rect = self.image.get_rect()
        self.rect.center = self.coords = coords
        self.angle = 0

    def update(self, keys):
        if self.n == 1:
            if keys[pygame.K_t]:
                self.updateCoords()
                #move forward
            if keys[pygame.K_f]:
                self.angle += self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_g]:
                self.updateCoords(True)
                #move backward
            if keys[pygame.K_h]:
                self.angle -= self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_q]:
                #shoot
                pass
        if self.n == 2:
            if keys[pygame.K_UP]:
                self.updateCoords()
            if keys[pygame.K_LEFT]:
                self.angle += self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_DOWN]:
                self.updateCoords(True)
            if keys[pygame.K_RIGHT]:
                self.angle -= self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_m]:
                #shoot
                pass
        self.rect.center = self.coords
        

    def updateCoords(self, backwards = False):
        if 0 <= self.angle <= 90:
            deltaCoords = [self.speed * math.cos(math.radians(self.angle - 90*math.floor(self.angle/90))), -self.speed * math.sin(math.radians(self.angle - 90*math.floor(self.angle/90)))]

        if 90 < self.angle <= 180:
            deltaCoords = [-self.speed * math.sin(math.radians(self.angle - 90*math.floor(self.angle/90))), -self.speed * math.cos(math.radians(self.angle - 90*math.floor(self.angle/90)))] 
        
        if 180 < self.angle <= 270:
            deltaCoords = [-self.speed * math.cos(math.radians(self.angle - 90*math.floor(self.angle/90))), self.speed * math.sin(math.radians(self.angle - 90*math.floor(self.angle/90)))] 
        
        if 270 < self.angle < 360:
            deltaCoords = [self.speed * math.sin(math.radians(self.angle - 90*math.floor(self.angle/90))), self.speed * math.cos(math.radians(self.angle - 90*math.floor(self.angle/90)))]

        if backwards:
            deltaCoords = -deltaCoords[0], -deltaCoords[1]
        
        self.coords = self.coords[0] + deltaCoords[0], self.coords[1] + deltaCoords[1]
        
        
    def rotate(self):
        center = self.rect.center
        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = center
    
class Projectile((pygame.sprite.Sprite)):
    def __init__(self, coords):
        pygame.sprite.Sprite().__init__(self)
        self.x, self.y = self.coords = coords

    def update(self):
        #self.rect.move_ip()
        pass

class Wall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(self)
        pass
    
class Game:
    def __init__(self, size):
        self.size = size
        self.screen = pygame.display.set_mode(size)
        self.player1 = Player(1, (650, 300), 0.75, 0.75, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/red tank.png')
        self.player2 = Player(2, (300, 300), 0.75, 0.75, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/blue tank.png')
        self.playersGroup = pygame.sprite.Group(self.player1, self.player2)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.playersGroup.draw(self.screen)
        
        
    def update(self):
        keys = pygame.key.get_pressed()
        self.playersGroup.update(keys)
        pygame.display.flip()
        
Main()
