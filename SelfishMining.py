# Outil de simulation d'un attaque double spend sur bitcoin

#Libraries:
import math
import os
import random as rnd

rnd.seed()

from time import process_time, sleep

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Creation de la classe "blockchain"

class Blockchain:
    """
    classe représentant la blockchain.
    Elle a plusieurs paramètres, un tableau de blocs, la récompense de minage, un mempool
    """
    def __init__(self):
        self.blocks = []
        self.miningReward = 6.3
    
    def __repr__(self):
        return "%s" % self.blocks 

    def addBlock(self):
        self.blocks.append("")

    def getBlocks(self):
        
        return self.blocks

    def modifChain(self, newChain):
        self.blocks = []
        for i in range(0, len(newChain)):
            self.blocks.append(newChain[i])

# Selfish mining attack

def attackCycle(q, connectivite, chaine, NbrCycles):
    blocksMined = 0

    bchainAttaquant = Blockchain()
    tailleInitiale = len(chaine.getBlocks())
    bchainOff = chaine
    
    blockCounterBeforeAdj = 0
    timeToAdj = 0
    miningTime = 600
    duree = 0

    tab_returns = [0]

    tab_duree = [0]
    n = 1
    while n <= NbrCycles:
        ### PREMINING ###
        bchainAttaquant.modifChain(bchainOff.getBlocks()) 
        #Compteur pour connaitre l'ordre de minage (exple: "H mines one block before S validates a second"), représente l'état
        counter = 0
        while True:

            # Ajustement de difficulte
            if (blockCounterBeforeAdj >= 2016):
                miningTime = miningTime * (2016 * 600) / timeToAdj
                timeToAdj = 0
                blockCounterBeforeAdj = 0
                
                tab_duree.append(duree)
                tab_returns.append(blocksMined/duree * 100)
            
            duree += miningTime
            timeToAdj += miningTime
            
            # mining
            resultat = np.random.binomial(1, q)
            if (resultat == 0):
                bchainOff.addBlock()
                blockCounterBeforeAdj += 1
                bchainAttaquant.modifChain(bchainOff.getBlocks()) 


            if(resultat == 1):
                bchainAttaquant.addBlock()
                # if the attackers mines a block, the attack starts
                counter += 1
                break

        ############# DEBUT DE L'ATTAQUE #################
        # S mines on top of the last block of the official blockchain
        # print(len(bchainOff.getBlocks()))
        # print(len(bchainAttaquant.getBlocks()))
        # n+=1
        while True:

            # Difficulty adustment
            if (blockCounterBeforeAdj >= 2016):
                miningTime = miningTime * (2016 * 600) / timeToAdj
                timeToAdj = 0
                blockCounterBeforeAdj = 0
                tab_duree.append(duree)
                tab_returns.append(blocksMined/duree *100)

            duree += miningTime
            timeToAdj += miningTime

            # The attacker mines with a probability q
            resultat = np.random.binomial(1, q)

            ecartEntreChaines = len(bchainAttaquant.getBlocks()) - len(bchainOff.getBlocks())

            # If H mines a block, different scenarios
            if(resultat == 0):
                #scenario 1, H mines first, that is it, end of the cycle

                #scenatio 2, If S mines first but H mines a block before S mines a second one, STATE 0'
                if(counter == 1 & ecartEntreChaines == 1):
                    bchainOff.addBlock()
                    blockCounterBeforeAdj += 1

                    # Competition, 3 solutions: q / connectivite * p / (1- connectivite) * p
                    #the attackers mines on top of his fork
                    if(rnd.random() < q):
                        bchainAttaquant.addBlock()
                        bchainOff.modifChain(bchainAttaquant.getBlocks())
                        blocksMined += 2  # Supposed to be + 2
                        n += 1
                        # counter = 0

                        break
                    else:
                        #honest mine on top of attackers' fork
                        if(rnd.random() < (connectivite)*(1- q)):
                            bchainOff.modifChain(bchainAttaquant.getBlocks())
                            blocksMined += 1  # Supposed to be + 1

                            bchainOff.addBlock()
                            duree += miningTime
                            
                            # counter = 0
                            n += 1
                            break
                        #honest mine on honest chain
                        else:
                            bchainOff.addBlock()
                            # counter = 0
                            n += 1
                            break

                if(counter == 2 & ecartEntreChaines == 2):
                    bchainOff.addBlock()
                    blockCounterBeforeAdj += 1

                    bchainOff.modifChain(bchainAttaquant.getBlocks())
                    blocksMined += 2
                    n +=1
                    break

                # if(counter > 2):
                #     bchainOff.addBlock()
                #     blockCounterBeforeAdj += 1
                #     counter -= 1
                # If len(Attacker Fork) - len(Official fork) >=2 and if H mines a block
                # the attacker publishes its fork
                if(ecartEntreChaines > 2):
                    bchainOff.addBlock()
                    blockCounterBeforeAdj += 1
                    tailleOff = len(bchainOff.getBlocks())
                    bchainOff.modifChain(bchainAttaquant.getBlocks()[0:tailleOff-1])
                    blocksMined += 1
                    counter -=1
                    
                    

            
            if(resultat == 1):
                bchainAttaquant.addBlock()
                # if(counter >= 2):
                #     blocksMined +=1
                counter += 1
        
        tab_duree.append(duree)
        tab_returns.append(blocksMined/duree * 100)

        
    # return blocksMined/duree * 100, duree, len(bchainOff.getBlocks())
    return tab_returns, tab_duree
    
def CreationChart(tab1, tab2):

    # fig = go.Figure(data=go.Scatter(x=dataframe.index, y=dataframe['Sentiment'], name="Sentiment"))
    # if(len(args) != 0):
    #     fig2 = go.Figure(data=go.Scatter(x=args[0]['Date'], y=args[0]['Dernier'], name="Bitcoin price"))
    fig = go.Figure(go.Scatter(x=tab2, y=tab1, name="rewards"))

    fig.show()

def Attaque():
    
    bitcoin = Blockchain()
    # print(attackCycle(0.6, 0.3, bitcoin, 5)

    (tab1, tab2) = attackCycle(0.6, 0.3, bitcoin, 20)
    print(tab1)
    print()
    
    print(tab2)
    
    CreationChart(tab1, tab2)



Attaque()
