#Import XML Change Variables for tree, league, and season
import xml.etree.ElementTree as ET
tree = ET.parse('c:/Users/Jeff/Dropbox/Top Scorer FC/EPL19-20.xml')
league = "English Premier League"
season = "2019-2020"
root = tree.getroot()

#Create/Open Files for output
outTable = open("TopTables.txt", "w", encoding='utf-8')
outResults = open("TopResults.txt", "w", encoding='utf-8')
tableHTML = open("TopTable.html", "w", encoding='utf-8')

#Variables
tslist = [] #List of Scorers
teamlist = [] #Teams list
tsActual = [] #Top Scorer List
tsVTeam = [] #Top Scorer V Team Collation
resultsList = [] #Game Results
table = [] #Table Results

#Create Player Class
class player:
    def __init__(self, name, team, goalcount):
        self.name = name 
        self.team = team
        self.goalcount = goalcount

#Create TS Player Class
class playerTS:
    def __init__(self, name, team, goalcount, wins = 0, loses = 0, draws = 0, goaldif = 0, points = 0, goalsFor = 0, goalsAgainst = 0):
        self.name = name 
        self.team = team
        self.goalcount = goalcount
        self.wins = wins
        self.loses = loses
        self.draws = draws
        self.goaldif = goaldif
        self.points = points
        self.goalsFor = goalsFor
        self.goalsAgainst = goalsAgainst

####CREATE FUNCTIONS####
#create team list
def getTeamList():
    for team in root.findall("league/team"):
        teamlist.append(team.text)
    teamlist.sort()

#Top Scorer List Duplicate and Count Function
def tsCheck(name, team):
    #check for duplicate
    checkList = []
    tuplist = ()
    tupCheck = (name, team)
    for obj in tslist:
        tuplist = (obj.name, obj.team)
        checkList.append(tuplist)
    #Add goal if in list
    if tupCheck in checkList:
        x = checkList.index(tupCheck)
        tslist[x].goalcount = tslist[x].goalcount + 1
    #Create new entry
    else:
        tslist.append( player(name, team, 1))

#Determine Top Scorer By Team
def tsTeam(x):
    tempList = []
    for obj in tslist:
        if obj.team == x:
            if not tempList:
                tempList.append( playerTS(obj.name, obj.team, obj.goalcount))
            elif obj.goalcount > tempList[0].goalcount:
                tempList.clear()
                tempList.append( playerTS(obj.name, obj.team, obj.goalcount))
            elif obj.goalcount == tempList[0].goalcount:
                tempList.append( playerTS(obj.name, obj.team, obj.goalcount)) 
    #If goalcount tied, get stats for players
    if len(tempList) > 1:
        for obj in tempList:
            statList = gameReader(obj.team, obj.name, 1)
            obj.wins = statList[0]
            obj.draws = statList[1]
            obj.loses = statList[2]
            obj.points = statList[3]
            obj.goalsFor = statList[4]
            obj.goalsAgainst = statList[5]
            obj.goaldif = statList[6]
        #[wins, draws, loses, points, goalsFor, goalsAgainst, goalDif] 
    #Sort player list
    tempList.sort(key=lambda x: (x.goalcount, x.points, x.goaldif, x.wins), reverse=True)
    #Add top player of list to Actual Top Scorers list
    if len(tempList) != 0:
        tsActual.append(playerTS(tempList[0].name, tempList[0].team, tempList[0].goalcount))

