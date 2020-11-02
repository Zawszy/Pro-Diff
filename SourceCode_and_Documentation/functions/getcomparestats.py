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

#open runes json
with open('app/static/runesReforged.json') as frunes:
    runes = json.loads(frunes.read())

#get all relevant data from specific match one and specific match two
def compare_stats(match_one_id, user_one_id, match_two_id, user_two_id, r1, r2):
    #api call to retrieve player one data
    user_one_url = f'https://{regions[r1]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user_one_id}'
    user_one_profile = requests.get(user_one_url, headers=headers)
    user_one_data = json.loads(user_one_profile.content.decode('utf-8'))

    #api call to retrieve player one ranked data
    rank_one_url = f'https://{regions[r1]}.api.riotgames.com/lol/league/v4/entries/by-summoner/{user_one_data["id"]}'
    rank_one = requests.get(rank_one_url, headers = headers)
    rank_one_data = json.loads(rank_one.content.decode('utf-8'))
    
    #api call to retrieve player two data
    user_two_url = f'https://{regions[r2]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{user_two_id}'
    user_two_profile = requests.get(user_two_url, headers=headers)
    user_two_data = json.loads(user_two_profile.content.decode('utf-8'))

    #api call to retrieve player two ranked data
    rank_two_url = f'https://{regions[r2]}.api.riotgames.com/lol/league/v4/entries/by-summoner/{user_two_data["id"]}'
    rank_two = requests.get(rank_two_url, headers = headers)
    rank_two_data = json.loads(rank_two.content.decode('utf-8'))

    #api call to retrieve match one data
    match_one_url = f'https://{regions[r1]}.api.riotgames.com/lol/match/v4/matches/{match_one_id}'
    match_one_response = requests.get(match_one_url, headers=headers)
    match_one = json.loads(match_one_response.content.decode('utf-8'))

    #api call to retrieve match two data
    match_two_url = f'https://{regions[r2]}.api.riotgames.com/lol/match/v4/matches/{match_two_id}'
    match_two_response = requests.get(match_two_url, headers=headers)
    match_two = json.loads(match_two_response.content.decode('utf-8'))
    
    #api call to retrieve match one timeline
    match_one_timeline = f'https://{regions[r1]}.api.riotgames.com/lol/match/v4/timelines/by-match/{match_one_id}'
    match_one_tresponse = requests.get(match_one_timeline, headers=headers)
    match_one_time = json.loads(match_one_tresponse.content.decode('utf-8'))
    
    #api call to retrieve match two timeline
    match_two_timeline = f'https://{regions[r2]}.api.riotgames.com/lol/match/v4/timelines/by-match/{match_two_id}'
    match_two_tresponse = requests.get(match_two_timeline, headers=headers)
    match_two_time = json.loads(match_two_tresponse.content.decode('utf-8'))

    player_one = get_player(match_one, user_one_data['accountId'])
    player_one_team = get_player_team(player_one, match_one)
    
    match_one_skills = get_skills(match_one_time, player_one)
    
    player_one_primary_rune = get_primary(player_one['stats']['perk0'], runes)
    player_one_primary_rune_name = get_primary_name(player_one['stats']['perk0'], runes)
    player_one_secondary_rune = get_secondary(player_one['stats']['perkSubStyle'], runes)
    player_one_secondary_rune_name = get_secondary_name(player_one['stats']['perkSubStyle'], runes)

    outcome_one = get_outcome(player_one)
    match_one_length = match_length_f(match_one)
    match_one_date = match_date_f(match_one)
    champ_one_url = get_champ_icon(player_one['championId'], champs['data'])
    champ_one_summ1 = get_champ_summ(player_one['spell1Id'], summons['data'])
    champ_one_summ1_name = get_champ_summ_name(player_one['spell1Id'], summons['data'])
    champ_one_summ2 = get_champ_summ(player_one['spell2Id'], summons['data'])
    champ_one_summ2_name = get_champ_summ_name(player_one['spell2Id'], summons['data'])
    champ_one_name = get_champ_name(player_one['championId'], champs['data'])
    champ_one_level = f'({str(player_one["stats"]["champLevel"])})'
    champ_one_kda = f'{str(player_one["stats"]["kills"])}/{str(player_one["stats"]["deaths"])}/{str(player_one["stats"]["assists"])}'
    champ_one_kda_decimal = kda_decimal(player_one["stats"]["kills"], player_one["stats"]["deaths"], player_one["stats"]["assists"])
    champ_one_cs = str(player_one['stats']['totalMinionsKilled'] + player_one['stats']['neutralMinionsKilled']) + ' CS'
    item_order_one = items_purchased(match_one_time, player_one['participantId'])
    champ_one_cs_min = cs_min(player_one['stats']['totalMinionsKilled'], player_one['stats']['neutralMinionsKilled'], match_length(match_one))
    champ_one_kills = str(player_one["stats"]["kills"])
    champ_one_assists = str(player_one["stats"]["assists"])
    champ_one_cs_fifteen = get_cs_at_fifteen(match_one_time, player_one['participantId'])

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

    player_two = get_player(match_two, user_two_data['accountId'])
    player_two_team = get_player_team(player_two, match_two)
    
    match_two_skills = get_skills(match_two_time, player_two)
    
    player_two_primary_rune = get_primary(player_two['stats']['perk0'], runes)
    player_two_primary_rune_name = get_primary_name(player_two['stats']['perk0'], runes)
    player_two_secondary_rune = get_secondary(player_two['stats']['perkSubStyle'], runes)
    player_two_secondary_rune_name = get_secondary_name(player_two['stats']['perkSubStyle'], runes)

    outcome_two = get_outcome(player_two)
    match_two_length = match_length_f(match_two)
    match_two_date = match_date_f(match_two)
    champ_two_url = get_champ_icon(player_two['championId'], champs['data'])
    champ_two_summ1 = get_champ_summ(player_two['spell1Id'], summons['data'])
    champ_two_summ1_name = get_champ_summ_name(player_two['spell1Id'], summons['data'])
    champ_two_summ2 = get_champ_summ(player_two['spell2Id'], summons['data'])
    champ_two_summ2_name = get_champ_summ_name(player_two['spell2Id'], summons['data'])
    champ_two_name = get_champ_name(player_two['championId'], champs['data'])
    champ_two_level = f'({str(player_two["stats"]["champLevel"])})'
    champ_two_kda = f'{str(player_two["stats"]["kills"])}/{str(player_two["stats"]["deaths"])}/{str(player_two["stats"]["assists"])}'
    champ_two_kda_decimal = kda_decimal(player_two["stats"]["kills"], player_two["stats"]["deaths"], player_two["stats"]["assists"])
    champ_two_cs = str(player_two['stats']['totalMinionsKilled'] + player_two['stats']['neutralMinionsKilled']) + ' CS'
    item_order_two = items_purchased(match_two_time, player_two['participantId'])
    champ_two_cs_min = cs_min(player_two['stats']['totalMinionsKilled'], player_two['stats']['neutralMinionsKilled'], match_length(match_two))
    champ_two_kills = str(player_two["stats"]["kills"])
    champ_two_assists = str(player_two["stats"]["assists"])
    champ_two_cs_fifteen = get_cs_at_fifteen(match_two_time, player_two['participantId'])

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
    
    player_one_team_id = player_one_team['teamId']
    player_two_team_id = player_two_team['teamId']
    
    t1kills = 0
    t1cs = 0
    t1gold = 0
    t2kills = 0
    t2cs = 0
    t2gold = 0
    
    #iterate through list to find total team one statistics
    for i in match_one['participants']:
        if i['teamId'] == player_one_team_id:
            t1kills += i['stats']['kills']
            t1cs += i['stats']['totalMinionsKilled']
            t1cs += i['stats']['neutralMinionsKilled']
            t1gold += i['stats']['goldEarned']
    
    #iterate through list to find total team two statistics
    for i in match_two['participants']:
        if i['teamId'] == player_two_team_id:
            t2kills += i['stats']['kills']
            t2cs += i['stats']['totalMinionsKilled']
            t2cs += i['stats']['neutralMinionsKilled']
            t2gold += i['stats']['goldEarned']
    
    #dictionary of both player's match details
    players = {
        'player_one_match' : {
            'player_one_name' : user_one_data['name'],
            'player_one_rank' : rank(rank_one_data),
            'player_one_icon' : icon(user_one_data),
            'player_one_gold' : match_one_time,
            'player_one_id'   : player_one['participantId'],
            'player_one_region' : r1.upper(),
            'match_outcome_one' : outcome_one,
            'l_match_outcome_one' : outcome_one.lower(),
            'match_one_length' : match_one_length,
            'match_one_date' : match_one_date,
            'champ_one_url' : champ_one_url,
            'champ_one_name' : champ_one_name,
            'champ_one_summ1' : champ_one_summ1,
            'champ_one_summ1_name' : champ_one_summ1_name,
            'champ_one_summ2' : champ_one_summ2,
            'champ_one_summ2_name' : champ_one_summ2_name,
            'champ_one_level' : champ_one_level,
            'champ_one_kda' : champ_one_kda,
            'champ_one_kills' : champ_one_kills,
            'champ_one_assists': champ_one_assists,
            'champ_one_kda_decimal': champ_one_kda_decimal,
            'champ_one_cs' : champ_one_cs,
            'item_order_one' : item_order_one,
            'champ_one_cs_min': champ_one_cs_min,
            'champ_one_cs_fifteen' : champ_one_cs_fifteen,
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
            't1_barons' : player_one_team['baronKills'],
            't1_dragons' : player_one_team['dragonKills'],
            't1_towers' : player_one_team['towerKills'],
            'skills': match_one_skills,
            'player_one_primary_rune': player_one_primary_rune,
            'player_one_primary_rune_name': player_one_primary_rune_name,
            'player_one_secondary_rune': player_one_secondary_rune,
            'player_one_secondary_rune_name': player_one_secondary_rune_name,
            't1kills': t1kills,
            't1cs': t1cs,
            't1gold': t1gold,
        },
        'player_two_match' : {
            'player_two_name' : user_two_data['name'],
            'player_two_rank' : rank(rank_two_data),
            'player_two_icon' : icon(user_two_data),
            'player_two_gold' : match_two_time,
            'player_two_id'   : player_two['participantId'],
            'player_two_region' : r2.upper(),
            'match_outcome_two' : outcome_two,
            'l_match_outcome_two' : outcome_two.lower(),
            'match_two_length' : match_two_length,
            'match_two_date' : match_two_date,
            'champ_two_url' : champ_two_url,
            'champ_two_name' : champ_two_name,
            'champ_two_summ1' : champ_two_summ1,
            'champ_two_summ1_name' : champ_two_summ1_name,
            'champ_two_summ2' : champ_two_summ2,
            'champ_two_summ2_name' : champ_two_summ2_name,
            'champ_two_level' : champ_two_level,
            'champ_two_kda' : champ_two_kda,
            'champ_two_kills' : champ_two_kills,
            'champ_two_assists': champ_two_assists,
            'champ_two_kda_decimal': champ_two_kda_decimal,
            'champ_two_cs' : champ_two_cs,
            'item_order_two' : item_order_two,
            'champ_two_cs_min': champ_two_cs_min,
            'champ_two_cs_fifteen' : champ_two_cs_fifteen,
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
            't2_barons' : player_two_team['baronKills'],
            't2_dragons' : player_two_team['dragonKills'],
            't2_towers' : player_two_team['towerKills'],
            'skills': match_two_skills,
            'player_two_primary_rune': player_two_primary_rune,
            'player_two_primary_rune_name': player_two_primary_rune_name,
            'player_two_secondary_rune': player_two_secondary_rune,
            'player_two_secondary_rune_name': player_two_secondary_rune_name,
            't2kills': t2kills,
            't2cs': t2cs,
            't2gold': t2gold,
        }
    }

    return players

