# -*- coding: utf-8 -*-
"""
Created Sun May 17 

Dart player aim, noise, land
300x300 Backboard -> x and y in (-150,150)

https://www.101computing.net/darts-scoring-algorithm/
https://vivilearns2code.github.io/reinforcement-learning/2018/08/15/value-iteration-for-darts.html
https://medium.com/@BonsaiAI/deep-reinforcement-learning-models-tips-tricks-for-writing-reward-functions-a84fe525e8e0

"""
import math
from random import random
from array import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from imageio import imread
import sys

import streamlit as st
st.set_option('deprecation.showPyplotGlobalUse', False)
# from images import *


######################################################
# BOARD & ARRAY SETUP #
######################################################
def GameReset():

    turns = 0

    # 0-20; 1-19; 2-18; 3-17; 4-16; 5-15; 6-B; 7-T; 8-D
    board = np.zeros((2, 9))            # number of Xs for each number for each player
    current_score = np.zeros((2, 1))    # current score for each player
    darts_to_finish = np.zeros((2, 1))  # minimum number of darts needed to finish game
    max_poss_scoring = np.zeros((2, 1)) # maximum can score on based on what's open for the opponent
    fewer_remaining = np.zeros((2, 1))  # binary for whoever has the fewest darts needed to finish the game - either both 0 (tie) or only one 1
    game_end = np.zeros((2, 1))         # game over

    # 0-20; 1-19; 2-18; 3-17; 4-16; 5-15; 6-B; 7-T; 8-D
    completed = np.zeros((2, 9))        # binary completed for each number for each player
    scoring = np.zeros((2, 9))          # binary scoring for each number for each player - either both 0 (tie) or only one 1
    highest_score = np.zeros((2, 1))    # binary for whoever has the highest score - either both 0 (tie) or only one 1
    triples = np.zeros((2, 1))          # binary for completed triples
    doubles = np.zeros((2, 1))          # binary for completed doubles

    dartm = np.zeros((3))               # multiples Single, Double, Triple
    dartn = np.zeros((3))               # 1 to 20, or 25
    entryscore = 0                      # human score from three darts

    return turns, board, current_score, darts_to_finish, max_poss_scoring, fewer_remaining, game_end, completed, scoring, highest_score, triples, doubles, dartm, dartn, entryscore


######################################################
    # WHAT IS MY GENERAL SKILL? #
######################################################
def Skill():

    generalspread = np.zeros((2, 1))

#  while True:
#    try:
#        level  = int(input("Enter Skill Level of Opponent from 5 high to 1 low: "))
#    except ValueError:
#        print("Please enter an integer between 1 and 5...")
#        continue
#    if level < 0 or level > 5:
#        print("Please enter an integer between 1 and 5...")
#        continue
#    else:
#        break
#    print("You have chosen level: "+str(level))

    level = 4  # 5 is high, 1 is low

    generalspread[0] = np.round((6 - level) * 15 - np.sqrt(5 - level) * 10 + (3 - 6 * random()), 0)
    generalspread[1] = np.round((6 - level) * 15 - np.sqrt(5 - level) * 10 + (3 - 6 * random()), 0)

    return generalspread


######################################################
    # WHAT SHOULD I AIM AT? #                 # Replace with RL Policy
######################################################
def Decide(player, completed, scoring, highest_score, triples, doubles):
    aiming_for = 0
    aiming_for_mult = 0
    i = 0

    # 20->15
    while i <= 5:
        if completed[player, i] == 0:
            aiming_for = 20 - i
            aiming_for_mult = 3  # single = 1; double = 2; triple = 3
            print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult))
            return aiming_for, aiming_for_mult

        i = i + 1

    # Bulls
    if completed[player, 6] == 0:
        aiming_for = 25
        aiming_for_mult = 2  # single = 1; double = 2; triple = 3
        print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult))
        return aiming_for, aiming_for_mult