#Get Player Who Gets Most Points
def tsMVP(x, penalty=False):
    tempList = []
    for obj in tslist:
        if obj.team == x:
            tempList.append( playerTS(obj.name, obj.team, obj.goalcount)) 
    #If goalcount tied, get stats for players
        for obj in tempList:
            if penalty == False:
                statList = gameReader(obj.team, obj.name, 1)
            elif penalty == True:
                statList = gameReaderP(obj.team, obj.name, 1)
            obj.wins = statList[0]
            obj.draws = statList[1]
            obj.loses = statList[2]
            obj.points = statList[3]
            obj.goalsFor = statList[4]
            obj.goalsAgainst = statList[5]
            obj.goaldif = statList[6]
            #Check status of players by team
            #if obj.team == "Manchester United":
                #print(obj.name, obj.points)
        #[wins, draws, loses, points, goalsFor, goalsAgainst, goalDif] 
    #Sort player list
    tempList.sort(key=lambda x: (x.points, x.goalcount, x.goaldif, x.wins), reverse=True)
    #Add top player of list to Actual Top Scorers list
    if len(tempList) != 0:
        tsActual.append(playerTS(tempList[0].name, tempList[0].team, tempList[0].goalcount, tempList[0].wins, tempList[0].loses, tempList[0].draws, tempList[0].goaldif, tempList[0].points, tempList[0].goalsFor, tempList[0].goalsAgainst))       

#Evaluate Games Function
def gameReader(team, player, numPlayers, tsTeam = 'none', results = 0):
    wins = 0
    draws = 0
    loses = 0
    points = 0
    goalsFor = 0
    goalsAgainst = 0
    goalDif = 0
    global resultsList
    for game in root.findall("games/gameweek/game"):
        home = game.find('home').get('team')
        homeScore = 0
        away = game.find('away').get('team')
        awayScore = 0
        otherPlayer = 'nobody'

        if home == team or away == team: #run if team played game
            if numPlayers == 0: #No top scorer
                #Parse goals
                if tsTeam == home or tsTeam == away: #If opponent is currently calculating Top Scorer Team
                    otherPlayer = findTopScorer(tsTeam)
                    for goal in game.iter('goal'):
                        if goal.get('team') == team and goal.get('team') == home: #Add goal if team is home 
                            homeScore = homeScore + 1
                        elif goal.get('team') == team and goal.get('team') == away: #Add goal if team is home
                                awayScore = awayScore + 1
                        elif goal.get('team') != team and goal.get('team') == home: #Add goal if not top scorer team
                            if goal.text == otherPlayer:
                                homeScore = homeScore + 1
                        elif goal.get('team') != team and goal.get('team') == away: #Add goal if not top scorer team
                            if goal.text == otherPlayer:
                                awayScore = awayScore + 1   
                else: #if opponent is not current top scorer team
                    for goal in game.iter('goal'):
                        if goal.get('team') == home:
                            homeScore = homeScore + 1
                        else:
                            awayScore = awayScore + 1
            elif numPlayers == 1: #1 top scorer
                #parse goals
                for goal in game.iter('goal'):
                    if goal.get('team') == team and goal.get('team') == home: #Add goal if Top scorer is home team
                        if goal.text == player:
                            homeScore = homeScore + 1
                    elif goal.get('team') == team and goal.get('team') == away: #Add goal if Top Scorer is away team
                        if goal.text == player:
                            awayScore = awayScore + 1
                    elif goal.get('team') != team and goal.get('team') == home: #Add goal if not top scorer team
                        homeScore = homeScore + 1
                    elif goal.get('team') != team and goal.get('team') == away: #Add goal if not top scorer team
                        awayScore = awayScore + 1    
            elif numPlayers == 2: #2 Top scorers
                #Get top scorers
                if home == team:
                    otherPlayer = findTopScorer(away)
                    #print(findTopScorer(away))
                else:
                    otherPlayer = findTopScorer(home)
                    #print(findTopScorer(home))
                #parse goals
                for goal in game.iter('goal'):
                    if goal.get('team') == team and goal.get('team') == home: #Add goal if Top scorer is home team
                        if goal.text == player:
                            homeScore = homeScore + 1
                    elif goal.get('team') == team and goal.get('team') == away: #Add goal if Top Scorer is away team
                        if goal.text == player:
                            awayScore = awayScore + 1
                    elif goal.get('team') != team and goal.get('team') == home: #Add goal if not top scorer and is other team top scorer
                        if goal.text == otherPlayer:
                            homeScore = homeScore + 1 
                    elif goal.get('team') != team and goal.get('team') == away: #Add goal if not top scorer and is other team top scorer
                        if goal.text == otherPlayer:
                            awayScore = awayScore + 1
            #Collect Game Results
            if results:
                resultsList.append(f'{home} {homeScore}-{awayScore} {away}')
                resultsList.sort()
            #Remove Duplicate Results if evaluating all players
            if numPlayers == 2:
                resultsList = list(dict.fromkeys(resultsList))
            #Parse Wins, Draws, Loses, Points, GF, GA
            if team == home:
                if homeScore > awayScore:
                    wins = wins + 1
                    points = points + 3
                    goalsFor = goalsFor + homeScore
                    goalsAgainst = goalsAgainst + awayScore
                elif homeScore < awayScore:
                    loses = loses + 1
                    points = points + 0
                    goalsFor = goalsFor + homeScore
                    goalsAgainst = goalsAgainst + awayScore
                elif homeScore == awayScore:
                    draws = draws + 1
                    points = points + 1
                    goalsFor = goalsFor + homeScore
                    goalsAgainst = goalsAgainst + awayScore
            elif team == away:
                if awayScore > homeScore:
                    wins = wins + 1
                    points = points + 3
                    goalsFor = goalsFor + awayScore
                    goalsAgainst = goalsAgainst + homeScore
                elif awayScore < homeScore:
                    loses = loses + 1
                    points = points + 0
                    goalsFor = goalsFor + awayScore
                    goalsAgainst = goalsAgainst + homeScore
                elif awayScore == homeScore:
                    draws = draws + 1
                    points = points + 1
                    goalsFor = goalsFor + awayScore
                    goalsAgainst = goalsAgainst + homeScore
    #Calculate Goal Dif
    goalDif = goalsFor - goalsAgainst
    return [wins, draws, loses, points, goalsFor, goalsAgainst, goalDif] 

