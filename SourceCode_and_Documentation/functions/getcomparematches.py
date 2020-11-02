import sys
import requests
import json
import urllib.request
import datetime

#global variables
api_key = 'RGAPI-f352ff9e-e0f5-434d-9b3a-8bdc5beed1bc'
headers = {'X-Riot-Token' : f'{api_key}'}
current_patch = '10.8.1'
regions = {'oce' : 'oc1', 'na' : 'na1', 'euw' : 'euw1', 'eun' : 'eun1',
'kr' : 'kr'}

#open champion json
with open('app/static/champion.json') as fchampion:
    champs = json.loads(fchampion.read())

#open summoner spell json
with open('app/static/summoner.json') as fsummoners:
    summons = json.loads(fsummoners.read())

#open item json
with open('app/static/item.json') as fitems:
    items = json.loads(fitems.read())

#compare matches between summoner 1 and 2
def compare_matches(summ1, r1, summ2, r2):
    p1d = None
    p2d = None
    #if summ1 is in header
    if (summ1 != None):
        p1d = get_player_one_matches(summ1, r1)
    #if summ2 is in header
    if (summ2 != None):
        p2d = get_player_two_matches(summ2, r2)
    #summ1 is not valid
    if p1d == "no-user":
        p1d = None
    #summ2 is not valid
    if p2d == "no-user":
        p2d = None
    #match is not provided
    if p1d is not None:
        if len(p1d) == 1:
            p1d = (p1d, None)
    #match is not provided
    if p2d is not None:
        if len(p2d) == 1:
            p2d = (p2d, None)
    return (p1d, p2d)

