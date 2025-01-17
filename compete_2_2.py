from profitModel import profitModels

from DataLoading import *
from InitialCostModel import costModel_complete
from Initial_Cost_Model_simple import costModel_PW_WU
from CostsCalc import Costs
from allocateCosts import allocateCost
import time

class competition():
    def __init__(self):
        
        self.demandData = demandFile('./given_data/demanddata.xlsx')
        self.demand = self.demandData.demand
        self.vCost = varCost('./given_data/variablecosts.xlsx')
        self.fCost = fixedCost('./given_data/fixedcosts.xlsx') 
        # demandData.printFile()

    def bestResponse(self):
        
        UB_profit, SE_profit = 0,0
        UB_warehouse, SE_warehouse = self.demandData.W[:2],self.demandData.W[2:]

        ##### UB Going First

        initial_UB = self.runModel(self.demand,UB_warehouse)
    
        UB_profit_old = UB_profit
        UB_profit = initial_UB[0]
        SE_profit_old = 0

        counter = 0
        
        while ((UB_profit_old != UB_profit) and (SE_profit_old != SE_profit)) or (counter<10):
            print(counter)

            CHECK= self.runModel(self.demand,UB_warehouse)

            counter +=1
        ##### SE First




    def runModel(self,givenDemand,warehouses):
        profitModel = profitModels(
                                        W = warehouses,  ## Removes the cross docks
                                        P = self.demandData.P,
                                        cap = self.demandData.capacity,
                                        U = self.demandData.U,   ## Change this to which universities you want, give it a list
                                        K = self.demandData.K,
                                        c = self.vCost.varCost,
                                        f = self.fCost.fixedCost,
                                        demand = givenDemand,
                                        supply = self.demandData.supply
                                    )
    
        model  = profitModel.model()

        newStrat = self.updateStrat(model)
        newDemand = self.updateDemand(newStrat)

        profit = model.objVal

        return [profit,newStrat,newDemand]



        # print(demandData.demand)
    def updateStrat(self,model):
        newDemand = self.demand.copy()

        strat = np.zeros_like(newDemand)
        deliveringToU = []
        for w,u,k in model.x_wu_values.keys(): 
            index = [u,k]
            if index not in deliveringToU:
                deliveringToU.append([u,k])
            strat[u,k] = 1
        return strat

    def updateDemand(self,strat):
        halving = np.ones_like(self.demand) * 0.5
        newDemand = strat * halving     ### might need to floor the numbers so no half book
        return newDemand

