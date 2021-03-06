# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 22:06:17 2018
@author: Ole
"""

import retro
import numpy as np
import cv2 
import neat
import pickle

all_level = ['GreenHillZone.Act1',
             'GreenHillZone.Act2',
             'GreenHillZone.Act3',
             'LabyrinthZone.Act1',
             'LabyrinthZone.Act2',
             'LabyrinthZone.Act3',
             'MarbleZone.Act1',
             'MarbleZone.Act2',
             'MarbleZone.Act3',
             'ScrapBrainZone.Act1',
             'ScrapBrainZone.Act2',
             'SpringYardZone.Act1',
             'SpringYardZone.Act2',
             'SpringYardZone.Act3',
             'StarLightZone.Act1',
             'StarLightZone.Act2',
             'StarLightZone.Act3']
   
env = retro.make('SonicTheHedgehog-Genesis', 'GreenHillZone.Act1')

imgarray = []

xpos_end = 0

def eval_genomes(genomes, config):

    for genome_id, genome in genomes:
        ob = env.reset()

        inx, iny, inc = env.observation_space.shape

        inx = int(inx/8)
        iny = int(iny/8)
            
        saved_nn = pickle.load( open( "solutions/GreenHillZone/Act1/solution_002.pkl", "rb" ) )
    
        net = neat.nn.recurrent.RecurrentNetwork.create(saved_nn, config)
        
        current_max_fitness = 0
        fitness_current = 0
        frame = 0
        counter = 0
        done = False
        
        # self-made
        
        xpos = 0
        xpos_tmp = 0
        
        xpos_start = 0
        
        xpos_check = 0
        
        ring_counter = 0
        time = 0
        
        # end
        while not done:
            env.render()
            frame += 1
            ob = cv2.resize(ob, (inx, iny))
            ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY)
            ob = np.reshape(ob, (inx,iny))

            imgarray = np.ndarray.flatten(ob)

            nnOutput = net.activate(imgarray)
            
            ob, rew, done, info = env.step(nnOutput)
            
            # self-made
            
            time += 1
            
            xpos = int(info['screen_x'])
            
            if xpos >= info['screen_x_end'] and xpos > 0:
                fitness_current += 100000
                done = True
                print("Level geschafft!")
            
            if xpos_start == 0:
                xpos_start = xpos
            
            if time % 10 == 0:
                if xpos > xpos_tmp:
                    rew += 1
                xpos_tmp = xpos
            
            if ring_counter < int(info['rings']):
                ring_counter += 1
                rew += 10
                
            if time == 250:
                if xpos <= xpos_start:
                    rew -= 100
                xpos_start = xpos
                    
            # end    
                
            fitness_current += rew
            
            if fitness_current > current_max_fitness:
                current_max_fitness = fitness_current
                counter = 0
            else:
                counter += 1
                
            if done or counter == 250:
                done = True
                print(genome_id, fitness_current)
                
            genome.fitness = fitness_current
            
            # self-made
            
            if time == 250:
                if xpos_check == 0:
                    xpos_check == xpos
                else:
                    if xpos <= xpos_check:
                        done = True
                
                time = 0
                
            # end

                
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforward.txt')

p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)
p.add_reporter(neat.Checkpointer(10))

winner = p.run(eval_genomes)

env.close()