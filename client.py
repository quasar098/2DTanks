from tools import *
from math import pi, atan2
from _thread import start_new_thread
import socket
from json import dumps, loads
from math import sin, cos
from time import sleep as wait
from pygameinfo import *
# noinspection PyUnresolvedReferences
from random import randint as rand
from os import listdir

self_name = 'Please enter name'
self_player = Player(str(self_name))

pygame.init()

entering_username = False
online = False
connecting = False
screen_stage = 0  # 0 = enter name, 1 = play game

width = 1280
height = 720
halfw = int(width/2)
halfh = int(height/2)
screen = pygame.display.set_mode([width, height])
pygame.display.set_icon(pygame.image.load(img('icon', suffix='.ico')))
pygame.display.set_caption('Funny Shoot Game (by quasar098)')
font = pygame.font.SysFont('Arial', 20)

fps = get_refresh_rate()
tick = 0
clock = pygame.time.Clock()

x = 100
y = 100
dx = 0
dy = 0
speed = 1
proj_speed = 10
shootcooldown = 0

possibleskins = [x[:-4] for x in listdir(f'images\\skins')]
skin = 'player'
skinitem = 0
player = pygame.image.load(img(f'skins\\{skin}'))
logo = pygame.image.load(img('logo')).convert_alpha()
world_data = [(0, 0, 200, 200)]

HOST = '192.168.1.13'
PORT = 25565

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

send_data = self_player.pack(x, y, [], skin)
incomingpackets = []
other_data = {}
other_players = {}
explosion_particles = []
packets = []
lasthit = 'null null null'

mixerstorage = {}
soundplayer = []
for i in range(0, 8):
    soundplayer.append(pygame.mixer.Channel(i))


def play_sound(name, suffix='.wav', vol=0.2):
    count = 0
    for channel in soundplayer:
        count += 1
        if not channel.get_busy():
            if not mixerstorage.__contains__(name):
                mixerstorage[name] = pygame.mixer.Sound(f'{getcwd()}\\sounds\\{name}{suffix}')
                mixerstorage[name].set_volume(vol)
            channel.play(mixerstorage[name])
            break


def connect_thread():
    global online
    global screen_stage
    global connecting
    global self_player
    self_player = Player(str(self_name))
    add_info_text('Attempting to connect to server...', font, fps)
    connecting = True
    wait(0.1)
    try:
        s.connect((HOST, PORT))
        online = True
        screen_stage = 1
        add_info_text('Connection Succesful', font, fps)
    except WindowsError as errno:
        online = False
        if errno.errno == 10061:
            add_info_text('(Server Offline)', font, fps)
        else:
            add_info_text('Try restarting your game', font, fps)
        add_info_text('Connection Failed', font, fps)
    finally:
        connecting = False


def packet_thread():
    global other_data
    global online
    global screen_stage
    global send_data
    global self_player
    global world_data
    global incomingpackets
    self_player = Player(str(self_name))
    prold = None
    keep_pressing_send = True
    while keep_pressing_send:
        if online:
            send_data = self_player.pack(x, y, packets, skin)
            s.sendall(bytes(dumps(send_data), encoding='utf8'))
            raw_data = loads(s.recv(32768))
            if isinstance(raw_data, list):
                add_info_text('Username unavailable', font, fps)
                online = False
                screen_stage = 0
                s.detach()
                keep_pressing_send = False
            else:
                other_data = raw_data
                world_data = [d for d in raw_data['world data'] if d[len(d)-1] != 'notworlddata']
                incomingpackets = [d for d in raw_data['world data'] if d not in world_data]
            if prold != other_data:
                prold = other_data
                if debug:
                    print(other_data)
        else:
            wait(1/fps)


