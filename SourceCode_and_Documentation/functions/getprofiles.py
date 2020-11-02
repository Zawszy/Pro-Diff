import json
import datetime
import requests
import pprint
import urllib.request

#global variables
api_key = 'RGAPI-8d26b56c-137d-46d2-a8f5-a55af7d82f55'
headers = {'X-Riot-Token' : f'{api_key}'}
current_patch = '10.8.1'
regions = {'oce' : 'oc1', 'na' : 'na1', 'euw' : 'euw1', 'eun' : 'eun1',
'kr' : 'kr'}

#open champion json
with open('app/static/champion.json') as champion:
    champs = json.loads(champion.read())

#open summoner spell json
with open('app/static/summoner.json') as summoners:
    summon = json.loads(summoners.read())

#open item json
with open('app/static/item.json') as items:
    item = json.loads(items.read())
        
def get_profiles(summoner, region, filter_champ_id, filter_role_id):
    #initial profile
    url = f'https://{regions[region]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner}'
    profile = requests.get(url, headers=headers)
    d = json.loads(profile.content.decode('utf-8'))
    
    #if summoner doesn't exist
    for key, values in d.items():
        if key == "status":
            return "no-user"
            
    #6 month long calculation
    epoch = datetime.datetime.utcfromtimestamp(0)
    start_time = int((datetime.datetime.now() - datetime.timedelta(6*365/12) - epoch).total_seconds() * 1000)

    #ranked info
    url = f'https://{regions[region]}.api.riotgames.com/lol/league/v4/entries/by-summoner/' + d['id']
    ranks = requests.get(url, headers = headers)
    r = json.loads(ranks.content.decode('utf-8'))

    #if a filter champion is given
    if filter_champ_id is not None:
        url = f'https://{regions[region]}.api.riotgames.com/lol/match/v4/matchlists/by-account/' + d['accountId'] + '/?queue=420&beginTime=' + str(start_time) + '&champion=' + str(filter_champ_id)
    else:
        url = f'https://{regions[region]}.api.riotgames.com/lol/match/v4/matchlists/by-account/' + d['accountId'] + '/?queue=420&beginTime=' + str(start_time)
    #api call to retrieve match history data
    match = requests.get(url, headers = headers)
    m = json.loads(match.content.decode('utf-8'))
    
    #get details of player
    p_name = name(d)
    p_url = icon(d)
    p_rank = rank(r)
    
    #if player has no matches in the past 6 months
    for key, value in m.items():
        if key == "status":        
            return {'p_url': p_url,
            'p_name': p_name,
            'p_region': region,
            'p_rank': p_rank,
            'matches': 'no-match',
            }
    
    #get match details for those that fit the role
    num = 0
    matches = []
    for curr_game in m['matches']:

        if (num > 9):
            break

        if (filter_role_id != None):
            if (eval_role(curr_game, int(filter_role_id))) == False:
                continue
        
        #get match data of player
        f_match = requests.get(f'https://{regions[region]}.api.riotgames.com/lol/match/v4/matches/' + str(curr_game['gameId']) + '?api_key=' + api_key)
        f = f_match.json()
        
        #if player doesn't exist
        try:
            participant_id = find_participant_id(f, d['accountId'])
        except:
            break

        player = find_player(f, participant_id)
        match_outcome = match_outcome_f(player)
        match_length = match_length_f(f)
        match_date = match_date_f(f)
        
        c_url = champ_url(player['championId'], champs['data'])
        c_name = champ_name(player['championId'], champs['data'])
        s_url1 = summoner_url(player['spell1Id'], summon['data'])
        s_name1 = summoner_name(player['spell1Id'], summon['data'])
        s_url2 = summoner_url(player['spell2Id'], summon['data'])
        s_name2 = summoner_name(player['spell2Id'], summon['data'])
        
        c_level = '(' + str(player['stats']['champLevel']) + ')'
        c_kda = str(player['stats']['kills']) + '/' + str(player['stats']['deaths']) + '/' + str(player['stats']['assists'])
        c_cs = str(player['stats']['totalMinionsKilled'] + player['stats']['neutralMinionsKilled']) + ' CS'
        
        i1_url = item_url(player['stats']['item0'])
        i1_name = item_name(player['stats']['item0'], item['data'])
        i2_url = item_url(player['stats']['item1'])
        i2_name = item_name(player['stats']['item1'], item['data'])
        i3_url = item_url(player['stats']['item2'])
        i3_name = item_name(player['stats']['item2'], item['data'])
        i4_url = item_url(player['stats']['item3'])
        i4_name = item_name(player['stats']['item3'], item['data'])
        i5_url = item_url(player['stats']['item4'])
        i5_name = item_name(player['stats']['item4'], item['data'])
        i6_url = item_url(player['stats']['item5'])
        i6_name = item_name(player['stats']['item5'], item['data'])
        t_url = item_url(player['stats']['item6'])
        t_name = item_name(player['stats']['item6'], item['data'])
        
        bteams = []
        rteams = []
        #get details of all participants within the match
        for i in f['participants']:
            if i['teamId'] == 100:
                bteams.append({'url': champ_url(i['championId'], champs['data']),
                'name': champ_name(i['championId'], champs['data']),
                'summoner_name': player_name(i['participantId'], f)})
            elif i['teamId'] == 200:
                rteams.append({'url': champ_url(i['championId'], champs['data']),
                'name': champ_name(i['championId'], champs['data']),
                'summoner_name': player_name(i['participantId'], f)})
         
        #dictionary containing all details of the match 
        match_info = {'match_outcome': match_outcome,
        'l_match_outcome': match_outcome.lower(),
        'match_length' : match_length,
        'match_date' : match_date,
        'c_url': c_url,
        'c_name': c_name,
        's_url1': s_url1,
        's_url2': s_url2,
        's_name1': s_name1,
        's_name2': s_name2,
        'c_level': c_level,
        'c_kda': c_kda,
        'c_cs': c_cs,
        'i1_url': i1_url,
        'i2_url': i2_url,
        'i3_url': i3_url,
        'i4_url': i4_url,
        'i5_url': i5_url,
        'i6_url': i6_url,
        'i1_name': i1_name,
        'i2_name': i2_name,
        'i3_name': i3_name,
        'i4_name': i4_name,
        'i5_name': i5_name,
        'i6_name': i6_name,
        't_name': t_name,
        't_url': t_url,
        'bteams': bteams,
        'rteams': rteams,
        'matchId': f['gameId']
        }
        matches.append(match_info)
        num += 1
    return {'p_url': p_url,
    'p_name': p_name,
    'p_region': region,
    'p_rank': p_rank,
    'matches': matches,
    }