# NEED TO AIM AT SOMETHING SCORING ON BEFORE DEFAULTING TO 14; THEN FIX SCORING DECISION (15-20 and <14)!

    # Triples
    if completed[player, 7] == 0:
        aiming_for = 20
        aiming_for_mult = 3  # single = 1; double = 2; triple = 3
        print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult))
        return aiming_for, aiming_for_mult

    # Doubles
    if completed[player, 8] == 0:
        aiming_for = 20
        aiming_for_mult = 2  # single = 1; double = 2; triple = 3
        print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult))
        return aiming_for, aiming_for_mult

    # ONLY SCORING NEEDED
    j = 0
    scoring_on = 0
    while j <= 8:
        if scoring[player, 8-j] == 1:
            scoring_on = 8-j
            print('######scoring_on: '+str(scoring_on))
        j = j + 1

    if scoring_on <= 5:  # RARE BUG EVERY 30-40 GAMES ??scoring_on?? ##################
        aiming_for = 20 - scoring_on
        aiming_for_mult = 3  # single = 1; double = 2; triple = 3
        print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult))
        return aiming_for, aiming_for_mult

    else:
        if scoring_on == 6:
            aiming_for = 25
            aiming_for_mult = 2  # single = 1; double = 2; triple = 3
            print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult))
            return aiming_for, aiming_for_mult

        if scoring_on == 7:
            aiming_for = 20
            aiming_for_mult = 3  # single = 1; double = 2; triple = 3
            print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult))
            return aiming_for, aiming_for_mult

        if scoring_on == 8:
            aiming_for = 20
            aiming_for_mult = 2  # single = 1; double = 2; triple = 3
            print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult))
            return aiming_for, aiming_for_mult

    print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult))

    return aiming_for, aiming_for_mult


######################################################
    # WHERE SHOULD I AIM THIS DART? #
######################################################
def Aim(aiming_for, aiming_for_mult):
    a = array('i', [0, 72, 306, 270, 36, 108, 0, 234, 198, 144,
                    342, 180, 126, 18, 162, 324, 216, 288, 54, 252, 90])
    d = array('i', [0, 109, 139, 79])
    aiming_arrow_x = 0
    aiming_arrow_y = 0

    if aiming_for <= 20:
        aiming_arrow_x = d[aiming_for_mult] * math.cos(a[aiming_for]*math.pi/180)
        aiming_arrow_y = d[aiming_for_mult] * math.sin(a[aiming_for]*math.pi/180)
    else:
        aiming_arrow_x = 0  # Bull
        aiming_arrow_y = 0

    # print(aiming_for,aiming_for_mult,a[aiming_for],d[aiming_for_mult],np.round(aiming_arrow_x,0),np.round(aiming_arrow_y,0))

    return aiming_arrow_x, aiming_arrow_y


######################################################
    # HOW GOOD WILL THIS DART BE? #
######################################################
def Accuracy(player,generalspread):

    nowspread = 0

    nowspread = np.round(generalspread[player] * (random()*0.8+0.6), 0)
    # print(nowspread)

    return nowspread


######################################################
    # WHERE DID THIS DART LAND? #
######################################################
def Throw(aiming_arrow_x, aiming_arrow_y, nowspread):

    arrow_x = np.round(aiming_arrow_x + 2*(nowspread*(0.5-random())), 0)
    arrow_y = np.round(aiming_arrow_y + 2*(nowspread*(0.5-random())), 0)

    return arrow_x[0], arrow_y[0]


######################################################
    # HOW DID THIS DART SCORE? #
######################################################

