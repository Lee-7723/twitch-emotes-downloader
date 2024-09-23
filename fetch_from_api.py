import requests, os, re, json, sys, argparse

argparser = argparse.ArgumentParser(description='Download streamer emotes from Twitch.')

class TwApi:
    session = requests.Session()
    def __init__(self):
        resp = self.session.get("https://www.twitch.tv/")
        client_id = re.search('clientId="(.*?)",', resp.content.decode()).group(1)
        self.client_id = client_id
        # return client_id

    def gqlPlaybackAccessToken(self, channel: str) -> str:
        'input channel name, return channel_id'
        resp = self.session.post(
            url="https://gql.twitch.tv/gql",
            json={
                "operationName": "PlaybackAccessToken_Template",
                "query": 'query PlaybackAccessToken_Template($login: String!, $isLive: Boolean!, $vodID: ID!, $isVod: Boolean!, $playerType: String!, $platform: String!) {  streamPlaybackAccessToken(channelName: $login, params: {platform: $platform, playerBackend: "mediaplayer", playerType: $playerType}) @include(if: $isLive) {    value    signature   authorization { isForbidden forbiddenReasonCode }   __typename  }  videoPlaybackAccessToken(id: $vodID, params: {platform: $platform, playerBackend: "mediaplayer", playerType: $playerType}) @include(if: $isVod) {    value    signature   __typename  }}',
                "variables": {
                    "isLive": True,
                    "login": channel,
                    "isVod": False,
                    "vodID": "",
                    "playerType": "site",
                    "platform": "web",
                },
            },
            headers={"Client-Id": self.client_id},
        )
        r_dict: dict = resp.json()
        v = json.loads(r_dict['data']['streamPlaybackAccessToken']['value'])
        r = v['channel_id']
        # print(r)
        return r.__str__()


    def gqlEmotePicker(self, channelOwnerID: str) -> dict:
        'return a dict like `{\'pewdiepieLegendBroFist\': \'emotesv2_b6e72807df1b4c78a0b70c8bb534b2fc\'}`'
        resp = self.session.post(
            url="https://gql.twitch.tv/gql",
            json=[
                {
                    "operationName": "EmotePicker_EmotePicker_UserSubscriptionProducts",
                    "variables": {"channelOwnerID": channelOwnerID},
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "71b5f829a4576d53b714c01d3176f192cbd0b14973eb1c3d0ee23d5d1b78fd7e",
                        }
                    },
                }
            ],
            headers={"Client-Id": self.client_id},
        )
        resp_dict = resp.json()
        r_dict = dict()
        if resp_dict[0]['data']['channel']['localEmoteSets'] != None:
            for emo_set in resp_dict[0]['data']['channel']['localEmoteSets']:
                for emo in emo_set['emotes']:
                    r_dict[emo['token']] = emo['id']

        for emo_set in resp_dict[0]['data']['user']['subscriptionProducts']:
            for emo in emo_set['emotes']:
                # if emo['assetType'] == 'ANIMATED':
                #     ext = '.gif'
                # elif emo['assetType'] == 'STATIC':
                #     ext = '.png'
                r_dict[emo['token']] = emo['id']

        return r_dict
    
    def downloadEmote(self, filename: str, url: str):
        resp = self.session.get(url)
        ext = resp.headers['Content-Type'].split('/')[-1]
        # if ('.png' not in filename) and ('.gif' not in filename):
        #     from PIL import Image
        #     from io import BytesIO
        #     img = Image.open(BytesIO(resp.content))
        #     ext = img.format.lower()
        filename += f'.{ext}'
        with open(filename, mode='wb') as f:
            f.write(resp.content)
        print(f'download as {filename}')


    def downloadEmotes(self, emote_dict: dict, max_workers: int = 20, dir: str = ''):
        if not os.path.exists(dir):
            os.mkdir(dir)
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        thr_set = set()
        for filename, url in emote_dict.items():
            thr = executor.submit(
                self.downloadEmote, 
                filename=os.path.join(dir, filename), 
                url=f'https://static-cdn.jtvnw.net/emoticons/v2/{url}/default/light/3.0')
            thr_set.add(thr)
        executor.shutdown()

        for thr in thr_set:
            thr: concurrent.futures.Future
            e = thr.exception()
            if e != None:
                print(thr.result())

if __name__ == '__main__':
    argparser.add_argument('-c', '--channel', dest='channel', help='Channel name.', required=True)
    argparser.add_argument('-d', '--dir', dest='dir', help='Download files into this directory. (default: \'./emotes\', will create if not exist.)', default='./emotes')
    argparser.add_argument('-p', '--proxy', dest='proxy', help='Use specified HTTP proxy server. (e.g. \'http://localhost:10809\', or you can set https_proxy or all_proxy in the terminal)', default='')
    args = argparser.parse_args()

    if args.proxy != '':
        os.environ["all_proxy"] = args.proxy

    api = TwApi()
    channel_id = api.gqlPlaybackAccessToken(args.channel)
    emote_dict = api.gqlEmotePicker(channel_id)
    api.downloadEmotes(emote_dict=emote_dict, dir=args.dir)
    # print(emote_dict)