#get match history of summoner one
def get_player_one_matches(summ1, r1):

    summoner_name_one = summ1
    
    #api call to retrieve player data
    url_one = f'https://{regions[r1]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name_one}'
    response_one = requests.get(url_one, headers=headers)
    data_one = json.loads(response_one.content.decode('utf-8'))
    
    #if summoner doesn't exist
    for key, values in data_one.items():
        if key == "status":
            return "no-user"
    
    #6 month long calculation
    epoch = datetime.datetime.utcfromtimestamp(0)
    start_time = int((datetime.datetime.now() - datetime.timedelta(6*365/12) - epoch).total_seconds() * 1000)
    
    #api call to retrieve match history of player
    matches_url_one = f'https://{regions[r1]}.api.riotgames.com/lol/match/v4/matchlists/by-account/{data_one["accountId"]}/?queue=420&beginTime=' + str(start_time)
    matches_one_response = requests.get(matches_url_one, headers=headers)
    matches_one = json.loads(matches_one_response.content.decode('utf-8'))
    
    #dictionary of player info
    player_info = {
        'player_one_info' : {
            'acc_id' : data_one['accountId'],
            'name' : data_one['name'],
            'icon' : icon(data_one),
            'level' : data_one['summonerLevel'],
            'region' : r1.upper(),
        }
    }
    
    #if there are no matches within 6 months
    for key, value in matches_one.items():
        if key == "status":
            return player_info
    
    matches = []
    
    #5 matches or length of match history
    length = 5
    if len(matches_one['matches']) < 5:
        length = len(matches_one['matches'])

    for i in range(0, length):
        #api call to retrieve match data
        curr_match_url_one = f'https://{regions[r1]}.api.riotgames.com/lol/match/v4/matches/{matches_one["matches"][i]["gameId"]}'
        curr_match_one_response = requests.get(curr_match_url_one, headers=headers)
        curr_match_one = json.loads(curr_match_one_response.content.decode('utf-8'))

        player_one = get_player(curr_match_one, player_info['player_one_info'])

        outcome_one = get_outcome(player_one)

        matchDate = match_date_f(curr_match_one)
        matchLength = match_length_f(curr_match_one)

        champ_one_url = get_champ_icon(player_one['championId'], champs['data'])
        champ_one_summ1 = get_champ_summ(player_one['spell1Id'], summons['data'])
        champ_one_summ1_name = get_champ_summ_name(player_one['spell1Id'], summons['data'])
        champ_one_summ2 = get_champ_summ(player_one['spell2Id'], summons['data'])
        champ_one_summ2_name = get_champ_summ_name(player_one['spell2Id'], summons['data'])
        champ_one_name = get_champ_name(player_one['championId'], champs['data'])
        champ_one_level = f'({str(player_one["stats"]["champLevel"])})'
        champ_one_kda = f'{str(player_one["stats"]["kills"])}/{str(player_one["stats"]["deaths"])}/{str(player_one["stats"]["assists"])}'
        champ_one_cs = str(player_one['stats']['totalMinionsKilled'] + player_one['stats']['neutralMinionsKilled']) + ' CS'

        p1_i1_icon = get_item_icon(player_one['stats']['item0'])
        p1_i1_icon_name = get_item_name(player_one['stats']['item0'], items['data'])
        p1_i2_icon = get_item_icon(player_one['stats']['item1'])
        p1_i2_icon_name = get_item_name(player_one['stats']['item1'], items['data'])
        p1_i3_icon = get_item_icon(player_one['stats']['item2'])
        p1_i3_icon_name = get_item_name(player_one['stats']['item2'], items['data'])
        p1_i4_icon = get_item_icon(player_one['stats']['item3'])
        p1_i4_icon_name = get_item_name(player_one['stats']['item3'], items['data'])
        p1_i5_icon = get_item_icon(player_one['stats']['item4'])
        p1_i5_icon_name = get_item_name(player_one['stats']['item4'], items['data'])
        p1_i6_icon = get_item_icon(player_one['stats']['item5'])
        p1_i6_icon_name = get_item_name(player_one['stats']['item5'], items['data'])
        p1_t_icon = get_item_icon(player_one['stats']['item6'])
        p1_t_icon_name = get_item_name(player_one['stats']['item6'], items['data'])
        
        #dictionary with all in-game info
        matches_info = {
            'matchId' : curr_match_one['gameId'],
            'match_outcome_one' : outcome_one,
            'l_match_outcome_one' : outcome_one.lower(),
            'matchDate'           : matchDate,
            'matchLength'         : matchLength,
            'champ_one_url' : champ_one_url,
            'champ_one_name' : champ_one_name,
            'champ_one_summ1' : champ_one_summ1,
            'champ_one_summ1_name' : champ_one_summ1_name,
            'champ_one_summ2' : champ_one_summ2,
            'champ_one_summ2_name' : champ_one_summ2_name,
            'champ_one_level' : champ_one_level,
            'champ_one_kda' : champ_one_kda,
            'champ_one_cs' : champ_one_cs,
            'p1_i1_icon' : p1_i1_icon,
            'p1_i1_icon_name' : p1_i1_icon_name,
            'p1_i2_icon' : p1_i2_icon,
            'p1_i2_icon_name' : p1_i2_icon_name,
            'p1_i3_icon' : p1_i3_icon,
            'p1_i3_icon_name' : p1_i3_icon_name,
            'p1_i4_icon' : p1_i4_icon,
            'p1_i4_icon_name' : p1_i4_icon_name,
            'p1_i5_icon' : p1_i5_icon,
            'p1_i5_icon_name' : p1_i5_icon_name,
            'p1_i6_icon' : p1_i6_icon,
            'p1_i6_icon_name' : p1_i6_icon_name,
            'p1_t_icon' : p1_t_icon,
            'p1_t_icon_name' : p1_t_icon_name,
        }

        matches.append(matches_info)

    return (player_info, matches)