def gameReaderP(team, player, numPlayers, tsTeam = 'none', results = 0):
    wins = 0
    draws = 0
    loses = 0
    points = 0
    goalsFor = 0
    goalsAgainst = 0
    goalDif = 0
    global resultsList
    for game in root.findall("games/gameweek/game"):
        home = game.find('home').get('team')
        homeScore = 0
        away = game.find('away').get('team')
        awayScore = 0
        otherPlayer = 'nobody'

        if home == team or away == team: #run if team played game
            if numPlayers == 0: #No top scorer
                #Parse goals
                if tsTeam == home or tsTeam == away: #If opponent is currently calculating Top Scorer Team
                    otherPlayer = findTopScorer(tsTeam)
                    for goal in game.iter('goal'):
                        if goal.get('team') == team and goal.get('team') == home and goal.get('pen') != 'true': #Add goal if team is home 
                            homeScore = homeScore + 1
                        elif goal.get('team') == team and goal.get('team') == away and goal.get('pen') != 'true': #Add goal if team is home
                                awayScore = awayScore + 1
                        elif goal.get('team') != team and goal.get('team') == home and goal.get('pen') != 'true': #Add goal if not top scorer team
                            if goal.text == otherPlayer:
                                homeScore = homeScore + 1
                        elif goal.get('team') != team and goal.get('team') == away and goal.get('pen') != 'true': #Add goal if not top scorer team
                            if goal.text == otherPlayer:
                                awayScore = awayScore + 1   
                else: #if opponent is not current top scorer team
                    for goal in game.iter('goal'):
                        if goal.get('team') == home and goal.get('pen') != 'true':
                            homeScore = homeScore + 1
                        elif goal.get('pen') != 'true':
                            awayScore = awayScore + 1
            elif numPlayers == 1: #1 top scorer
                #parse goals
                for goal in game.iter('goal'):
                    if goal.get('team') == team and goal.get('team') == home and goal.get('pen') != 'true': #Add goal if Top scorer is home team
                        if goal.text == player:
                            homeScore = homeScore + 1
                    elif goal.get('team') == team and goal.get('team') == away and goal.get('pen') != 'true': #Add goal if Top Scorer is away team
                        if goal.text == player:
                            awayScore = awayScore + 1
                    elif goal.get('team') != team and goal.get('team') == home and goal.get('pen') != 'true': #Add goal if not top scorer team
                        homeScore = homeScore + 1
                    elif goal.get('team') != team and goal.get('team') == away and goal.get('pen') != 'true': #Add goal if not top scorer team
                        awayScore = awayScore + 1    
            elif numPlayers == 2: #2 Top scorers
                #Get top scorers
                if home == team:
                    otherPlayer = findTopScorer(away)
                    #print(findTopScorer(away))
                else:
                    otherPlayer = findTopScorer(home)
                    #print(findTopScorer(home))
                #parse goals
                for goal in game.iter('goal'):
                    if goal.get('team') == team and goal.get('team') == home and goal.get('pen') != 'true': #Add goal if Top scorer is home team
                        if goal.text == player:
                            homeScore = homeScore + 1
                    elif goal.get('team') == team and goal.get('team') == away and goal.get('pen') != 'true': #Add goal if Top Scorer is away team
                        if goal.text == player:
                            awayScore = awayScore + 1
                    elif goal.get('team') != team and goal.get('team') == home and goal.get('pen') != 'true': #Add goal if not top scorer and is other team top scorer
                        if goal.text == otherPlayer:
                            homeScore = homeScore + 1 
                    elif goal.get('team') != team and goal.get('team') == away and goal.get('pen') != 'true': #Add goal if not top scorer and is other team top scorer
                        if goal.text == otherPlayer:
                            awayScore = awayScore + 1
            #Collect Game Results
            if results:
                resultsList.append(f'{home} {homeScore}-{awayScore} {away}')
                resultsList.sort()
            #Remove Duplicate Results if evaluating all players
            if numPlayers == 2:
                resultsList = list(dict.fromkeys(resultsList))
            #Parse Wins, Draws, Loses, Points, GF, GA
            if team == home:
                if homeScore > awayScore:
                    wins = wins + 1
                    points = points + 3
                    goalsFor = goalsFor + homeScore
                    goalsAgainst = goalsAgainst + awayScore
                elif homeScore < awayScore:
                    loses = loses + 1
                    points = points + 0
                    goalsFor = goalsFor + homeScore
                    goalsAgainst = goalsAgainst + awayScore
                elif homeScore == awayScore:
                    draws = draws + 1
                    points = points + 1
                    goalsFor = goalsFor + homeScore
                    goalsAgainst = goalsAgainst + awayScore
            elif team == away:
                if awayScore > homeScore:
                    wins = wins + 1
                    points = points + 3
                    goalsFor = goalsFor + awayScore
                    goalsAgainst = goalsAgainst + homeScore
                elif awayScore < homeScore:
                    loses = loses + 1
                    points = points + 0
                    goalsFor = goalsFor + awayScore
                    goalsAgainst = goalsAgainst + homeScore
                elif awayScore == homeScore:
                    draws = draws + 1
                    points = points + 1
                    goalsFor = goalsFor + awayScore
                    goalsAgainst = goalsAgainst + homeScore
    #Calculate Goal Dif
    goalDif = goalsFor - goalsAgainst
    return [wins, draws, loses, points, goalsFor, goalsAgainst, goalDif]