#find cs per minute for player
def cs_min(minions, jungle, length):
    return round(float((float(minions)+float(jungle))/float(length)), 1)

#find kill/death/assist ratio for player
def kda_decimal(kills, deaths, assists):
    if deaths == 0:
        return -2
    else:
        return round(float((float(kills)+float(assists))/float(deaths)), 2)

#find primary rune name for player
def get_primary_name(r_id, data):
    for i in data:
        for j in i['slots'][0]['runes']:
            if j['id'] == r_id:
                return j['name']

#find primary rune icon for player
def get_primary(r_id, data):
    for i in data:
        for j in i['slots'][0]['runes']:
            if j['id'] == r_id:
                return f'https://ddragon.leagueoflegends.com/cdn/img/{j["icon"]}'

#find secondary rune name for player
def get_secondary_name(r_id, data):
    for i in data:
        if i['id'] == r_id:
            return i['name']

#find secondary rune icon for player
def get_secondary(r_id, data):
    for i in data:
        if i['id'] == r_id:
            return f'https://ddragon.leagueoflegends.com/cdn/img/{i["icon"]}'

#find skill level up order
def get_skills(timeline, player):
    skills = [
    ['Q', [None] * 18], ['W', [None] * 18], ['E', [None] * 18], ['R', [None] * 18]
    ]
    k = 0
    for i in timeline['frames']:
            for j in i['events']:
                if j['type'] == "SKILL_LEVEL_UP" and j['participantId'] == player['participantId']:
                    if j['skillSlot'] == 1:
                        skills[0][1][k] = k+1
                    elif j['skillSlot'] == 2:
                        skills[1][1][k] = k+1
                    elif j['skillSlot'] == 3:
                        skills[2][1][k] = k+1
                    elif j['skillSlot'] == 4:
                        skills[3][1][k] = k+1
                    k+=1
    return skills

