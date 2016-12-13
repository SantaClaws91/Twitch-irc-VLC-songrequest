from packets.connect import sendmsg, get_twitch_chatters, get_twitch_info
from packets.safeprint import safeprint
from packets.playlist import current_song_info, skip_song, getPlayList

skip_votes = dict()

def skip_Requirement(config):
    channel = config['irc']['channels'][0].strip('#')
    skip_min = config['playlist']['skip']['skip_minimum']
    viewers = 0
    chatters = 0
    
    math_string = config['playlist']['skip']['skip_conditions']
    if not math_string:
        return skip_min    

    if '{c}' in math_string:
        chatt = get_twitch_chatters(channel)
        if not chatt:
            print("Failed to find chatters count")
            chatters = 0
        else:
            chatters = chatt['chatter_count']
            if not chatters:
                print("Failed to find chatters count")
                chatters = 0
                
    if '{v}' in math_string:
        twitch_info = get_twitch_info('streams', channel)
        if twitch_info:
            viewers = twitch_info['stream']['viewers']
        else:
            print("Failed to find viewer count.")
            viewers = 0
        
    skip_requirement = eval(math_string.format(v=viewers, c=chatters))

    if not skip_requirement:
        skip_requirement = skip_min
        
    if skip_min > skip_requirement:
        skip_requirement = skip_min
        
    return skip_requirement

##    except Exception:
##        print("Math string appears to have failed. Reverting skiprequirement to: {}".format(skip_min))
##        return skip_min

def skip_handling(user, config):
    host = config['vlc']['web_intf']['host']
    password = config['vlc']['web_intf']['password']
    playlist = getPlayList(host, password)
    
    if not playlist:
        return
    
    if user in config['irc']['moderating']['banlist']:
        return

    current_song = current_song_info(playlist)
    id_ = current_song['id']
    title = current_song['name']
    if not current_song:
        return

    if not id_ in skip_votes:
        skip_votes[id_] = dict()
        skip_votes[id_]['requirement'] = skip_Requirement(config)
        skip_votes[id_]['voters'] = []

        for chan in config['irc']['channels']:
            sendmsg(chan, "{} requests to skip song: {}. Need {} more votes"
                    .format(user, title, skip_votes[id_]['requirement'] - 1)
                    )
            
    if user in skip_votes[id_]['voters']:
        return

    skip_requirement = skip_votes[id_]['requirement']
    skip_votes[id_]['voters'].append(user)
    skippers = len(skip_votes[id_]['voters'])

    if not skippers >= skip_requirement:
        if (skip_requirement - skippers) % 3 == 0:
            for chan in config['irc']['channels']:
                sendmsg(
                    chan,
                    "{} requested to skip song: {}. {} more required to skip."
                    .format(skippers, title, skip_requirement - skippers)
                    )
            safeprint("{} requested to skip song: {}. {} more required to skip."
                  .format(user, title, skip_requirement - skippers)
                  )
        return

    msg = '{} users requested to skip song. Now attempting to skip...'.format(skippers)
    print(msg)
    for chan in config['irc']['channels']:
        sendmsg(chan, msg)
    
    skip_song(host, password, playlist)