def Score(arrow_x, arrow_y):
    dart_score = 0
    dart_score_mult = 0
    distance = 0
    comment = "Hit!"

    distance = (arrow_x ** 2 + arrow_y ** 2) ** 0.5  # Pythagoras

    angle = math.degrees(math.atan2(arrow_y, arrow_x))

    if angle < 0:
        angle += 360

    #print("d: "+str(distance)+" a: "+str(angle))


    ######################
    # Miss / Wire / Bull #
    ######################

    ### Miss Board ###
    if distance > 144:
        dart_score = 0
        dart_score_mult = 0
        comment = "Backboard!"
        return dart_score, dart_score_mult, comment

    ### Wire Shots ###
    wireshotbounce = 0.2
    if np.round(distance, 0) in [10, 20, 74, 84, 134, 144]:
        if random() < wireshotbounce:
            dart_score = 0
            dart_score_mult = 0
            comment = "Bounced!"
            return dart_score, dart_score_mult, comment

    if np.round(angle, 0) in [9, 27, 45, 63, 81, 99, 117, 135, 153, 171, 189, 207, 225, 243, 261, 279, 297, 315, 333, 351]:
        if random() < wireshotbounce:
            dart_score = 0
            dart_score_mult = 0
            comment = "Bounced!"
            return dart_score, dart_score_mult, comment

    if distance < 10:
        dart_score = 25
        dart_score_mult = 2
        comment = "Double Bull!"
        return dart_score, dart_score_mult, comment

    if distance < 20:
        dart_score = 25
        dart_score_mult = 1
        comment = "Single Bull!"
        return dart_score, dart_score_mult, comment



    ######################
            # 20...1 #
    ######################
    triple_distance_limit_lower = 74
    triple_distance_limit_upper = 84
    double_distance_limit_lower = 134
    double_distance_limit_upper = 144
    
    angles_distances_array = [
        #[angle_start, angle_end, score]
        [0,     9,  6],    # 6 (part 1 of 2)
        [9,    27, 13],    # 13
        [27,   45,  4],    # 4
        [45,   63, 18],    # 18
        [63,   81,  1],    # 1
        [81,   99, 20],    # 20
        [99,  117,  5],    # 5
        [117, 135, 12],    # 12
        [135, 153,  9],    # 9
        [153, 171, 14],    # 14
        [171, 189, 11],    # 11
        [189, 207,  8],    # 8
        [207, 225, 16],    # 16
        [255, 243,  7],    # 7
        [243, 261, 19],    # 19
        [261, 279,  3],    # 3
        [279, 297, 17],    # 17
        [297, 315,  2],    # 2
        [315, 333, 15],    # 15
        [333, 351, 10],    # 10
        [351, 361,  6]     # 6 (part 1 of 2)
    ] 

    for angle_start, angle_end, score in angles_distances_array:
        if angle_start <= angle < angle_end:
                dart_score = score
                
    if triple_distance_limit_lower < distance <= triple_distance_limit_upper:
        dart_score_mult = 3
    elif double_distance_limit_lower < distance <= double_distance_limit_upper:
        dart_score_mult = 2
    else:
        dart_score_mult = 1

    return dart_score, dart_score_mult, comment 

    
    


######################################################
    # WHAT SHOULD I TAKE THIS DART AS? #   DEPENDS ON STRATEGY
######################################################
def DecideScore(player, dart_score, dart_score_mult):

    ########## NOT PROGRAMMED ####################
    # THERE'S A DECISION ON HOW TO TAKE THE SCORING WHEN THERE ARE MULTIPLE OPTIONS?? When to take a double or triple rather than two or three twenties?
    # When multiple options: Triple; Three 15s; or 45 points – which one?

    return player, dart_score, dart_score_mult


###########################################################
    # WHAT DOES THE UPDATED SCOREBOARD LOOK LIKE? #
