import sys
import pygame
import math
import random

pygame.mixer.pre_init(16500, -16, 3, 2048)
pygame.init()

def updateCoords(speed, angle, coords, backwards = False):
    angle %= 360
    deltaCoords = [speed * math.cos(math.radians(angle)), -speed * math.sin(math.radians(angle))]
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
    def __init__(self, playerNumb, coords, speed, turnSpeed, image, mapSize):
        pygame.sprite.Sprite.__init__(self)
        self.mapSize = mapSize
        self.speed = speed
        self.turnSpeed = turnSpeed
        self.playerNumb = playerNumb
        self.originalImage = pygame.transform.scale(pygame.image.load(image).convert(), (30, 30))
        self.originalImage.set_colorkey((0, 0, 0))
        self.image = self.originalImage
        self.rect = self.image.get_rect()
        self.coords = self.prevCoords = self.rect.center = coords
        self.angle = self.prevAngle = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.upgrade = None
        self.upgradeCounter = 0

    def update(self, keys):
        self.prevCoords = self.coords
        self.prevAngle = self.angle
        if self.playerNumb == 1:
            if keys[pygame.K_t]:
                self.coords = updateCoords(self.speed, self.angle, self.coords)
            if keys[pygame.K_f]:
                self.angle += self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_h]:
                self.angle -= self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_g]:
                self.coords = updateCoords(self.speed, self.angle, self.coords, True)
                
        if self.playerNumb == 2:
            if keys[pygame.K_UP]:
                self.coords = updateCoords(self.speed, self.angle, self.coords)
            if keys[pygame.K_LEFT]:
                self.angle += self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_RIGHT]:
                self.angle -= self.turnSpeed
                self.angle %= 360
                self.rotate()
            if keys[pygame.K_DOWN]:
                self.coords = updateCoords(self.speed, self.angle, self.coords, True)

        self.rect.center = self.coords

        if self.upgradeCounter == 0:  
            self.upgrade = None

    def rotate(self):
        center = self.rect.center
        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.mask = pygame.mask.from_surface(self.image)

    def collide(self):
        self.coords = self.prevCoords
        self.angle = self.prevAngle

    def reset(self):
        self.coords = self.prevCoords = self.rect.center = random.randint(0, self.mapSize[0]), random.randint(60, self.mapSize[1])
        self.angle = 0
        self.rotate()
        self.upgradeCounter = 0

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
        self.subProj = None
        
    def update(self):
        self.prevCoords = self.coords
        if self.length > 0:
            if not self.spawned:
                self.subProj = SubProj(self.prevCoords, self.radius, self.color, self.screen, self.length - 1, self)
                self.spawned = True
            self.subProj.update()
    