#find url of profile icon image
def icon(data):
    p_url = f'http://ddragon.leagueoflegends.com/cdn/10.6.1/img/profileicon/{data["profileIconId"]}.png'
    return p_url

#find rank of player
def rank(r):
    for i in r:
        if i['queueType'] == 'RANKED_SOLO_5x5':
            return i['tier'] + ' ' + i['rank']

#find dictionary of player info in specific match
def get_player(match, accId):
    p_id = None
    for i in match['participantIdentities']:
        if i['player']['currentAccountId'] == accId:
            p_id = i['participantId']
    
    for i in match['participants']:
        if i['participantId'] == p_id:
            return i

#get the correct teamId for given player
def get_player_team(player, match):
    for i in match['teams']:
        if i['teamId'] == player['teamId']:
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

#find name of image
def get_item_name(i_id, data):
    if i_id == 0:
        return
    return data[str(i_id)]['name']

#find length of match int
def match_length(match):
    length = int(match['gameDuration'])
    h = length // 3600
    m = length % 3600 // 60
    
    h * 60 + m
    
    if h > 0:
        return h * 60 + m
    else:
        return m  

#find length of match string
def match_length_f(match):
    length = int(match['gameDuration'])
    h = length // 3600
    m = length % 3600 // 60
    
    if h > 0:
        return '{:02d} H {:02d} MINS'.format(h, m)
    else:
        return '{:02d} MINS'.format(m)