#get match history of summoner two
def get_player_two_matches(summ2, r2):

    summoner_name_two = summ2

    #open champion json
    with open('app/static/champion.json') as fchampion:
        champs = json.loads(fchampion.read())

    #open summoner spell json
    with open('app/static/summoner.json') as fsummoners:
        summons = json.loads(fsummoners.read())

    #open item json
    with open('app/static/item.json') as fitems:
        items = json.loads(fitems.read())
    
    #api call to retrieve player data
    url_two = f'https://{regions[r2]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name_two}'
    response_two = requests.get(url_two, headers=headers)
    data_two = json.loads(response_two.content.decode('utf-8'))
    
    #if summoner doesn't exist
    for key, values in data_two.items():
        if key == "status":
            return "no-user"
    
    #6 month long calculation
    epoch = datetime.datetime.utcfromtimestamp(0)
    start_time = int((datetime.datetime.now() - datetime.timedelta(3*365/12) - epoch).total_seconds() * 1000)
    
    #api call to retrieve match history of player
    matches_url_two = f'https://{regions[r2]}.api.riotgames.com/lol/match/v4/matchlists/by-account/{data_two["accountId"]}/?queue=420&beginTime=' + str(start_time)
    matches_two_response = requests.get(matches_url_two, headers=headers)
    matches_two = json.loads(matches_two_response.content.decode('utf-8'))
    
    #dictionary of player info
    player_info = {
        'player_two_info' : {
            'acc_id' : data_two['accountId'],
            'name' : data_two['name'],
            'icon' : icon(data_two),
            'level' : data_two['summonerLevel'],
            'region' : r2.upper(),
        }
    }
    
    #if there are no matches within 6 months
    for key, value in matches_two.items():
        if key == "status":        
            return player_info
    
    #5 matches or length of match history
    length = 5
    if len(matches_two['matches']) < 5:
        length = len(matches_two['matches'])
    
    matches = []

    for i in range(0, length):
        #api call to retrieve match data
        curr_match_url_two = f'https://{regions[r2]}.api.riotgames.com/lol/match/v4/matches/{matches_two["matches"][i]["gameId"]}'
        curr_match_two_response = requests.get(curr_match_url_two, headers=headers)

        curr_match_two = json.loads(curr_match_two_response.content.decode('utf-8'))

        player_two = get_player(curr_match_two, player_info['player_two_info'])

        matchDate = match_date_f(curr_match_two)
        matchLength = match_length_f(curr_match_two)
        
        outcome_two = get_outcome(player_two)

        champ_two_url = get_champ_icon(player_two['championId'], champs['data'])
        champ_two_summ1 = get_champ_summ(player_two['spell1Id'], summons['data'])
        champ_two_summ1_name = get_champ_summ_name(player_two['spell1Id'], summons['data'])
        champ_two_summ2 = get_champ_summ(player_two['spell2Id'], summons['data'])
        champ_two_summ2_name = get_champ_summ_name(player_two['spell2Id'], summons['data'])
        champ_two_name = get_champ_name(player_two['championId'], champs['data'])
        champ_two_level = f'({str(player_two["stats"]["champLevel"])})'
        champ_two_kda = f'{str(player_two["stats"]["kills"])}/{str(player_two["stats"]["deaths"])}/{str(player_two["stats"]["assists"])}'
        champ_two_cs = str(player_two['stats']['totalMinionsKilled'] + player_two['stats']['neutralMinionsKilled']) + ' CS'

        p2_i1_icon = get_item_icon(player_two['stats']['item0'])
        p2_i1_icon_name = get_item_name(player_two['stats']['item0'], items['data'])
        p2_i2_icon = get_item_icon(player_two['stats']['item1'])
        p2_i2_icon_name = get_item_name(player_two['stats']['item1'], items['data'])
        p2_i3_icon = get_item_icon(player_two['stats']['item2'])
        p2_i3_icon_name = get_item_name(player_two['stats']['item2'], items['data'])
        p2_i4_icon = get_item_icon(player_two['stats']['item3'])
        p2_i4_icon_name = get_item_name(player_two['stats']['item3'], items['data'])
        p2_i5_icon = get_item_icon(player_two['stats']['item4'])
        p2_i5_icon_name = get_item_name(player_two['stats']['item4'], items['data'])
        p2_i6_icon = get_item_icon(player_two['stats']['item5'])
        p2_i6_icon_name = get_item_name(player_two['stats']['item5'], items['data'])
        p2_t_icon = get_item_icon(player_two['stats']['item6'])
        p2_t_icon_name = get_item_name(player_two['stats']['item6'], items['data'])
        
        #dictionary with all in-game info
        matches_info = {
            'matchId' : curr_match_two['gameId'],
            'match_outcome_two' : outcome_two,
            'l_match_outcome_two' : outcome_two.lower(),
            'matchDate'           : matchDate,
            'matchLength'         : matchLength,
            'champ_two_url' : champ_two_url,
            'champ_two_name' : champ_two_name,
            'champ_two_summ1' : champ_two_summ1,
            'champ_two_summ1_name' : champ_two_summ1_name,
            'champ_two_summ2' : champ_two_summ2,
            'champ_two_summ2_name' : champ_two_summ2_name,
            'champ_two_level' : champ_two_level,
            'champ_two_kda' : champ_two_kda,
            'champ_two_cs' : champ_two_cs,
            'p2_i1_icon' : p2_i1_icon,
            'p2_i1_icon_name' : p2_i1_icon_name,
            'p2_i2_icon' : p2_i2_icon,
            'p2_i2_icon_name' : p2_i2_icon_name,
            'p2_i3_icon' : p2_i3_icon,
            'p2_i3_icon_name' : p2_i3_icon_name,
            'p2_i4_icon' : p2_i4_icon,
            'p2_i4_icon_name' : p2_i4_icon_name,
            'p2_i5_icon' : p2_i5_icon,
            'p2_i5_icon_name' : p2_i5_icon_name,
            'p2_i6_icon' : p2_i6_icon,
            'p2_i6_icon_name' : p2_i6_icon_name,
            'p2_t_icon' : p2_t_icon,
            'p2_t_icon_name' : p2_t_icon_name,
        }

        matches.append(matches_info)

    return (player_info, matches)

