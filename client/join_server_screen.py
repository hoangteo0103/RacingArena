import pygame
from pygame.locals import *
from components import *
from  constant import  *
from menu_screen import *
import socket

from racing_client import *


class JoinServerScreen:
    def __init__(self, screen, join_callback, back_callback):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.join_callback = join_callback
        self.back_callback = back_callback
        self.client = None


        menu_entry_w = 500
        entry_x = (WIDTH - menu_entry_w) / 2
        place_y = 50  # Adjust this as needed

        self.entry_ip = GuiEntry((entry_x, place_y), self.font, initial_text="127.0.0.13", min_w=menu_entry_w, max_length=30, _type=ENTRY_TYPE_TEXT)
        place_y += 60  # Padding
        self.entry_name = GuiEntry((entry_x, place_y), self.font, initial_text="newbie", min_w=menu_entry_w, max_length=25, _type=ENTRY_TYPE_TEXT)
        place_y += 60  # Padding

        self.btn_entry_join = GuiButton((entry_x, place_y), self.font.render("Join", True, (0, 0, 0)), min_w=menu_entry_w)
        place_y += 70  # Padding

        self.btn_entry_back = GuiButton((GUI_BTN_PAD, GUI_BTN_PAD), self.font.render("Back", True, (0, 0, 0)), min_w=120, callback=self.back_callback)
        self.entry_err_txt = None
        self.menu_entry_focus = EntryFocusManager([self.entry_ip, self.entry_name])
        self.server = None

    def join_server(self):
        ## parse input
        ip = self.entry_ip.get()
        port = 1337
        if ":" in ip:
            ip, port = ip.split(":")[0:2]
            port = int(port)

        nick = self.entry_name.get()

        err_string = None
        try:
            print("HEHEHR")
            self.client = RacingClient(ip, port)
            print("GETHERRE")
            response = self.client.register(nick)
            print(response)
            if "Successfully" in response:
                self.join_callback(self.client)
            else:
                raise Exception(response)
            # self.join_callback()

        ## connection errors
        except Exception as e:
            err_string = str(e)
        except ConnectionRefusedError:
            err_string = "Error: Connection refused!"
        except OSError as e:
            print(e)
            ## fuck errno.h
            ## !!!!!
            known_winerrors = {11001: "Error: Invalid address!",
                               10048: "Error: Address already in use.",
                               10049: "Error: Cannot bind/connect to this address.",
                               10060: "Error: Timed out."}

            if e.errno in known_winerrors:
                err_string = known_winerrors[e.errno]
            else:
                err_string = "Invalid error :("
        except socket.timeout:
            err_string = "Error: Timed out!"
        except socket.gaierror:
            err_string = "Error: Invalid address!"
        print(err_string)
        if not err_string is None:
            self.entry_err_txt = FONT_ACCENT.render(err_string, True, (0, 0, 0))
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()

        self.btn_entry_join.update(events, mouse_pos)
        self.btn_entry_back.update(events, mouse_pos)

        if self.btn_entry_join.pressed:
            self.join_server()
        self.menu_entry_focus.update(events,mouse_pos)
        return True

    def draw(self):
        self.screen.fill((255, 255, 255))

        title_text = FONT_SMALL_ACCENT.render("Create Server", True, (0, 0, 0))
        self.screen.blit(title_text, (200, 20))
        if not self.entry_err_txt is None:
            self.screen.blit(self.entry_err_txt, center_horiz((WIDTH, HEIGHT), self.entry_err_txt.get_size(),
                                                    self.btn_entry_join.pos[1] + self.btn_entry_join.rect.h + GUI_PAD))

        self.entry_ip.draw(self.screen)
        self.entry_name.draw(self.screen)

        self.btn_entry_join.draw(self.screen)
        self.btn_entry_back.draw(self.screen)


        pygame.display.flip()
