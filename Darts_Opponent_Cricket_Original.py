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



######################################################
            # BOARD & ARRAY SETUP #
######################################################
def GameReset():

    turns = 0

    
    # 0-20; 1-19; 2-18; 3-17; 4-16; 5-15; 6-B; 7-T; 8-D
    board           = np.zeros((2, 9))         # number of Xs for each number for each player
    currentscore    = np.zeros((2, 1))         # current score for each player
    dartstofinish   = np.zeros((2, 1))         # minimum number of darts needed to finish game
    maxpossscoring  = np.zeros((2, 1))         # maximum can score on based on what's open for the oppoenent
    fewerremaining  = np.zeros((2, 1))         # binary for whoever has the fewest darts needed to finish the game - either both 0 (tie) or only one 1
    gameend         = np.zeros((2, 1))         # game over

    
    # 0-20; 1-19; 2-18; 3-17; 4-16; 5-15; 6-B; 7-T; 8-D
    completed       = np.zeros((2, 9))         # binary completed for each number for each player
    scoring         = np.zeros((2, 9))         # binary scoring for each number for each player - either both 0 (tie) or only one 1
    highestscore    = np.zeros((2, 1))         # binary for whoever has the highest score - either both 0 (tie) or only one 1
    triples         = np.zeros((2, 1))         # binary for completed triples
    doubles         = np.zeros((2, 1))         # binary for completed doubles
    

    dartm           = np.zeros((3))            # multiples Single, Double, Triple
    dartn           = np.zeros((3))            # 1 to 20, or 25
    entryscore      = 0                        # human score from three darts
    
    return turns, board, currentscore, dartstofinish, maxpossscoring, fewerremaining, gameend, completed, scoring, highestscore, triples, doubles, dartm, dartn, entryscore



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

    
  level  = 4  #5 is high, 1 is low
  
  
  generalspread [0] = np.round((6 - level) * 15 - np.sqrt( 5 - level) * 10 + (3 - 6 * random()), 0) 
  generalspread [1] = np.round((6 - level) * 15 - np.sqrt( 5 - level) * 10 + (3 - 6 * random()), 0) 
    
  return generalspread



######################################################
            # WHAT SHOULD I AIM AT? #                 # Replace with RL Policy
######################################################
def Decide(player, completed, scoring, highestscore, triples, doubles):
  aimingfor = 0
  aimingformult = 0
  i = 0
  
  #20->15
  while i <= 5 :  
   if completed[player,i] == 0 :
       aimingfor = 20 - i
       aimingformult = 3  # single = 1; double = 2; triple = 3
       print("Aiming At: "+str(aimingfor)+"*"+str(aimingformult))
       return aimingfor, aimingformult 
  
   i = i + 1  
  
  #Bulls  
  if completed[player,6] == 0 :
       aimingfor = 25
       aimingformult = 2  # single = 1; double = 2; triple = 3
       print("Aiming At: "+str(aimingfor)+"*"+str(aimingformult))
       return aimingfor, aimingformult

