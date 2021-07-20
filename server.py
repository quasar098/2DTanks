from _thread import start_new_thread
import socket
from json import loads, dumps
from tools import debug


HOST = "192.168.1.13"
PORT = 25565

all_data = {'world data':
            [(0, 0, 500, 1500),
             (1000, 0, 1500, 1500),
             (500, 1000, 1000, 1500),
             (500, 0, 1000, 500), ['say', 'pog', 'notworlddata']]}  # todo: make packets


marauder = []


def cmdprompt():
    supportedcmds = {'/help': 'help im underwater.\t\tusage: /help'}
    while True:
        prompt = input('>>> ')
        if len(prompt.split()) >= 1:
            firstword = prompt.split()[0]
        else:
            firstword = ''
        if firstword in supportedcmds:
            # put cmds
            if firstword == '/help':
                for cmd in supportedcmds:
                    print(f'{cmd}: \t{supportedcmds[cmd]}')
        else:
            print('Command unknown! \tTry /help to see a list of commands')


# noinspection PyUnusedLocal
def client(address, num, _conn):
    prold = None
    data = {'name'}
    times = 0
    while True:
        try:
            data = _conn.recv(32768)
            if data:
                if prold != data:
                    prold = data
                    if debug:
                        print(data)
                        print(all_data)
                data = loads(data)
                if times == 0:
                    if all_data.__contains__(data['name']):  # name already exists
                        _conn.sendall(bytes(dumps(['name active']), encoding='utf8'))
                        break
                times += 1
                all_data[data['name']] = data  # save data from client
                mod_data = all_data.copy()
                for cmd in marauder:
                    if not cmd[len(cmd)-2].__contains__(data['name']):
                        mod_data['world data'].append(cmd)
                        if cmd[len(cmd)-2].__contains__(data['name']):  # tell marauder to not double send
                            cmd[len(cmd)-2].pop(data['name'])  # todo: FIX THIS, it keeps accidentally adding more to worlddata
                            if len(cmd[len(cmd)-2]) == 0:
                                marauder.remove(cmd)
                _conn.sendall(bytes(dumps(mod_data), encoding='utf8'))  # send out all data
        except ConnectionResetError:
            if all_data.__contains__(data['name']):
                all_data.pop(data['name'])
            marauder.append(['removehitbox', data['name'],
                             [player for player in all_data if player != 'world data'], 'notworlddata'])
            break


start_new_thread(cmdprompt, ())

players_amount = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socks:
    socks.bind((HOST, PORT))
    socks.listen()
    while True:
        conn, addr = socks.accept()
        start_new_thread(client, (addr, players_amount, conn))
        players_amount += 1
