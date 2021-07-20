from os import getcwd
import pygame
from win32api import EnumDisplayDevices, EnumDisplaySettings

debug = False
__imagestorage = {}


def get_refresh_rate():
    device = EnumDisplayDevices()
    settings = EnumDisplaySettings(device.DeviceName, -1)
    return getattr(settings, 'DisplayFrequency')


def img(path, suffix='.png', folder='images'):
    return getcwd() + f'\\{folder}\\{path}{suffix}'


def is_hover(mouseloc, loc1, loc2):
    if loc1[0] < mouseloc[0] < loc2[0]:
        if loc1[1] < mouseloc[1] < loc2[1]:
            return True
    return False


def loadimg(path):
    if not __imagestorage.__contains__(path):
        __imagestorage[path] = pygame.image.load(path)
    return __imagestorage[path]


class Player:
    def __init__(self, name):
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.rotation = 0
        self.name = name
        self.prog = []
        self.skin = 'player'
        self.hp = 100

    def draw(self, screen, icon, center, font):
        if isinstance(icon, pygame.Surface):
            new_player = pygame.transform.rotate(icon, self.rotation)
        else:
            new_player = pygame.transform.rotate(loadimg(img(f'skins\\{icon}')), self.rotation)

        # todo: loading the sprite every frame is very laggy

        surfloc = new_player.get_rect(center=center)
        screen.blit(new_player, surfloc)
        surf = font.render(self.name, True, (0, 0, 0))
        screen.blit(surf, (surf.get_rect(midbottom=(center[0], center[1]-40))))
        hpbackgroundrect = (center[0]-25, center[1]-40, 50, 10)
        hpbackgroundrect2 = (center[0]-24, center[1]-39, 48, 8)
        pygame.draw.rect(screen, (0, 0, 0), hpbackgroundrect)
        pygame.draw.rect(screen, (130, 100, 100), hpbackgroundrect2)
        hpbar = (center[0]-24, center[1]-39, self.hp/2-2, 8)
        # noinspection PyTypeChecker
        pygame.draw.rect(screen, (120, 255, 140), hpbar)

    def reset(self):
        self.hp = 100
        self.prog = []
        self.dx = 0
        self.dy = 0

    def pack(self, x, y, packets, skin):
        return {'x': x, 'y': y, 'dx': 0, 'dy': 0, 'rot': self.rotation,
                'name': self.name, 'prog': self.prog, 'packets': packets, 'skin': skin, 'hp': self.hp}

    def unpack(self, box):
        self.x = box['x']
        self.y = box['y']
        self.dx = box['dx']
        self.dy = box['dy']
        self.rotation = box['rot']
        self.name = box['name']
        self.prog = box['prog']
        self.skin = box['skin']
        self.hp = box['hp']


class Particle:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, screen, offsetx, offsety, deltima):
        pygame.draw.circle(screen, (255, 255, 255), (self.x+offsetx, self.y+offsety), self.size)
        self.size -= deltima / 75


# todo:
# add better gameplay (diff blasters)
# disconnect reconnect messages
# marauder server AND client side cmd handling
# fix skins

# FEATURES:
# server connection screen
# fun gameplay? maybe?
# resizable window options
# muliplayer <-- (doesnt crash on fail)
# sounds
# name choosing
# fps sync (NOT vsync)
# fps not reliant on internet latency
# skins
# death system + packet conversation
# server side command prompt

# bug logger:
# packet conversations
# name unavaiblile softlock
#

# dev tools:
# for server -> client packets, put notworlddata as a tag (at the very very end)
# also, 2nd last tag would be the received players
#
#