###########################################################
def BoardUpdate(board, player, current_score, dart_score, dart_score_mult, highest_score, completed, game_end, darts_to_finish, max_poss_scoring, fewer_remaining, scoring, triples, doubles):

    #dart_score = 17
    #dart_score_mult = 2
    #player = 0
    #board[1 - player,0] = 3
    done = 0

    # Take partially to close off soemthing being scored on vs. take instead of scoring as they are more difficult to get
    # call ScoringDecision(completed, scoring, highest_score, triples, doubles) ??

    # Needing both Triples and the 15-20 hit

    # Bulls
    if dart_score == 25:
        if board[player, 6] + dart_score_mult >= 3 and board[1 - player, 6] < 3:
            current_score[player, 0] = current_score[player, 0] + \
                ((board[player, 6] + dart_score_mult - 3) * dart_score)
            done = 1
        if board[player, 6] + dart_score_mult > 3:
            board[player, 6] = 3
            done = 1
        if board[player, 6] + dart_score_mult <= 3:
            board[player, 6] = board[player, 6] + dart_score_mult
            done = 1

    # Triples
    if dart_score_mult == 3 and done == 0:
        if board[player, 7] + 1 <= 3:
            board[player, 7] = board[player, 7] + 1
            done = 1
        else:
            if board[1 - player, 7] < 3 and dart_score < 15:
                current_score[player, 0] = current_score[player,
                                                       0] + 3 * dart_score
                done = 1
            if board[1 - player, 7] < 3 and 15 <= dart_score <= 20:
                if completed[player, 20 - dart_score] == 1:
                    current_score[player, 0] = current_score[player,
                                                           0] + 3 * dart_score
                    done = 1

    # Doubles
    if dart_score_mult == 2 and done == 0:
        if board[player, 8] + 1 <= 3:
            board[player, 8] = board[player, 8] + 1
            done = 1
        else:
            if board[1 - player, 8] < 3:
                current_score[player, 0] = current_score[player,
                                                       0] + 2 * dart_score
                done = 1
            if board[1 - player, 8] < 3 and 15 <= dart_score <= 20 and done == 0:
                if completed[player, 20 - dart_score] == 1:
                    current_score[player, 0] = current_score[player,
                                                           0] + 2 * dart_score
                    done = 1

    # 20-15
    if dart_score >= 15 and done == 0:
        if 15 <= dart_score <= 20 and board[player, 20 - dart_score] + dart_score_mult <= 3:
            board[player, 20 - dart_score] = board[player,
                                                  20 - dart_score] + dart_score_mult
            done = 1
        else:
            if 15 <= dart_score <= 20 and board[1 - player, 20 - dart_score] < 3:
                current_score[player, 0] = current_score[player, 0] + \
                    ((board[player, 20 - dart_score] +
                      dart_score_mult - 3) * dart_score)
                done = 1
            if 15 <= dart_score <= 20 and board[player, 20 - dart_score] + dart_score_mult > 3:
                board[player, 20 - dart_score] = 3
                done = 1


    # update who has the highest score

    if current_score[player] < current_score[1-player]:
        highest_score[player] = 0
        highest_score[1-player] = 1

    else:
        if current_score[player] > current_score[1-player]:
            highest_score[player] = 1
            highest_score[1-player] = 0
        else:
            highest_score[player] = 0
            highest_score[1-player] = 0

    # update 'completed' array
    i = 0
    while i <= 8:

        if board[player, i] == 3:
            completed[player, i] = 1
            if completed[1 - player, i] == 0:
                scoring[player, i] = 1
            else:
                scoring[player, i] = 0

        i = i+1

    # Track if everything is completed and score is higher
    game_end[player] = min(min(completed[player]),
                          (current_score[player, 0] > current_score[1 - player, 0]))


    # Count minimum darts remaining to win

    # calculate min darts to finish game, including a higher score

    i = 0
    darts_to_finish[player] = 0
    max_poss_scoring[player] = 0

    while i <= 8:

        if i <= 5:  # For 20 to 15, always 0,1 darts to finish each
            if board[player, i] < 3:
                darts_to_finish[player] = darts_to_finish[player] + \
                    1  # count number of darts needed to finish
            if board[1-player, i] < 3:
                # assess maximum number that can be scored on, if behind on score
                max_poss_scoring[player] = max(
                    max_poss_scoring[player], (20 - i)*(1-completed[1-player, i])*3)
        else:
            if i == 6:  # For Bulls(6), always 0,1,2 darts to finish
                if board[player, i] == 0:
                    darts_to_finish[player] = darts_to_finish[player] + 2
                if board[player, i] in (1, 2):
                    darts_to_finish[player] = darts_to_finish[player] + 1
                if board[1-player, i] < 3:
                    max_poss_scoring[player] = max(max_poss_scoring[player], 50)
            else:
                # For Triples(7) or Doubles(8), always 0,1,2,3 darts to finish each
                if i == 7 or i == 8:
                    if board[player, i] < 3:
                        darts_to_finish[player] = darts_to_finish[player] + (3 - board[player, i])
                    if board[1-player, i] < 3:
                        max_poss_scoring[player] = (8-i)*max(max_poss_scoring[player], 60) + (i-7)*max(max_poss_scoring[player], 50)

        i = i+1


    # for player with lower score, divide by maximum of what other player has not completed

    if highest_score[player] == 0:
        darts_to_finish[player] = darts_to_finish[player] + np.ceil(
            (current_score[1-player] - current_score[player]) / max_poss_scoring[player] + 0.01)  # min of one darts if tied or losing


    # assess whether winning or not
    if darts_to_finish[player] < darts_to_finish[1-player]:
        fewer_remaining[player] = 1
        fewer_remaining[1-player] = 0

    else:
        if darts_to_finish[player] > darts_to_finish[1-player]:
            fewer_remaining[player] = 0
            fewer_remaining[1-player] = 1
        else:
            fewer_remaining[player] = 0
            fewer_remaining[1-player] = 0


    # print current state variables
    print('---')
    print('Board: '+str(board[player]))
    print('Score: '+str(current_score[player]) +
          ' Leading: '+str(highest_score[player]))
    print('Completed: '+str(completed[player]))
    print('Scoring: '+str(scoring[player]))
    print('Darts to Finish: '+str(darts_to_finish[player])+' Fewer remaining: '+str(fewer_remaining[player])+' Max Poss. Scoring Left: '+str(
        current_score[player])+'-'+str(current_score[1-player])+' / '+str(max_poss_scoring[player]))
    print('GameOver: '+str(game_end[player]))
    print('---')

    return board, current_score, game_end, completed, scoring, highest_score, triples, doubles, darts_to_finish, max_poss_scoring, fewer_remaining


