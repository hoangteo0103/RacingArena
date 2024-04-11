import pygame
from components import *
from waitingScreen import *

class homeScreen():
    def __init__(self):
        self.running = True
        self.isNextScreen = False

        pygame.init()
        self.screenWidth, self.screenHeight = SCREEN_WIDTH, SCREEN_HEIGHT
        self.gameScreen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        pygame.display.set_caption("Racing Arena")

        self.backgroundImage = pygame.transform.scale(pygame.image.load("../assets/images/p3.png"), (self.screenWidth, self.screenHeight))

        nameInputWidth, nameInputHeight = self.screenWidth / 3, 40
        nameInputX, nameInputY = (self.screenWidth - nameInputWidth) / 2, (self.screenHeight - nameInputHeight) / 2
        self.nameInput = TextInputBox(nameInputX, nameInputY, nameInputWidth, nameInputHeight, pygame.font.Font(None, FONT_SIZE))
        self.name = ""
        self.loginButtonSize = (212, 50)
        self.loginButtonCoord = ((self.screenWidth - self.loginButtonSize[0]) / 2, nameInputY + 100)
        self.loginButton = Button(pygame.transform.scale(pygame.image.load("../assets/images/p2_login_here.png"), self.loginButtonSize),
                                  pygame.transform.scale(pygame.image.load("../assets/images/p2_login.png"), self.loginButtonSize),
                                  self.loginButtonCoord)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.nameInput.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.nameInput.text:
                    self.name = self.nameInput.text
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
        
        if self.loginButton.isClicked(self.gameScreen):
            self.name = self.nameInput.text
            self.isNextScreen = True
            self.running = False

    def draw(self):
        self.gameScreen.blit(self.backgroundImage, (0, 0))
        self.nameInput.draw(self.gameScreen)
        self.loginButton.draw(self.gameScreen)

    def run(self):
        while self.running:
            self.handle_events()

            self.draw()

            pygame.display.flip()
        
        pygame.quit()

        if self.isNextScreen == True:
            nextScreen = waitingScreen()
            nextScreen.run()

if __name__ == "__main__":
    screen = homeScreen()
    screen.run()