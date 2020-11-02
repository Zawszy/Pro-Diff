from flask import render_template, request
from app import app

from pprint import pprint

from functions.getstreams import get_streams
from functions.getprofiles import get_profiles, get_one_match
from functions.getcomparematches import compare_matches
from functions.getcomparestats import compare_stats
from functions.ppData import get_pros

@app.route('/')
@app.route('/index')
def index():
    
    data = get_streams()

    return render_template('index.html', data=data)

@app.route('/profile')
def profile():

    summoner = request.args.get('username')
    region = request.args.get('region')
    filter_champ_id = request.args.get('cid')
    filter_role_id = request.args.get('rid')
    
    data = get_profiles(summoner, region, filter_champ_id, filter_role_id)


    if data == "no-user":
        return render_template('profile.html', data=None)            
    elif data['matches'] == "no-match":
        return render_template('profile.html', data=data, match=False)
    return render_template('profile.html', data=data)

@app.route('/compare')
def compare():

    summ1 = request.args.get('user1')
    r1 = request.args.get('r1')
    summ2 = request.args.get('user2')
    r2 = request.args.get('r2')
    match1 = request.args.get('match1')
    match2 = request.args.get('match2')

    data = compare_matches(summ1, r1, summ2, r2)
    
    case1 = True
    case2 = True
    case3 = True
    case4 = True
    
    #if summ1 is not given or is not found in database
    if summ1 is None or data[0] is None:
        case1 = False
    #if summ1 has no matches or match1 is not given
    if data[0] is not None:
        if data[0][1] is None or match1 is None:
            case3 = False
    #if summ2 is not given or is not found in database
    if summ2 is None or data[1] is None:
        case2 = False
    #if summ2 has no matches or match2 is not given
    if data[1] is not None:
        if data[1][1] is None or match2 is None:    
            case4 = False
    
    #flags for various cases
    flags = {
        'summ1_exists' : case1,
        'summ2_exists' : case2,
        'match1_exists' : (match1 is not None) or case3,
        'match2_exists' : (match2 is not None) or case4,
    }
    
    #no summoners
    if not flags['summ1_exists'] and not flags['summ2_exists']:
        return render_template('compare-template.html', player_info = None, flags=flags)
    #summ1 doesnt exist summ2 exists with match2
    elif not flags['summ1_exists'] and flags['summ2_exists'] and flags['match2_exists']:
        player2_match = []
        for i in data[1][1]:
            if str(i['matchId']) == str(match2):
                player2_match.append(i)
        return render_template('compare-template.html', player_info = (None, data[1][0]),
        matches=(None, player2_match), flags=flags)
    #summ1 doesnt exist summ2 exists but no match2
    elif not flags['summ1_exists'] and flags['summ2_exists'] and not flags['match2_exists']:
        return render_template('compare-template.html', player_info = (None, data[1][0]),
        matches=(None, data[1][1]), flags=flags)
    #summ1 exist summ2 doesnt exist with match1
    elif flags['match1_exists'] and flags['summ1_exists'] and not flags['summ2_exists']:
        player1_match = get_one_match(summ1, match1, r1)
        return render_template('compare-template.html', player_info=(data[0][0], None),
        matches=(player1_match, None), flags=flags)
    #summ1 exist summ2 doesnt exist but no match1
    elif flags['summ1_exists'] and not flags['match1_exists'] and not flags['summ2_exists']:
        return render_template('compare-template.html', player_info = (data[0][0], None),
        matches=(data[0][1], None), flags=flags)
    #summ1 exist summ2 exist but no match1 no match2
    elif flags['summ1_exists'] and flags['summ2_exists'] and not flags['match1_exists'] and not flags['match2_exists']:
        return render_template('compare-template.html', player_info = (data[0][0], data[1][0]),
        matches=(data[0][1], data[1][1]), flags=flags)
    #summ1 exist summ2 exist but no match1 yes match2
    elif flags['summ1_exists'] and flags['summ2_exists'] and not flags['match1_exists'] and flags['match2_exists']:
        player2_match = []
        for i in data[1][1]:
            if str(i['matchId']) == str(match2):
                player2_match.append(i)
        return render_template('compare-template.html', player_info = (data[0][0], data[1][0]),
        matches=(data[0][1], player2_match), flags=flags)
    #summ1 exist summ2 exist but yes match1 no match2
    elif flags['summ1_exists'] and flags['summ2_exists'] and flags['match1_exists'] and not flags['match2_exists']:
        player1_match = get_one_match(summ1, match1, r1)
        return render_template('compare-template.html', player_info = (data[0][0], data[1][0]),
        matches=(player1_match, data[1][1]), flags=flags)
    #summ1 exist summ2 exist but no match1 no match2
    elif flags['summ1_exists'] and flags['summ2_exists'] and not flags['match1_exists'] and not flags['match2_exists']:
        return render_template('compare-template.html', player_info = (data[0][0], data[1][0]),
        matches=(data[0][1], data[1][1]), flags=flags)
    #everything exists
    else:
        return render_template('compare-template.html', player_info=(data[0][0], data[1][0]),
        matches=(data[0][1], data[1][1]), flags=flags)

@app.route('/compare-stats')
def comparestats():

    match_one_id = request.args.get('match1')
    summ1 = request.args.get('user1')
    r1 = request.args.get('r1')
    match_two_id = request.args.get('match2')
    summ2 = request.args.get('user2')
    r2 = request.args.get('r2')

    data = compare_stats(match_one_id, summ1, match_two_id, summ2, r1, r2)

    return render_template('compare-stats.html', data=data)

@app.route('/pro-players')
def pro_players():

    update = request.args.get('update')

    region = request.args.get('reid')
    role = request.args.get('rid')

    data = get_pros(update, region, role)

    return render_template('pros.html', data=data)