#Find top scorer
def findTopScorer(team):
    for obj in tsActual:
        if obj.team == team:
            return obj.name

#Create Top Scorers list from Goals
def createScorerList(penalty=False):
    for goal in root.findall("games/gameweek/game/goal"):
        if goal.get('pen') == 'true' and penalty==True:
            #print('penalty')
            continue
        else:
            #Get player name and team
            scorer = goal.text
            team = goal.get('team')
            #Send to top scorer list function
            tsCheck(scorer, team)

#create table
def tableCreate(team, allScorers=False, addPlayer=False, penalty=False):
    tempList = []
    if penalty == False:
        for x in teamlist:
            if x == team:
                tempList = gameReader(x, findTopScorer(x), 1, team, 1)
                table.append(playerTS(findTopScorer(x), x, tempList[4], tempList[0], tempList[2], tempList[1], tempList[6], tempList[3], tempList[4], tempList[5]))
                if addPlayer == True: 
                    tsVTeam.append(playerTS(findTopScorer(x), x, tempList[4], tempList[0], tempList[2], tempList[1], tempList[6], tempList[3], tempList[4], tempList[5]))
            elif allScorers:
                tempList = gameReader(x, findTopScorer(x), 2, team, 1)
                table.append(playerTS(findTopScorer(x), x, tempList[4], tempList[0], tempList[2], tempList[1], tempList[6], tempList[3], tempList[4], tempList[5])) 
            else:
                tempList = gameReader(x, findTopScorer(x), 0, team, 0)
                table.append(playerTS(findTopScorer(x), x, tempList[4], tempList[0], tempList[2], tempList[1], tempList[6], tempList[3], tempList[4], tempList[5]))
        table.sort(key=lambda x: (x.points, x.goaldif, x.goalsFor), reverse=True)
    elif penalty == True:
        for x in teamlist:
            if x == team:
                tempList = gameReaderP(x, findTopScorer(x), 1, team, 1)
                table.append(playerTS(findTopScorer(x), x, tempList[4], tempList[0], tempList[2], tempList[1], tempList[6], tempList[3], tempList[4], tempList[5]))
                if addPlayer == True: 
                    tsVTeam.append(playerTS(findTopScorer(x), x, tempList[4], tempList[0], tempList[2], tempList[1], tempList[6], tempList[3], tempList[4], tempList[5]))
            elif allScorers:
                tempList = gameReaderP(x, findTopScorer(x), 2, team, 1)
                table.append(playerTS(findTopScorer(x), x, tempList[4], tempList[0], tempList[2], tempList[1], tempList[6], tempList[3], tempList[4], tempList[5])) 
            else:
                tempList = gameReaderP(x, findTopScorer(x), 0, team, 0)
                table.append(playerTS(findTopScorer(x), x, tempList[4], tempList[0], tempList[2], tempList[1], tempList[6], tempList[3], tempList[4], tempList[5]))
        table.sort(key=lambda x: (x.points, x.goaldif, x.goalsFor), reverse=True)