#############################################  NEED TO AIM AT SOMETHNG SCORING ON BEFORE DEFAULTING TO 14; THEN FIX SCORING DECISION (15-20 and <14)!
  
  #Triples
  if completed[player,7] == 0 :
       aimingfor = 20
       aimingformult = 3  # single = 1; double = 2; triple = 3
       print("Aiming At: "+str(aimingfor)+"*"+str(aimingformult))
       return aimingfor, aimingformult
  
  #Doubles  
  if completed[player,8] == 0 :
       aimingfor = 20
       aimingformult = 2  # single = 1; double = 2; triple = 3
       print("Aiming At: "+str(aimingfor)+"*"+str(aimingformult))
       return aimingfor, aimingformult

  #ONLY SCORING NEEDED
  j = 0
  while j <= 8 :
    if scoring[player,8-j] == 1 :
       scoringon = 8-j
       print('###### ScoringOn: '+str(scoringon))
    j = j + 1

  if scoringon <= 5 :   ############### RARE BUG EVERY 30-40 GAMES ??scoringon?? ##################
     aimingfor = 20 - scoringon
     aimingformult = 3  # single = 1; double = 2; triple = 3
     print("Aiming At: "+str(aimingfor)+"*"+str(aimingformult))
     return aimingfor, aimingformult

  else :
     if scoringon == 6 :
       aimingfor = 25
       aimingformult = 2  # single = 1; double = 2; triple = 3
       print("Aiming At: "+str(aimingfor)+"*"+str(aimingformult))
       return aimingfor, aimingformult         
  
     if scoringon == 7 :    
       aimingfor = 20
       aimingformult = 3  # single = 1; double = 2; triple = 3
       print("Aiming At: "+str(aimingfor)+"*"+str(aimingformult))
       return aimingfor, aimingformult  

     if scoringon == 8 :    
       aimingfor = 20
       aimingformult = 2  # single = 1; double = 2; triple = 3
       print("Aiming At: "+str(aimingfor)+"*"+str(aimingformult))
       return aimingfor, aimingformult
   

  print("Aiming At: "+str(aimingfor)+"*"+str(aimingformult))

  return aimingfor, aimingformult 


######################################################
            # WHERE SHOULD I AIM THIS DART? #
######################################################
def Aim(aimingfor, aimingformult):
  a = array('i',[0,72,306,270,36,108,0,234,198,144,342,180,126,18,162,324,216,288,54,252,90])
  d = array('i',[0,109,139,79]) 
  aimingarrowx = 0
  aimingarrowy = 0

  if aimingfor <= 20:
    aimingarrowx = d[aimingformult] * math.cos(a[aimingfor]*math.pi/180)
    aimingarrowy = d[aimingformult] * math.sin(a[aimingfor]*math.pi/180)
  else:
    aimingarrowx = 0 #Bull
    aimingarrowy = 0
    
  #print(aimingfor,aimingformult,a[aimingfor],d[aimingformult],np.round(aimingarrowx,0),np.round(aimingarrowy,0))
  
  
  return aimingarrowx, aimingarrowy


######################################################
            # HOW GOOD WILL THIS DART BE? #
######################################################
def Accuracy(generalspread):
    
  nowspread = 0
  
  nowspread = np.round(generalspread[player] * (random()*0.8+0.6),0) 
  #print(nowspread)
  
  return nowspread


######################################################
            # WHERE DID THIS DART LAND? #
######################################################
def Throw(aimingarrowx,aimingarrowy,nowspread):
  
  arrowx = np.round(aimingarrowx + 2*(nowspread*(0.5-random())),0)
  arrowy = np.round(aimingarrowy + 2*(nowspread*(0.5-random())),0)

  return arrowx[0], arrowy[0]



######################################################
            # HOW DID THIS DART SCORE? #
######################################################
  
def Score(arrowx,arrowy):
  dartscore = 0
  dartscoremult = 0
  distance = 0
  comment = "Hit!"
  
  distance = (arrowx ** 2 + arrowy ** 2) ** 0.5  #Pythagoras 
  
  angle = math.degrees(math.atan2(arrowy,arrowx))
  
  if angle<0:
    angle+=360
  
    
  #print("d: "+str(distance)+" a: "+str(angle))
  
    
######################
# Miss / Wire / Bull #
######################
  
### Miss Board ###
  if distance > 144:
      dartscore = 0
      dartscoremult = 0
      comment = "Backboard!"
      return dartscore, dartscoremult, comment
  
### Wire Shots ###
  wireshotbounce = 0.2
  if np.round(distance,0) in [10,20,74,84,134,144]:
      if random() < wireshotbounce:
            dartscore = 0
            dartscoremult = 0
            comment = "Bounced!"
            return dartscore, dartscoremult, comment
    
  if np.round(angle,0) in [9,27,45,63,81,99,117,135,153,171,189,207,225,243,261,279,297,315,333,351]:
      if random() < wireshotbounce : 
            dartscore = 0
            dartscoremult = 0
            comment = "Bounced!"
            return dartscore, dartscoremult, comment
  
  if distance < 10 : 
            dartscore = 25
            dartscoremult = 2
            comment = "Double Bull!"
            return dartscore, dartscoremult, comment
  
  if distance < 20 : 
            dartscore = 25
            dartscoremult = 1
            comment = "Single Bull!"
            return dartscore, dartscoremult, comment

