import yaml

def readconfig():
    try:
        with open("songrequest.yaml", 'r') as stream:
            return yaml.load(stream)
    except FileNotFoundError:
        writeconfig(default_yaml)
        return default_yaml
    except yaml.YAMLError:
        from os import rename
        rename("songrequest.yaml", "songrequest.yaml.corrupted")
        writeconfig(default_yaml)
        return default_yaml

def writeconfig(string):
    with open("songrequest.yaml", 'w') as stream:
        yaml.dump(string, stream, default_flow_style=False)
        return default_yaml

default_yaml = {
  "vlc": {
    "vlc_path": "",
    "vlc_options": [
      "--playlist-enqueue",
      "--no-random",
      "--no-loop",
      "--no-repeat",
      "--one-instance",
      "--extraintf=http",
      "--http-password=password"
    ],
    "web_intf": {
      "host": "http://localhost:8080/",
      "password": "password"
    }
  },
  "youtube": {
    "audio_formats": "251/171/140/bestaudio",
    "maxsongduration": 900,
    "category_whitelist": [
        "All"
        ]
  },
  "playlist": {
     "private_playlist": {
        "youtubelink": '',
        "autoplay_playlist": False,
        "shuffle": True
         },
     "skip": {
        "skip_conditions": "4 + {c} // 20",
        "skip_minimum": 2
      },
      "autoresume": True
    },
  "irc": {
    "moderating": {
      "banlist": [],
      "extra_op_privileges": True
    },
    "bot": {
      "nick": "",
      "password": "",
      "host": "",
      "port": "",
      "pswbool": ""
    },
    "channels": [],
    "songrequest": {
      "cmd": [
        "!songrequest",
        "!requestsong",
        "!sr"
      ],
      "delay": 30
    }
  }
}

def de_con_ice(config):
    try:
        for string in default_yaml:
            if not string in config:
                config[string] = default_yaml[string]
        for string2 in default_yaml[string]:
            if not string2 in config[string]:
                config[string][string2] = default_yaml[string][string2]
        for string3 in default_yaml[string][string2]:
            if not string3 in config[string][string2]:
                config[string][string2][string3] = default_yaml[string][string2][string3]
        for string4 in default_yaml[string][string2][string3]:
            if not string4 in config[string][string2][string3]:
                config[string][string2][string3][string4] = default_yaml[string][string2][string3][string4]
        return config
    except Exception:
        return config

def request_info(config):
    config = de_con_ice(config)

    bot = config['irc']['bot']
    if not bot['host']:
        yesno = input("Is host: irc.twitch.tv (y/N) ")
        if yesno.lower() == "y":
            host = "irc.twitch.tv"
            port = 6667
            bot["port"] = port
        else:
            host = input("Insert host address: ")
        bot['host'] = host
        port = ''

    if not bot['port'] and not port:
        yesno = input("Is port: 6667 (y/N) ")
        if yesno.lower() == "y":
            port = 6667
        else:
            port = int(input("Insert port: "))
        bot["port"] = port

    if not bot['nick']:
        nick = input("Insert bot nick: ")
        bot["nick"] = nick

    if not bot["password"]:
        if bot["pswbool"] != False:
            password = input("Insert password (leave blank if non): ")
            bot["password"] = password
            if not password:
                bot["pswbool"] = False
                
    if not config['irc']['channels']:
        chan = input("Insert channel: ")
        if not chan.startswith('#'):
            chan = '#' + chan
        config['irc']['channels'].append(chan)

    if not config['vlc']['vlc_path']:
        from packets.vlc import vlc_path
        if not vlc_path:
            vlc_path = input("Insert vlc destination: ")
        if not vlc_path.endswith('vlc.exe'):
            if not vlc_path.endswith('/') and not vlc_path.endswith('\\'):
                vlc_path += '\\'
            vlc_path += 'vlc.exe'
        config['vlc']["vlc_path"] = vlc_path

config = readconfig()