#find player name within match
def player_name(participantId, f):
    for i in f['participantIdentities']:
        if i['participantId'] == participantId:
            if len(i['player']['summonerName']) > 10:
                return i['player']['summonerName'][0:10] + '...'
            return i['player']['summonerName']

#find url of item icon image
def item_url(itemId):
    if itemId == 0:
        return 'static/Blank0.png'
    return 'http://ddragon.leagueoflegends.com/cdn/10.6.1/img/item/' + str(itemId) + '.png'

#find name of item
def item_name(itemId, items):
    if itemId == 0:
        return 'Blank'
    return items[str(itemId)]['name']

#find url of champion icon image
def champ_url(championId, champs):
    for key, value in champs.items():
        if type(value) is dict and champ_url(championId, value) is None:
            if value['key'] == str(championId):
                return 'http://ddragon.leagueoflegends.com/cdn/10.6.1/img/champion/' + value['id'] + '.png'
        elif type(value) is dict:
            return champ_url(championId, value)
        else:
            return

#find name of champion
def champ_name(championId, champs):
    for key, value in champs.items():
        if type(value) is dict and champ_name(championId, value) is None:
            if value['key'] == str(championId):
                return value['name']
        elif type(value) is dict:
            return champ_name(championId, value)
        else:
            return    

#find name of summoner
def summoner_name(summonerId, summoner):
    for key, value in summoner.items():
        if type(value) is dict and summoner_name(summonerId, value) is None:
            if value['key'] == str(summonerId):
                return value['name']
        elif type(value) is dict:
            return summoner_name(summonerId, value)
        else:
            return

#find url of summoner icon image
def summoner_url(summonerId, summoner):
    for key, value in summoner.items():
        if type(value) is dict and summoner_url(summonerId, value) is None:
            if value['key'] == str(summonerId):
                return 'http://ddragon.leagueoflegends.com/cdn/9.19.1/img/spell/' + value['id'] + '.png'
        elif type(value) is dict:
            return summoner_url(summonerId, value)
        else:
            return 

#find if given player wins or loses the match
def match_outcome_f(player):
    if player['stats']['win'] is True:
        return 'WIN'
    else:
        return 'LOSS'

#find dictionary of player info in specific match
def find_player(m, participant_id):
     for i in m['participants']:
        if i['participantId'] == participant_id:
            return i

#find participant id of player in specific match
def find_participant_id(f, accountId):
    for i in f['participantIdentities']:
        if i['player']['currentAccountId'] == accountId:
            return i['participantId']

#find name of player
def name(d):
    if len(d['name']) > 12:
        return d['name'][0:12]
    return d['name']
    
#find rank of player
def rank(r):
    for i in r:
        if i['queueType'] == 'RANKED_SOLO_5x5':
            return i['tier'] + ' ' + i['rank']

#find url of profile icon image
def icon(d):
    p_url = 'http://ddragon.leagueoflegends.com/cdn/10.6.1/img/profileicon/' + str(d['profileIconId']) + '.png'
    return p_url