#find url of profile icon image
def icon(data):
    p_url = f'http://ddragon.leagueoflegends.com/cdn/10.6.1/img/profileicon/{data["profileIconId"]}.png'
    return p_url

#find dictionary of player info in specific match
def get_player(match, player_info):
    p_id = None
    for i in match['participantIdentities']:
        if i['player']['currentAccountId'] == player_info['acc_id']:
            p_id = i['participantId']
    
    for i in match['participants']:
        if i['participantId'] == p_id:
            return i

#find if given player wins or loses the match
def get_outcome(player):
    if player['stats']['win'] == True:
        return 'WIN'
    elif player['stats']['win'] == False:
        return 'LOSS'

#find url of champion icon image
def get_champ_icon(c_id, data):
    for key, value in data.items():
        if type(value) is dict and get_champ_icon(c_id, value) is None:
            if value['key'] == str(c_id):
                return f'http://ddragon.leagueoflegends.com/cdn/10.6.1/img/champion/{value["id"]}.png'
        elif type(value) is dict:
            return get_champ_icon(c_id, value)
        else:
            return

#find name of champion
def get_champ_name(c_id, data):
    for key, value in data.items():
        if type(value) is dict and get_champ_name(c_id, value) is None:
            if value['key'] == str(c_id):
                return value['name']
        elif type(value) is dict:
                return get_champ_name(c_id, value)
        else:
                return

#find url of summoner spell icon image
def get_champ_summ(s_id, data):
    for key, value in data.items():
        if type(value) is dict and get_champ_summ(s_id, value) is None:
            if value['key'] == str(s_id):
                return f'http://ddragon.leagueoflegends.com/cdn/9.19.1/img/spell/{value["id"]}.png'
        elif type(value) is dict:
            return get_champ_summ(s_id, value)
        else:
            return

#find name of summoner spell
def get_champ_summ_name(s_id, data):
    for key, value in data.items():
        if type(value) is dict and get_champ_summ_name(s_id, value) is None:
            if value['key'] == str(s_id):
                return value['name']
        elif type(value) is dict:
            return get_champ_summ_name(s_id, value)
        else:
            return

#find url of item icon image
def get_item_icon(i_id):
    if i_id == 0:
        return 'static/Blank0.png'
    return f'http://ddragon.leagueoflegends.com/cdn/10.6.1/img/item/{str(i_id)}.png'

#find name of item
def get_item_name(i_id, data):
    if i_id == 0:
        return
    return data[str(i_id)]['name']

#find length of match
def match_length_f(f):
    length = int(f['gameDuration'])
    h = length // 3600
    m = length % 3600 // 60
    
    if h > 0:
        return '{:02d} H {:02d} MINS'.format(h, m)
    else:
        return '{:02d} MINS'.format(m)
        
#find date of match
def match_date_f(match):
    epochSecs = int(match['gameCreation']) // 1000
    return datetime.datetime.fromtimestamp(epochSecs).strftime('%d/%m/%Y')
