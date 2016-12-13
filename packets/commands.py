from packets.configuration import readconfig, writeconfig, config
from packets.playlist import next_song_info, skip_song, current_song_info, getPlayList, request_webvlc
from packets.connect import sendmsg, request_userlist, get_twitch_chatters
from packets.songrequest import songrequest
from packets.skip import skip_handling

channelusers = dict()

def ban(user, op, nick):
    config = readconfig()
    banlist = config['irc']['moderating']['banlist']
    if nick in banlist:
        return
    if user in op:
        banlist.append(nick)
        writeconfig(config)
        print('user {} has banned: {}\n'.format(user, nick))

def unban(user, op, nick):
    config = readconfig()
    banlist = config['irc']['moderating']['banlist']
    if nick in banlist:
        if user in op:
            banlist.remove(nick)
            writeconfig(config)
            print('user {} has unbanned: {}\n'.format(user, nick))

def current_song(playlist):
    current_song = current_song_info(playlist)
    if not current_song:
        return
    if not current_song['name']:
        return
    title = current_song['name']

    from packets.configuration import config
    
    if not title.startswith('https://'):
        for chan in config['irc']['channels']:
            sendmsg(chan,
                    "Current song is: {}"
                    .format(title)
                    )
        
def nextsong(playlist):
    config = readconfig()
    next_song = next_song_info(playlist)
    if not next_song:
        return

    if not next_song['name'].startswith("https://"):
        for chan in config['irc']['channels']:
            sendmsg(chan,
                    "Next song is: {}"
                    .format(next_song['name'])
                    )
        return
    
    from packets.songrequest import songs
    if not songs:
        return

    for song in songs:
        if songs[song]['uri'] == next_song['uri']:
            for chan in config['irc']['channels']:
                sendmsg(chan,
                        "Next song is: {}"
                        .format(songs[song]['title'])
                        )
            return

def Edit_skip_conditions(user, op, arg):
    config = readconfig()
    print("{} attempted to edit skip conditions"
          .format(user)
          )
    if user in config['irc']['moderating']['banlist']:
        print("{} appears to be banned"
              .format(user)
              )
        return
    if not user in op:
        print("{} does not have op"
              .format(user)
              )
        return
    
    config['playlist']['skip']['skip_conditions'] = ' '.join(arg)
    writeconfig(config)
    print("{} has edited skip conditions to: {}"
          .format(user, ' '.join(arg))
          )
    
def skip_song_op(user, op, host, password, playlist, extra_priv):
    if not extra_priv:
        return
    if user in op:
        current_song = current_song_info(playlist)
        title = current_song['name']
        for chan in config['irc']['channels']:
            sendmsg(chan, "{} skipped song: {}."
                    .format(user, title)
                    )
            skip_song(host, password, playlist)
            return

def chatters(channel):
    request_userlist(channel)
    return channelusers[channel]

def chatters_count(users, channel):
    channelusers[channel] = users

def command_handling(data, user, op, config):
    channel = data.pop(0)
    command = data.pop(0)[1:]
    command.lower()
    arguments = data
    web_pw = config['vlc']['web_intf']['password']
    web_host = config['vlc']['web_intf']['host']

    #Non admin commands:
    if command == '!chatters':
        sendmsg(
            '#nejtilsvampe',
            "There are {} users on {}"
            .format(chatters('#bitey'), '#bitey')
            )
        return

    elif command == '!skip':
        config = readconfig()
        skip_handling(user, config)
        return

    elif command == '!currentsong':
        playlist_ = getPlayList(web_host, web_pw)
        current_song(playlist_)
        return

    elif command == '!nextsong':
        playlist_ = getPlayList(web_host, web_pw)
        nextsong(playlist_)
        return

    elif command in config['irc']['songrequest']['cmd']:
        if not arguments:
            return
        songrequest(channel, user, op, config['vlc']['vlc_path'], arguments)
        return
        
    #Admin commands:
    elif command == '#sr.ban':
        addbanlist(user, op, arguments[0])
        return
        
    elif command == '#sr.unban':
        removebanlist(user, op, arguments[0])
        return
        
    elif command == '#skip':
        extra_priv = config['irc']['moderating']['extra_op_privileges']
        playlist_ = getPlayList(web_host, web_pw)
        skip_song_op(
            user,
            op,
            web_host,
            web_pw,
            playlist_,
            extra_priv
            )
        return

    elif command == '#skipcondition':
        Edit_skip_conditions(user, op, arguments)
        return
