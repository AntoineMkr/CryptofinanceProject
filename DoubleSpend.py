# Outil de simulation d'un attaque double spend sur bitcoin

#Libraries:
import math
import os
import random
# Pour l'interface graphique
import tkinter
import matplotlib.pyplot as plt
import numpy as np
# To display curves in the GUI
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings
from matplotlib.figure import Figure


#Creation de la classe "blockchain"
class Blockchain:
    """
    classe représentant la blockchain.
    Elle a plusieurs paramètres, un tableau de blocs, la récompense de minage, un mempool
    """
    
    def __init__(self):
        """
        Initilisation des instances, deux param: mempool et liste de blocs
        """
        self.blocks = []
        self.mempool = []
    

    def __repr__(self):
        """
        Ce qui est affiché si l'ont print une instance
        """
        return "%s" %(self.blocks) 

    def addTxinMempool(self, tx):
        """
        pour ajouter des transactions dans le mempool
        """
        self.mempool.append(tx)

    def addBlock(self):
        """
        pour ajouter un bloc dans la blockchain
        """
        self.blocks.append(self.mempool)
        self.mempool = []

    def getBlocks(self):
        """
        pour obtenir la liste des blocs
        """
        return self.blocks
    
    def modifChain(self, newChain):
        """
        pour modifier la blockchain (par exemple si l'attaquant publie sa chaine, la blockchain officielle devient celle de l'attaquant)
        """
        self.blocks = []
        for i in range(0, len(newChain)):
            self.blocks.append(newChain[i])


# double spend attack
def attackCycle(q, z, A, v, btc, btcAttacker, NbrCycles):
    """
    Fonction pour simuler une attaque à la double dépense.
    plusieurs params: 
    q = hashrate de l'attaquant
    z = nombre de confirmations
    A = délai maximum accepté par l'attaquant
    v = montant de la double dépense
    btc = instance de la classe blockchain, blockchain officielle
    btcAttacker = instante de la classe blockchain, blockchain de l'attaquant
    NbrCycle = nbr de cycles d'attaque
    """

    NbAttaques = 0
    #Nombre d'attaques réussies
    attaquesReussies = 0
    #Nombres de blocs minés par l'attaquant
    blockMined = 0
    #Gains
    gains = 0
    #Durée de l'attaque
    dureeAttaque = 1 / q

    while NbAttaques < NbrCycles:
        
        btc.modifChain([])
        btcAttacker.modifChain([])

        NbAttaques += 1

        #PREMINAGE- ETAPE 0
        counterBlocks = 0
        diffBlocks = 0

        # ETAPE 1

        # achat d'un bien = tx
        btc.addTxinMempool("tx")

        btcAttacker.addTxinMempool("txA")

        # Mineurs honnetes minent normalement
        while True:
            #Minage simulé par une loi binomiale. L'attaquant a une proba q de miner un bloc
            res = np.random.binomial(1, q)
            dureeAttaque +=1

            if(res == 1):
                # aucun bloc de A ne contient tx mais contient txA en conflit
                btcAttacker.addBlock()

            else:
                # un bloc miné par H contient tx
                btc.addBlock()
                counterBlocks +=1

            diffBlocks = len(btc.getBlocks()) - len(btcAttacker.getBlocks())
            
            #Si on atteint z confirmations ou que la limite A est atteinte, le bien est envoyé
            if(counterBlocks >= z or (diffBlocks >= A)):
                counterBlocks = 0
                break 
        
        #Si la chaine de l'attaquant est inférieure à la chaine officielle & que le délai est encore acceptable
        if((len(btcAttacker.getBlocks()) < len(btc.getBlocks())) & (diffBlocks < A)):

            while True:
                res = np.random.binomial(1, q)
                dureeAttaque += 1

                #L'attauqant mine toujours en secret
                if(res == 1):
                    
                    btcAttacker.addBlock()

                #les honnetes minent toujours normalement.
                else:
                    btc.addBlock()

                # calcul de la différence de longueur entre les deux chaines
                diffBlocks = len(btc.getBlocks()) - len(btcAttacker.getBlocks())
                
                #Si la chaine de l'attaquant devient plus longue que la chaine officielle ou si le délai devient trop grand
                if((diffBlocks < 0) or diffBlocks >= A):
                    break 
        
        #Si l'attaquant mine une blokchain plus longue que l'officielle:
        if (len(btcAttacker.getBlocks()) > len(btc.getBlocks())):

            attaquesReussies +=1
            blockMined += len(btcAttacker.getBlocks())
            #l'attaquant publie sa blockchain qui devient officielle
            btc.modifChain(btcAttacker.getBlocks())

            gains = v + blockMined

        #gains par unité de temps
        EsperanceGains = gains / dureeAttaque

    return EsperanceGains

