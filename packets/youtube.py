from __future__ import unicode_literals
import youtube_dl
import random

global index
index = 0
s = set()

from packets.configuration import config
playlist = config['playlist']['private_playlist']['youtubelink']

def ydl_opts(privatelist=False):
    #from packets.configuration import config
    #format_ = config['youtube']['audio_formats']
    format_ = "251/171/140/bestaudio"
    
    result = {
    'quiet': True,
    'playlist_random': True,
    'youtube_skip_dash_manifest': True,
    'skip_download': True,
    'format': format_
    }
    if privatelist:
        result['playlist_items'] = str(privatelist)
        
    return result

def get_youtube_info(youtube_link, privatelist=False):
    if not youtube_link:
        return
    try:
        with youtube_dl.YoutubeDL(ydl_opts(privatelist)) as ydl:
            result = ydl.extract_info(
                youtube_link,
                download=False
            )
    except Exception:
        print("Failed to download youtube video.")
        return
        
    if 'entries' in result:
        result = result['entries'][0]

    return result


def add_private(random):
    global index
    index += 1

    if random == True:
        return get_youtube_info(playlist, non_repeating_random(200))
    else:
        s.add(index)
        return get_youtube_info(playlist, index)

def non_repeating_random(n):
    if n < len(s):
        return
    while len(s) < n:
        r = random.randint(1,n)
        if r in s:
            continue
        s.add(r)
        return r    
