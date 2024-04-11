import pygame
from constant import *
# Constants.
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
WIDTH, HEIGHT = 800, 600
FPS = 60
FONT_SIZE = 24
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

NAME_LIMIT = 10

def mul(originTuple, scale):
    return (originTuple[0] * scale, originTuple[1] * scale)

def middle(originCoord, originLen, targetLen, scale = 0.5):
    return (originCoord[0] + (originLen[0] - targetLen[0]) / 2, originCoord[1] + (originLen[1] - targetLen[1]) * scale)

class Player():
    def __init__(self, nickname, position):
        self.nickname = nickname
        self.position = position
        self.points = 0
        self.disqualified = False

    def move(self, steps):
        self.position += steps

class TextInputBox:
    def __init__(self, x, y, width, height, font):
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.inactiveImage = pygame.image.load("../assets/images/bar_here.png")
        self.button = pygame.transform.scale(self.inactiveImage, (width, height))
        self.buttonRect = pygame.Rect(x, y, width, height)

        self.text = ""
        self.font = font
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttonRect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) < NAME_LIMIT:
                    self.text += event.unicode

    def draw(self, screen):
        # Blit the rect.
        screen.blit(self.button, (self.x, self.y))

        # Render the text.
        text_surface = self.font.render(self.text, True, BLACK)
        # Blit the text.
        textY = self.y + (self.height - text_surface.get_height()) / 2
        screen.blit(text_surface, (self.x + 5, textY))
        # Blit the cursor.
        if self.active:
            pygame.draw.rect(screen, BLACK, (self.x + 5 + text_surface.get_width(), textY, 2, text_surface.get_height()))


class Button():
    def __init__(self, activeImage, inactiveImage, initCoord):
        self.activeImage = activeImage
        self.inactiveImage = inactiveImage

        self.image = self.inactiveImage
        self.rect = self.image.get_rect()
        self.rect.topleft = (initCoord[0], initCoord[1])
        self.clicked = False

    def draw(self, gameScreen):
        gameScreen.blit(self.image , (self.rect.x , self.rect.y))

    def isClicked(self, gameScreen): 
        action = False 

        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) :
            self.image = self.activeImage
            if(pygame.mouse.get_pressed()[0] == 1  and self.clicked == False):
                self.clicked = True
                action = True 
        else: 
            self.image = self.inactiveImage
        if(pygame.mouse.get_pressed()[0] == 0): 
            self.clicked = False 
        return action


class GuiButton:
    def __init__(self, pos, content, normal_clr=(0, 196, 0), pressed_clr=(169, 128, 0), min_w=300, callback=None):
        self.pos = pos
        self.callback = callback

        self.content = content
        self.c_w, self.c_h = self.content.get_size()
        self.rect = pygame.Rect(0, 0, max(self.c_w + (GUI_BTN_PAD) * 2, min_w), self.c_h + GUI_BTN_PAD * 2)

        self.hover = False
        self.pressed = False

        self.normal_clr = normal_clr
        self.pressed_clr = pressed_clr

        self.set_pos(self.pos)

    def set_pos(self, pos):
        self.pos = pos
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def draw(self, screen):
        screen.fill((0, 0, 0), self.rect.inflate(GUI_BTN_OUTLINE_W, GUI_BTN_OUTLINE_W))
        screen.fill(self.pressed_clr if self.hover else self.normal_clr, self.rect)
        screen.blit(self.content, transform(center((self.rect.w, self.rect.h), (self.c_w, self.c_h)), self.pos))

    def update(self, events, mouse_pos):
        self.hover = False
        self.pressed = False
        if self.rect.collidepoint(mouse_pos):
            self.hover = True

        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.hover = self.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and self.hover:
                self.pressed = True
                self.callback()


ENTRY_TYPE_TEXT = 0
ENTRY_TYPE_NUM = 1
ENTRY_TYPE_IP = 2

class GuiEntry:
    def __init__(self, pos, font, initial_text="", max_length=12, min_w=300, _type=ENTRY_TYPE_TEXT):
        self.pos = pos

        self.font = font
        self.max_length = max_length
        self.h = self.font.get_height() + GUI_BTN_PAD * 2
        self.w = max(min_w, self.font.size("a" * self.max_length)[0] + GUI_BTN_PAD * 2)

        self.rect = pygame.Rect(*self.pos, self.w, self.h)

        self.input = initial_text
        self.focus = False

        self.type = _type

        self.blink = 0

        self.set_pos(self.pos)

    def set_focus(self, f):
        if type(f) == bool:
            self.focus = f

    def set_pos(self, pos):
        self.pos = pos
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def set_input(self, text):
        self.input = text

    def get(self):
        return self.input

    def update(self, events, mouse_pos):
        pressed = False
        for e in events:
            if e.type == pygame.KEYDOWN and self.focus:
                if e.unicode.isprintable():
                    char = e.unicode

                    if len(self.input) < self.max_length:
                        if self.type == ENTRY_TYPE_NUM:
                            if char.isdigit():
                                self.input += char
                        if self.type == ENTRY_TYPE_IP:
                            if char.isdigit() or char in [".", ":"]:
                                self.input += char
                        if self.type == ENTRY_TYPE_TEXT:
                            self.input += char
                if e.key == 8:
                    self.input = self.input[0:-1]
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == pygame.BUTTON_LEFT:
                pressed = self.rect.collidepoint(mouse_pos)
        return pressed

    def draw(self, screen):
        text_surf = self.font.render(self.input, True, (0, 0, 0))

        if self.focus:
            screen.fill((196, 196, 0), self.rect.inflate(GUI_BTN_OUTLINE_W * 2, GUI_BTN_OUTLINE_W * 2))

        screen.fill((0, 0, 0), self.rect.inflate(GUI_BTN_OUTLINE_W, GUI_BTN_OUTLINE_W))
        screen.fill((160, 160, 160), self.rect)

        screen.blit(text_surf, transform(self.pos, (GUI_BTN_PAD, GUI_BTN_PAD)))

        if self.blink % 20 > 10:
            if self.focus:
                screen.fill((255, 255, 255),
                            pygame.Rect(self.pos[0] + text_surf.get_size()[0] + 5, self.pos[1], 5, self.h - 5))
        self.blink += 1


class EntryFocusManager:
    def __init__(self, entries):
        self.entries = entries
        self.idx = 0
        self.focus_to_idx(self.idx)

    def focus_to_idx(self, i):
        self.idx = i
        for entry in self.entries:
            entry.set_focus(False)

        self.entries[self.idx].set_focus(True)

    def update(self, events, mouse_pos):
        for i, e in enumerate(self.entries):
            if e.update(events, mouse_pos):  ## clicked
                self.focus_to_idx(i)
                return


def transform(pos, pos2):
    return (pos[0] + pos2[0], pos[1] + pos2[1])


def center(container_size, size):
    return ((container_size[0] - size[0]) / 2, (container_size[1] - size[1]) / 2)


def center_horiz(container_size, size, h):
    return (center(container_size, size)[0], h)


def below_title():
    return GUI_PAD * 2 + FONT_TITLE.get_height()