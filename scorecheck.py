# -------------------------------------------------#
# Title: Baseball Score Check
# Dev:   David Tobey
# Date:  9/5/2017
# ChangeLog: (Who, When, What)
# DT, 9-5, beta launch
# -------------------------------------------------#

#### Summary
'''This Alexa skill returns the score of any game and its pitcher W/L back to 2005.
Formatting keys:
1. decorator name matches method name, camelCase
2. yaml renders are always_underscored
3. voice mapping in decorators uses lowercase for python variable : uppercase for Alexa variable'''

#### Directives
import os
import mlbgame
import datetime
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

#### Skill Metadata
app = Flask(__name__)
ask = Ask(app, "/")

'''Important variable that is used across functions.'''
global games
global team
games = None
team = None
team_list = open("./speech_assets/customSlotTypes/LIST_OF_TEAMS", "r").read().split('\n')


#### Classes & Methods
@ask.launch
def launchSkill():
    '''The launchSkill() function returns a welcome message and user instructions. It is not required.'''
    greeting = render_template('greeting')
    greeting_help = render_template('greeting_help')
    return question(greeting).reprompt(greeting_help)


@ask.intent("scoreCheck",
            mapping={'user_date': 'Date', 'team': 'Team'},
            convert={'user_date': 'date'})
def scoreCheck(user_date, team):
    if team == 'diamondbacks':
        team = 'd-backs'

    if len(str(user_date)) == 0:
        '''Captures missing date requests'''
        bad_date = render_template('bad_date')
        return question(bad_date)

    if isinstance(user_date, datetime.date) is not True:
        '''Tests whether the user_date is a valid date'''
        bad_date = render_template('bad_date')
        return question(bad_date)

    if team.capitalize() not in team_list:
        '''Tests whether an accurate team name was given'''
        bad_team = render_template('bad_team')
        return question(bad_team)

    if user_date < datetime.datetime.strptime('2005-04-03', "%Y-%m-%d").date():
        out_of_date = render_template('out_of_date')
        return question(out_of_date)

    try:
        '''The scoreCheck() function accepts a team name and spoken date from the user, converts the month name to a
        number (because mlbgame requires integer dates), and returns the game score.'''
        _year = user_date.year
        _month = user_date.month
        _day = user_date.day

        global games
        games = mlbgame.day(_year, _month, _day, away=team.capitalize(), home=team.capitalize())
        win_team = games[0].w_team
        win_pitcher = 'The winning pitcher was %s of the %s.' % (games[0].w_pitcher, games[0].w_team)
        for game in games:
            if len(games) == 0:
                '''mlbgame() returns data in a dictionary. If there is no game, the dictionary will be empty.'''
                no_game_look_up = render_template('no_game_look_up')
                return question(no_game_look_up)
            elif win_team == team.capitalize():
                game_info = 'The ' + team.capitalize() + ' won. The final score was ' + str(game) + '. The winning pitcher was ' + str(games[0].w_pitcher) + ' of the ' + str(games[0].w_team) + '. Please CHECK another team and date, or say STOP to stop.'
                return question(game_info)
            elif win_team != team.capitalize():
                game_info = 'The ' + team.capitalize() + ' lost. The final score was ' + str(game) + '. The winning pitcher was ' + str(games[0].w_pitcher) + ' of the ' + str(games[0].w_team) + '. Please CHECK another team and date, or say STOP to stop.'
                return question(game_info)

    except OSError:
        '''Returned if the user asked for a date before 2005'''
        out_of_date = render_template('out_of_date')
        return question(out_of_date)

    except IndexError:
        '''Rarely returned if the user asked for a date before 2005'''
        out_of_date = render_template('no_game_look_up')
        return question(out_of_date)

@ask.intent("badInput")
def badInput():
    bad_input = render_template('bad_input')
    return question(bad_input)

@ask.intent("teamList")
def teamList():
    team_list = render_template('team_list')
    return question(team_list)

@ask.intent('AMAZON.StopIntent')
def handle_stop():
    """
    (STATEMENT) Handles the 'stop' built-in intention.
    """
    stop_cancel = render_template('stop_cancel')
    return statement(stop_cancel)

@ask.intent('AMAZON.CancelIntent')
def handle_cancel():
    stop_cancel = render_template('stop_cancel')
    return statement(stop_cancel)

@ask.intent('AMAZON.HelpIntent')
def handle_help():
    greeting_help = render_template('greeting_help')
    return question(greeting_help)

#### Main
if __name__ == "__main__":
    app.config['ASK_VERIFY_REQUESTS'] = False
    app.run()
