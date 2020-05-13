import sys
import pygame
import math

pygame.init()

def updateCoords(speed, angle, coords, backwards = False):
    angle %= 360
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

def better_collide_mask(sprite1, sprite2):
    if pygame.sprite.collide_mask(sprite1, sprite2) != None:
        return True
    else:
        return False


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
        self.originalImage.set_colorkey((0, 0, 0))
        self.image = self.originalImage
        self.rect = self.image.get_rect()
        self.rect.center = self.coords = coords
        self.angle = 0
        self.mask = pygame.mask.from_surface(self.image)
        #print(str(self.mask.count()))

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
        #print(str(self.image.get_at((0, 0))) + ' ' + str(self.image.get_at((15, 15))))
        
        
    def rotate(self):
        center = self.rect.center
        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.mask = pygame.mask.from_surface(self.image)

    def wallCollide(self):
        self.coords = self.prevCoords
        self.angle = self.prevAngle

class Projectile(pygame.sprite.Sprite):
    def __init__(self, coords, radius, color, screen, length):
        pygame.sprite.Sprite.__init__(self)
        self.radius = radius
        self.color = color
        self.screen = screen
        self.length = length
        self.image = pygame.Surface((radius * 2, radius * 2)).convert()
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.coords = coords
        self.spawned = False
        
    def update(self):
        self.prevCoords = self.coords
        if self.length > 0:
            if not self.spawned:
                self.subProj = SubProj(self.prevCoords, self.radius, self.color, self.screen, self.length - 1, self)
                self.spawned = True
            self.subProj.update()
    
class LeadProj(Projectile):
    def __init__(self, coords, radius, color, screen, length, speed, angle, timer = 3000):
        super().__init__(coords, radius, color, screen, length - 1)
        self.speed = speed
        self.angle = angle
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.startTime = pygame.time.get_ticks()
        self.timer = timer 
        
    def update(self):
        super().update()
        self.rect.center = self.coords = updateCoords(self.speed, self.angle, self.coords)
        if pygame.time.get_ticks() > self.startTime + self.timer:
            self.kill()

    def wallCollide(self, walls):
        for wall in walls:
            if wall.orient:
                self.angle = 360 - self.angle

            if not wall.orient:
                if 0 < self.angle < 180:
                    self.angle = 180 - self.angle
                if 180 < self.angle < 360:
                    self.angle = 360 - (self.angle - 180)
                
class SubProj(Projectile):
    def __init__(self, coords, radius, color, screen, length, proj):
        super().__init__(coords, radius, color, screen, length)
        self.proj = proj
        self.screen = screen

    def update(self):
        super().update()
        self.coords = self.proj.prevCoords
        self.rect.center = self.coords
        self.screen.blit(self.image, self.rect)

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
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = coords
        self.mask = pygame.mask.from_surface(self.image)
        #print(str(self.mask.count()))

    
class Game:
    def __init__(self, size, laserLength = 10, cooldown = 500):
        self.size = size
        self.laserLength = laserLength
        self.cooldown = cooldown
        self.screen = pygame.display.set_mode(size)
        self.player1 = Player(1, (650, 300), 1, 0.5, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/red tank.png')
        self.player2 = Player(2, (300, 300), 1, 0.5, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/blue tank.png')
        #self.player1 = Player(1, (650, 300), 0.5, 0.5, 'C:/Users/WaffleFlower/Desktop/Skole/Programmering/ExamProgram/red_tank_exp_v2.png')
        #self.player2 = Player(2, (300, 300), 0.5, 0.5, 'C:/Users/WaffleFlower/Desktop/Skole/Programmering/ExamProgram/blue_tank_exp.png')
        self.players = pygame.sprite.Group(self.player1, self.player2)
        self.lasers = pygame.sprite.Group()
        self.lastShot = -cooldown
        self.walls = pygame.sprite.Group(Wall((200, 200), True), Wall((200, 200), False))
        #self.rects = [self.player1.rect, self.player2.rect]

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.players.draw(self.screen)
        self.walls.draw(self.screen)
        self.lasers.draw(self.screen)
        #pygame.draw.lines(self.screen, (255, 255, 255), False, (self.player1.rect.bottomleft, (self.player1.rect.bottomright), (self.player1.rect.topright), (self.player1.rect.topleft), self.player1.rect.bottomleft)) 
        
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.players.update(keys)
        self.lasers.update()
        #self.rects[0] = self.players.sprites()[0].rect
        #self.rects[1] = self.players.sprites()[1].rect
        if pygame.time.get_ticks() > self.lastShot + self.cooldown:
            if keys[pygame.K_q]:
                #coords, radius, color, screen, length, speed, angle
                self.lasers.add(LeadProj(updateCoords(10, self.player1.angle, self.player1.coords), 2, (0, 255, 0), self.screen, self.laserLength, 1, self.player1.angle,))
                #self.rects.append(self.laserGroups[-1].sprites()[0].rect)
                self.lastShot = pygame.time.get_ticks()
            if keys[pygame.K_m]:
                self.lasers.add(LeadProj(updateCoords(10, self.player2.angle, self.player2.coords), 2, (0, 255, 0), self.screen, self.laserLength, 1, self.player2.angle,))
                #self.rects.append(self.laserGroups[-1].sprites()[0].rect)
                self.lastShot = pygame.time.get_ticks()  

        self.collideGroups(self.players, self.walls, 'player-wall')
        self.collideGroups(self.lasers, self.walls, 'laser-wall')
        #self.collideGroups()    

    def collideGroups(self, group1, group2, resultType):
        collisions = pygame.sprite.groupcollide(group1, group2, False, False)
        for sprite in collisions:
            if collisions[sprite].__len__() > 0:
                collisions = pygame.sprite.groupcollide(group1, group2, False, False, pygame.sprite.collide_mask)
                for sprite in collisions:
                    if collisions[sprite].__len__() > 0:
                        if resultType == 'player-wall':
                            sprite.wallCollide()
                        if resultType == 'laser-wall':
                            sprite.wallCollide(collisions[sprite])

        

        #
        # collisions = pygame.sprite.groupcollide(self.lasers, self.walls, False, False)
        # for leadProj in collisions:
        #     if collisions[leadProj].__len__() > 0:
        #         collisions = pygame.sprite.groupcollide(self.lasers, self.walls, False, False, pygame.sprite.collide_mask)
        #         for leadProj in collisions:
        #             if collisions[leadProj].__len__() > 0:
        #                 leadProj.wallCollide(collisions[leadProj])
                        
        
        #pygame.display.update(self.rects)
        pygame.display.flip()

Main()
