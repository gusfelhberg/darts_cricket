from Darts_Opponent_Cricket import Accuracy, Throw, Score, Aim, Decide, BoardViz, Skill, GameReset, BoardUpdate
import streamlit as st

import numpy as np
# from Darts_Opponent_Cricket import *
st.set_page_config(layout="wide")


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)


def get_dart_count_string(num_darts):
    return ''.join([':dart:' for x in range(int(num_darts))])


def draw_board(results, current_score, col):
    # results: 2 dimention arrays. Each dimensions contains the number of hits. The last position of the array is the current score
    # Example:
    # results = [[3,2,3,0,0,0,0,0,100],  --> Player 0
    #            [2,3,1,2,0,0,0,0,115]   --> Player 1
    #           ]

    table = f'''
    | PLAYER 0 |    | PLAYER 1
    | -------|----|-------
    | {get_dart_count_string(results[0][0])} | 20 | {get_dart_count_string(results[1][0])} |
    | {get_dart_count_string(results[0][1])} | 19 | {get_dart_count_string(results[1][1])} |
    | {get_dart_count_string(results[0][2])} | 18 | {get_dart_count_string(results[1][2])} |
    | {get_dart_count_string(results[0][3])} | 17 | {get_dart_count_string(results[1][3])} |
    | {get_dart_count_string(results[0][4])} | 16 | {get_dart_count_string(results[1][4])} |
    | {get_dart_count_string(results[0][5])} | 15 | {get_dart_count_string(results[1][5])} |
    | {get_dart_count_string(results[0][6])} | Bullseye | {get_dart_count_string(results[1][6])} |
    | {get_dart_count_string(results[0][7])} | Triple | {get_dart_count_string(results[1][7])} |
    | {get_dart_count_string(results[0][8])} | Double | {get_dart_count_string(results[1][8])} |
    |  <span class="scores">{int(current_score[0])}</span>  | <span class="scores">SCORE</span>   |  <span class="scores">{int(current_score[1])}</span>  |
    '''
    col.markdown('<center>', unsafe_allow_html=True)
    col.markdown(table, unsafe_allow_html=True)
    col.markdown('</center>', unsafe_allow_html=True)