#Write Tables and Results
def tableResultsWrite(team, allScorers=False):
    i=1
    #Print Tables
    if allScorers:
        #print('All Top Scorers')
        outTable.write('\nAll Top Scorers - Versus Individual\n\n')
        tableHTML.write('\n<h2>All Top Scorers - Versus Individual</h2>\n')
        outTable.write('|Pos|Team|Name|W|D|L|GF|GA|GD|Points|\n|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|\n')
        tableHTML.write('<table><tr><th>Pos</th><th>Team</th><th>Name</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Points</th></tr>\n')
    else:
        #print(f'{team} - {findTopScorer(team)}')
        outTable.write(f'\n{team} - {findTopScorer(team)}\n\n')
        tableHTML.write(f'\n<h2>{team} - {findTopScorer(team)}</h2>\n')
        outTable.write('|Pos|Team|W|D|L|GF|GA|GD|Points|\n|:-|:-|:-|:-|:-|:-|:-|:-|:-|\n')
        tableHTML.write('<table><tr><th>Pos</th><th>Team</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Points</th></tr>\n')
    for obj in table:
        if allScorers:
            #print(obj.team, obj.name, obj.wins, obj.draws, obj.loses, obj.goalsFor, obj.goalsAgainst, obj.goaldif, obj.points)
            outTable.write(f'|{i}|{obj.team}|{obj.name}|{obj.wins}|{obj.draws}|{obj.loses}|{obj.goalsFor}|{obj.goalsAgainst}|{obj.goaldif}|{obj.points}|\n')
            tableHTML.write(f'<tr><td>{i}</td><td>{obj.team}</td><td>{obj.name}</td><td>{obj.wins}</td><td>{obj.draws}</td><td>{obj.loses}</td><td>{obj.goalsFor}</td><td>{obj.goalsAgainst}</td><td>{obj.goaldif}</td><td>{obj.points}</td></tr>\n')
        else:
            #print(obj.team, obj.wins, obj.draws, obj.loses, obj.goalsFor, obj.goalsAgainst, obj.goaldif, obj.points)
            outTable.write(f'|{i}|{obj.team}|{obj.wins}|{obj.draws}|{obj.loses}|{obj.goalsFor}|{obj.goalsAgainst}|{obj.goaldif}|{obj.points}|\n')
            tableHTML.write(f'<tr><td>{i}</td><td>{obj.team}</td><td>{obj.wins}</td><td>{obj.draws}</td><td>{obj.loses}</td><td>{obj.goalsFor}</td><td>{obj.goalsAgainst}</td><td>{obj.goaldif}</td><td>{obj.points}</td></tr>\n')
        i= i + 1
    tableHTML.write('</table>\n')

    #Print Results
    #if allScorers:
        #print('All Top Scorers')
        #outResults.write('\nAll Top Scorers\n\n')
    #else:
       # print(f'{team} - {findTopScorer(team)}')
        #outResults.write(f'\n{team} - {findTopScorer(team)}\n\n')
    #outResults.write('|Results|\n|:-|\n')
    #for x in resultsList:
        #print(x)
        #outResults.write(f'|{x}|\n')

