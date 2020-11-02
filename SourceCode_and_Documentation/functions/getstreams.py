import json
import requests

def get_streams():
    # Base Info
    nstreams_to_get = 5 # get top 5 streams
    return_streams = []

    client_id = 'stk6hgxp85l3auv3aluj1jl34qik2t'
    headers = {'Client-ID': f'{client_id}'}

    # Check if Riot Official Streams are live.
    official_api_url = 'https://api.twitch.tv/helix/streams?user_id=124425627&user_id=124425501&user_id=124420521&user_id=124422593&user_id=400524247' 
    official_response = requests.get(official_api_url, headers=headers)
    official_data = json.loads(official_response.content.decode('utf-8'))

    #find data of all officials streams
    for stream in official_data['data']:
        url = f'https://api.twitch.tv/helix/users?id={stream["user_id"]}'
        response = requests.get(url, headers=headers)

        user_response = json.loads(response.content.decode('utf-8'))
        user_data = user_response['data'][0]

        return_dict = dict({'login' : user_data['login'],'name' : stream['user_name'], 'title' : stream['title'], 'view_count' : stream['viewer_count'], 'official': True})

        return_streams.append(return_dict)
        nstreams_to_get -= 1
    
    #api call to retrieve all league of legends stream data
    url = f'https://api.twitch.tv/helix/streams?game_id=21779&first={nstreams_to_get}'
    response = requests.get(url, headers=headers)

    data = json.loads(response.content.decode('utf-8'))
    
    #find data of all league of legends streams
    for stream in data['data']:
        
        url = f'https://api.twitch.tv/helix/users?id={stream["user_id"]}'
        response = requests.get(url, headers=headers)

        user_response = json.loads(response.content.decode('utf-8'))
        user_data = user_response['data'][0]

        return_dict = dict({'login' : user_data['login'],'name' : stream['user_name'], 'title' : stream['title'], 'view_count' : stream['viewer_count'], 'official': False})

        if not any(d['login'] == return_dict['login'] for d in return_streams):
            return_streams.append(return_dict)

    return return_streams
