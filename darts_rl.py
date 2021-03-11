# -*- coding: utf-8 -*-
"""
Created Sun May 17 

Dart player aim, noise, land
300x300 Backself.board-> x and y in (-150,150)

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

import warnings
warnings.filterwarnings('ignore')



class Darts:

    # Similar to previous GameReset()
    def __init__(self):
        self.turns = 0

        self.throw_history = []

        # 0-20; 1-19; 2-18; 3-17; 4-16; 5-15; 6-B; 7-T; 8-D
        self.board                  = np.zeros((2, 9))         # number of Xs for each number for each player
        self.current_score          = np.zeros((2, 1))         # current score for each player
        self.darts_to_finish        = np.zeros((2, 1))         # minimum number of darts needed to finish game
        # self.darts_to_finish        = np.array([[15],[15]])         # minimum number of darts needed to finish game
        self.max_possible_scoring   = np.zeros((2, 1))         # maximum can score on based on what's open for the oppoenent
        self.has_fewer_remaining    = np.zeros((2, 1))         # binary for whoever has the fewest darts needed to finish the game - either both 0 (tie) or only one 1
        self.game_end               = np.zeros((2, 1))         # game over

        # 0-20; 1-19; 2-18; 3-17; 4-16; 5-15; 6-B; 7-T; 8-D
        self.completed          = np.zeros((2, 9))         # binary completed for each number for each player
        self.scoring            = np.zeros((2, 9))         # binary scoring for each number for each player - either both 0 (tie) or only one 1
        self.has_highest_score  = np.zeros((2, 1))         # binary for whoever has the highest score - either both 0 (tie) or only one 1
        self.triples            = np.zeros((2, 1))         # binary for completed triples
        self.doubles            = np.zeros((2, 1))         # binary for completed doubles

        self.dartm           = np.zeros((3))            # multiples Single, Double, Triple
        self.dartn           = np.zeros((3))            # 1 to 20, or 25
        self.entry_score     = 0

        self.done = 0

        self.reward = np.zeros((2, 1))
        self.log_rewards = [[],[]]

        self.verbose = 1

        # self.state_space = [self.board[0], self.completed[0], self.scoring[0], self.current_score[0], self.darts_to_finish[0]]
        # self.state_space = [item for sublist in self.state_space for item in sublist]

        self.state_space = [self.board, self.completed, self.scoring, self.current_score, self.darts_to_finish]
        self.state_space = [item for sublist in [item for sublist in self.state_space for item in sublist] for item in sublist]


        # action_id: [self.aiming_for, aiming_for_mult]
        self.action_space = { 
                            0: [25, 1],
                            1: [25, 2],
                            2: [1, 2],
                            3: [1, 3],
                            4: [2, 2],
                            5: [2, 3],
                            6: [3, 2],
                            7: [3, 3],
                            8: [4, 2],
                            9: [4, 3],
                            10: [5, 2],
                            11: [5, 3],
                            12: [6, 2],
                            13: [6, 3],
                            14: [7, 2],
                            15: [7, 3],
                            16: [8, 2],
                            17: [8, 3],
                            18: [9, 2],
                            19: [9, 3],
                            20: [10, 2],
                            21: [10, 3],
                            22: [11, 2],
                            23: [11, 3],
                            24: [12, 2],
                            25: [12, 3],
                            26: [13, 2],
                            27: [13, 3],
                            28: [14, 2],
                            29: [14, 3],
                            30: [15, 1],
                            31: [15, 2],
                            32: [15, 3],
                            33: [16, 1],
                            34: [16, 2],
                            35: [16, 3],
                            36: [17, 1],
                            37: [17, 2],
                            38: [17, 3],
                            39: [18, 1],
                            40: [18, 2],
                            41: [18, 3],
                            42: [19, 1],
                            43: [19, 2],
                            44: [19, 3],
                            45: [20, 1],
                            46: [20, 2],
                            47: [20, 3],
        }


    def get_action_space(self):
        return len(self.action_space.keys())

    # def Skill():
    def assign_player_skill(self, level=4):

        self.general_spread = np.zeros((2, 1)) 

        self.general_spread[0] = np.round((6 - level) * 15 - np.sqrt( 5 - level) * 10 + (3 - 6 * random()), 0) 
        self.general_spread[1] = np.round((6 - level) * 15 - np.sqrt( 5 - level) * 10 + (3 - 6 * random()), 0) 


    # def Decide(player, completed, scoring, highestscore, triples, doubles):
    def decide_target(self):

        aiming_for = 0
        aiming_for_mult = 0
        i = 0

        #20->15
        while i <= 5 :
            if self.completed[self.player,i] == 0 :
                aiming_for = 20 - i
                aiming_for_mult = 3  # single = 1; double = 2; triple = 3
                if self.verbose == 1:
                    print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult), end=' -> ')
                return aiming_for, aiming_for_mult

            i = i + 1

        #Bulls
        if self.completed[self.player,6] == 0 :
            aiming_for = 25
            aiming_for_mult = 2  # single = 1; double = 2; triple = 3
            if self.verbose == 1:
                print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult), end=' -> ')
            return aiming_for, aiming_for_mult

        ##################  NEED TO AIM AT SOMETHNG SCORING ON BEFORE DEFAULTING TO 14; THEN FIX SCORING DECISION (15-20 and <14)!

        #Triples
        if self.completed[self.player,7] == 0 :
            aiming_for = 20
            aiming_for_mult = 3  # single = 1; double = 2; triple = 3
            if self.verbose == 1:
                print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult), end=' -> ')
            return aiming_for, aiming_for_mult

        #Doubles
        if self.completed[self.player,8] == 0 :
            aiming_for = 20
            aiming_for_mult = 2  # single = 1; double = 2; triple = 3
            if self.verbose == 1:
                print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult), end=' -> ')
            return aiming_for, aiming_for_mult

        # ALL THE NUMBERS ARE CLOSED FOR THIS PLAYER
        # ONLY SCORING NEEDED
        scoring_on = 0
        for j in range(0,9): # from 0 to 8
            if self.scoring[self.player,8-j] == 1:
                scoring_on = 8-j
                # print('###### Scoring On: '+str(scoring_on))

        if scoring_on <= 5 :   ##### RARE BUG EVERY 30-40 GAMES ??scoring_on?? ##################
            aiming_for = 20 - scoring_on
            aiming_for_mult = 3  # single = 1; double = 2; triple = 3
            if self.verbose == 1:
                print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult), end=' (Scoring Only!) -> ')
            return aiming_for, aiming_for_mult

        elif scoring_on == 6:
            aiming_for = 25
            aiming_for_mult = 2  # single = 1; double = 2; triple = 3
            if self.verbose == 1:
                print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult), end=' (Scoring Only!) -> ')
            return aiming_for, aiming_for_mult

        elif scoring_on == 7 :
            aiming_for = 20
            aiming_for_mult = 3  # single = 1; double = 2; triple = 3
            if self.verbose == 1:
                print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult), end=' (Scoring Only!) -> ')
            return aiming_for, aiming_for_mult

        elif scoring_on == 8 :
            aiming_for = 20
            aiming_for_mult = 2  # single = 1; double = 2; triple = 3
            if self.verbose == 1:
                print("Aiming At: "+str(aiming_for)+"*"+str(aiming_for_mult), end=' (Scoring Only!) -> ')
            return aiming_for, aiming_for_mult


    ######################################################
                # WHERE SHOULD I AIM THIS DART? #
    ######################################################

    # def Aim(aimingfor, aimingformult):
    def set_aim_coordinates(self):
        
        a = array('i',[0,72,306,270,36,108,0,234,198,144,342,180,126,18,162,324,216,288,54,252,90])
        d = array('i',[0,109,139,79]) 

        if self.aiming_for <= 20:
            self.aiming_arrow_x = d[self.aiming_for_mult] * math.cos(a[self.aiming_for]*math.pi/180)
            self.aiming_arrow_y = d[self.aiming_for_mult] * math.sin(a[self.aiming_for]*math.pi/180)
        else:
            self.aiming_arrow_x = 0 #Bull
            self.aiming_arrow_y = 0


    ######################################################
            # HOW GOOD WILL THIS DART BE? #
    ######################################################
    
    # def Accuracy(generalspread):
    def get_dart_accuracy(self):

        self.now_spread = 0
        self.now_spread = np.round(self.general_spread[self.player] * (random()*0.8+0.6),0) 


    ######################################################
                # WHERE DID THIS DART LAND? #
    ######################################################

    # def Throw(aimingarrowx,aimingarrowy,nowspread):
    def throw_dart(self):
    
        self.arrow_x = np.round(self.aiming_arrow_x + 2*(self.now_spread*(0.5-random())),0)[0]
        self.arrow_y = np.round(self.aiming_arrow_y + 2*(self.now_spread*(0.5-random())),0)[0]


    ######################################################
        # HOW DID THIS DART SCORE? #
    ######################################################

    # def Score(arrowx,arrowy):
    def get_dart_score(self):
        # Returning values in case of not matching any of the scenarios
        dart_score = 999
        dart_score_mult = 0
        distance = 0
        comment = "Error??"

        distance = (self.arrow_x ** 2 + self.arrow_y ** 2) ** 0.5  # Pythagoras

        angle = math.degrees(math.atan2(self.arrow_y, self.arrow_x))

        if angle < 0:
            angle += 360

        ######################
        # Miss / Wire / Bull #
        ######################

        ### Miss self.board###
        if distance > 144:
            dart_score = 0
            dart_score_mult = 0
            comment = "Backboard!"
            return dart_score, dart_score_mult, comment

        ### Wire Shots ###        

        # Here the original code was using the same return values for two distinct conditions
        # The new code combines the two conditions, but using an OR
        else:
            wireshot_bounce = 0.2
            if (np.round(distance, 0) in [10, 20, 74, 84, 134, 144]) or \
               (np.round(angle, 0) in [9, 27, 45, 63, 81, 99, 117, 135, 153, 171, 189, 207, 225, 243, 261, 279, 297, 315, 333, 351]):
            
                if random() < wireshot_bounce:
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

        # The original code was repeting the same logic for different angles
        # To make it simpler, all the combinations of angles (start and end)
        # and respective score number were combined in the list 'angles_distances_arrays' below
        # This way, instead of having a similar block of code for each angle range, 
        # we can have one block of code being used for each element of the array

        # A similar idea applies to the code that compares the distances to select the multiplication factor
        # The new code adds only one comparison of the distances after the code below.

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
            [351, 361,  6]     # 6 (part 2 of 2)
        ] 

        for angle_start, angle_end, score in angles_distances_array:
            if angle_start <= angle < angle_end:
                    dart_score = score
                    comment = 'Hit!'

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
    def DecideScore(self):

        ########## NOT PROGRAMMED ####################
            ##### THERE'S A DECISION ON HOW TO TAKE THE SCORING WHEN THERE ARE MULTIPLE OPTIONS?? When to take a double or triple rather than two or three twenties? 
            ##### When multiple options: Triple; Three 15s; or 45 points – which one?

        # return player, self.dart_score, self.dart_score_mult
        pass




    ###########################################################
                # WHAT DOES THE UPDATED SCOREself.boardLOOK LIKE? #
    ###########################################################

    # def BoardUpdate(player, dartscore, dartscoremult):
    def update_board(self):

        done = 0

        #Bulls
        if self.dart_score == 25:
            if self.board[self.player, 6] + self.dart_score_mult >= 3 and self.board[1 - self.player, 6] < 3:
                self.current_score[self.player,0] =  self.current_score[self.player,0] + ((self.board[self.player, 6] + self.dart_score_mult - 3) * self.dart_score)
                done = 1
            if self.board[self.player, 6] + self.dart_score_mult > 3:
                self.board[self.player, 6] = 3
                done = 1
            if self.board[self.player, 6] + self.dart_score_mult <= 3:
                self.board[self.player, 6] = self.board[self.player, 6]  + self.dart_score_mult
                done = 1

        #Triples
        if self.dart_score_mult == 3 and done == 0:
            if self.board[self.player, 7] + 1 <= 3:
                self.board[self.player, 7] = self.board[self.player, 7] + 1
                done = 1
            else:
                if self.board[1 - self.player, 7] < 3 and self.dart_score < 15:
                    self.current_score[self.player,0] =  self.current_score[self.player,0] + 3 * self.dart_score
                    done = 1
                if self.board[1 - self.player, 7] < 3 and 15 <= self.dart_score <= 20:
                    if self.completed[self.player, 20 - self.dart_score] == 1:
                        self.current_score[self.player,0] =  self.current_score[self.player,0] + 3 * self.dart_score
                        done = 1

        #Doubles
        if self.dart_score_mult == 2 and done == 0:
            if self.board[self.player, 8] + 1 <= 3:
                self.board[self.player, 8] = self.board[self.player, 8] + 1
                done = 1
            else:
                if self.board[1 - self.player, 8] < 3 :
                    self.current_score[self.player,0] =  self.current_score[self.player,0] + 2 * self.dart_score
                    done = 1
                if self.board[1 - self.player, 8] < 3 and 15 <= self.dart_score <= 20 and done == 0 :
                    if self.completed[self.player, 20 - self.dart_score] == 1 :
                        self.current_score[self.player,0] =  self.current_score[self.player,0] + 2 * self.dart_score
                        done = 1

        #20-15
        if self.dart_score >= 15 and done == 0 :
            if  15 <= self.dart_score <= 20 and self.board[self.player, 20 - self.dart_score] + self.dart_score_mult <= 3 :
                self.board[self.player, 20 - self.dart_score] = self.board[self.player, 20 - self.dart_score]  + self.dart_score_mult
                done = 1
            else:
                if 15 <= self.dart_score <= 20 and self.board[1 - self.player, 20 - self.dart_score] < 3 :
                    self.current_score[self.player,0] =  self.current_score[self.player,0] + ((self.board[self.player, 20 - self.dart_score] + self.dart_score_mult - 3) * self.dart_score)  
                    done = 1
                if 15 <= self.dart_score <= 20 and self.board[self.player, 20 - self.dart_score] + self.dart_score_mult > 3 :
                    self.board[self.player, 20 - self.dart_score] = 3
                    done = 1


        # Update who has the highest score
        if self.current_score[self.player] < self.current_score[1-self.player]:
            self.has_highest_score[self.player]  = 0
            self.has_highest_score[1-self.player]  = 1
        elif self.current_score[self.player] > self.current_score[1-self.player]:
            self.has_highest_score[self.player]  = 1
            self.has_highest_score[1-self.player]  = 0
        else:
            self.has_highest_score[self.player]  = 0
            self.has_highest_score[1-self.player]  = 0

        # Update 'completed' array
        for i in range(9):  # from 0 to 8
            if self.board[self.player,i] == 3:
                self.completed[self.player,i] = 1
                if self.completed[1 - self.player,i] == 0:
                    self.scoring[self.player,i] = 1
                else:
                    self.scoring[self.player,i] = 0

        #Track if everything is completed and score is higher
        self.game_end[self.player] = min(min(self.completed[self.player]),(self.current_score[self.player,0] > self.current_score[1 - self.player,0]))
        self.game_end[self.player] = self.game_end[self.player][0]
        #####Count minimum darts remaining to win
        # calculate min darts to finish game, including a higher score

        self.darts_to_finish[self.player] = 0
        self.max_possible_scoring[self.player] = 0

        for i in range(9): # from 0 to 8

            #For 20 to 15, always 0,1 darts to finish each
            if i <= 5:
                if self.board[self.player,i] < 3 :
                    self.darts_to_finish[self.player] = self.darts_to_finish[self.player] + 1  #count number of darts needed to finish
                if self.board[1-self.player,i] < 3 :
                    self.max_possible_scoring[self.player] = max(self.max_possible_scoring[self.player],(20 - i)*(1-self.completed[1-self.player,i])*3)   #assess maximum number that can be scored on, if behind on score     
            #For Bulls(6), always 0,1,2 darts to finish
            elif i == 6 :
                if self.board[self.player,i] == 0 :
                    self.darts_to_finish[self.player] = self.darts_to_finish[self.player] + 2
                if self.board[self.player,i] in (1,2) :
                    self.darts_to_finish[self.player] = self.darts_to_finish[self.player] + 1
                if self.board[1-self.player,i] < 3 :
                    self.max_possible_scoring[self.player] = max(self.max_possible_scoring[self.player],50)
            else:
                #For Triples(7) or Doubles(8), always 0,1,2,3 darts to finish each
                if i == 7 or i == 8 :
                    if self.board[self.player,i] < 3 :
                        self.darts_to_finish[self.player] = self.darts_to_finish[self.player] + (3 - self.board[self.player,i])
                    if self.board[1-self.player,i] < 3 :
                        self.max_possible_scoring[self.player] = (8-i)*max(self.max_possible_scoring[self.player],60) + (i-7)*max(self.max_possible_scoring[self.player],50)

        # For player with lower score, divide by maximum of what other player has not completed
        if self.has_highest_score[self.player] == 0 :
            
            ##### VERIFY IF OTHER PLAYER HAS NOT COMPLETED THE BOARD
            ##### IF THE OTHER PLAYER HAS COMPLETED, PASS
            if self.completed[1-self.player].sum() < 9:
            
                self.darts_to_finish[self.player] = self.darts_to_finish[self.player] + \
                                                    np.ceil((self.current_score[1-self.player] - self.current_score[self.player] ) / \
                                                            self.max_possible_scoring[self.player] + 0.01) #min of one darts if tied or losing
            

        # Assess whether winning or not
        if self.darts_to_finish[self.player] < self.darts_to_finish[1-self.player]:
            self.has_fewer_remaining[self.player]  = 1
            self.has_fewer_remaining[1-self.player]  = 0
        elif self.darts_to_finish[self.player] > self.darts_to_finish[1-self.player]:
            self.has_fewer_remaining[self.player]  = 0
            self.has_fewer_remaining[1-self.player]  = 1
        else:
            self.has_fewer_remaining[self.player]  = 0
            self.has_fewer_remaining[1-self.player]  = 0

        if self.game_end[self.player] == 1:
            self.done = 1



    def print_main_variables(self):
        
        def get_string(x):
            if x == 0:
                return '   '
            elif x == 1:
                return ('').join(['X' for i in range(int(x))])+'  '
            elif x == 2:
                return ('').join(['X' for i in range(int(x))])+' '
            else:
                return ('').join(['X' for i in range(int(x))])
        
        print(f'''
------------------------------------------   ---------------
   {'-=' if self.player == 0 else '  '}PLAYER 0{'=-' if self.player == 0 else '  '}        {'-=' if self.player == 1 else '  '}PLAYER 1{'=-' if self.player == 1 else '  '}             COMPLETED
------------------------------------------   ---------------
         {get_string(self.board[0][0])}   |  20  |   {get_string(self.board[1][0])}                       {'X' if self.completed[0][0] + self.completed[1][0] == 2 else ''}
         {get_string(self.board[0][1])}   |  19  |   {get_string(self.board[1][1])}                       {'X' if self.completed[0][1] + self.completed[1][1] == 2 else ''}
         {get_string(self.board[0][2])}   |  18  |   {get_string(self.board[1][2])}                       {'X' if self.completed[0][2] + self.completed[1][2] == 2 else ''}
         {get_string(self.board[0][3])}   |  17  |   {get_string(self.board[1][3])}                       {'X' if self.completed[0][3] + self.completed[1][3] == 2 else ''}
         {get_string(self.board[0][4])}   |  16  |   {get_string(self.board[1][4])}                       {'X' if self.completed[0][4] + self.completed[1][4] == 2 else ''}
         {get_string(self.board[0][5])}   |  15  |   {get_string(self.board[1][5])}                       {'X' if self.completed[0][5] + self.completed[1][5] == 2 else ''}
         {get_string(self.board[0][6])}   | BULL |   {get_string(self.board[1][6])}                       {'X' if self.completed[0][6] + self.completed[1][6] == 2 else ''}
         {get_string(self.board[0][7])}   |  x3  |   {get_string(self.board[1][7])}                       {'X' if self.completed[0][7] + self.completed[1][7] == 2 else ''}
         {get_string(self.board[0][8])}   |  x2  |   {get_string(self.board[1][8])}                       {'X' if self.completed[0][8] + self.completed[1][8] == 2 else ''}
------------------------------------------   ---------------
SCORE     {int(self.current_score[0][0])}\t\t  {int(self.current_score[1][0])} 
LEADING   {'o/' if self.current_score[0][0] > self.current_score[1][0] else '   '}\t\t  {'o/' if self.current_score[0][0] < self.current_score[1][0] else ''}
DTF       {int(self.darts_to_finish[0][0])}\t\t  {int(self.darts_to_finish[1][0])}
MPSL      {int(self.current_score[0][0])}-{int(self.current_score[1][0])}/{int(self.max_possible_scoring[0][0])}\t  {int(self.current_score[1][0])}-{int(self.current_score[0][0])}/{int(self.max_possible_scoring[1][0])}
REWARDS   {self.reward[0]:.2f}\t\t  {self.reward[1]:.2f}
DTF -> Darts to finish    MPSL -> Max Poss. Scoring Left

REWARD LOG:
{'Throw 1: '+' ; '.join(self.log_rewards_full[self.player][1]) if len(self.log_rewards_full[self.player].keys()) >= 1 else ""}
{'Throw 2: '+' ; '.join(self.log_rewards_full[self.player][2]) if len(self.log_rewards_full[self.player].keys()) >= 2 else ""}
{'Throw 3: '+' ; '.join(self.log_rewards_full[self.player][3]) if len(self.log_rewards_full[self.player].keys()) >= 3 else ""}
''')



    ######################################################
                # WHAT DOES THE DARTBOARD LOOK LIKE? #
    ######################################################

    # def BoardViz(arrowx,arrowy,i):
    def draw_board(self):
        x = 0
        y = 0
        
        # x/y outer wire = 1.25 to 8.75
        # arrowx/y between -150 adn 150 
        x = (self.arrow_x + 150) / (300/(8.77-1.23)) + 1.23
        y = (self.arrow_y + 150) / (300/(8.77-1.23)) + 1.23
        
        # datafile = cbook.get_sample_data('C:/Users/nayrb/Documents/Bryan/Python/Darts/nodordartboard.jpg')
        # img = imread(datafile)
        # datafile2 = cbook.get_sample_data('C:/Users/nayrb/Documents/Bryan/Python/Darts/chalkboard.jpg')
        # img2 = imread(datafile2)
        # datafile3 = cbook.get_sample_data('C:/Users/nayrb/Documents/Bryan/Python/Darts/dart.bmp')
        # img3 = imread(datafile3)

        # #plt.scatter(x,y,zorder=2)
        # plt.axis('off')
        # plt.imshow(img3, zorder=2, extent=[x-.39, x+.61, y-.9, y+.05])    ###DART
        # plt.imshow(img2, zorder=1, extent=[8.5, 10, 0, 2])               ###CHALK BOARD
        # plt.imshow(img, zorder=0, extent=[0, 10, 0, 10])                  ###DARTBOARD
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
        plt.imshow(img, zorder=0, extent=[0, 10, 0, 10])  # DARTBOARD

        plt.show()


    def Entry(self):

        ############### NOT FULLY PROGRAMMED ################
        #####Capture each of the three darts thrown by the human and any score and then boardupdate??  
        #####Needs error checking/validation like entering the skill level   

        dartscoremult      = input("Enter S/D/T as 1 to 3: ")
        dartscore          = input("Enter 1 to 20 or 25: ")
        entryscore         = input("Enter any scored points: ")

        print(str(dartscoremult)+" "+str(dartscore)+" "+str(entryscore)) 

        return dartscore, dartscoremult, entryscore



    ######################################################
                        # MAIN #
    ######################################################
    
    def run_game(self):

        max_turns = 50

        self.assign_player_skill(level=4)

        self.player = 0

        while self.done == 0 and self.turns < max_turns:

            print()
            print('###############################################################################')
            print(f'######################## PLAYER {str(self.player)} - TURN {str(self.turns+1)} ####################################')
            print('###############################################################################')
            print()
            
            self.log_rewards_full = [{},{}]

            for i in range(1,4): # from 1 to 3
                self.aiming_for, self.aiming_for_mult = self.decide_target()
                self.reward, self.state_space, self.done = self.step(action = self.aiming_for, action_mult = self.aiming_for_mult, player=self.player)
                self.log_rewards_full[self.player][i] = self.log_rewards[self.player]
                
                if self.verbose == 1:
                    print(str(self.dart_score)+"*"+str(self.dart_score_mult)+' ('+self.comment+")")

                if self.game_end[self.player] == 1 :
                    self.turns = self.turns + 1
                    
                    if self.verbose == 1:
                        self.print_main_variables()
                    print(f"\nPlayer {self.player} Wins! Great Game! Turns: "+str(self.turns))
                    sys.exit()

            if self.verbose == 1:
                self.print_main_variables()
            self.player = 1 - self.player
            self.turns = self.turns + 1
            cont = input("Press ENTER to continue")

        if self.turns == 50:
            if self.verbose == 1:
                self.print_main_variables()
            print(f"\nNo winner after {str(self.turns)} turns!")
            sys.exit()



    #####################################################
                        # AI CONTROL #
    #####################################################

    ### GENERAL RULES

    ## RL Agent is Player 0. Player 1 will also play, but just to update the board/scores
    ## The training will be focused on Player 0
    ## State Space is composed of the full board, array completed, array scoring, respective scores, and darts to finish
    ## Example:
    ##      state_space = [
    #                       [
    #                           [3,3,3,2,0,0,0,0,0],    --> Player 0 (RL Agent) board
    #                           [3,3,0,0,0,0,0,2,0]     --> Player 1 board
    #                       ],
    #                       [
    #                           [1,1,1,0,0,0,0,0,0],    --> Player 0 (RL Agent) completed
    #                           [1,1,0,0,0,0,0,0,0]     --> Player 1 board
    #                       ],
    #                       [
    #                           [0,0,1,0,0,0,0,0,0],    --> Player 0 (RL Agent) scoring
    #                           [0,0,0,0,0,0,0,0,0]     --> Player 1 board
    #                       ],#     
    #                       [
    #                           [30],  --> Player 0 (RL Agent) current total score
    #                           [25]   --> Player 1 current total score
    #                       ],
    #                       [
    #                           [10],  --> Player 0 (RL Agent) darts to finish
    #                           [12]   --> Player 1 darts to finish
    #                       ]     
    #                   ]
    # This array is then flattened to be used in the RL engine (file darts_dql.py)


    def reset(self):

        self.turns = 0
        self.throw_history = []

        # 0-20; 1-19; 2-18; 3-17; 4-16; 5-15; 6-B; 7-T; 8-D
        self.board                  = np.zeros((2, 9))         # number of Xs for each number for each player
        self.current_score          = np.zeros((2, 1))         # current score for each player
        self.darts_to_finish        = np.zeros((2, 1))         # minimum number of darts needed to finish game
        self.darts_to_finish        = np.array([[15],[15]])         # minimum number of darts needed to finish game
        self.max_possible_scoring   = np.zeros((2, 1))         # maximum can score on based on what's open for the oppoenent
        self.has_fewer_remaining    = np.zeros((2, 1))         # binary for whoever has the fewest darts needed to finish the game - either both 0 (tie) or only one 1
        self.game_end               = np.zeros((2, 1))         # game over

        # 0-20; 1-19; 2-18; 3-17; 4-16; 5-15; 6-B; 7-T; 8-D
        self.completed          = np.zeros((2, 9))         # binary completed for each number for each player
        self.scoring            = np.zeros((2, 9))         # binary scoring for each number for each player - either both 0 (tie) or only one 1
        self.has_highest_score  = np.zeros((2, 1))         # binary for whoever has the highest score - either both 0 (tie) or only one 1
        self.triples            = np.zeros((2, 1))         # binary for completed triples
        self.doubles            = np.zeros((2, 1))         # binary for completed doubles

        self.dartm           = np.zeros((3))            # multiples Single, Double, Triple
        self.dartn           = np.zeros((3))            # 1 to 20, or 25
        self.entry_score     = 0

        self.done = 0
        # self.reward = np.zeros((2, 1))

        self.state_space = [self.board, self.completed, self.scoring, self.current_score, self.darts_to_finish]
        self.state_space = [item for sublist in [item for sublist in self.state_space for item in sublist] for item in sublist]

        # self.state_space = [self.board[0], self.completed[0], self.scoring[0], self.current_score[0], self.darts_to_finish[0]]
        # self.state_space = [item for sublist in self.state_space for item in sublist]
        return self.state_space



    def step(self, action, action_mult, player=0):

        self.player = player

        self.reward = [0.0,0.0]
        self.log_rewards[self.player] = []

        self.done = 0

        self.aiming_for = action
        self.aiming_for_mult = action_mult
        
        self.set_aim_coordinates()
        self.get_dart_accuracy()
        self.throw_dart()
        self.dart_score, self.dart_score_mult, self.comment = self.get_dart_score()

        step_result = [self.turns,self.player,self.aiming_for,self.aiming_for_mult,self.dart_score,self.dart_score_mult]
        self.throw_history.append(step_result) 

        previous_num_valid_hits = self.board[self.player].sum()
        previous_num_completed = self.completed[self.player].sum()
        previous_score = self.current_score[self.player]
        self.update_board()  
        updated_score = self.current_score[self.player]
        updated_num_completed = self.completed[self.player].sum()
        updated_num_valid_hits = self.board[self.player].sum()

        if self.game_end[self.player] == 1:
            self.done = 1


        ## position of number in board array
        board_position = {
            20: 0,
            19: 1,
            18: 2,
            17: 3,
            16: 4,
            15: 5,
            25: 6
            ### doubles and tiples are not included here (different combination)
        }

        ## REWARDS
        self.reward[self.player] -= 0.1
        
        self.log_rewards[self.player].append('Throw penalty: -0.1')

        # If it hits a number < 15, but the double or tiple slot is closed, penalize
        if self.aiming_for < 15:
            if self.aiming_for_mult == 2:
                if self.board[0][-1] == 1:    ## Double slot
                    self.reward[self.player] -= 1
                    self.log_rewards[self.player].append('Hit closed Double: -1')
            else:
                if self.board[0][-2] == 1:    ## Triple slot
                    self.reward[self.player] -= 1
                    self.log_rewards[self.player].append('Hit closed Triple: -1')

        else:
            # if number is already closed, penalize
            if self.completed[0][board_position[self.aiming_for]] + self.completed[1][board_position[self.aiming_for]] == 2:
                self.reward[self.player] -= 1
                self.log_rewards[self.player].append('Hit closed number: -1')


        
        # If it hits a valid number (15-20 or Bull) and the number is not completed yet
        if previous_num_valid_hits < updated_num_valid_hits:
            self.reward[self.player] += 1
            self.log_rewards[self.player].append('Hit a valid number: +1')

        if self.darts_to_finish[self.player][0] < self.darts_to_finish[1-self.player][0] and self.turns > 1:
            self.reward[self.player] += 2
            self.log_rewards[self.player].append('Less darts to finish: +0.3')
        elif self.darts_to_finish[self.player][0] > self.darts_to_finish[1-self.player][0] and self.turns > 1:
            self.reward[self.player] -= 1
            self.log_rewards[self.player].append('More darts to finish: -0.3')

        # If it scores, reward it
        if updated_score > previous_score:
            self.reward[self.player] += 1
            self.log_rewards[self.player].append(f'Score increase: +1')

        # if it completes a number, reward it
        if updated_num_completed > previous_num_completed:
            self.reward[self.player] += 1
            self.log_rewards[self.player].append(f'Completed a number: +1')

        # if it wins a game, reward it. Otherwise, penalize
        if self.game_end[self.player] == 1:
            self.reward[self.player] += 20
            self.log_rewards[self.player].append('Won the game: +20')
            self.reward[1-self.player] -= 20
            self.log_rewards[1-self.player].append('Lost the game: -20')

        
        self.state_space = [self.board, self.completed, self.scoring, self.current_score, self.darts_to_finish]
        self.state_space = [item for sublist in [item for sublist in self.state_space for item in sublist] for item in sublist]
        # self.state_space = [self.board[0], self.completed[0], self.scoring[0], self.current_score[0], self.darts_to_finish[0]]
        # self.state_space = [item for sublist in self.state_space for item in sublist]

        return self.reward, self.state_space, self.done      


if __name__ == "__main__":
    env = Darts()
    env.run_game()
