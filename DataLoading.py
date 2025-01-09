import pandas as pd


class demandFile():
    def __init__(self,path):
        self.demandFile = pd.read_excel(path)
        
        supplyDemandCap = self.demandFile
        supplyCols = [col for col in supplyDemandCap if col.startswith('Supply')]
        demandCols = [col for col in supplyDemandCap if col.startswith('Demand')]

        self.supply = supplyDemandCap[supplyCols ].dropna(axis=0, how='all')
        self.capacity = supplyDemandCap[~supplyDemandCap['Capacity'].isna()].dropna(axis=1)
        self.demand = supplyDemandCap[demandCols].dropna(axis=0, how='all')
        
    

    def printFile(self):
        print(self.demandFile)

class fixedCost():
    def __init__(self,path):
        self.fixedCost = pd.read_excel('fixedcosts.xlsx')

class varCost():
    def __init__(self):
        self.varCost = pd.read_excel('variablecosts.xlsx')
        
