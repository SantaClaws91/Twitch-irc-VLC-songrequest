import re
import subprocess
from packets import youtube, configuration, playlist
from datetime import datetime
from packets.connect import sendmsg
from packets.safeprint import safeprint
import time

sruser = dict()
songs = dict()

def matchYou(youtubelink):
    r = [
        "^(.{11})$",
        "(?:https:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?"
        ]
    for index in r:
        matchYou = re.match(
            index,
            youtubelink[0]
            )
        if matchYou:
            return matchYou
    return ''

def songrequest(channel, user, op, vlc_path, youtubelink):
    print(
        "\nAttempting to play: {}\nRequested by: {}\n"
        .format(youtubelink, user)
        )

    config = configuration.readconfig()

    if user in config['irc']['moderating']['banlist']:
        print(
            'Request denied, user {} is banned from songrequests'
              .format(user)
              )
        return
    match_You = matchYou(youtubelink)

    if not match_You:
        print("Warning: Did not recognize the link. Will now attempt to search for the song.")
        youtubelink = 'gvsearch1:' + ' '.join(youtubelink)
    else:
        youtubelink = 'https://www.youtube.com/watch?v=' + match_You.group(1)
    
    songrequestdelay = config['irc']['songrequest']['delay']
    maxsongduration = config['youtube']['maxsongduration']

    if not user in op:
        if user in sruser:
            srdelta = datetime.now() - sruser[user]
            if srdelta.total_seconds() < songrequestdelay:
                print("Request denied. User {} is adding songs too quickly"
                      .format(user)
                      )
                return

    youtube_info = youtube.get_youtube_info(youtubelink)
    if not youtube_info:
        return
    youtubelink = "https://www.youtube.com/watch?v=" + youtube_info['id']
    title = youtube_info['title']
    if title:
        safeprint("Video title: {}".format(title))

    category = youtube_info["categories"][0]

    if not config['youtube']['category_whitelist'][0].lower() == 'all':
        if not category in config['youtube']['category_whitelist']:
            safeprint(
                "Request denied. Video titled: {} is not classified as Music".format(title))
            return

    duration = youtube_info['duration']

    if duration > maxsongduration:
        safeprint(
            "Request denied. Video titled: {} is too long. Seconds: {}"
              .format(title, duration)
              )
        return
        
    if youtubelink in songs:
        safeprint(
            "Request by {} denied. Song {} has already been added once."
              .format(user, title)
              )
        return
    
    glink = youtube_info['url']
    
    if not glink.startswith("https://"):
        print(
            "Unknown error occured during converting stream. Update youtube-dl or contact nejtilsvampe."
            )
        return

    sendmsg(channel, title + ", Requested by: "+ user)

    vlc_options = config['vlc']['vlc_options']

    subprocess.Popen(
        [ vlc_path ]
        + vlc_options
        + [
            glink,
            ":meta-title={}".format(title)
            ]
        )

    songs[youtubelink] = {
        'id': len(songs) + 1,
        'link': youtubelink,
        'title': title,
        'uri': glink,
        'duration': duration,
        'category': category,
        'user': user
        }
        
    sruser[user]=datetime.now()

    if config['playlist']['autoresume'] != True:
        return
    
    #Auto Resume Check:
    web_pw = config['vlc']['web_intf']['password']
    web_host = config['vlc']['web_intf']['host']

    if not web_pw:
        return
    
    state = playlist.getPlayerInfo(
        web_host,
        web_pw
        )

    if not 'state' in state:
        return

    if state['state'] != 'stopped':
        return

    time.sleep(0.05)

    playlist.auto_resume(
        glink,
        web_host,
        web_pw,
        title
        )
