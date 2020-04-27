import sys
import pygame

pygame.init()

class Player:
    def __init__(self, xPos, yPos, radius):
        self.xPos = xPos
        self.yPos = yPos
        self.radius = radius
    
    def update(self):
        if self.xPos < 0:
            self.xPos = 0 + self.radius

class MainFrame:
    def __init__(self):
        self.size = self.width, self.height = 1300, 700
        self.speed = [2, 2]
        self.black = 0, 0, 0

        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("INSERT TITLE")

        self.ball = pygame.image.load("C:/Users/WaffleFlower/Picture/Emojis/lenny.png")    # For ur mom's PC
        #self.ball = pygame.image.load("C:/Users/andre/OneDrive/Billeder/Wrench.png")      # For Andreas' PC
        self.ballrect = self.ball.get_rect()

    def draw(self):
        print("do stuff")

    def update(self):
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

            self.ballrect = self.ballrect.move(self.speed)
            if self.ballrect.left < 0 or self.ballrect.right > self.width:
                self.speed[0] = -self.speed[0]
            if self.ballrect.top < 0 or self.ballrect.bottom > self.height:
                self.speed[1] = -self.speed[1]

            self.screen.fill(self.black)
            self.screen.blit(self.ball, self.ballrect)
            pygame.display.flip()

game = MainFrame()
game.draw()
game.update()