#create top text
def createHeader():
    tableHTML.write(f'<h1>Top Scorer FC</h1>\n<h3>{league} - {season}</h3>\n\n')
    createTOC()

#create table of contents
def createTOC():
    tableHTML.write('<a href="#tsi">Top Scorer - Versus Individual</a>: Points total where only top scorer goals count for any team</br>\n')
    tableHTML.write('<a href="#tst">Top Scorer - Versus Teams</a>: - Individual Team Tables where only top scorer goals count versus entire team</br>\n')
    tableHTML.write('<a href="#tstc">Top Scorer - Versus Teams</a>: Points total where only top scorer goals count versus entire team - collated</br>\n')
    tableHTML.write('<a href="#mei">Most Effective - Versus Individuals</a>: Points total where most effective players goals count for any team</br>\n')
    tableHTML.write('<a href="#metc">Most Effective - Versus Teams</a>: Most effective player versus entire team results - collated</br>\n')
    tableHTML.write('<h3>No Penalties</h3>Penalties do not count for anybody</br>\n')
    tableHTML.write('<a href="#tsip">Top Scorer - Versus Individual</a>: Points total where only top scorer goals count for any team</br>\n')
    tableHTML.write('<a href="#tstp">Top Scorer - Versus Teams</a>: - Individual Team Tables where only top scorer goals count versus entire team</br>\n')
    tableHTML.write('<a href="#tstcp">Top Scorer - Versus Teams</a>: Points total where only top scorer goals count versus entire team - collated</br>\n')
    tableHTML.write('<a href="#meip">Most Effective - Versus Individuals</a>: Points total where most effective players goals count for any team</br>\n')
    tableHTML.write('<a href="#metcp">Most Effective - Versus Teams</a>: Most effective player versus entire team results - collated</br>\n')
        
        