######################
     # 20...1 #
######################
#
## 20
  if 81 <= angle < 99 :
      if  74 < distance <= 84 : 
            dartscore = 20
            dartscoremult = 3
      else:
        if  134 < distance <= 144 : 
            dartscore = 20
            dartscoremult = 2
        else :
            dartscore = 20
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 5
  if 99 <= angle < 117 :
      if  74 < distance <= 84 : 
            dartscore = 5
            dartscoremult = 3
      else:
        if  134 < distance <= 144 : 
            dartscore = 5
            dartscoremult = 2
        else :
            dartscore = 5
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 12
  if 117 <= angle < 135 :
      if  74 < distance <= 84 : 
            dartscore = 12
            dartscoremult = 3
      else:
        if  134 < distance <= 144 : 
            dartscore = 12
            dartscoremult = 2
        else :
            dartscore = 12
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 9
  if 135 <= angle < 153 :
      if  74 < distance <= 84 : 
            dartscore = 9
            dartscoremult = 3
      else:
        if  134 < distance <= 144 : 
            dartscore = 9
            dartscoremult = 2
        else :
            dartscore = 9
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 14
  if 153 <= angle < 171 :
      if  74 < distance <= 84 : 
            dartscore = 14
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 14
            dartscoremult = 2
        else :
            dartscore = 14
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 11
  if 171 <= angle < 189 :
      if  74 < distance <= 84 : 
            dartscore = 11
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 11
            dartscoremult = 2
        else :
            dartscore = 11
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 8
  if 189 <= angle < 207 :
      if  74 < distance <= 84 : 
            dartscore = 8
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 8
            dartscoremult = 2
        else :
            dartscore = 8
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 16
  if 207 <= angle < 225 :
      if  74 < distance <= 84 : 
            dartscore = 16
            dartscoremult = 3
      else:
        if  134 < distance <= 144 : 
            dartscore = 16
            dartscoremult = 2
        else :
            dartscore = 16
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 7
  if 225 <= angle < 243 :
      if  74 < distance <= 84 : 
            dartscore = 7
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 7
            dartscoremult = 2
        else :
            dartscore = 7
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 19
  if 243 <= angle < 261 :
      if  74 < distance <= 84 : 
            dartscore = 19
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 19
            dartscoremult = 2
        else :
            dartscore = 19
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 3
  if 261 <= angle < 279 :
      if  74 < distance <= 84 : 
            dartscore = 3
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 3
            dartscoremult = 2
        else :
            dartscore = 3
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 17
  if 279 <= angle < 297 :
      if  74 < distance <= 84 : 
            dartscore = 17
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 17
            dartscoremult = 2
        else :
            dartscore = 17
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 2
  if 297 <= angle < 315 :
      if  74 < distance <= 84 : 
            dartscore = 2
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 2
            dartscoremult = 2
        else :
            dartscore = 2
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 15
  if 315 <= angle < 333 :
      if  74 < distance <= 84 : 
            dartscore = 15
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 15
            dartscoremult = 2
        else :
            dartscore = 15
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 10
  if 333 <= angle < 351 :
      if  74 < distance <= 84 : 
            dartscore = 10
            dartscoremult = 3
      else:
        if  134 < distance <= 144 : 
            dartscore = 10
            dartscoremult = 2
        else :
            dartscore = 10
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 6
  if (351 <= angle < 361) or (0 <= angle < 9) :
      if  74 < distance <= 84 : 
            dartscore = 6
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 6
            dartscoremult = 2
        else :
            dartscore = 6
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 13
  if 9 <= angle < 27 :
      if  74 < distance <= 84 : 
            dartscore = 13
            dartscoremult = 3
      else:
        if  134 < distance <= 144 : 
            dartscore = 13
            dartscoremult = 2
        else :
            dartscore = 13
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 4
  if 27 <= angle < 45 :
      if  74 < distance <= 84 : 
            dartscore = 4
            dartscoremult = 3
      else:
        if  134 < distance <= 144 : 
            dartscore = 4
            dartscoremult = 2
        else :
            dartscore = 4
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 18
  if 45 <= angle < 63 :
      if  74 < distance <= 84 : 
            dartscore = 18
            dartscoremult = 3
      else: 
        if  134 < distance <= 144 : 
            dartscore = 18
            dartscoremult = 2
        else :
            dartscore = 18
            dartscoremult = 1      
      return dartscore, dartscoremult, comment
