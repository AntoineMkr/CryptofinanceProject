# Outil de simulation d'un attaque double spend sur bitcoin

#Libraries:
import math
import os
import random as rnd
rnd.seed()
import time
# Pour l'interface graphique
import tkinter
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
# To display curves in the GUI
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings
from matplotlib.figure import Figure
from plotly.subplots import make_subplots

#Creation de la classe "blockchain"

class Blockchain:
    """
    classe représentant la blockchain.
    Elle n'a comme variable d'instance qu'un tableau représentant les blocs
    """
    def __init__(self):
        self.blocks = []
    
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
    """
    pour simuler un cycle d'attaque
    q est le hashrate
    """
    blocksMined = 0
    coinbase = 6.25
    bchainAttaquant = Blockchain()
    tailleInitiale = len(chaine.getBlocks())
    bchainOff = chaine
    blockCounterBeforeAdjustment = 0
    timeToAdjustment = 0
    miningTime = 600
    duree = 0
    n = 1
    esperanceGains = 0
    while n <= NbrCycles:
        bchainAttaquant.modifChain(bchainOff.getBlocks()) 

        #Compteur pour connaitre l'ordre de minage (exple: "H mines one block before S validates a second"), représente l'état de l'attaque
        counter = 0

        ############# DEBUT DE L'ATTAQUE #################
        # S mines on top of the last block of the official blockchain

        while True:

            # # Difficulty adustment
            if (blockCounterBeforeAdjustment >= 2016):
                miningTime = miningTime * (2016 * 600) / timeToAdjustment
                timeToAdjustment = 0
                blockCounterBeforeAdjustment = 0

            duree += miningTime
            timeToAdjustment += miningTime

            # The attacker mines with a probability q
            resultat = np.random.binomial(1, q)

            ecartEntreChaines = len(bchainAttaquant.getBlocks()) - len(bchainOff.getBlocks())

            # If H mines a block, different scenarios
            if(resultat == 0):
                if(counter == 0):
                    bchainOff.addBlock()
                    break
                #scenatio 1, If S mines first but H mines a block before S mines a second one, STATE 0'
                if(counter == 1 & ecartEntreChaines == 1):
                    bchainOff.addBlock()
                    blockCounterBeforeAdjustment += 1

                    # Competition, 3 solutions: q / connectivite * p / (1- connectivite) * p
                    #the attackers mines on top of his fork
                    tmp = rnd.random()
                    if(tmp < q):
                        bchainAttaquant.addBlock()
                        bchainOff.modifChain(bchainAttaquant.getBlocks())
                        blocksMined += 2  # Supposed to be + 2
                        n += 1
                        # duree += miningTime

                        break
                    else:
                        #honest mine on top of attackers' fork
                        if(tmp < (connectivite)*(1 - q)):
                            bchainOff.modifChain(bchainAttaquant.getBlocks())
                            blocksMined += 1  # Supposed to be + 1
                            bchainOff.addBlock()
                            # duree += miningTime
                            n += 1
                            break
                        #honest mine on honest chain
                        else:
                            bchainOff.addBlock()
                            n += 1
                            # duree += miningTime
                            break
                #If S mines twice but H mines before the third block, S publishes its fork and earn 2 coinbases                    
                if(counter == 2 & ecartEntreChaines == 2):
                    bchainOff.addBlock()
                    blockCounterBeforeAdjustment += 1
                    bchainOff.modifChain(bchainAttaquant.getBlocks())
                    blocksMined += 2
                    n +=1
                    break

                # If len(Attacker Fork) - len(Official fork) >=2 and if H mines a block
                # the attacker publishes its fork of the size of the honnest chain
                if(ecartEntreChaines > 2):
                    bchainOff.addBlock()
                    blockCounterBeforeAdjustment += 1
                    tailleOff = len(bchainOff.getBlocks())
                    bchainOff.modifChain(bchainAttaquant.getBlocks()[0:tailleOff-1])
                    blocksMined += 1
                    counter -=1
                    
            # the attacker mines another block        
            if(resultat == 1):
                bchainAttaquant.addBlock()
                counter += 1

        esperanceGains = (blocksMined * coinbase)/(duree) 

    return esperanceGains

#### PARTIE DU CODE CONCERNANT L'INTERFACE GRAPHIQUE ####

root = tkinter.Tk()
root.wm_title("Simulation de minage égoïste")
fig = Figure(figsize=(5, 4), dpi=100)

# To create a canvas for the figure
canvas = FigureCanvasTkAgg(fig, master=root) 
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

# To create a toolbar under the figure
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)



def calculateRatiosForListOfHashrates(gamma, NbrCycles):
    # liste de hashrate, doit aller de 0.01 à 1
    listeDeHashrate = [0] * 49
    # lsite qui contient les esperances de gains
    listeEsperanceGains = [0] * 49
    
    for idx in range(1,50):
        #l'attaque est générée pour chaque idx, variable représentant q, le hashrate de l'attaquant
        bitcoin = Blockchain()

        listeEsperanceGains[idx-1] = attackCycle(idx/100, gamma, bitcoin, NbrCycles)
        listeDeHashrate[idx-1] = idx/100

    return listeEsperanceGains, listeDeHashrate

#Fonction pour mettre à jour les params.
def simulationDesAttaques(event):

    fig.clear()
    #On génère l'attaque 
    listeEsperanceGains, listeDeHashrate = calculateRatiosForListOfHashrates(gamma.get()/100, nbrAttaques.get())

    #Espérance de gains en fonction du hashrate, concerne l'attaquant
    fig.add_subplot(111).plot(listeDeHashrate, listeEsperanceGains, label='minage égoïste')
    #gains des mineurs honnetes, c'est une droite
    y1 = [0] * 49
    for i in range(len(y1)):
        y1[i]=(listeDeHashrate[i]*6.25)/600
    fig.add_subplot(111).plot(listeDeHashrate, y1, label='stratégie honnête')
    
    fig.add_subplot(111).legend(loc='best')
    fig.add_subplot(111).set_xlabel('Hashrate')
    fig.add_subplot(111).set_ylabel('Esperance de gain')
    fig.add_subplot(111).set_title('Simulation de minage égoïste')
    canvas.draw()

#Pour créer les "sliders"
gamma = tkinter.Scale(master=root, from_=0,to=100, orient=tkinter.HORIZONTAL, length=200,
                                        label="gamma : divisé par 100. connectivité", command=simulationDesAttaques)
gamma.pack(side=tkinter.LEFT)

nbrAttaques = tkinter.Scale(master=root, from_=1, to=500, orient=tkinter.HORIZONTAL, length=200,
                                  label="n : nbr d'attaques", command=simulationDesAttaques)
nbrAttaques.pack(side=tkinter.RIGHT)

tkinter.mainloop()