######################################################
    # WHAT DOES THE DARTBOARD LOOK LIKE? #
######################################################

def BoardViz(arrow_x, arrow_y, i,col):
    x = 0
    y = 0

    # x/y outer wire = 1.25 to 8.75
    # arrow_x/y between -150 adn 150
    x = (arrow_x + 150) / (300/(8.77-1.23)) + 1.23
    y = (arrow_y + 150) / (300/(8.77-1.23)) + 1.23

    # datafile = cbook.get_sample_data('./nodordartboard.jpg')
    datafile = './nodordartboard-min.png'
    
    img = imread(datafile)
    # datafile2 = cbook.get_sample_data('./chalkboard.jpg')
    # datafile2 = './chalkboard.jpg'
    # img2 = imread(datafile2)
    # datafile3 = cbook.get_sample_data('./dart.bmp')
    datafile3 = './dart-min.png'

    # datafile3 = dart_img
    img3 = imread(datafile3)

    # plt.scatter(x,y,zorder=2)
    plt.axis('off')
    plt.imshow(img3, zorder=2, extent=[x-.39, x+.61, y-.9, y+.05])  # DART
    # plt.imshow(img2, zorder=1, extent=[8.5, 10, 0, 2])  # CHALK BOARD
    plt.imshow(img, zorder=0, extent=[0, 10, 0, 10])  # DARTBOARD

    # if i == 3:
        # plt.show()
    col.pyplot()

    # print(x,y)


######################################################
        # WHICH DARTS DID THE HUMAN THROW #
######################################################

def Entry():

    ############### NOT FULLY PROGRAMMED ################
    # Capture each of the three darts thrown by the human and any score and then boardupdate??
    # Needs error checking/validation like entering the skill level

    dart_score_mult = input("Enter S/D/T as 1 to 3: ")
    dart_score = input("Enter 1 to 20 or 25: ")
    entryscore = input("Enter any scored points: ")

    print(str(dart_score_mult)+" "+str(dart_score)+" "+str(entryscore))

    return dart_score, dart_score_mult, entryscore


######################################################
    # MAIN #
######################################################

# NEED TO SET UP TO PLAY AGAINST HUMAN CALLING Entry()...
# NEED TO DISPLAY UPDATED CHALKBOARD BEFORE HUMAN Entery()

# turns, board, current_score, darts_to_finish, max_poss_scoring, fewer_remaining, game_end, completed, scoring, highest_score, triples, doubles, dartm, dartn, entryscore = GameReset()  # RESET variables
# generalspread = Skill()  # SKILL level

# player = 0

# while game_end[0, 0] == 0:

#     i = 1

#     print('')
#     print('#####PLAYER '+str(player))

#     while i <= 3:
#         aiming_for, aiming_for_mult = Decide(player, completed, scoring, highest_score, triples, doubles)  # DECISION -> Replace with RL
#         # AIM -> Consoder (x,y) policy instead?
#         aiming_arrow_x, aiming_arrow_y = Aim(aiming_for, aiming_for_mult)
#         nowspread = Accuracy(generalspread)  # SKILL/FOCUS/LUCK
#         arrow_x, arrow_y = Throw(aiming_arrow_x, aiming_arrow_y, nowspread)  # THROW/LAND
#         dart_score, dart_score_mult, comment = Score(arrow_x, arrow_y)  # DART SCORE

#         print(comment+" "+str(dart_score)+"*"+str(dart_score_mult))

#         board, current_score, game_end, completed, scoring, highest_score, triples, doubles,  darts_to_finish, max_poss_scoring, fewer_remaining = BoardUpdate(
#             player, dart_score, dart_score_mult)  # UPDATE variables after throw

#         #print("aiminingarrow_x: "+str(np.round(aiming_arrow_x,0))+" aiming_arrow_y: "+str(np.round(aiming_arrow_y,0)))
#         #print("arrow_x: "+str(np.round(arrow_x,0))+" arrow_y: "+str(np.round(arrow_y,0)))