class LeadProj(Projectile):
    def __init__(self, coords, radius, color, screen, length, speed, angle, player, timer = 1100):
        super().__init__(coords, radius, color, screen, length - 1)
        self.speed = speed
        self.angle = angle
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.frames = 0
        self.timer = timer
        self.player = player
        self.projUpgrade = player.upgrade
        if player.upgrade == 'passWall':    
            self.player.upgradeCounter -= 1
        
    def update(self):
        self.frames += 1
        super().update()
        self.rect.center = self.coords = updateCoords(self.speed, self.angle, self.coords)
        if self.frames == self.timer:
            self.kill()

    def wallCollide(self, wall):
        if self.projUpgrade != 'passWall':
            if wall.orient:
                self.angle = 360 - self.angle
                print('dis is also wron')

            if not wall.orient:
                print(self.angle)
                if 0 <= self.angle <= 180:
                    self.angle = 180 - self.angle
                elif 180 < self.angle <= 360:
                    print('dis is wron')
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

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, color, coords, upType):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.image.set_colorkey((0, 0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        print(coords)
        self.rect.center = coords
        self.upType = upType
    
class Game:
    def __init__(self, size, laserLength = 10, cooldown = 500):
        self.size = size
        self.laserSound = pygame.mixer.Sound('C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/laserShotSound.wav')
        self.laserBounceSound = pygame.mixer.Sound('C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/laserBounceSound.wav')
        self.explosionSound = pygame.mixer.Sound('C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/explosionSound.wav')
        self.laserLength = laserLength
        self.cooldown = cooldown
        self.lastShot = -cooldown
        self.screen = pygame.display.set_mode(size)
        self.player1 = Player(1, (0, 0), 0.6, 0.5, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/red tank.png', size)
        self.player2 = Player(2, (0, 0), 0.6, 0.5, 'C:/Users/andre/OneDrive - AARHUS TECH/Programmering/ExamProgram/blue tank.png', size)
        #self.player1 = Player(1, (650, 300), 0.5, 0.5, 'C:/Users/WaffleFlower/Desktop/Skole/Programmering/ExamProgram/red_tank_exp_v2.png')
        #self.player2 = Player(2, (300, 300), 0.5, 0.5, 'C:/Users/WaffleFlower/Desktop/Skole/Programmering/ExamProgram/blue_tank_exp.png')
        self.players = pygame.sprite.Group(self.player1, self.player2)
        self.fixPlayerSpawn()
        self.lasers = pygame.sprite.Group()
        self.upgrades = pygame.sprite.Group()
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
        counter = 0
        for sprite in self.walls:
            if counter <= 3:
                pass
            else:
                self.walls.add(Wall((1300 - sprite.coords[0], 660 - sprite.coords[1]), sprite.orient, sprite.length, sprite.width, True))
            counter += 1

        self.p1score = 0
        self.p2score = 0
        self.scoreFont = pygame.font.Font(pygame.font.get_default_font(), 50)
        self.upgradeFont = pygame.font.Font(pygame.font.get_default_font(), 10)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.players.draw(self.screen)
        self.walls.draw(self.screen)
        self.lasers.draw(self.screen)
        self.upgrades.draw(self.screen)

        self.screen.blit(self.scoreFont.render('Player 1: ' + str(self.p1score), False, (255, 0, 0)), (self.size[0] / 2 - 150, 1))
        self.screen.blit(self.scoreFont.render('Player 2: ' + str(self.p2score), False, (0, 0, 255)), (self.size[0] / 2 + 150, 1))
        
        for player in self.players:
            if player.upgrade:
                self.screen.blit(self.upgradeFont.render('UPGRADED!', False, (255, 255, 0)), (player.rect.topleft[0] - 11, player.rect.topleft[1] - 11))

    def update(self):
        keys = pygame.key.get_pressed()
        self.players.update(keys)
        self.lasers.update()
        if pygame.time.get_ticks() > self.lastShot + self.cooldown:
            if keys[pygame.K_q]:
                self.lasers.add(LeadProj(updateCoords(20, self.player1.angle, self.player1.coords), 2, (0, 255, 0), self.screen, self.laserLength, 1.25, self.player1.angle, self.player1))
                self.laserSound.play()
                self.lastShot = pygame.time.get_ticks()
            if keys[pygame.K_m]:
                self.lasers.add(LeadProj(updateCoords(20, self.player2.angle, self.player2.coords), 2, (0, 255, 0), self.screen, self.laserLength, 1.25, self.player2.angle, self.player2))
                self.laserSound.play()
                self.lastShot = pygame.time.get_ticks()

        self.collideGroups(self.players, self.walls, 'player-wall')
        self.collideGroups(self.lasers, self.walls, 'laser-wall')
        self.collideGroups(self.lasers, self.players, 'laser-player')
        self.collideGroups(self.players, self.players, 'player-player')
        self.collideGroups(self.players, self.upgrades, 'player-upgrade')

        self.spawnUpgrade(10000)
        pygame.display.flip()

    def collideGroups(self, group1, group2, resultType):
        collisions = pygame.sprite.groupcollide(group1, group2, False, False)
        for sprite in collisions:
            collisions = pygame.sprite.groupcollide(group1, group2, False, False, pygame.sprite.collide_mask)
            for sprite in collisions:
                if resultType == 'player-wall':
                    sprite.collide()
                if resultType == 'laser-wall':
                    sprite.wallCollide(collisions[sprite][0])
                    self.laserBounceSound.play()
                if resultType == 'laser-player':
                    if collisions[sprite][0] == self.player1:
                        self.p2score += 1
                    if collisions[sprite][0] == self.player2:
                        self.p1score += 1
                    self.explosionSound.play()
                    sprite.kill()
                    self.reset()
                if resultType == 'player-player':
                    if sprite != collisions[sprite][0]:
                        sprite.collide()
                        collisions[sprite][0].collide()
                if resultType == 'player-upgrade':
                    sprite.upgrade = collisions[sprite][0].upType
                    sprite.upgradeCounter = 3
                    collisions[sprite][0].kill()
        
    def reset(self):
        self.player1.reset()
        self.player2.reset()
        self.fixPlayerSpawn()
        self.upgrades.empty()
        self.lasers.empty()

    def fixPlayerSpawn(self):
        spawnCoords = [(50, 105), (90, 400), (150, 550), (160, 90), (400, 200), (550, 450), (700, 410), 
            (1000, 400), (1120, 110), (1150, 570), (1200, 110)]
        loop = True
        while loop:
            for firstPlayer in self.players:
                numb = random.randint(0, len(spawnCoords) - 1)
                firstPlayer.prevCoords = firstPlayer.coords = firstPlayer.rect.center = spawnCoords[numb]
                for secPlayer in self.players:
                    if firstPlayer != secPlayer:
                        if firstPlayer.rect.center == secPlayer.rect.center:
                            numb = random.randint(0, len(spawnCoords) - 1)
                            firstPlayer.prevCoords = firstPlayer.coords = firstPlayer.rect.center = spawnCoords[numb]
                        else:
                            loop = False

    def fixUpgradeSpawn(self, group1, group2):
        loop = True
        while loop:
            collisions = pygame.sprite.groupcollide(group1, group2, False, False, pygame.sprite.collide_mask)
            for sprite in collisions:
                if sprite != collisions[sprite][0]:
                    sprite.prevCoords = sprite.coords = sprite.rect.center = random.randint(0, self.size[0]), random.randint(60, self.size[1])
            if collisions == {} or sprite == collisions[sprite][0]:
                loop = False
    

    def spawnUpgrade(self, prob):
        numb = random.randint(1, prob)
        if numb == 1:
            tempGroup = pygame.sprite.Group(Upgrade((255, 255, 0), (random.randint(0, self.size[0]), random.randint(60, self.size[1])), 'passWall'))
            self.fixUpgradeSpawn(tempGroup, self.walls)
            self.fixUpgradeSpawn(tempGroup, self.players)
            self.upgrades.add(tempGroup.sprites()[-1])

Main()