### 1
  if 63 <= angle < 81 :
      if  74 < distance <= 84 : 
            dartscore = 1
            dartscoremult = 3
      else:
        if  134 < distance <= 144 : 
            dartscore = 1
            dartscoremult = 2
        else :
            dartscore = 1
            dartscoremult = 1      
      return dartscore, dartscoremult, comment

  
  dartscore = 999
  dartscoremult = 9
  comment = "Error??"
  
  return dartscore, dartscoremult, comment



######################################################
            # WHAT SHOULD I TAKE THIS DART AS? #   DEPENDS ON STRATEGY
######################################################
def DecideScore(player, dartscore, dartscoremult):

    
########## NOT PROGRAMMED ####################
     ##### THERE'S A DECISION ON HOW TO TAKE THE SCORING WHEN THERE ARE MULTIPLE OPTIONS?? When to take a double or triple rather than two or three twenties? 
     ##### When multiple options: Triple; Three 15s; or 45 points – which one?
 

   return player, dartscore, dartscoremult



###########################################################
            # WHAT DOES THE UPDATED SCOREBOARD LOOK LIKE? #
###########################################################
def BoardUpdate(player, dartscore, dartscoremult):
   

    #dartscore = 17
    #dartscoremult = 2
    #player = 0
    #board[1 - player,0] = 3
    done = 0

########### Take partially to close off soemthing being scored on vs. take instead of scoring as they are more difficult to get
# call ScoringDecision(completed, scoring, highestscore, triples, doubles) ??

    #Needing both Triples and the 15-20 hit

    #Bulls
    if  dartscore == 25:
        if board [player, 6] + dartscoremult >= 3 and board [1 - player, 6] < 3 :
            currentscore [player,0] =  currentscore [player,0] + ((board [player, 6] + dartscoremult - 3) * dartscore)
            done = 1
        if board [player, 6] + dartscoremult > 3 :
            board [player, 6] = 3
            done = 1
        if board [player, 6] + dartscoremult <= 3 :
            board [player, 6] = board [player, 6]  + dartscoremult
            done = 1
            
    #Triples
    if  dartscoremult == 3 and done == 0 :
            if board [player, 7] + 1 <= 3 :
               board [player, 7] = board [player, 7]  + 1 
               done = 1
            else: 
              if board [1 - player, 7] < 3 and dartscore < 15 :  
               currentscore [player,0] =  currentscore [player,0] + 3 * dartscore
               done = 1    
              if board [1 - player, 7] < 3 and 15 <= dartscore <= 20 :  
               if completed [player, 20 - dartscore] == 1 :
                  currentscore [player,0] =  currentscore [player,0] + 3 * dartscore
                  done = 1  

    #Doubles
    if  dartscoremult == 2 and done == 0 :
            if board [player, 8] + 1 <= 3 :
               board [player, 8] = board [player, 8]  + 1
               done = 1
            else:
              if board [1 - player, 8] < 3 :
                currentscore [player,0] =  currentscore [player,0] + 2 * dartscore     
                done = 1
              if board [1 - player, 8] < 3 and 15 <= dartscore <= 20 and done == 0 :  
                if completed [player, 20 - dartscore] == 1 :
                   currentscore [player,0] =  currentscore [player,0] + 2 * dartscore
                   done = 1     

    #20-15
    if  dartscore >= 15 and done == 0 :
            if  15 <= dartscore <= 20 and board [player, 20 - dartscore] + dartscoremult <= 3 :
                board [player, 20 - dartscore] = board [player, 20 - dartscore]  + dartscoremult
                done = 1
            else:
              if 15 <= dartscore <= 20 and board [1 - player, 20 - dartscore] < 3 :
                 currentscore [player,0] =  currentscore [player,0] + ((board [player, 20 - dartscore] + dartscoremult - 3) * dartscore)  
                 done = 1 
              if 15 <= dartscore <= 20 and board [player, 20 - dartscore] + dartscoremult > 3 :
                 board [player, 20 - dartscore] = 3
                 done = 1
                

