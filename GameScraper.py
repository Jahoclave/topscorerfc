#Variables
matchStart = 58897
matchEnd = 59275
preURL = "https://www.premierleague.com/match/"
season = "2020-2021"
league = "English Premier League"

#Import html process
from lxml import html
import requests
import time

#create output file
outGames = open("LeagueResults.xml", "w", encoding='utf-8')

#Define HTML Class
def getTeams(tree):
    _home = tree.xpath('//div[@class="team home"]/a[@class="teamName"]/span[@class="long"]/text()')
    _away = tree.xpath('//div[@class="team away"]/a[@class="teamName"]/span[@class="long"]/text()')
    _home = _home[0]
    _away = _away[0]
    return [_home, _away]

#Clean list
def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

#Get goals
def getGoals(tree, team):
    _red = "Red"
    _goals = []
    _type = []
    _finalTemp = []
    _finalPlayer = []
    for node in tree.xpath(f'//div[@class="matchEvents matchEventsContainer"]/div[@class="{team}"]'):
        #_type = node.xpath(f'//div[@class="matchEvents matchEventsContainer"]/div[@class="{team}"]/div/div/div/span/text()')
        #_type.append('Goal')
        #print(_type)
        _player = node.xpath(f'//div[@class="matchEvents matchEventsContainer"]/div[@class="{team}"]/div/a/text()')
        #print(_player)
        _tempString = node.xpath(f'//div[@class="matchEvents matchEventsContainer"]/div[@class="{team}"]/div/text()')
        _tempInfo = node.xpath(f'//div[@class="matchEvents matchEventsContainer"]/div[@class="{team}"]/div/div/div/span/text()')


         
    #clean up string

    _tempString = [x for x in _tempString if not x.startswith('\n')]

    #remove red cards
    q = 0
    if(len(_tempInfo)) > 0:
        for x in _tempInfo:
            if _red in x:
                _player.pop(q)
                _tempString.pop(q)
            else:
                q += 1
  
    
    #Seperate events and adjust players
    i = 0
    for x in _tempString:
        l = 1
        newX = []
        newX = x.split(',')
        _finalTemp.extend(newX)
        #print(len(newX))
        if len(newX) > l:
           TimeAdd = len(newX) - l
           while TimeAdd >= 0:
                #increase player by new amount
               _finalPlayer.append(_player[i])
               TimeAdd -= 1
        else:
            #only add one instance of player
            _finalPlayer.append(_player[i])
        i += 1
        
    #print(_finalPlayer)
    #print(_finalTemp)
    #Create Type
    for x in _finalTemp:
        if "pen" in x:
            _type.append('Penalty')
        elif "og" in x:
            _type.append('Own Goal')
        else:
            _type.append('Goal')
    #print(_type)
    #create tuple          
    _goals = playerTuples(_type, _finalPlayer)
    #print (_goals)
    return _goals

def playerTuples(gType, player):
    i = 0
    l = len(gType)
    _list = []
    while i < (l):
        p = player[i]
        g = gType[i]
        
        _tuple = (p, g)
        _list.append(_tuple)
        i += 1
    return _list

#xml writing functions
def xmlStart(season):
    outGames.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<season year="{season}">\n\t<games>\n\t\t<gameweek>\n')

def endGameXML():
    outGames.write('\n\t\t</gameweek>\n\t</games>\n')

def endXML():
    outGames.write('</season>')
    
def gameXML(home, away, homeGoals, awayGoals):
    outGames.write(f'\t\t\t<game>\n\t\t\t\t<home team="{home}" />\n\t\t\t\t<away team="{away}" />\n')
    for x in homeGoals:
        if x[1] == 'Own Goal':
            outGames.write(f'\t\t\t\t<goal team="{home}" pen="false">Own Goal</goal>\n')
        if x[1] == 'Penalty':
            outGames.write(f'\t\t\t\t<goal team="{home}" pen="true">{x[0]}</goal>\n')
        if x[1] == 'Goal':
            outGames.write(f'\t\t\t\t<goal team="{home}" pen="false">{x[0]}</goal>\n')
    for x in awayGoals:
        if x[1] == 'Own Goal':
            outGames.write(f'\t\t\t\t<goal team="{away}" pen="false">Own Goal</goal>\n')
        if x[1] == 'Penalty':
            outGames.write(f'\t\t\t\t<goal team="{away}" pen="true">{x[0]}</goal>\n')
        if x[1] == 'Goal':
            outGames.write(f'\t\t\t\t<goal team="{away}" pen="false">{x[0]}</goal>\n')
    outGames.write('\t\t\t</game>\n')

def printTeamXML(teams, league):
    outGames.write(f'\t<league name="{league}">\n')
    for x in teams:
        outGames.write(f'\t\t<team>{x}</team>\n')
    outGames.write('\t</league>\n')

def main(mStart, mEnd, pUrl):
    #function variables
    _teamMasterList = []

    #write opening xml
    xmlStart(season)
    while mStart < (mEnd + 1):
        print(mStart)
        #Gets url content
        tries = 10
        for i in range (tries):
            try:
                page = requests.get(f'{pUrl}{mStart}', timeout=30)
            except requests.ConnectionError as e:
                if i < tries - 1:
                    print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
                    print(str(e))
                    time.sleep(30)
                    continue
                else:
                    raise
            except requests.Timeout as e:
                if i < tries - 1:
                    print("OOPS!! Timeout Error")
                    print(str(e))
                    time.sleep(30)
                    continue
                else:
                    raise
            except requests.RequestException as e:
                if i < tries - 1:
                    print("OOPS!! General Error")
                    print(str(e))
                    time.sleep(30)
                    continue
                else:
                    raise
            break

        #Sets html to variable tree        
        tree = html.fromstring(page.content)
        
        #gets teams and appends to master list
        _teamList = getTeams(tree)
        _home = _teamList[0]
        _away = _teamList[1]
        _teamMasterList.append(_home)
        _teamMasterList.append(_away)

        #Get goals
        _homeGoals = getGoals(tree, 'home')
        _awayGoals = getGoals(tree, 'away')

        #Write game xml
        gameXML(_home, _away, _homeGoals, _awayGoals)

        #Iterate game page url number
        mStart += 1
        time.sleep(3)
    
    #Print End of Games XML
    endGameXML()

    #Remove Duplicates from team list
    _teamMasterList = list(dict.fromkeys(_teamMasterList))
    printTeamXML(_teamMasterList, league)

    #Print end of XML
    endXML()
    print('finished')

if __name__ == "__main__": main(matchStart, matchEnd, preURL)