import sys, requests, mwclient
from collections import OrderedDict
from json import loads, dumps
import pprint
import leaguepedia_parser
import re
import pickle
import datetime

lp = leaguepedia_parser.LeaguepediaParser()
roles = {'top':'Top Laner', 'jg':'Jungler', 'mid':'Mid Laner', 'bot':'Bot Laner', 'support':'Support'}

def to_dict(data):
    return loads(dumps(data))

def get_pros(update, region, role):

	fileExists = True
	if update == 'false':
		try:
			with open('app/static/proplayers.pickle', 'rb') as input:
				
				result = pickle.load(input)

				if region or role:
					result['result'] = filter_roles(filter_regions(result['result'], region), role)

				return result
		except FileNotFoundError:
			fileExists = False

	if update == 'true' or fileExists == False:
		site = mwclient.Site('lol.gamepedia.com', path='/')

		result = [
			{'region' : 'NORTH AMERICA', 
				'teams' : [],},
			{'region' : 'EUROPE', 
				'teams' : []},
			{'region' : 'OCEANIA', 
				'teams' : []},
			{'region' : 'KOREA', 
				'teams' : []}
		]

		sort_order = { "Top Laner" : 0, "Jungler" : 1, "Mid Laner" : 2, "Bot Laner" : 3, "Support" : 4, "" : 5 }

		northAmerica = site.api('cargoquery',
			limit = 'max',
			tables = "ListplayerCurrent=PC",
			where = 'Team = \'Immortals\' or Team = \'Team SoloMid\' or Team = \'Team Liquid\' or Team = \'Flyquest\' or Team = \'Cloud9\' or Team = \'100 Thieves\' or Team = \'Evil Geniuses.NA\' or Team = \'Counter Logic Gaming\' or Team = \'Dignitas\' or Team = \'Golden Guardians\'',
			fields = "PC.Team, PC.ID, PC.Residency, PC.Role"
		)

		northAmerica = to_dict(northAmerica)
		na = []
		naPlayersCheck = []
		for x in range(0, len(northAmerica['cargoquery'])):
			# For Team Names
			if northAmerica['cargoquery'][x]['title']['Team'] not in na:
				na.append(northAmerica['cargoquery'][x]['title']['Team'])
				result[0]['teams'].append({'id' : 'id' + ''.join(filter(str.isalnum, northAmerica['cargoquery'][x]['title']['Team'])), 'name' : northAmerica['cargoquery'][x]['title']['Team'], 'img_name' : lp.get_team_logo(northAmerica['cargoquery'][x]['title']['Team'])})

		# For players in team
		for y in range(0, len(result[0]['teams'])):
			#For players that we havent checked yet
			naPlayers = []
			for z in range(0, len(northAmerica['cargoquery'])):
				if northAmerica['cargoquery'][z]['title']['Team'] == result[0]['teams'][y]['name'] and northAmerica['cargoquery'][z]['title']['ID'] not in naPlayersCheck:
					playerId = northAmerica['cargoquery'][z]['title']['ID']
					naPlayersCheck.append(northAmerica['cargoquery'][z]['title']['ID'])
					soloqid = site.api('cargoquery',
						limit = 'max',
						tables = "Players=P",
						where = f'ID = "{playerId}"',
						fields = "P.SoloqueueIds"
					)
					soloqid = to_dict(soloqid)
					if not soloqid['cargoquery']:
						naPlayers.append({'name' : northAmerica['cargoquery'][z]['title']['ID'], 'role' : northAmerica['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, northAmerica['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'na', 'soloqid' : '-1'})
					else:
						if not soloqid['cargoquery'][0]['title']['SoloqueueIds']:
							naPlayers.append({'name' : northAmerica['cargoquery'][z]['title']['ID'], 'role' : northAmerica['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, northAmerica['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'na', 'soloqid' : '-1'})
						else:
							soloqid = soloqid['cargoquery'][0]['title']['SoloqueueIds']
							soloqid = (soloqid.split(","))[0]
							soloqid = soloqid.split("(")
							soloqid[0] = soloqid[0].replace(" ", "")
							naPlayers.append({'name' : northAmerica['cargoquery'][z]['title']['ID'], 'role' : northAmerica['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, northAmerica['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'na', 'soloqid' : soloqid[0].lower()})
							if len(soloqid) > 1:
								soloqid[1] = soloqid[1].replace(')', '')
								naPlayers[0]['region'] = soloqid[1].lower()
			naPlayers.sort(key=lambda valna: sort_order[valna['role']])
			for i in naPlayers:
				if i['soloqid'] != '-1' and not re.search("[']{3}.*[']{3}.*", i['soloqid']) == None:
					i['soloqid'] = i['soloqid'].split("'''", 2)[2]
			result[0]['teams'][y].update({'players' : naPlayers})

		europe = site.api('cargoquery',
			limit = 'max',
			tables = "ListplayerCurrent=PC",
			where = 'Team = \'G2 Esports\' or Team = \'Rogue (European Team)\' or Team = \'Origen\' or Team = \'Fnatic\' or Team = \'Misfits Gaming\' or Team = \'FC Schalke 04 Esports\' or Team = \'Excel Esports\' or Team = \'MAD Lions\' or Team = \'SK Gaming\' or Team = \'Team Vitality\'',
			fields = "PC.Team, PC.ID, PC.Residency, PC.Role"
		)

		europe = to_dict(europe)
		eu = []
		euPlayersCheck = []
		for x in range(0, len(europe['cargoquery'])):
			# For Team Names
			if europe['cargoquery'][x]['title']['Team'] not in eu:
				eu.append(europe['cargoquery'][x]['title']['Team'])
				result[1]['teams'].append({'id' : 'id' + ''.join(filter(str.isalnum, europe['cargoquery'][x]['title']['Team'])), 'name' : europe['cargoquery'][x]['title']['Team'], 'img_name' : lp.get_team_logo(europe['cargoquery'][x]['title']['Team'])})

		# For players in team
		for y in range(0, len(result[1]['teams'])):
			#For players that we havent checked yet
			euPlayers = []
			for z in range(0, len(europe['cargoquery'])):
				if europe['cargoquery'][z]['title']['Team'] == result[1]['teams'][y]['name'] and europe['cargoquery'][z]['title']['ID'] not in euPlayersCheck:
					playerId = europe['cargoquery'][z]['title']['ID']
					euPlayersCheck.append(europe['cargoquery'][z]['title']['ID'])
					soloqid = site.api('cargoquery',
						limit = 'max',
						tables = "Players=P",
						where = f'ID = "{playerId}"',
						fields = "P.SoloqueueIds"
					)
					soloqid = to_dict(soloqid)
					if not soloqid['cargoquery']:
						euPlayers.append({'name' : europe['cargoquery'][z]['title']['ID'], 'role' : europe['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, europe['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'euw', 'soloqid' : '-1'})
					else:
						if not soloqid['cargoquery'][0]['title']['SoloqueueIds']:
							euPlayers.append({'name' : europe['cargoquery'][z]['title']['ID'], 'role' : europe['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, europe['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'euw', 'soloqid' : '-1'})
						else:
							soloqid = soloqid['cargoquery'][0]['title']['SoloqueueIds']
							soloqid = (soloqid.split(","))[0]
							soloqid = soloqid.split("(")
							soloqid[0] = soloqid[0].replace(" ", "")
							euPlayers.append({'name' : europe['cargoquery'][z]['title']['ID'], 'role' : europe['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, europe['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'euw', 'soloqid' : soloqid[0].lower()})
							if len(soloqid) > 1:
								soloqid[1] = soloqid[1].replace(')', '')
								euPlayers[0]['region'] = soloqid[1].lower()
			euPlayers.sort(key=lambda valeu: sort_order[valeu['role']])
			for i in euPlayers:
				if i['soloqid'] != '-1' and not re.search("[']{3}.*[']{3}.*", i['soloqid']) == None:
					i['soloqid'] = i['soloqid'].split("'''", 2)[2]
			result[1]['teams'][y].update({'players' : euPlayers})



		oceania = site.api('cargoquery',
			limit = 'max',
			tables = "ListplayerCurrent=PC",
			where = 'Team = \'Chiefs Esports Club\' or Team = \'Legacy Esports\' or Team = \'Dire Wolves\' or Team = \'Order\' or Team = \'Gravitas\' or Team = \'Avant Gaming\' or Team = \'Pentanet.GG\' or Team = \'MAMMOTH\'',
			fields = "PC.Team, PC.ID, PC.Residency, PC.Role"
		)

		oceania = to_dict(oceania)
		oce = []
		ocePlayersCheck = []
		for x in range(0, len(oceania['cargoquery'])):
			# For Team Names
			if oceania['cargoquery'][x]['title']['Team'] not in oce:
				oce.append(oceania['cargoquery'][x]['title']['Team'])
				result[2]['teams'].append({'id' : 'id' + ''.join(filter(str.isalnum, oceania['cargoquery'][x]['title']['Team'])), 'name' : oceania['cargoquery'][x]['title']['Team'], 'img_name' : lp.get_team_logo(oceania['cargoquery'][x]['title']['Team'])})
		# For players in team
		for y in range(0, len(result[2]['teams'])):
			#For players that we havent checked yet
			ocePlayers = []
			for z in range(0, len(oceania['cargoquery'])):
				if oceania['cargoquery'][z]['title']['Team'] == result[2]['teams'][y]['name'] and oceania['cargoquery'][z]['title']['ID'] not in ocePlayersCheck:
					playerId = oceania['cargoquery'][z]['title']['ID']
					ocePlayersCheck.append(oceania['cargoquery'][z]['title']['ID'])
					soloqid = site.api('cargoquery',
						limit = 'max',
						tables = "Players=P",
						where = f'ID = "{playerId}"',
						fields = "P.SoloqueueIds"
					)
					soloqid = to_dict(soloqid)
					if not soloqid['cargoquery']:
						ocePlayers.append({'name' : oceania['cargoquery'][z]['title']['ID'], 'role' : oceania['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, oceania['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'oce', 'soloqid' : '-1'})
					else:
						if not soloqid['cargoquery'][0]['title']['SoloqueueIds']:
							ocePlayers.append({'name' : oceania['cargoquery'][z]['title']['ID'], 'role' : oceania['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, oceania['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'oce', 'soloqid' : '-1'})
						else:
							soloqid = soloqid['cargoquery'][0]['title']['SoloqueueIds']
							soloqid = (soloqid.split(","))[0]
							soloqid = soloqid.split("(")
							soloqid[0] = soloqid[0].replace(" ", "")
							ocePlayers.append({'name' : oceania['cargoquery'][z]['title']['ID'], 'role' : oceania['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, oceania['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'oce', 'soloqid' : soloqid[0].lower()})
							if len(soloqid) > 1:
								soloqid[1] = soloqid[1].replace(')', '')
								ocePlayers[0]['region'] = soloqid[1].lower()
			ocePlayers.sort(key=lambda valoce: sort_order[valoce['role']])
			for i in ocePlayers:
				if i['soloqid'] != '-1' and not re.search("[']{3}.*[']{3}.*", i['soloqid']) == None:
					i['soloqid'] = i['soloqid'].split("'''", 2)[2]
			result[2]['teams'][y].update({'players' : ocePlayers})


		korea = site.api('cargoquery',
			limit = 'max',
			tables = "ListplayerCurrent=PC",
			where = 'Team = \'Gen.G\' or Team = \'T1\' or Team = \'DragonX\' or Team = \'Afreeca Freecs\' or Team = \'Damwon Gaming\' or Team = \'APK Prince\' or Team = \'Griffin\' or Team = \'Hanwha Life Esports\' or Team = \'KT Rolster\' or Team = \'Sandbox Gaming\'',
			fields = "PC.Team, PC.ID, PC.Residency, PC.Role"
		)

		korea = to_dict(korea)
		kr = []
		krPlayersCheck = []
		for x in range(0, len(korea['cargoquery'])):
			# For Team Names
			if korea['cargoquery'][x]['title']['Team'] not in kr:
				kr.append(korea['cargoquery'][x]['title']['Team'])
				result[3]['teams'].append({'id' : 'id' + ''.join(filter(str.isalnum, korea['cargoquery'][x]['title']['Team'])), 'name' : korea['cargoquery'][x]['title']['Team'], 'img_name' : lp.get_team_logo(korea['cargoquery'][x]['title']['Team'])})
		# For players in team
		for y in range(0, len(result[3]['teams'])):
			#For players that we havent checked yet
			krPlayers = []
			for z in range(0, len(korea['cargoquery'])):
				if korea['cargoquery'][z]['title']['Team'] == result[3]['teams'][y]['name'] and korea['cargoquery'][z]['title']['ID'] not in krPlayersCheck:
					playerId = korea['cargoquery'][z]['title']['ID']
					krPlayersCheck.append(korea['cargoquery'][z]['title']['ID'])
					soloqid = site.api('cargoquery',
						limit = 'max',
						tables = "Players=P",
						where = f'ID = "{playerId}"',
						fields = "P.SoloqueueIds"
					)
					soloqid = to_dict(soloqid)
					if not soloqid['cargoquery']:
						krPlayers.append({'name' : korea['cargoquery'][z]['title']['ID'], 'role' : korea['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, korea['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'kr', 'soloqid' : '-1'})
					else:
						if not soloqid['cargoquery'][0]['title']['SoloqueueIds']:
							krPlayers.append({'name' : korea['cargoquery'][z]['title']['ID'], 'role' : korea['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, korea['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'kr', 'soloqid' : '-1'})
						else:
							soloqid = soloqid['cargoquery'][0]['title']['SoloqueueIds']
							soloqid = (soloqid.split(","))[0]
							soloqid = soloqid.split("(")
							soloqid[0] = soloqid[0].replace(" ", "")
							krPlayers.append({'name' : korea['cargoquery'][z]['title']['ID'], 'role' : korea['cargoquery'][z]['title']['Role'], 'img_url' : ''.join(filter(str.isalnum, korea['cargoquery'][z]['title']['Role'])) + '.png', 'region' : 'kr', 'soloqid' : soloqid[0].lower()})
							if len(soloqid) > 1:
								soloqid[1] = soloqid[1].replace(')', '')
								krPlayers[0]['region'] = soloqid[1].lower()
			krPlayers.sort(key=lambda valkr: sort_order[valkr['role']])
			for i in krPlayers:
				if i['soloqid'] != '-1' and not re.search("[']{3}.*[']{3}.*", i['soloqid']) == None:
					i['soloqid'] = i['soloqid'].split("'''", 2)[2]
			result[3]['teams'][y].update({'players' : krPlayers})

		return_dict = {
			'lastUpdated' : datetime.datetime.now().strftime("%H:%M:%S, %d/%m/%Y"),
			'result' : result
		}

		with open('app/static/proplayers.pickle', 'wb') as output:
			pickle.dump(return_dict, output, pickle.HIGHEST_PROTOCOL)

		return (return_dict)

def filter_regions(x, region):

	if (region != None):
		
		filtered = list(filter(lambda d: d['region'] == region , x))
		return filtered

	else:
		return x

def filter_roles(x, role):

	if (role != None):
		for region in x:
			for team in region['teams']:
				toFilter = team['players']
				filtered = list(filter(lambda d: d['role'] == roles[role] , toFilter))
				team['players'] = filtered
	
	return x