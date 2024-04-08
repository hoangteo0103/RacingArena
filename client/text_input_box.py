import pygame

class TextInputBox:
    def __init__(self, x, y, width, height, font, color=pygame.Color('black')):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = ''
        self.font = font
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('dodgerblue') if self.active else pygame.Color('gray')
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def update(self):
        width = max(200, self.font.size(self.text)[0] + 10)
        self.rect.w = width

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        text_surface = self.font.render(self.text, True, pygame.Color('black'))
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        if self.active:
            pygame.draw.rect(screen, pygame.Color('black'), (self.rect.x + 5 + text_surface.get_width(), self.rect.y + 5, 2, text_surface.get_height()))
