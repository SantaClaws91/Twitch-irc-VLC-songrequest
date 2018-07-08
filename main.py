import logging
import _thread

from packets import configuration, connect, songrequest, ascii_art, commands, playlist, skip, privatelist
from packets.configuration import config
import os

if not os.path.exists('log'):
    os.makedirs('log')
    
ERROR_LOG_FILENAME = 'log/Error.log'
logging.basicConfig(filename=ERROR_LOG_FILENAME,level=logging.ERROR,)

configuration.request_info(config)

bot = config['irc']['bot']
vlc_path = config['vlc']["vlc_path"]

connect.connect(
    bot['host'],
    bot['port'],
    bot['nick'],
    bot['password']
    )

send = connect.send
ircsock = connect.ircsock
users = 0
mainchannel = config['irc']['channels'][0]
op = connect.define_ops(
    mainchannel.strip('#')
    )

print('operators: ' + ' '.join(op))

_privatelistconfig = config['playlist']['private_playlist']
if _privatelistconfig['autoplay_playlist']:
    _thread.start_new_thread(privatelist.privatelist, (mainchannel.strip('#'), _privatelistconfig['shuffle'],))
    
while True:
    try:       
        ircmsg = ircsock.recv(4096).decode('UTF-8')

        temp = ircmsg.split('\n')
        ircmsg = temp.pop()
    
        for line in temp:
            line = line.rstrip()

            if line.startswith(':jtv MODE '):
                string = line.split(' ')
                if string[3] == '+o':
                    if not string[4] in op:
                        op.append(string[4])

            if line.startswith("PING"):
                send("PONG " + line.split(':')[1] + "\r\n")
            
            data = line.split(' ')
            if len(data) < 2:
                continue
            if data[1] == '001':
                connect.on_connect(config)
                continue
            elif data[1] == '353':
                users+=1
                continue
            elif data[1] == '366':
                commands.chatters_count(users, data[3])
                users = 0
                continue
            if len(data) < 4:
                continue
            user = data.pop(0)
            if '!' in user:
                user = user.split('!')[0][1:]
            method = data.pop(0)
            if method != 'PRIVMSG':
                continue
            commands.command_handling(data, user, op, config)
                
    except:
        logging.exception('Got exception on main handler')