def main():
    getTeamList()
    createScorerList()
    #Create top scorers
    for x in teamlist:
        tsTeam(x)
    #Prep Html files
    tableHTML.write("<html><body>")
    #Generate and Print table for all top scorers
    createHeader()
    tableCreate('All Jeff FC', 1)
    tableHTML.write('<a name="tsi"></a>')
    tableResultsWrite('All Jeff FC', 1)
    resultsList.clear()
    table.clear()
  
    #Generate and Print tables for top scorers
    tableHTML.write('<a name="tst"></a>')
    for x in teamlist:
        tableCreate(x, addPlayer=1)
        tableResultsWrite(x)
        resultsList.clear()
        table.clear()

    #Print Collated Top Scorer v teams list
    tsVTeam.sort(key=lambda x: (x.points, x.goaldif, x.goalsFor), reverse=True)
    tableHTML.write('<a name="tstc"></a>')
    outTable.write('\nTop Scorer - Versus Teams\n\n')
    tableHTML.write('\n<h2>Top Scorer - Versus Teams</h2>\n')
    outTable.write('|Team|Name|W|D|L|GF|GA|GD|Points|\n|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|\n')
    tableHTML.write('<table><tr><th>Team</th><th>Name</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Points</th></tr>\n')
    for obj in tsVTeam:
        #print(obj.team, obj.name, obj.wins, obj.draws, obj.loses, obj.goalsFor, obj.goalsAgainst, obj.goaldif, obj.points)
        outTable.write(f'{obj.team}|{obj.name}|{obj.wins}|{obj.draws}|{obj.loses}|{obj.goalsFor}|{obj.goalsAgainst}|{obj.goaldif}|{obj.points}|\n')
        tableHTML.write(f'<tr><td>{obj.team}</td><td>{obj.name}</td><td>{obj.wins}</td><td>{obj.draws}</td><td>{obj.loses}</td><td>{obj.goalsFor}</td><td>{obj.goalsAgainst}</td><td>{obj.goaldif}</td><td>{obj.points}</td></tr>\n')
    resultsList.clear()
    table.clear()
    tableHTML.write('</table>\n')
    

    #Create MVP Players
    tsActual.clear()
    for x in teamlist:
        tsMVP(x)
    tableHTML.write('<a name="mei"></a>')
    tableHTML.write('\n<h1>Most Effective Player</h1>\nTables for player whose goals would contribute the highest points total.\n\n')
    tableCreate('All Jeff FC', 1, penalty=True)
    tableResultsWrite('All Jeff FC', 1)
    tsActual.sort(key=lambda x: (x.points, x.goaldif, x.goalsFor), reverse=True)
    #print('All Top Scorers')
    outTable.write('\nMost Effective Player - Versus Teams\n\n')
    tableHTML.write('<a name="metc"></a>')
    tableHTML.write('\n<h2>Most Effective Player - Versus Teams</h2>\n')
    outTable.write('|Team|Name|W|D|L|GF|GA|GD|Points|\n|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|\n')
    tableHTML.write('<table><tr><th>Team</th><th>Name</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Points</th></tr>\n')
    for obj in tsActual:
        #print(obj.team, obj.name, obj.wins, obj.draws, obj.loses, obj.goalsFor, obj.goalsAgainst, obj.goaldif, obj.points)
        outTable.write(f'{obj.team}|{obj.name}|{obj.wins}|{obj.draws}|{obj.loses}|{obj.goalsFor}|{obj.goalsAgainst}|{obj.goaldif}|{obj.points}|\n')
        tableHTML.write(f'<tr><td>{obj.team}</td><td>{obj.name}</td><td>{obj.wins}</td><td>{obj.draws}</td><td>{obj.loses}</td><td>{obj.goalsFor}</td><td>{obj.goalsAgainst}</td><td>{obj.goaldif}</td><td>{obj.points}</td></tr>\n')
    resultsList.clear()
    table.clear()
    tableHTML.write('</table>\n')

    #no penalties

    tslist.clear()
    tsActual.clear() 
    tsVTeam.clear()
    resultsList.clear()

    tableHTML.write('<h1>Top Scorer FC - No Penalties</h1>\n')

    createScorerList(penalty=True)
    #Create top scorers
    for x in teamlist:
        tsTeam(x)

    #Generate and Print table for all top scorers (no pen)
    tableCreate('All Jeff FC', 1, penalty=True)
    tableHTML.write('<a name="tsip"></a>')
    tableResultsWrite('All Jeff FC', 1)
    resultsList.clear()
    table.clear()
  
    #Generate and Print tables for top scorers (no pen)
    tableHTML.write('<a name="tstp"></a>')
    for x in teamlist:
        tableCreate(x, addPlayer=1, penalty=True)
        tableResultsWrite(x)
        resultsList.clear()
        table.clear()

    #Print Collated Top Scorer v teams list (no pen)
    tsVTeam.sort(key=lambda x: (x.points, x.goaldif, x.goalsFor), reverse=True)
    tableHTML.write('<a name="tstcp"></a>')
    outTable.write('\nTop Scorer - Versus Teams (no pens)\n\n')
    tableHTML.write('\n<h2>Top Scorer - Versus Teams (no pens)</h2>\n')
    outTable.write('|Team|Name|W|D|L|GF|GA|GD|Points|\n|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|\n')
    tableHTML.write('<table><tr><th>Team</th><th>Name</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Points</th></tr>\n')
    for obj in tsVTeam:
        #print(obj.team, obj.name, obj.wins, obj.draws, obj.loses, obj.goalsFor, obj.goalsAgainst, obj.goaldif, obj.points)
        outTable.write(f'{obj.team}|{obj.name}|{obj.wins}|{obj.draws}|{obj.loses}|{obj.goalsFor}|{obj.goalsAgainst}|{obj.goaldif}|{obj.points}|\n')
        tableHTML.write(f'<tr><td>{obj.team}</td><td>{obj.name}</td><td>{obj.wins}</td><td>{obj.draws}</td><td>{obj.loses}</td><td>{obj.goalsFor}</td><td>{obj.goalsAgainst}</td><td>{obj.goaldif}</td><td>{obj.points}</td></tr>\n')
    resultsList.clear()
    table.clear()
    tableHTML.write('</table>\n')

    #Create MVP Players (no pen)
    tsActual.clear()
    for x in teamlist:
        tsMVP(x, penalty=True)
    tableHTML.write('<a name="meip"></a>')
    tableHTML.write('\n<h1>Most Effective Player (no pens)</h1>\nTables for player whose goals would contribute the highest points total. (no pens)\n\n')
    tableCreate('All Jeff FC', 1, penalty=True)
    tableResultsWrite('All Jeff FC', 1)
    tsActual.sort(key=lambda x: (x.points, x.goaldif, x.goalsFor), reverse=True)
    #print('All Top Scorers')
    outTable.write('\nMost Effective Player - Versus Teams (no pens)\n\n')
    tableHTML.write('<a name="metcp"></a>')
    tableHTML.write('\n<h2>Most Effective Player - Versus Teams (no pens)</h2>\n')
    outTable.write('|Team|Name|W|D|L|GF|GA|GD|Points|\n|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|\n')
    tableHTML.write('<table><tr><th>Team</th><th>Name</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Points</th></tr>\n')
    for obj in tsActual:
        #print(obj.team, obj.name, obj.wins, obj.draws, obj.loses, obj.goalsFor, obj.goalsAgainst, obj.goaldif, obj.points)
        outTable.write(f'{obj.team}|{obj.name}|{obj.wins}|{obj.draws}|{obj.loses}|{obj.goalsFor}|{obj.goalsAgainst}|{obj.goaldif}|{obj.points}|\n')
        tableHTML.write(f'<tr><td>{obj.team}</td><td>{obj.name}</td><td>{obj.wins}</td><td>{obj.draws}</td><td>{obj.loses}</td><td>{obj.goalsFor}</td><td>{obj.goalsAgainst}</td><td>{obj.goaldif}</td><td>{obj.points}</td></tr>\n')
    resultsList.clear()
    table.clear()
    tableHTML.write('</table>\n')

    #Finish files
    tableHTML.write("</body></html>")
    outTable.close
    outResults.close
    tableHTML.close

    #End
    print('Finished')

if __name__ == "__main__": main()
#Testing Purposes
#print('BREAK FOR TEST PRINTS')
#print(root[1][1].attrib)
#for obj in tslist:
   #print(obj.name, obj.team, obj.goalcount)
#for obj in tsActual:
    #print(obj.name, obj.team, obj.wins, obj.draws, obj.loses, obj.goalsFor, obj.goalsAgainst, obj.goaldif, obj.points)
#print(teamlist)

#Sort Top Scorers List by goals
#tslist.sort(key=lambda x: (x.team, x.goalcount), reverse=True)