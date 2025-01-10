import pandas as pd
import numpy as np


class demandFile():
    def __init__(self,path):
        self.demandFile = pd.read_excel(path)
        
        supplyDemandCap = self.demandFile
        supplyCols = [col for col in supplyDemandCap if col.startswith('Supply')]
        demandCols = [col for col in supplyDemandCap if col.startswith('Demand')]

        self.currentIndex = 0

        self.supply = supplyDemandCap[supplyCols ].dropna(axis=0, how='all').fillna(0).to_numpy()
        self.P = [i for i in range(len(self.supply))]
        self.currentIndex += len(self.supply)

        self.capacity = supplyDemandCap[~supplyDemandCap['Capacity'].isna()].dropna(axis=1)['Capacity'].fillna(0).to_numpy()
        self.W = [i for i in range(self.currentIndex,self.currentIndex + len(self.capacity))]
        self.currentIndex += len(self.capacity)
        self.capacity = np.concatenate((np.zeros(len(self.supply)), self.capacity))

        self.demand = supplyDemandCap[demandCols].dropna(axis=0, how='all').to_numpy()
        self.U = [i for i in range(self.currentIndex,self.currentIndex + len(self.demand))]

        self.demand = np.concatenate((np.zeros([len(self.capacity),len(self.demand[0])]), self.demand))

        self.K = [i for i in range(len(self.demand[0]))]

        
        
    

    def printFile(self):
        print(self.demandFile)

class fixedCost():
    def __init__(self,path):
        self.fixedCost = pd.read_excel(path).to_numpy()

class varCost():
    def __init__(self,path):
        self.varCost = pd.read_excel(path).to_numpy()
    def __repr__(self):
        return print(self.varCost)
    def __str__(self):
        return 'file'
        
   