#update who has the highest score
 
    if currentscore[player] < currentscore[1-player]:
      highestscore[player]  = 0
      highestscore[1-player]  = 1

    else:
      if currentscore[player] > currentscore[1-player]:
       highestscore[player]  = 1
       highestscore[1-player]  = 0
      else: 
        highestscore[player]  = 0
        highestscore[1-player]  = 0

#update 'completed' array
    i = 0
    while i <= 8 :
     
     if board[player,i] == 3 :
         completed[player,i] = 1
         if completed[1 - player,i] == 0 :
           scoring[player,i] = 1
         else:
           scoring[player,i] = 0  
    
        
     i = i+1
     
    gameend[player] = min(min(completed[player]),(currentscore [player,0] > currentscore [1 - player,0]))  #Track if everything is completed and score is higher   
    
    
   

#####Count minimum darts remaining to win  
   
#calculate min darts to finish game, including a higher score
     
    i = 0
    dartstofinish[player] = 0
    maxpossscoring[player] = 0
    
    while i <= 8 :
     
     if i <= 5 :                                #For 20 to 15, always 0,1 darts to finish each
       if board[player,i] < 3 :
         dartstofinish[player] = dartstofinish[player] + 1                                           #count number of darts needed to finish
       if board[1-player,i] < 3 :
         maxpossscoring[player] = max(maxpossscoring[player],(20 - i)*(1-completed[1-player,i])*3)   #assess maximum number that can be scored on, if behind on score     
     else: 
       if i == 6 :                              #For Bulls(6), always 0,1,2 darts to finish 
        if board[player,i] == 0 :  
          dartstofinish[player] = dartstofinish[player] + 2
        if board[player,i] in (1,2) :   
          dartstofinish[player] = dartstofinish[player] + 1 
        if board[1-player,i] < 3 :    
          maxpossscoring[player] = max(maxpossscoring[player],50)                 
       else: 
         if i == 7 or i == 8 :                  #For Triples(7) or Doubles(8), always 0,1,2,3 darts to finish each
          if board[player,i] < 3 :  
           dartstofinish[player] = dartstofinish[player] + (3 - board[player,i])
          if board[1-player,i] < 3 :   
            maxpossscoring[player] = (8-i)*max(maxpossscoring[player],60) + (i-7)*max(maxpossscoring[player],50)

     i = i+1
    
     
    
#for player with lower score, divide by maximum of what other player has not completed
    
    if highestscore[player] == 0 :
      dartstofinish[player] = dartstofinish[player] + np.ceil((currentscore[1-player] - currentscore[player] ) / maxpossscoring[player] + 0.01) #min of one darts if tied or losing
      
    
    
#assess whether winning or not   
    if dartstofinish[player] < dartstofinish[1-player]:
      fewerremaining[player]  = 1
      fewerremaining[1-player]  = 0

    else:
      if dartstofinish[player] > dartstofinish[1-player]:
       fewerremaining[player]  = 0
       fewerremaining[1-player]  = 1
      else: 
        fewerremaining[player]  = 0
        fewerremaining[1-player]  = 0
  
    
    
