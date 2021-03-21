from streamlit.hashing import _CodeHasher
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from random import choices
from string import ascii_letters
import streamlit as st
import pandas as pd 
from streamlit_darts_aiming import aim_dart
import math
import numpy as np
from random import random


from darts_rl import Darts
# from darts_streamlit import draw_board

       
# st.set_page_config(layout='wide')

def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)
local_css('style.css')


def main():
    
    state = _get_state()
    state.throws_history = []
    # st.set_page_config(layout='wide')

    if state.game is None:
        state.game = Darts()

    if state.aim_throw_history is None:
        state.aim_throw_history = []

    st.title('Welcome to the Darts Challenge!')
    # st.write(f'state.aiming_for: {state.aiming_for}')
    # st.write(f'state.game.aiming_for: {state.game.aiming_for}')
    # st.write(state.throw_num)
    


    # st.sidebar.title('Game Config')
    # if state.player0_name is None:
    #     player0_name = st.sidebar.text_input('Player 0 Name:')
    #     player1_name = st.sidebar.text_input('Player 1 Name:')
    #     players_skills = st.sidebar.number_input('Inform Players Skill (1-5):',4)
    # if state.player0_name is not None:
    #     st.sidebar.write(f"Player 0: {state.player0_name}")
    #     st.sidebar.write(f"Player 1: {state.player1_name}")
    #     st.sidebar.write(f"Skills: {state.players_skills}")
    # bt_cols = st.sidebar.beta_columns(2)
    # if bt_cols[0].button("Save"):
    #     state.player0_name = player0_name
    #     state.player1_name = player1_name
    #     state.players_skills = players_skills
    # if bt_cols[1].button('Edit'):
    #     state.player0_name = None
    #     state.player1_name = None
    #     state.players_skills = None


    # if state.game_start:
    throw_num = 1
    max_turns = 50
    # state.game.player = 0
    # if state.players_skills is None:
    #     st.error('Please assign a skill for the players')
    # else:



    state.players_skills = 4
    state.game.assign_player_skill(level=state.players_skills)
    if state.game.player is None:
        state.game.player = 0
    state.wish_to_continue = True
    if state.throw_num is None:
        state.throw_num = 1

    if state.game.aiming_for is None and state.wish_to_continue == True:

        # state.wish_to_continue = False
        st.write('---')
        st.title(f'Player {state.game.player} - Turn {state.game.turns+1} - Throw # {state.throw_num}')
        st.subheader('Select your target')
        radio_aim = st.radio('',['Double Click Board','Select from List'])
        if radio_aim == 'Double Click Board':
            x = aim_dart()
            if x != 0.0:
                state.aiming_for, state.aiming_for_mult, _ = get_dart_aim(x[0],x[1])
                st.subheader(f"Aiming at {state.aiming_for} * {state.aiming_for_mult}")
                if state.aiming_for not in [15,16,17,18,19,20,25]:
                    st.warning("Please select a valid number: 15-20 or Bulls Eye (in dev to allow any numbers)")

        else:
            st.subheader('Select Aiming options')
            col1,col2 = st.beta_columns(2)
            aiming_for = col1.selectbox('Aiming At',['Bulls Eye',20,19,18,17,16,15])
            if aiming_for == 'Bulls Eye':
                aiming_for_mult = col2.selectbox('Aiming At - Mult',['Single','Double'])
            else:
                aiming_for_mult = col2.selectbox('Aiming At - Mult',['Single','Double','Triple'])
            if aiming_for == 'Bulls Eye':
                state.aiming_for = 25
            else:
                state.aiming_for = aiming_for
            if aiming_for_mult == 'Single':
                state.aiming_for_mult = 1
            elif aiming_for_mult == 'Double':
                state.aiming_for_mult = 2
            else:
                state.aiming_for_mult = 2


        if st.button('Throw Dart'):
            state.confirm = True

        if state.confirm:
            state.game.aiming_for = int(state.aiming_for)
            state.game.aiming_for_mult = int(state.aiming_for_mult)

            state.game.reward, state.game.state_space, state.game.done = state.game.step(action = state.game.aiming_for, action_mult = state.game.aiming_for_mult, player=state.game.player)
            
            state.aim_throw_history.append([state.game.player,state.game.aiming_for,state.game.aiming_for_mult,state.game.dart_score,state.game.dart_score_mult])

            state.throw_num += 1
            if state.throw_num == 4:
                state.game.turns += 1
                state.game.player = 1 - state.game.player
                state.throw_num = 1

            

            state.game.aiming_for = None
            state.game.aiming_for_mult = None
            state.confirm = False

        if state.game.dart_score is not None:
            st.subheader(str(state.game.dart_score)+"*"+str(state.game.dart_score_mult)+' ('+state.game.comment+")" )
        draw_board(state.game.board,state.game.current_score,state.game.player)

        if state.game.done == 1:
            st.balloons()
            st.title('GAME OVER')
            st.title(f'Player {state.game.player} Wins!')
        
        st.write('---')
        st.title('Aim x Throw History')
        st.table(pd.DataFrame(state.aim_throw_history,columns=['Player','Aiming At','Aiming At Mult','Score','Score - Mult']))





            


    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


def get_dart_aim(arrow_x,arrow_y):

        distance = (arrow_x ** 2 + arrow_y ** 2) ** 0.5  # Pythagoras

        angle = math.degrees(math.atan2(arrow_y, arrow_x))

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

        wireshot_bounce = 0.2

        wire_distances = [10, 20, 74, 84, 134, 144]
        for dist in wire_distances:
            if dist - wireshot_bounce <= distance <= dist + wireshot_bounce:
                dart_score = 0
                dart_score_mult = 0
                comment = "Bounced!"
                return dart_score, dart_score_mult, comment
    
        wire_angles = [9*(1+2*n) for n in range(0,20)] 
        if np.round(angle, 0) in wire_angles:
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
            [225, 243,  7],    # 7
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


def get_dart_count_string(num_darts):
    return ''.join([':dart:' for x in range(int(num_darts))])

def draw_board(results, current_score,next_player):
    # results: 2 dimention arrays. Each dimensions contains the number of hits. The last position of the array is the current score
    # Example:
    # results = [[3,2,3,0,0,0,0,0,100],  --> Player 0
    #            [2,3,1,2,0,0,0,0,115]   --> Player 1
    #           ]



    table = f'''
    | PLAYER 0 {":raised_hand:" if next_player == 0 else ''} |    | PLAYER 1 {":raised_hand:" if next_player == 1 else ''}
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
    st.markdown('<center>', unsafe_allow_html=True)

    st.markdown(table, unsafe_allow_html=True)
    st.markdown('</center>', unsafe_allow_html=True)


class _SessionState:

    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)
        
    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value
    
    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()
    
    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False
        
        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    
    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


if __name__ == "__main__":
    main()