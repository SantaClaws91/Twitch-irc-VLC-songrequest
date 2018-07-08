from packets import playlist, youtube, songrequest, configuration
import logging
import os

if not os.path.exists('log'):
    os.makedirs('log')

ERROR_LOG_FILENAME = 'log/Error.log'
logging.basicConfig(filename=ERROR_LOG_FILENAME,level=logging.ERROR,)

def privatelist(channel, random):
    config = configuration.readconfig()
    vlc = dict(config['vlc']['web_intf'])
    while True:
        try:
            playerInfo = playlist.getPlayerInfo(
                vlc['host'],
                vlc['password']
                )
            
            if playlist.check_going(playerInfo) == True:
                continue

            youtube_info = youtube.add_private(random)

            songrequest.play_song(youtube_info, channel, channel)
            playlist.auto_resume('',
                                 vlc['host'],
                                 vlc['password'],
                                 'random song...'
                                 )
            
        except Exception:
            logging.exception('Got exception on privatelist')


