
from darts_rl import Darts

import random
import numpy as np
from keras import Sequential
from collections import deque
from keras.layers import Dense
import matplotlib.pyplot as plt
from keras.optimizers import Adam
import pickle
    
env = Darts()
np.random.seed(0)

import time
timestr = time.strftime("%Y%m%d-%H%M")
output_file_verbose = f'logs/output_episodes_verbose_{timestr}.txt'

output_file_episodes = f'logs/output_episodes_summary_{timestr}.txt'

class DQN:

    def __init__(self, action_space, state_space):

        self.action_space = action_space
        self.state_space = state_space
        self.gamma = 0.85
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.005
        self.tau = .125

        self.memory  = deque(maxlen=2000)
        self.model = self.build_model()
        self.target_model = self.build_model()

    def build_model(self):
        model = Sequential()
        model.add(Dense(64, input_shape=(self.state_space,), activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.action_space, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model


    def remember(self, state, action, reward, new_state, done):
        self.memory.append([state, action, reward, new_state, done])        


    def act(self, state):

        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return random.randrange(self.action_space)
        return np.argmax(self.model.predict(state)[0])


    def replay(self):

        batch_size = 32
        if len(self.memory) < batch_size: 
            return

        samples = random.sample(self.memory, batch_size)
        for sample in samples:
            state, action, reward, new_state, done = sample

            target = self.target_model.predict(state)
            if done:
                target[0][action] = reward
            else:
                Q_future = max(self.target_model.predict(new_state)[0])
                target[0][action] = reward + Q_future * self.gamma
            self.model.fit(state, target, epochs=1, verbose=0)     

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, fn):
        self.model.save(fn)       


def train_dqn(episode,verbose=0):

    loss = []
    
    action_space = len(env.action_space)
    state_space = len(env.state_space)
    max_steps = 50

    agent = DQN(action_space, state_space)

    agent_aims_history = []

    
    env.verbose = verbose

    episode_backup = dict()

    for e in range(1,episode+1):

        print(f"\n#################################",file=open(output_file_verbose, "a"))
        print(f"################# EPISODE {e}",file=open(output_file_verbose, "a"))
        print(f"#################################\n",file=open(output_file_verbose, "a"))
        
        state = env.reset()
        state = np.reshape(state, (1, state_space))

        done = 0
        env.verbose = verbose

        total_reward_agent = 0
        total_reward_p1 = 0

        throw_history = []

        
        env.assign_player_skill(level=4)

        while done == 0 and env.turns < max_steps:
            env.player = 0
            
            if env.verbose == 1:
                print(f"######## TURN {env.turns} - PLAYER 0")
                print(f"######## TURN {env.turns} - PLAYER 0",file=open(output_file_verbose, "a"))
            else:
                print(f"######## TURN {env.turns} - PLAYER 0",file=open(output_file_verbose, "a"))
                                    

            for throw_num in range(1,4): 
                
                action = agent.act(state)
                if env.verbose == 1:
                    print(f"Aiming At: "+str(env.action_space[action][0])+"*"+str(env.action_space[action][1]), end=' -> ')
                    print(f"Aiming At: "+str(env.action_space[action][0])+"*"+str(env.action_space[action][1]), end=' -> ',file=open(output_file_verbose, "a"))
                else:
                    print(f"Aiming At: "+str(env.action_space[action][0])+"*"+str(env.action_space[action][1]), end=' -> ',file=open(output_file_verbose, "a"))

                reward, next_state, done = env.step(action=env.action_space[action][0],
                                                    action_mult=env.action_space[action][1],
                                                    player=env.player)
                if env.verbose == 1:
                    print(str(env.dart_score)+"*"+str(env.dart_score_mult)+' ('+env.comment+") - Reward: "+str(np.round(reward[env.player],2)))
                    print(str(env.dart_score)+"*"+str(env.dart_score_mult)+' ('+env.comment+") - Reward: "+str(np.round(reward[env.player],2)),file=open(output_file_verbose, "a"))
                else:
                    print(str(env.dart_score)+"*"+str(env.dart_score_mult)+' ('+env.comment+") - Reward: "+str(np.round(reward[env.player],2)),file=open(output_file_verbose, "a"))                    

                total_reward_agent += reward[0]
                next_state = np.reshape(next_state, (1, state_space))

                agent.remember(state, action, reward[0], next_state, done)
                state = next_state
                agent.replay()
                agent.target_train() # iterates target model

                
                step_result = [e,env.turns,env.player,throw_num,env.action_space[action][0],env.action_space[action][1],env.dart_score,env.dart_score_mult]
                throw_history.append(step_result) 
                agent_aims_history.append([e, env.action_space[action][0],env.action_space[action][1]])
                pickle.dump(agent_aims_history, open('agent_aims_history.pkl','wb'))

                if done==1:
                    print(f"Episode: {e}/{episode} \t Agent Reward: {total_reward_agent:.2f} \t Agent Score: {env.current_score[0][0]:.2f} \t P1 Reward: {total_reward_p1:.2f}      P1 Score: {env.current_score[1][0]:.2f}      Winner: Agent")
                    print(f"Episode: {e}/{episode} \t Agent Reward: {total_reward_agent:.2f} \t Agent Score: {env.current_score[0][0]:.2f} \t P1 Reward: {total_reward_p1:.2f}      P1 Score: {env.current_score[1][0]:.2f}      Winner: Agent", file=open(output_file_verbose, "a"))
                    print(f"Episode: {e}/{episode} \t Agent Reward: {total_reward_agent:.2f} \t Agent Score: {env.current_score[0][0]:.2f} \t P1 Reward: {total_reward_p1:.2f}      P1 Score: {env.current_score[1][0]:.2f}      Winner: Agent", file=open(output_file_episodes, "a"))
                    break
            env.turns += 1
            # env.print_main_variables()

            if done == 0:

                env.player = 1
                if env.verbose == 1:
                    print()
                    print(f"######## TURN {env.turns} - PLAYER 1")
                    print('',file=open(output_file_verbose, "a"))
                    print(f"######## TURN {env.turns} - PLAYER 1",file=open(output_file_verbose, "a"))                    
                else:
                    print('',file=open(output_file_verbose, "a"))
                    print(f"######## TURN {env.turns} - PLAYER 1",file=open(output_file_verbose, "a"))
                for throw_num in range(1,4): # from 1 to 3
                    env.aiming_for, env.aiming_for_mult = env.decide_target()

                    reward, next_state, done = env.step(action=env.aiming_for,
                                                        action_mult=env.aiming_for_mult,
                                                        player=env.player)
                    total_reward_p1 += reward[1]                                                        

                    step_result = [e,env.turns,env.player,throw_num,env.aiming_for,env.aiming_for_mult,env.dart_score,env.dart_score_mult]
                    throw_history.append(step_result) 

                    if env.verbose == 1:
                        print(str(env.dart_score)+"*"+str(env.dart_score_mult)+' ('+env.comment+") - Reward: "+str(np.round(reward[env.player],2)))
                        print(str(env.dart_score)+"*"+str(env.dart_score_mult)+' ('+env.comment+") - Reward: "+str(np.round(reward[env.player],2)),file=open(output_file_verbose, "a")) 
                    else:
                        print(str(env.dart_score)+"*"+str(env.dart_score_mult)+' ('+env.comment+") - Reward: "+str(np.round(reward[env.player],2)),file=open(output_file_verbose, "a"))                                                
                    if done==1:
                        print(f"Episode: {e}/{episode} \t Agent Reward: {total_reward_agent:.2f} \t Agent Score: {env.current_score[0][0]:.2f} \t P1 Reward: {total_reward_p1:.2f}      P1 Score: {env.current_score[1][0]:.2f}      Winner: P1")
                        print(f"Episode: {e}/{episode} \t Agent Reward: {total_reward_agent:.2f} \t Agent Score: {env.current_score[0][0]:.2f} \t P1 Reward: {total_reward_p1:.2f}      P1 Score: {env.current_score[1][0]:.2f}      Winner: P1", file=open(output_file_verbose, "a"))
                        print(f"Episode: {e}/{episode} \t Agent Reward: {total_reward_agent:.2f} \t Agent Score: {env.current_score[0][0]:.2f} \t P1 Reward: {total_reward_p1:.2f}      P1 Score: {env.current_score[1][0]:.2f}      Winner: P1", file=open(output_file_episodes, "a"))

                        break   
                env.turns += 1
                # env.print_main_variables()
                if env.verbose == 1:
                    print() 
                    print("",file=open(output_file_verbose, "a"))
                else:
                    print("",file=open(output_file_verbose, "a")) 

                
            

        # if e%10==0:
        # cont = input("Hit ENTER to continue...")    

        loss.append([e,total_reward_agent,env.current_score[0][0],total_reward_p1,env.current_score[1][0]])
        pickle.dump(loss,open('rewards_per_episodes.pkl','wb'))
        
        env_backup = {
            'board': env.board,
            'completed': env.completed,
            'scoring': env.scoring,
            'game_end': env.game_end,
            'num_turns': env.turns,
            'current_score': env.current_score,
            'rewards_per_episode': [e,total_reward_agent,env.current_score[0][0],total_reward_p1,env.current_score[1][0]],
            'throw_history': throw_history
        }

        episode_backup[e] = env_backup

        pickle.dump(episode_backup,open('episode_history.pkl','wb'))

        if e % 50 == 0:
            agent.save_model("models/darts-episode-{}.model".format(e))
            
    agent.save_model("models/success.model")
       
    


if __name__ == '__main__':

    ep = 1000
    train_dqn(ep,verbose=0)
    