#find length of match string
def match_length_f(f):
    length = int(f['gameDuration'])
    h = length // 3600
    m = length % 3600 // 60
    
    if h > 0:
        return '{:02d} H {:02d} MINS'.format(h, m)
    else:
        return '{:02d} MINS'.format(m)

#find match date string
def match_date_f(f):
    epochSecs = int(f['gameCreation']) // 1000
    return datetime.datetime.fromtimestamp(epochSecs).strftime('%d/%m/%Y')

#find role of player
def eval_role(match, rid):
    if (rid == None):
        return True
    elif (rid == 0):        #TOP
        if (match["role"] == 'SOLO') and (match["lane"] == 'TOP'):
            return True
    elif (rid == 1):
        if (match["role"] == 'NONE') and (match["lane"] == 'JUNGLE'):
            return True
    elif (rid == 2):
        if (match["role"] == 'SOLO') and (match["lane"] == 'MID'):
            return True
    elif (rid == 3):
        if (match["role"] == 'DUO_CARRY') and (match["lane"] == 'BOTTOM'):
            return True
    elif (rid == 4):
        if (match["role"] == 'DUO_SUPPORT') and (match["lane"] == 'BOTTOM'):
            return True
    
    return False

#find details of one given match
def get_one_match(user, matchid, region):
    #initial profile
    url = f'https://{regions[region]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user}'
    profile = requests.get(url, headers=headers)
    d = json.loads(profile.content.decode('utf-8'))
    
    #get player details
    p_name = name(d)
    p_url = icon(d)
    
    #api call to retrieve match data
    f_match = requests.get(f'https://{regions[region]}.api.riotgames.com/lol/match/v4/matches/' + str(matchid) + '?api_key=' + api_key)
    f = f_match.json()
    
    player = find_player(f, find_participant_id(f, d['accountId']))
    
    match_outcome = match_outcome_f(player)
    match_length = match_length_f(f)
    match_date = match_date_f(f)
    
    c_url = champ_url(player['championId'], champs['data'])
    c_name = champ_name(player['championId'], champs['data'])
    s_url1 = summoner_url(player['spell1Id'], summon['data'])
    s_name1 = summoner_name(player['spell1Id'], summon['data'])
    s_url2 = summoner_url(player['spell2Id'], summon['data'])
    s_name2 = summoner_name(player['spell2Id'], summon['data'])
    
    c_level = '(' + str(player['stats']['champLevel']) + ')'
    c_kda = str(player['stats']['kills']) + '/' + str(player['stats']['deaths']) + '/' + str(player['stats']['assists'])
    c_cs = str(player['stats']['totalMinionsKilled'] + player['stats']['neutralMinionsKilled']) + ' CS'
    
    i1_url = item_url(player['stats']['item0'])
    i1_name = item_name(player['stats']['item0'], item['data'])
    i2_url = item_url(player['stats']['item1'])
    i2_name = item_name(player['stats']['item1'], item['data'])
    i3_url = item_url(player['stats']['item2'])
    i3_name = item_name(player['stats']['item2'], item['data'])
    i4_url = item_url(player['stats']['item3'])
    i4_name = item_name(player['stats']['item3'], item['data'])
    i5_url = item_url(player['stats']['item4'])
    i5_name = item_name(player['stats']['item4'], item['data'])
    i6_url = item_url(player['stats']['item5'])
    i6_name = item_name(player['stats']['item5'], item['data'])
    t_url = item_url(player['stats']['item6'])
    t_name = item_name(player['stats']['item6'], item['data'])
    
    match_info = []
    #dictionary with all match data
    s_match_info = {'match_outcome_one': match_outcome,
    'l_match_outcome_one': match_outcome.lower(),
    'matchLength' : match_length,
    'matchDate' : match_date,
    'champ_one_url': c_url,
    'champ_one_name': c_name,
    'champ_one_summ1': s_url1,
    'champ_one_summ2': s_url2,
    'champ_one_summ1_name': s_name1,
    'champ_one_summ2_name': s_name2,
    'champ_one_level': c_level,
    'champ_one_kda': c_kda,
    'champ_one_cs': c_cs,
    'p1_i1_icon': i1_url,
    'p1_i2_icon': i2_url,
    'p1_i3_icon': i3_url,
    'p1_i4_icon': i4_url,
    'p1_i5_icon': i5_url,
    'p1_i6_icon': i6_url,
    'p1_i1_icon_name': i1_name,
    'p1_i2_icon_name': i2_name,
    'p1_i3_icon_name': i3_name,
    'p1_i4_icon_name': i4_name,
    'p1_i5_icon_name': i5_name,
    'p1_i6_icon_name': i6_name,
    'p1_t_icon_name': t_name,
    'p1_t_icon': t_url,
    'matchId': f['gameId']
    }
    match_info.append(s_match_info)
    return match_info