#find match date string
def match_date_f(match):
    epochSecs = int(match['gameCreation']) // 1000
    return datetime.datetime.fromtimestamp(epochSecs).strftime('%d/%m/%Y')

#find items purchased in what order
def items_purchased(timeline, participantId):
    itemTimes = []
    for i in range(0, len(timeline['frames'])):
        j = timeline['frames'][i]
        item_dict = {}
        item_dict[i] = []
        for k in j['events']:
            if k['type'] == "ITEM_PURCHASED" and k['participantId'] == participantId:
                item_dict[i].append({
                                        'name' : get_item_name(k['itemId'], items['data']),
                                        'id' : get_item_icon(k['itemId'])
                                    })
        itemTimes.append(item_dict)
    
    itemTimesFinal = []

    for i in itemTimes:
        (a, b), = i.items()
        if b:
            itemTimesFinal.append((a, b))
    
    return itemTimesFinal

#find creep score at fifteen minutes for specific player
def get_cs_at_fifteen(timeline, participantId):
    for i in range(0, len(timeline['frames'])):
        j = timeline['frames'][i]
        if j['timestamp'] >= (60000 * 15) and j['timestamp'] < (60000 * 16):
            for key, value in j['participantFrames'].items():
                if value['participantId'] == participantId:
                    return value['minionsKilled'] + value['jungleMinionsKilled']
