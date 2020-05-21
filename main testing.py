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

def Main():
    game = Game((1300, 600))
    while 1:
        game.draw()
        game.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

class Player(pygame.sprite.Sprite):
    def __init__(self, n, coords, speed, turnSpeed, image, upgradeCool = 2000):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        self.turnSpeed = turnSpeed
        self.n = n
        self.originalImage = pygame.transform.scale(pygame.image.load(image).convert(), (30, 30))
        self.originalImage.set_colorkey((0, 0, 0))
        self.image = self.originalImage
        self.rect = self.image.get_rect()
        self.rect.center = self.coords = self.startCoords = coords
        self.angle = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.upgradeCool = upgradeCool
        self.upgrade = None
        self.upgradeTime = 0

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

        if self.upgradeTime + self.upgradeCool < pygame.time.get_ticks():
            self.upgrade = None
        if self.upgrade != None:
            print('upgraded!')
        
    def rotate(self):
        center = self.rect.center
        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.mask = pygame.mask.from_surface(self.image)

    def wallCollide(self):
        self.coords = self.prevCoords
        self.angle = self.prevAngle

    def reset(self):
        self.coords = self.startCoords
        self.angle = 0
        self.rotate()

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
    def __init__(self, coords, radius, color, screen, length, speed, angle, timer = 400):
        super().__init__(coords, radius, color, screen, length - 1)
        self.speed = speed
        self.angle = angle
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.frames = 0
        self.timer = timer
        
    def update(self):
        self.frames += 1
        super().update()
        self.rect.center = self.coords = updateCoords(self.speed, self.angle, self.coords)
        if self.frames == self.timer:
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
    def __init__(self, coords, orient, length = 100, width = 3, invert = False):
        pygame.sprite.Sprite.__init__(self)
        self.coords = coords
        self.length = length
        self.width = width
        self.orient = orient
        if orient:
            self.image = pygame.Surface((length + width, width))
        else:
            self.image = pygame.Surface((width, length + width))
        self.image.fill((255, 255, 255))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        if not invert:
            self.rect.bottomleft = coords
        if invert:
            self.rect.topright = coords
        
        self.mask = pygame.mask.from_surface(self.image)
        #print(str(self.mask.count()))

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, color, coords):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = coords
    
class Game:
    def __init__(self, size, laserLength = 10, cooldown = 500):
        self.size = size
        self.laserLength = laserLength
        self.cooldown = cooldown
        self.screen = pygame.display.set_mode(size)
        self.player1StartPos = 60, 100
        self.player2StartPos = 650, 300
        #self.player1 = Player(1, self.player1StartPos, 0.75, 0.5, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/red tank.png')
        #self.player2 = Player(2, self.player2StartPos, 0.75, 0.5, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/blue tank.png')
        self.player1 = Player(1, (650, 300), 0.5, 0.5, 'C:/Users/WaffleFlower/Desktop/Skole/Programmering/ExamProgram/red_tank_exp_v2.png')
        self.player2 = Player(2, (300, 300), 0.5, 0.5, 'C:/Users/WaffleFlower/Desktop/Skole/Programmering/ExamProgram/blue_tank_exp.png')
        self.players = pygame.sprite.Group(self.player1, self.player2)
        self.lasers = pygame.sprite.Group()
        self.upgrades = pygame.sprite.Group(Upgrade((255, 255, 0), (450, 300)))
        self.lastShot = -cooldown
        self.walls = pygame.sprite.Group(
            #Laver de ydre mure
            Wall((0, 60), True, self.size[0]), Wall((0, self.size[1]), False, self.size[1] - 60), 
            Wall((0, self.size[1]), True, self.size[0]), Wall((self.size[0] - 3, self.size[1]), False, self.size[1] - 60), 
            #Laver de indre mure
            Wall((120, 120), False, 60), Wall((120, 120), True), Wall((220, 220), False), Wall((120, 320), True), 
            Wall((120, 420), False, 200), Wall((100, 510), True, 120), Wall((220, 510), False), Wall((220, 410), True), 
            Wall((320, 410), False), Wall((420, 410), False, 150), Wall((420, 410), True, 200), Wall((520, 310), False, 150), 
            Wall((420, 160), True), Wall((320, 160), False), Wall((420, 600), False, 90), Wall((320, 510), True), 
            Wall((500, 510), True, 120), Wall((500, 510), False), Wall((520, 200), True, 90)
            )
        self.counter = 0
        for sprite in self.walls:
            if self.counter <= 3:
                pass
            else:
                self.walls.add(Wall((1300 - sprite.coords[0], 660 - sprite.coords[1]), sprite.orient, sprite.length, sprite.width, True))
            self.counter += 1

        self.p1score = 0
        self.p2score = 0
        self.font = pygame.font.Font(pygame.font.get_default_font(), 50)
        #self.rects = [self.player1.rect, self.player2.rect]

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.players.draw(self.screen)
        self.walls.draw(self.screen)
        self.lasers.draw(self.screen)
        self.upgrades.draw(self.screen)

        self.screen.blit(self.font.render('Player 1: ' + str(self.p1score), False, (255, 0, 0)), (self.size[0] / 2 - 150, 1))
        self.screen.blit(self.font.render('Player 2: ' + str(self.p2score), False, (0, 0, 255)), (self.size[0] / 2 + 150, 1))
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
                self.lasers.add(LeadProj(updateCoords(20, self.player1.angle, self.player1.coords), 2, (0, 255, 0), self.screen, self.laserLength, 1.25, self.player1.angle,))
                #self.rects.append(self.laserGroups[-1].sprites()[0].rect)
                self.lastShot = pygame.time.get_ticks()
            if keys[pygame.K_m]:
                self.lasers.add(LeadProj(updateCoords(20, self.player2.angle, self.player2.coords), 2, (0, 255, 0), self.screen, self.laserLength, 1.25, self.player2.angle,))
                #self.rects.append(self.laserGroups[-1].sprites()[0].rect)
                self.lastShot = pygame.time.get_ticks()

        self.collideGroups(self.players, self.walls, 'player-wall')
        self.collideGroups(self.lasers, self.walls, 'laser-wall')
        self.collideGroups(self.lasers, self.players, 'laser-player')
        self.collideGroups(self.players, self.players, 'player-player')
        self.collideGroups(self.lasers, self.upgrades, 'player-upgrade')

        pygame.display.flip()

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
                        if resultType == 'laser-player':
                            if collisions[sprite][0] == self.player1:
                                self.p2score += 1
                            if collisions[sprite][0] == self.player2:
                                self.p1score += 1
                            sprite.kill()
                            self.reset()
                        if resultType == 'player-player':
                            if sprite != collisions[sprite][0]:
                                sprite.wallCollide()
                                collisions[sprite][0].wallCollide()
                        if resultType == 'player-upgrade':
                            sprite.upgrade = collisions[sprite][0].color
                            sprite.upgradeTime = pygame.time.get_ticks()
                            collisions[sprite][0].kill()
        
    def reset(self):
       self.player1.reset()
       self.player2.reset()

        # collisions = pygame.sprite.groupcollide(self.lasers, self.walls, False, False)
        # for leadProj in collisions:
        #     if collisions[leadProj].__len__() > 0:
        #         collisions = pygame.sprite.groupcollide(self.lasers, self.walls, False, False, pygame.sprite.collide_mask)
        #         for leadProj in collisions:
        #             if collisions[leadProj].__len__() > 0:
        #                 leadProj.wallCollide(collisions[leadProj])
                        
        
        #pygame.display.update(self.rects)    
Main()
