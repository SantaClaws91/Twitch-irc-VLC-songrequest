from __future__ import unicode_literals
import youtube_dl

def ydl_opts():
    from packets.configuration import config
    format_ = config['youtube']['audio_formats']
    return {
    'quiet': True,
    'skip_download': True,
    'format': format_
    }

def get_youtube_info(youtube_link):
    try:
        with youtube_dl.YoutubeDL(ydl_opts()) as ydl:
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

    
