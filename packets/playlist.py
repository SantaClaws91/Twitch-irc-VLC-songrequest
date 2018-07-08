import requests
from packets.safeprint import safeprint

from urllib.parse import quote_plus

def request_webvlc(password):
    s = requests.Session()
    s.auth = ('', password)     # Username is blank, just provide the password
    return s

def getPlayerInfo(host, password):
    request = request_webvlc(password)
    try:
        r = request.get(host + 'requests/status.json', verify=False)
        return r.json()
    except Exception:
        return {}
    
def getPlayList(host, password):
    request = request_webvlc(password)
    try:
        r = request.get(host + 'requests/playlist.json', verify=False)
        return r.json()
    except Exception:
        print('Request to load playlist malfunctioned. Make sure vlc settings are configured properly or contact nejtilsvampe')
        print("host: {}\npassword: {}".format(host, password))
        return {}

def send_command(host, password, command):
    request = request_webvlc(password)
    request.get(host + 'requests/status.json' + command, verify=False)

def skip_interm(host, password):
    command = '?command=pl_next'
    send_command(host, password, command)

def stop_song(host, password):
    command = '?command=pl_stop'
    send_command(host, password, command)
    
def skip_song(host, password, playlist):
    if not playlist:
        return
    next_song = next_song_info(playlist)
    if not next_song:
        stop_song(host, password)
        return
    skip_interm(host, password)
    
def play_id(host, password, id_=''):
    command = '?command=pl_play'
    if id_:
        command = command + '&id={}'.format(id_)
    send_command(host, password, command)

def pause_song(host, password):
    command = '?command=pl_forcepause'
    send_command(host, password, command)

#   Unfortunately, adding songs this way doesn't allow me to change the meta data.
#   So for now, do not use this. However, in the future it might allow for remote bots to be an option.
def add_song(mrl, host, password):
    gurl = quote_plus(mrl)
    command = '?command=in_enqueue&input=' + gurl
    send_command(host, password, command)

def current_song_info(playlist):
    if not playlist:
        return
    if not playlist['children']:
        return
    if not playlist['children'][0]['children']:
        return
    playlist = playlist['children'][0]['children']
    
    for current_song in playlist:
        if 'current' in current_song:
            return current_song
    print('Skip request denied, playlist has stopped.')
    return {}

def next_song_info(playlist):
    current_song = current_song_info(playlist)
    if not current_song:
        return

    if not playlist:
        return
    if not playlist['children']:
        return
    if not playlist['children'][0]['children']:
        return
    playlist = playlist['children'][0]['children']
    
    nextsongid = int(current_song['id']) + 1
    for next_song in playlist:
        if int(next_song['id']) == nextsongid:
            return next_song
    return {}

def check_going(playerinfo):
    if not 'state' in playerinfo:
        return False
    if playerinfo['state'] == 'stopped':
        return False
    return True

def auto_resume(glink, host, password, title):
    print('Attempting auto-resume...')
    id_ = ''
    playlist_ = getPlayList(host, password)
    playlist_ = playlist_['children'][0]['children']

    for added_song in playlist_:
        if (added_song['uri'] == glink
        or added_song['name'].startswith('https://')):  #Failsafe workaround (Not perfect)
            id_ = added_song['id']
            break
    if id_:
        play_id(host, password, id_)
        if title:
            safeprint('Attempting to resume with the song: {}, playlist id: {}'
                  .format(title, id_)
                  )
        else:
            print('Attempting to resume playlist. Playlist id: {}'
                  .format(id_)
                  )
        return
    print('Unknown error occured during auto-resume.')
    print('Attempting workaround...')

    play_id(host, password, '')
    skip_song(host, password, playlist_)
