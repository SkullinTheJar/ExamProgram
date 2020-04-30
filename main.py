import sys
import pygame
import math

pygame.init()

def updateCoords(speed, angle, coords, backwards = False):
    if 0 <= angle <= 90:
        deltaCoords = [speed * math.cos(math.radians(angle - 90*math.floor(angle/90))), -speed * math.sin(math.radians(angle - 90*math.floor(angle/90)))]

    if 90 < angle <= 180:
        deltaCoords = [-speed * math.sin(math.radians(angle - 90*math.floor(angle/90))), -speed * math.cos(math.radians(angle - 90*math.floor(angle/90)))] 
    
    if 180 < angle <= 270:
        deltaCoords = [-speed * math.cos(math.radians(angle - 90*math.floor(angle/90))), speed * math.sin(math.radians(angle - 90*math.floor(angle/90)))] 
    
    if 270 < angle <= 360:
        deltaCoords = [speed * math.sin(math.radians(angle - 90*math.floor(angle/90))), speed * math.cos(math.radians(angle - 90*math.floor(angle/90)))]

    if backwards:
        deltaCoords = -deltaCoords[0], -deltaCoords[1]
    
    coords = coords[0] + deltaCoords[0], coords[1] + deltaCoords[1]
    return coords

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
        self.prevCoords = self.coords
        self.prevAngle = self.angle
        if self.n == 1:
            if keys[pygame.K_t]:
                #move forward
                self.coords = updateCoords(self.speed, self.angle, self.coords)
            if keys[pygame.K_f]:
                self.angle += self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_g]:
                self.coords = updateCoords(self.speed, self.angle, self.coords, True)
                #move backward
            if keys[pygame.K_h]:
                self.angle -= self.turnSpeed
                self.angle %= 360
                self.rotate()
                
        if self.n == 2:
            if keys[pygame.K_UP]:
                self.coords = updateCoords(self.speed, self.angle, self.coords)
            if keys[pygame.K_LEFT]:
                self.angle += self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_DOWN]:
                self.coords = updateCoords(self.speed, self.angle, self.coords, True)
            if keys[pygame.K_RIGHT]:
                self.angle -= self.turnSpeed
                self.angle %= 360
                self.rotate()

        self.rect.center = self.coords
        
    def rotate(self):
        center = self.rect.center
        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def wallCollide(self):
        self.coords = self.prevCoords
        self.angle = self.prevAngle

    
class Projectile((pygame.sprite.Sprite)):
    def __init__(self, color, coords, radius, speed, angle):
        pygame.sprite.Sprite.__init__(self)
        self.radius = radius
        self.speed = speed
        self.angle = angle
        self.image = pygame.Surface((radius * 2, radius * 2)).convert()
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.coords = coords
        
    def update(self):
        self.prevCoords = self.coords
        self.rect.center = self.coords = updateCoords(self.speed, self.angle, self.coords)
        

class Wall(pygame.sprite.Sprite):
    def __init__(self, coords, orient, length = 100, width = 3):
        pygame.sprite.Sprite.__init__(self)
        self.coords = coords
        self.length = length
        self.width = width
        self.orient = orient
        if orient:
            self.image = pygame.Surface((length, width))
        else:
            self.image = pygame.Surface((width, length))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = coords

    
class Game:
    def __init__(self, size, laserLength = 10, cooldown = 500):
        self.size = size
        self.laserLength = laserLength
        self.cooldown = cooldown
        self.screen = pygame.display.set_mode(size)
        #Ander Ass
        self.player1 = Player(1, (650, 300), 0.5, 0.5, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/red_tank_exp_v2.png')
        self.player2 = Player(2, (300, 300), 0.5, 0.5, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/blue_tank_exp.png')
        #ur mom
        #self.player1 = Player(1, (650, 300), 0.5, 0.5, 'C:/Users/WaffleFlower/Desktop/Skole/Programmering/ExamProgram/red_tank_exp_v2.png')
        #self.player2 = Player(2, (300, 300), 0.5, 0.5, 'C:/Users/WaffleFlower/Desktop/Skole/Programmering/ExamProgram/blue_tank_exp.png')
        self.players = pygame.sprite.Group(self.player1, self.player2)
        self.laserGroups = []
        self.lastShot = 0
        self.walls = pygame.sprite.Group(Wall((200, 200), True), Wall((200, 200), False))
        #self.rects = [self.player1.rect, self.player2.rect]

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.players.draw(self.screen)
        self.walls.draw(self.screen)
        for group in self.laserGroups:
            group.draw(self.screen)
        
    def update(self):
        keys = pygame.key.get_pressed()
        self.players.update(keys)
        #self.rects[0] = self.players.sprites()[0].rect
        #self.rects[1] = self.players.sprites()[1].rect
        for group in self.laserGroups:
            group.update()
            if group.sprites().__len__() < self.laserLength:
                group.add(Projectile((0, 255, 0), group.sprites()[-1].prevCoords, 2, 1, group.sprites()[-1].angle))
            if group.sprites()[-1].coords[0] > self.size[0] or group.sprites()[-1].coords[0] < 0 or group.sprites()[-1].coords[1] > self.size[1] or group.sprites()[-1].coords[1] < 0:
                group.empty()
                self.laserGroups.remove(group) 
                 #self.rects.append(group.sprites()[-1].rect)
            #elif group.sprites().__len__() == self.laserLength:
            #    group.add(Projectile((0, 0, 0), group.sprites()[-1].prevCoords, 2, 1, group.sprites()[-1].angle))
            #    self.rects.append(group.sprites()[-1].rect)
        if pygame.time.get_ticks() > self.lastShot + self.cooldown:
            if keys[pygame.K_q]:
                self.laserGroups.append(pygame.sprite.Group(Projectile((0, 255, 0), updateCoords(10, self.player1.angle, self.player1.coords), 2, 1, self.player1.angle)))
                self.lastShot = pygame.time.get_ticks()
                #self.rects.append(self.laserGroups[-1].sprites()[0].rect)
            if keys[pygame.K_m]:
                self.laserGroups.append(pygame.sprite.Group(Projectile((0, 255, 0), updateCoords(10, self.player2.angle, self.player2.coords), 2, 1, self.player2.angle)))
                self.lastShot = pygame.time.get_ticks()
                #self.rects.append(self.laserGroups[-1].sprites()[0].rect)
        
        
        for player in pygame.sprite.groupcollide(self.players, self.walls, False, False):
            if pygame.sprite.groupcollide(self.players, self.walls, False, False).__len__() > 0:
                player.wallCollide()


        #pygame.display.update(self.rects)
        pygame.display.flip()

Main()