#         ##############
#         #ADD DARTBOARD ANIMATION AFTER EACH TURN BACK WHEN PLAYING AGAINST HUMAN ##
#         # Board(arrow_x,arrow_y,i)
#         ##############

#         if game_end[0, 0] == 1:
#             turns = turns + 1
#             print(board)
#             print(current_score)
#             print(game_end)
#             BoardViz(arrow_x, arrow_y, i)
#             print("I Win! Great Game! Turns: "+str(turns))
#             print("Skill:", generalspread)
#             sys.exit()

#         if game_end[1, 0] == 1:
#             turns = turns + 1
#             print(board)
#             print(current_score)
#             print(game_end)
#             BoardViz(arrow_x, arrow_y, i)
#             print("You Win! Great Game! Turns: "+str(turns))
#             print("Skill:", generalspread)
#             sys.exit()

#         i = i + 1

#     player = 1 - player
#     turns = turns + 1










    # #
    # # 20
    # if 81 <= angle < 99:
    #     if 74 < distance <= 84:
    #         dart_score = 20
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 20
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 20
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
    # # 5
    # if 99 <= angle < 117:
    #     if 74 < distance <= 84:
    #         dart_score = 5
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 5
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 5
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
    # # 12
    # if 117 <= angle < 135:
    #     if 74 < distance <= 84:
    #         dart_score = 12
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 12
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 12
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
    

    # # 9
    # if 135 <= angle < 153:
    #     if 74 < distance <= 84:
    #         dart_score = 9
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 9
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 9
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment

        
    # # 14
    # if 153 <= angle < 171:
    #     if 74 < distance <= 84:
    #         dart_score = 14
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 14
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 14
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
 
    # # 11
    # if 171 <= angle < 189:
    #     if 74 < distance <= 84:
    #         dart_score = 11
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 11
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 11
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
    # # 8
  
    # if 189 <= angle < 207:
    #     if 74 < distance <= 84:
    #         dart_score = 8
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 8
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 8
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment

    # # 16
    # if 207 <= angle < 225:
    #     if 74 < distance <= 84:
    #         dart_score = 16
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 16
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 16
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment

    # #   7
    # if 225 <= angle < 243:
    #     if 74 < distance <= 84:
    #         dart_score = 7
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 7
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 7
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
                 
    # # 19
    # if 243 <= angle < 261:
    #     if 74 < distance <= 84:
    #         dart_score = 19
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 19
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 19
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
   
    # # 3
    # if 261 <= angle < 279:
    #     if 74 < distance <= 84:
    #         dart_score = 3
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 3
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 3
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
     
    # # 17
    # if 279 <= angle < 297:
    #     if 74 < distance <= 84:
    #         dart_score = 17
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 17
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 17
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
   
    # # 2
    # if 297 <= angle < 315:
    #     if 74 < distance <= 84:
    #         dart_score = 2
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 2
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 2
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
  
    # # 15
    # if 315 <= angle < 333:
    #     if 74 < distance <= 84:
    #         dart_score = 15
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 15
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 15
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
      
    # # 10
    # if 333 <= angle < 351:
    #     if 74 < distance <= 84:
    #         dart_score = 10
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 10
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 10
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
    # # 6
    # if (351 <= angle < 361) or (0 <= angle < 9):
    #     if 74 < distance <= 84:
    #         dart_score = 6
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 6
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 6
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
     
    # # 13
    # if 9 <= angle < 27:
    #     if 74 < distance <= 84:
    #         dart_score = 13
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 13
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 13
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment

    # # 4
    # if 27 <= angle < 45:
    #     if 74 < distance <= 84:
    #         dart_score = 4
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 4
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 4
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
   
    # # 18
    # if 45 <= angle < 63:
    #     if 74 < distance <= 84:
    #         dart_score = 18
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 18
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 18
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment
    # # 1
    # if 63 <= angle < 81:
    #     if 74 < distance <= 84:
    #         dart_score = 1
    #         dart_score_mult = 3
    #     else:
    #         if 134 < distance <= 144:
    #             dart_score = 1
    #             dart_score_mult = 2
    #         else:
    #             dart_score = 1
    #             dart_score_mult = 1
    #     return dart_score, dart_score_mult, comment

    # dart_score = 999
    # dart_score_mult = 9
    # comment = "Error??"

    # return dart_score, dart_score_mult, comment