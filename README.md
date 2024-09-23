# twitch-emotes-downloader
Python script to download streamer emotes as local png/gif files using twitch api.  
e.g. `twitch_streamer_emotes_downloader.exe -c pewdiepie -d pdp -p http://localhost:10809`  
The command line above downloads emote files (the ones in the chat emotes picker) of pewdiepie via http proxy of localhost:10809, save them as <emote_name>.<png/gif> in a folder named 'pdp' in current working directory.  
```
usage: twitch_streamer_emotes_downloader.exe [-h] -c CHANNEL [-d DIR] [-p PROXY]

Download streamer emotes from Twitch.

options:
  -h, --help            show this help message and exit
  -c CHANNEL, --channel CHANNEL
                        Channel name.
  -d DIR, --dir DIR     Download files into this directory. (default: './emotes', will create if not
                        exist.)
  -p PROXY, --proxy PROXY
                        Use specified HTTP proxy server. (e.g. 'http://localhost:10809', or you can set
                        https_proxy or all_proxy in the terminal)
```
