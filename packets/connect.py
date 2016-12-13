import requests
import socket
from packets.configuration import writeconfig

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send(plaintext):
    ircsock.send(bytes(plaintext, 'UTF-8'))

def connect(host, port, nick, password):
    try:
        ircsock.connect((host, port))
    except socket.gaierror:
        print("Password Incorrect... Terminating process...")
        return

    print("Connecting to "+ host +"...\n")

    if password:
        send("PASS " + password + "\n")
    send("USER "+ nick +" "+ nick +" "+ nick +" :its a bot\n")
    send("NICK "+ nick +"\n")

def get_twitch_chatters(channel):
    try:
        url = "https://tmi.twitch.tv/group/user/{}/chatters".format(channel.strip('#'))
        r = requests.get(url, verify='certificate/cacert.pem')
        data = r.json()
        return data
    except:
        return []
    
def get_twitch_info(api, channel):
    url = "https://api.twitch.tv/kraken/{}/{}".format(api, channel.strip('#'))
    r = requests.get(url, verify='certificate/cacert.pem')
    data = r.json()
    try:
        if data['stream']:
            return data
    except Exception:
        return []
    
def define_ops(channel):
    op = get_twitch_chatters(channel)
    if not op:
        return []
    if not op['chatters']:
        return []
    op = op['chatters']
    if not op['moderators']:
        return []
    op = op['moderators']
    return op
    
def joinchan(chan):
    if not chan.startswith('#'):
        chan = '#'+ chan
    send("JOIN "+ chan +"\n")
    print("Joining channel: "+ chan)
    
def sendmsg(chan, msg):
    send("PRIVMSG "+ chan +" :"+ msg +"\n")

def request_userlist(chan):
    send("NAMES "+ chan +"\n")

def on_connect(config):
    irc = config['irc']
    print("{} is connected.\n".format(irc['bot']['nick']))
    channels = irc['channels']
    if not channels:
        temp_chan = input("Insert channel: ")
        if not temp_chan.startswith('#'):
            temp_chan = '#'+ temp_chan
        channels.append(temp_chan)

    for chan in channels:
        joinchan(chan)
        
    writeconfig(config)

    if irc['bot']['host'] == 'irc.twitch.tv':
        send('CAP REQ :twitch.tv/membership\r\n')
    sendmsg(
        channels[0],
        'Songrequest enabled. Request songs with the command: {} [youtubelink]'
        .format(irc['songrequest']['cmd'][0])
        )