def new_game(turns, 
             board, 
             current_score, 
             darts_to_finish, 
             max_poss_scoring, 
             fewer_remaining, 
             game_end, 
             completed, 
             scoring, 
             highest_score, 
             triples, 
             doubles, 
             dartm, 
             dartn, 
             entryscore):

    player = 0
    
    overall_score=[0,0]

    end_of_game = False
    
    cols_title = st.beta_columns([3,1,3])
    cols_title[0].title('Player 0')
    cols_title[2].title('Player 1')

    while game_end[0, 0] == 0:

        i = 1

        print('')
        print('##### PLAYER '+str(player))

        if player == 0:
            st.write('---')
            cols_player = st.beta_columns([1,1,1,2,1,1,1])
            cols_player[0].write('### Turn: '+str(turns+1))
            cols_player[4].write('### Turn: '+str(turns+2))            
            cols = st.beta_columns([1,1,1,2,1,1,1])

        for i in range(1, 4):
            aiming_for, aiming_for_mult = Decide(
                player, completed, scoring, highest_score, triples, doubles)  # DECISION -> Replace with RL
            if player == 0:
                cols[i-1].write("Aiming At: "+str(aiming_for) +"*"+str(aiming_for_mult))
            else:
                cols[i+4-1].write("Aiming At: "+str(aiming_for) +"*"+str(aiming_for_mult))                

            # AIM -> Consoder (x,y) policy instead?
            aiming_arrow_x, aiming_arrow_y = Aim(aiming_for, aiming_for_mult)
            nowspread = Accuracy(player, generalspread)  # SKILL/FOCUS/LUCK
            arrow_x, arrow_y = Throw(aiming_arrow_x, aiming_arrow_y, nowspread)  # THROW/LAND
            dartscore, darts_core_mult, comment = Score(arrow_x, arrow_y)  # DART SCORE
            
            # overall_score[player] = overall_score[player] + dartscore * darts_core_mult

            print(comment+" "+str(dartscore)+"*"+str(darts_core_mult))
            if player == 0:
                cols[i-1].write(comment+" "+str(dartscore) + "*"+str(darts_core_mult))
            else:
                cols[i+4-1].write(comment+" "+str(dartscore) + "*"+str(darts_core_mult))
            
            board, current_score, game_end, completed, scoring, highest_score, triples, doubles,  darts_to_finish, max_poss_scoring, fewer_remaining = BoardUpdate(
                board, player, current_score, dartscore, darts_core_mult, highest_score, completed, game_end, darts_to_finish, max_poss_scoring, fewer_remaining, scoring, triples, doubles)  # UPDATE variables after throw

            if player == 0:
                BoardViz(arrow_x, arrow_y, i, cols[i-1])
            else:
                BoardViz(arrow_x, arrow_y, i, cols[i+4-1])
            
            if player == 0:
                cols[i-1].write(f'Score: {current_score[player][0]}')
            else:
                cols[i+4-1].write(f'Score: {current_score[player][0]}')


            if game_end[0, 0] == 1:
                turns = turns + 1
                print(board)
                print(current_score)
                print(game_end)
                print("I Win! Great Game! Turns: "+str(turns+1))
                print("Skill:", generalspread)
                st.title("I Win! Great Game! Turns: "+str(turns+1))
                st.title(f"Skill Player 0: {generalspread[0][0]}")
                st.title(f"Skill Player 1: {generalspread[1][0]}")
                
                st.balloons()
                end_of_game = True
                break

                # sys.exit()

            if game_end[1, 0] == 1:
                turns = turns + 1
                print(board)
                print(current_score)
                print(game_end)
                # BoardViz(arrow_x, arrow_y, i)
                print("You Win! Great Game! Turns: "+str(turns+1))
                print("Skill:", generalspread)
                st.title("You Win! Great Game! Turns: "+str(turns+1))
                st.title(f"Skill Player 0: {generalspread[0][0]}")
                st.title(f"Skill Player 1: {generalspread[1][0]}")
                
                end_of_game = True
                break
        

        if player == 1:
            draw_board(board,current_score,cols[3])

        # st.write(f'')
        # st.write(f'Darts to Finish: {darts_to_finish[player][0]}')
        


        # st.write('Board: '+str(board[player]))
        # st.write('Score: '+str(current_score[player]))
        # if scoring[0][0] > scoring[1][0]:
        #     st.write('Player 0 is leading')
        # elif scoring[0][0] < scoring[1][0]:
        #     st.write('Player 1 is leading')
        # else:
        #     st.write('Players with same score')
        
        # st.write('Completed: '+str(completed[player]))
        # st.write('Scoring: '+str(scoring[player]))
        # st.write('Darts to Finish: '+str(darts_to_finish[player]))
        # st.write('Fewer remaining: '+str(fewer_remaining[player]))
        # st.write('Max Poss. Scoring Left: '+str(
        #     current_score[player])+'-'+str(current_score[1-player])+' / '+str(max_poss_scoring[player]))        

        player = 1 - player
        turns = turns + 1
        
        if end_of_game:
            break

    # draw_board(board, current_score)



if __name__ == "__main__":

    local_css('style.css')
    st.title('DARTS CHALLENGE')

    main_bt = st.button('Start New Game')

    if main_bt == True:

        turns, board, current_score, darts_to_finish, max_poss_scoring, fewer_remaining, game_end, completed, scoring, highest_score, triples, doubles, dartm, dartn, entryscore = GameReset()  # RESET variables
        generalspread = Skill()  # SKILL level

        new_game(turns, board, current_score, darts_to_finish, max_poss_scoring, fewer_remaining,
                 game_end, completed, scoring, highest_score, triples, doubles, dartm, dartn, entryscore)