def calculateRatiosForListOfHashrates(z, v, A, NbrCycles):
    # liste de hashrate, doit aller de 0.01 à 1
    listeDeHashrate = [0] * 100
    # lsite qui contient les esperances de gains
    listeEsperanceGains = [0] * 100

    # création des deux instances de Blockchain()
    bitcoin = Blockchain()
    bicoinAttaquant = Blockchain()
    
    for idx in range(1,100):
        #l'attaque est générée pour chaque idx représentant q, le hashrate de l'attaquant
        listeEsperanceGains[idx] = attackCycle(idx/100, z, A ,v, bitcoin, bicoinAttaquant, NbrCycles)
        listeDeHashrate[idx] = idx/100

    return listeEsperanceGains, listeDeHashrate



#### PARTIE DU CODE CONCERNANT L'INTERFACE GRAPHIQUE ####

root = tkinter.Tk()
root.wm_title("Attaque double dépense")
fig = Figure(figsize=(5, 4), dpi=100)

# To create a canvas for the figure
canvas = FigureCanvasTkAgg(fig, master=root) 
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

# To create a toolbar under the figure
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


#Fonction pour mettre à jour les params.
def simulationDesAttaques(event):

    fig.clear()

    #On génère l'attaque 
    listeEsperanceGains, listeDeHashrate = calculateRatiosForListOfHashrates(z.get(), v.get(), A.get(), nbrAttaques.get())

    #Espérance de gains en fonction du hashrate, concerne l'attaquant
    fig.add_subplot(111).plot(listeDeHashrate, listeEsperanceGains, label='Attaquant')
    #gains des mineurs honnetes, c'est une droite
    fig.add_subplot(111).plot(listeDeHashrate, listeDeHashrate, label='Honnete')
    
    fig.add_subplot(111).legend(loc='best')
    fig.add_subplot(111).set_xlabel('Hashrate')
    fig.add_subplot(111).set_ylabel('Esperance de gain')
    fig.add_subplot(111).set_title('Attaque double dépense')
    canvas.draw()

#Pour créer les "sliders"
z = tkinter.Scale(master=root, from_=0, to=10, orient=tkinter.HORIZONTAL, length=200,
                                        label="z : nbr de confirmations", command=simulationDesAttaques)
z.pack(side=tkinter.LEFT)

nbrAttaques = tkinter.Scale(master=root, from_=1, to=500, orient=tkinter.HORIZONTAL, length=200,
                                  label="n : nbr d'attaquees", command=simulationDesAttaques)
nbrAttaques.pack(side=tkinter.LEFT)

A = tkinter.Scale(master=root, from_=0, to=20, orient=tkinter.HORIZONTAL, length=200,
                                               label="A : délai maximum", command=simulationDesAttaques)
A.pack(side=tkinter.LEFT)

v = tkinter.Scale(master=root, from_=0, to=10, orient=tkinter.HORIZONTAL, length=200,
                                          label="v : taille de la double dépense", command=simulationDesAttaques)
v.pack(side=tkinter.LEFT)

tkinter.mainloop()