#print current state variables
    print('---')
    print('Board: '+str(board[player]))
    print('Score: '+str(currentscore[player])+' Leading: '+str(highestscore[player]))
    print('Completed: '+str(completed[player]))
    print('Scoring: '+str(scoring[player]))
    print('Darts to Finish: '+str(dartstofinish[player])+' Fewer remaining: '+str(fewerremaining[player])+' Max Poss. Scoring Left: '+str(currentscore[player])+'-'+str(currentscore[1-player])+' / '+str(maxpossscoring[player]))
    print('GameOver: '+str(gameend[player]))
    print('---')
     

    return board, currentscore, gameend, completed, scoring, highestscore, triples, doubles, dartstofinish, maxpossscoring, fewerremaining



######################################################
            # WHAT DOES THE DARTBOARD LOOK LIKE? #
######################################################

def BoardViz(arrowx,arrowy,i):
  x = 0
  y = 0
  
  # x/y outer wire = 1.25 to 8.75
  # arrowx/y between -150 adn 150 
  x = (arrowx + 150) / (300/(8.77-1.23)) + 1.23
  y = (arrowy + 150) / (300/(8.77-1.23)) + 1.23
  
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
  # plt.imshow(img2, zorder=1, extent=[8.5, 10, 0, 2])  # CHALK BOARD
  plt.imshow(img, zorder=0, extent=[0, 10, 0, 10])  # DARTBOARD

  if i == 3:
   plt.show()

  #print(x,y)
  


######################################################
            # WHICH DARTS DID THE HUMAN THROW #
######################################################

def Entry():

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

### NEED TO SET UP TO PLAY AGAINST HUMAN CALLING Entry()... 
### NEED TO DISPLAY UPDATED CHALKBOARD BEFORE HUMAN Entery() 

turns, board, currentscore, dartstofinish, maxpossscoring, fewerremaining, gameend, completed, scoring, highestscore, triples, doubles, dartm, dartn, entryscore    = GameReset()   #RESET variables                                     
generalspread = Skill()       #SKILL level

player = 0

while gameend[0,0] == 0: 

  i = 1  

  print('')
  print('#####PLAYER '+str(player))  
  
  while i <= 3 :
            aimingfor, aimingformmult           = Decide(player, completed, scoring, highestscore, triples, doubles)    #DECISION -> Replace with RL
            aimingarrowx, aimingarrowy          = Aim(aimingfor, aimingformmult)                                        #AIM -> Consoder (x,y) policy instead?
            nowspread                           = Accuracy(generalspread)                                               #SKILL/FOCUS/LUCK
            arrowx, arrowy                      = Throw(aimingarrowx,aimingarrowy,nowspread)                            #THROW/LAND
            dartscore, dartscoremult, comment   = Score(arrowx, arrowy)                                                 #DART SCORE

            print(comment+" "+str(dartscore)+"*"+str(dartscoremult))
            
            board, currentscore, gameend, completed, scoring, highestscore, triples, doubles,  dartstofinish, maxpossscoring, fewerremaining = BoardUpdate(player, dartscore, dartscoremult) #UPDATE variables after throw
        
            #print("aiminingarrowx: "+str(np.round(aimingarrowx,0))+" aimingarrowy: "+str(np.round(aimingarrowy,0)))
            #print("arrowx: "+str(np.round(arrowx,0))+" arrowy: "+str(np.round(arrowy,0)))
        
            ##############
            #ADD DARTBOARD ANIMATION AFTER EACH TURN BACK WHEN PLAYING AGAINST HUMAN ## 
            #Board(arrowx,arrowy,i)
            ##############
            
            if gameend[0,0] == 1 :
               turns = turns + 1 
               print(board)
               print(currentscore)
               print(gameend)
              #  BoardViz(arrowx,arrowy,i)
               print("I Win! Great Game! Turns: "+str(turns))  
               print("Skill:",generalspread)
               sys.exit()
        
            if gameend[1,0] == 1 :
               turns = turns + 1 
               print(board)
               print(currentscore)
               print(gameend)
              #  BoardViz(arrowx,arrowy,i)
               print("You Win! Great Game! Turns: "+str(turns))    
               print("Skill:",generalspread)
               sys.exit()
               
            i = i + 1
  
  player = 1 - player
  turns = turns + 1    

     
           

  

  
  



