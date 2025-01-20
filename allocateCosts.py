from itertools import permutations
import pandas as pd
from DataLoading import *
from InitialCostModel import costModel_complete
from Initial_Cost_Model_simple import costModel_PW_WU
from CostsCalc import Costs



class AllocateCost:
    # Company is either 'UB' - Uni Books or 'BI' - Book Import. It is used to understand which warehouses to utilize.
    def __init__(self,U,company):
        self.U = U
        self.company = company
        self.allPermutations = list(permutations(U))

        self.costDict = {}
        for item in self.allPermutations:
            self.costDict[str(item)] = {key : 0 for key in U}
        
        self.marginalTable = pd.DataFrame(self.costDict).transpose()

        self.demandData = demandFile('./given_data/demanddata.xlsx')
        self.vCost = varCost('./given_data/variablecosts.xlsx')
        self.fCost = fixedCost('./given_data/fixedcosts.xlsx') 

        self.shapleySavings = self.getShapleyValues()

    def permutationCosts(self):
        
        if self.company == 'UB':
            warehouses = self.demandData.W[:2]
        else: 
            warehouses = self.demandData.W[2:]
        for permutation in self.allPermutations:
            permutationCost = 0
            marginalDict = {}
            for i in range(len(permutation)):
                intermeditateU = list(permutation[:i+1])
                simpleModel = costModel_PW_WU(
                                                W = warehouses,  ## Removes the cross docks
                                                P = self.demandData.P,
                                                cap = self.demandData.capacity,
                                                U = intermeditateU,   ## Change this to which universities you want, give it a list
                                                K = self.demandData.K,
                                                c = self.vCost.varCost,
                                                f = self.fCost.fixedCost,
                                                demand = self.demandData.demand,
                                                supply = self.demandData.supply
                                            )
                
                interModel = simpleModel.model()
                cost = interModel.objVal

                marginal = cost - permutationCost
                print(f'{permutation}: {intermeditateU}, CurrentCost:{int(cost)}, Previous Cost:{int(permutationCost)},marginal: {int(marginal)}')
                permutationCost  = cost

                columnUniv = permutation[i]

                self.marginalTable.loc[str(permutation),columnUniv] = marginal

        self.shapleyCosts = self.marginalTable.mean(axis=0).to_dict()
            
    def allUniversityCost(self):
        self.aloneCosts = {}
        if self.company == 'UB':
            warehouses = self.demandData.W[:2]
        else: 
            warehouses = self.demandData.W[2:]
        for u in self.U:
            simpleModel = costModel_PW_WU(
                                        W = warehouses,
                                        P = self.demandData.P,
                                        cap = self.demandData.capacity,
                                        U = [u],   ## Change this to which universities you want, give it a list
                                        K = self.demandData.K,
                                        c = self.vCost.varCost,
                                        f = self.fCost.fixedCost,
                                        demand = self.demandData.demand,
                                        supply = self.demandData.supply
                                    )
            model = simpleModel.model()
            cost = model.objVal
            self.aloneCosts[u] = cost
    
    def getShapleyValues(self):
        self.permutationCosts()
        self.allUniversityCost()

        print("Shapley costs: ", self.shapleyCosts)
        savings = {}
        for u in self.U:
            marginal = self.shapleyCosts[u]
            aloneCost = self.aloneCosts[u]

            saving = aloneCost - marginal
            savings[u] = saving
        return savings
        

        



        
        