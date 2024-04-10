import pygame
from components import *

class waitingScreen():
    def __init__(self):
        self.running = True

        pygame.init()
        self.screenWidth, self.screenHeight = SCREEN_WIDTH, SCREEN_HEIGHT
        self.gameScreen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        pygame.display.set_caption("Racing Arena")

        self.backgroundImage = pygame.transform.scale(pygame.image.load("../assets/images/e1.png"), (self.screenWidth, self.screenHeight))
        self.backgroundImage2 = pygame.transform.scale(pygame.image.load("../assets/images/p0_blank.png"), mul((self.screenWidth, self.screenHeight), 0.9))

        self.players = [Player("cup", 0), Player("viet", 0), Player("hoang", 0), Player("noob", 0), Player("mmmmmmmmmm", 0), Player("thienngu", 0)]

        self.originCoord = ((self.screenWidth - self.backgroundImage2.get_width()) / 2, (self.screenHeight - self.backgroundImage2.get_height()) / 2)
        self.userInfoLen = (self.backgroundImage2.get_width() / 5, self.backgroundImage2.get_height() / 2)
        self.userInfoBg = pygame.transform.scale(pygame.image.load("../assets/images/d.png"), mul(self.userInfoLen, 0.8))
        self.userInfoAva = pygame.transform.scale(pygame.image.load("../assets/images/p11_user.png"), mul((self.userInfoBg.get_width(), self.userInfoBg.get_width()), 0.7))

        self.listCoords = [(self.originCoord[0] + self.userInfoLen[0] * (i % 5), self.originCoord[1] + self.userInfoLen[1] * (i // 5)) for i in range(10)]
        self.font = pygame.font.Font(None, FONT_SIZE)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            

    def draw(self):
        self.gameScreen.blit(self.backgroundImage, (0, 0))
        self.gameScreen.blit(self.backgroundImage2, self.originCoord)
        for i in range(len(self.players)):
            self.gameScreen.blit(self.userInfoBg, middle(self.listCoords[i], self.userInfoLen, (self.userInfoBg.get_width(), self.userInfoBg.get_height())))
            self.gameScreen.blit(self.userInfoAva, middle(self.listCoords[i], self.userInfoLen, (self.userInfoAva.get_width(), self.userInfoAva.get_height()), 0.4))
            text_surface = self.font.render(self.players[i].nickname, True, BLACK)
            if len(self.players[i].nickname) > 5:
                split_index = 5
                nickname_line1 = self.players[i].nickname[:split_index]
                nickname_line2 = self.players[i].nickname[split_index:]
                
                text_surface_line1 = self.font.render(nickname_line1, True, BLACK)
                text_surface_line2 = self.font.render(nickname_line2, True, BLACK)
                
                text_surface = pygame.Surface((self.userInfoBg.get_width(), text_surface_line1.get_height() * 2), pygame.SRCALPHA)
                text_surface.fill((0, 0, 0, 0))
                text_surface.blit(text_surface_line1, ((self.userInfoBg.get_width() - text_surface_line1.get_width()) / 2, 0))
                text_surface.blit(text_surface_line2, ((self.userInfoBg.get_width() - text_surface_line2.get_width()) / 2, text_surface_line1.get_height()))
            self.gameScreen.blit(text_surface, middle(self.listCoords[i], self.userInfoLen, (text_surface.get_width(), text_surface.get_height()), 0.75))

    def run(self):
        while self.running:
            self.handle_events()

            self.draw()

            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    screen = waitingScreen()
    screen.run()