start_new_thread(packet_thread, ())
running = True
while running:

    player = pygame.image.load(img(f'skins\\{possibleskins[divmod(skinitem, len(possibleskins))[1]]}'))

    if screen_stage == 1:

        # ACTUAL GAME
        tick += 1/fps
        shootcooldown -= 1
        packets = []
        screen.fill((200, 200, 200))
        mouseLoc = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if pygame.mouse.get_pressed(3)[0]:
            if shootcooldown <= 0:
                shootcooldown = fps/10
                play_sound('hit')
                atan_thing = atan2(mouseLoc[1]-height/2, mouseLoc[0]-width/2)
                thing = [x, y, (cos(atan_thing), sin(atan_thing)), self_player.dx, self_player.dy]
                self_player.prog.append(thing)

        # movement
        if pygame.key.get_pressed()[pygame.K_w]:
            self_player.dy -= 75/fps * speed
        if pygame.key.get_pressed()[pygame.K_d]:
            self_player.dx += 75/fps * speed
        if pygame.key.get_pressed()[pygame.K_s]:
            self_player.dy += 75/fps * speed
        if pygame.key.get_pressed()[pygame.K_a]:
            self_player.dx -= 75/fps * speed

        x += self_player.dx
        xbox = 0
        for box in world_data:
            if box[0] < x < box[2]:
                if box[1] < y < box[3]:
                    xbox += 1
        if xbox == 0:
            x -= self_player.dx
            self_player.dx = 0

        y += self_player.dy
        ybox = 0
        for box in world_data:
            if box[0] < x < box[2]:
                if box[1] < y < box[3]:
                    ybox += 1
        if ybox == 0:
            y -= self_player.dy
            self_player.dy = 0

        self_player.dx *= 0.9
        self_player.dy *= 0.9

        # boxes
        for box in world_data:
            pygame.draw.rect(screen, (25, 25, 255), (box[0]-x+halfw-1, box[1]-y+halfh-1,
                                                     box[2]-box[0]+2, box[3]-box[1]+2))

        # particles draw
        for particle in explosion_particles:
            particle.draw(screen, -x+halfw, -y+halfh, fps)
            if particle.size <= 0:
                explosion_particles.remove(particle)

        # other players
        if other_data.__contains__(str(self_name)):
            other_data.pop(str(self_name))
        if other_data.__contains__('world data'):
            other_data.pop('world data')

        playerlist = list(other_players.copy().keys())
        if playerlist.__contains__(str(self_name)):
            playerlist.remove(str(self_name))
        if playerlist.__contains__('world data'):
            playerlist.remove('world data')

        for cmd in incomingpackets:  # marauder recieveing end
            if cmd[0] == 'removehitbox':
                if other_players.__contains__(cmd[1]):  # remove corpses
                    other_players.pop(cmd[1])
            elif cmd[0] == 'say':
                add_info_text(cmd[1], font, fps, noise='key')

        for player_ in other_data:
            if not other_players.__contains__(player_):
                other_players[player_] = Player(player_)
            if player_ == 'world data':
                continue
            if player_ == str(self_name):
                continue
            player_p = other_players[player_]
            player_p.unpack(other_data[player_])
            player_p.x += player_p.dx*1
            player_p.y += player_p.dy*1
            player_p.draw(screen, other_data[player_]['skin'], (player_p.x-x+halfw, player_p.y-y+halfh), font)
            if other_data[player_]['packets']:
                if other_data[player_]['packets'][0].__contains__('playerhit'):
                    if other_data[player_]['packets'][0]['playerhit'][0] == str(self_name):
                        # self_player has been shot
                        packet = other_data[player_]['packets'][0]['playerhit']
                        lasthit = player_
                        self_player.dx = packet[1][0] * proj_speed/2
                        self_player.dy = packet[1][1] * proj_speed/2
                        explosion_particles.append(Particle(packet[2][0], packet[2][1], 15))
                        self_player.hp -= packet[3]
                if other_data[player_]['packets'][0].__contains__('playerdeath'):
                    # other player died, send client message that it happen
                    add_info_text(f'{player_} was killed by {other_data[player_]["packets"][0]["playerdeath"][0]}',
                                  font, fps)
            for px in player_p.prog:
                if 0 < px[0] < width:
                    if 0 < px[1] < height:
                        pygame.draw.rect(screen, (250, 58, 70), (px[0]+halfw+x*-1-5, px[1]+halfh+y*-1-5, 10, 10))

        # bullet loop
        for i in self_player.prog:
            doremove = False
            i[0] += i[2][0] * proj_speed * 75/fps + i[3]*0.2
            i[1] += i[2][1] * proj_speed * 75/fps + i[4]*0.2

            boxes = 0
            for box in world_data:
                if box[0] < i[0] < box[2]:
                    if box[1] < i[1] < box[3]:
                        boxes += 1
            if boxes == 0:
                doremove = True

            for player_ in other_players:
                player_ = other_players[player_]
                hitbox = pygame.rect.Rect(player_.x-25, player_.y-25, 50, 50)
                if hitbox.collidepoint(i[0], i[1]):
                    doremove = True
                    packets.append({'playerhit': [str(player_.name), i[2], (i[0], i[1]), 2]})
                    # convey bullet momemtum and x y

                    # todo: add different weapons, dodging, abilities, loot crates, powerups, etc

            bulletloc = (i[0]+halfw+x*-1-5, i[1]+halfh+y*-1-5, 10, 10)
            if 0 < bulletloc[0] < width:
                if 0 < bulletloc[1] < height:
                    pygame.draw.rect(screen, (7, 8, 9), bulletloc)
            if doremove:
                play_sound('boom', vol=0.1)
                self_player.prog.remove(i)
                explosion_particles.append(Particle(i[0], i[1], 15))

        # self draw
        self_player.draw(screen, player, (width/2, height/2), font)
        self_player.x = width/2
        self_player.y = height/2
        self_player.rotation = atan2(mouseLoc[1]-height/2, mouseLoc[0]-width/2)*-180/pi-90
        if self_player.hp <= 0:
            # die :(
            self_player.reset()
            add_info_text(f'You were killed by {lasthit}', font, fps)
            packets.append({'playerdeath': [lasthit]})
            x = 100
            y = 100

        info_put(screen)
        clock.tick(fps)
        pygame.display.flip()

    elif screen_stage == 0:
        # WAIT SCREEN
        play_online_surf = font.render('Play online', True, (0, 0, 0))
        choose_skin_1 = font.render('Choose your skin', True, (0, 0, 0))
        choose_skin_2 = font.render('with scrollwheel', True, (0, 0, 0))
        play_on_rect = play_online_surf.get_rect(center=(halfw, halfh*1.2))
        username_rect = play_online_surf.get_rect(center=(halfw, halfh*1.4))
        logo_loc = logo.get_rect(center=(halfw, halfh*0.6))
        screen.fill((255, 255, 255))
        mouseLoc = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not connecting:
                        if is_hover(mouseLoc, (username_rect[0]-50, username_rect[1]-10),
                                    (username_rect[0]+username_rect[2]+90, username_rect[1]+username_rect[3]+20)):
                            entering_username = True
                            if self_name == 'Please enter name':
                                self_name = ''
                        else:
                            entering_username = False
                            if self_name == '':
                                self_name = 'Please enter name'
                        if is_hover(mouseLoc, (play_on_rect[0]-10, play_on_rect[1]-10),
                                    (play_on_rect[0]+play_on_rect[2]+10, play_on_rect[1]+play_on_rect[3]+10)):
                            if self_name != 'Please enter name' and self_name != '%data':
                                # join
                                start_new_thread(connect_thread, ())
                            else:
                                add_info_text('Please enter name', font, fps)
                if event.button == 4:
                    skinitem += 1
                if event.button == 5:
                    skinitem -= 1

            if event.type == pygame.KEYDOWN:
                if entering_username:
                    if event.unicode in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_0987654321':
                        if len(self_name) < 20:
                            self_name += event.unicode
                    if event.key == pygame.K_BACKSPACE:
                        self_name = self_name[:-1]

        # skin show
        screen.blit(player, (20, 20))
        screen.blit(choose_skin_1, (10, 80))
        screen.blit(choose_skin_2, (10, 100))

        # play online button
        pygame.draw.rect(screen, (88, 111, 107), (play_on_rect[0]-10, play_on_rect[1]-10,
                                                  play_on_rect[2]+20, play_on_rect[3]+20))
        if entering_username:
            pygame.draw.rect(screen, (88, 145, 185), (username_rect[0]-41, username_rect[1]-11,
                                                      username_rect[2]+92, username_rect[3]+22))
        else:
            pygame.draw.rect(screen, (88, 211, 85), (username_rect[0]-40, username_rect[1]-10,
                                                     username_rect[2]+90, username_rect[3]+20))
        screen.blit(play_online_surf, play_on_rect)
        screen.blit(logo, logo_loc)
        username_surf = font.render(self_name, True, (0, 0, 0))
        username_surf_rect = username_surf.get_rect(topleft=username_rect.topleft)
        username_surf_rect[0] -= 30
        screen.blit(username_surf, username_surf_rect)

        info_put(screen)
        clock.tick(fps)
        pygame.display.update()
pygame.quit()
