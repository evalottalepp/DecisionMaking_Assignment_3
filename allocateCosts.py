from itertools import permutations
import pandas as pd
from DataLoading import *
from InitialCostModel import costModel_complete
from Initial_Cost_Model_simple import costModel_PW_WU
from CostsCalc import Costs



class allocateCost():
    def __init__(self,U):
        self.U = U
        self.allPermutations = list(permutations(U))

        self.costDict = {}
        for item in self.allPermutations:
            self.costDict[str(item)] = {key : 0 for key in U}
        
        self.marginalTable = pd.DataFrame(self.costDict).transpose()

        self.demandData = demandFile('./given_data/demanddata.xlsx')
        self.vCost = varCost('./given_data/variablecosts.xlsx')
        self.fCost = fixedCost('./given_data/fixedcosts.xlsx') 

        self.shapleyValues = self.getShapleyValues()

    def permutationCosts(self):
        
        for permutation in self.allPermutations:
            permutationCost = 0
            marginalDict = {}
            for i in range(len(permutation)):
                intermeditateU = list(permutation[:i+1])
                simpleModel = costModel_PW_WU(
                                                W = self.demandData.W[:2],  ## Removes the cross docks
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

                self.marginalTable.loc[str(permutation),columnUniv] = int(marginal)

        self.meanMarginals = self.marginalTable.mean(axis=0).to_dict()
            
    def allUniversityCost(self):
        self.totalDict = {}
        for u in self.U:
                    simpleModel = costModel_PW_WU(
                                                W = self.demandData.W[:2],  ## Removes the cross docks
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
                    self.totalDict[u] = cost
    
    def getShapleyValues(self):
        self.permutationCosts()
        self.allUniversityCost()

        shapleyValues = {}
        for u in self.U:
            marginal = self.meanMarginals[u]
            aloneCost = self.totalDict[u]

            saving = aloneCost - marginal
            shapleyValues[u] = saving
        return shapleyValues
        

        



        
        