from DataLoading import *
from InitialCostModel import costModel_complete
from Initial_Cost_Model_simple import costModel_PW_WU
from CostsCalc import Costs
from allocateCosts import allocateCost
from Collab_2_1_b_c import collaboration
from compete_2_2 import Competition
import time

demandData = demandFile('./given_data/demanddata.xlsx')
vCost = varCost('./given_data/variablecosts.xlsx')
fCost = fixedCost('./given_data/fixedcosts.xlsx') 
# demandData.printFile()

# start = time.time()

simpleModel = costModel_PW_WU(
    W = demandData.W[:2],  ## Removes the cross docks
    P = demandData.P,
    cap = demandData.capacity,
    U = demandData.U,   ## Change this to which universities you want, give it a list
    K = demandData.K,
    c = vCost.varCost,
    f = fCost.fixedCost,
    demand = demandData.demand,
    supply = demandData.supply
)


model  = simpleModel.model()


simpleModel.summarize_results()

#simpleModel.visualize_results()
simpleModel.visualize_network(model)

# end = time.time()

# print(f'Time for Model: {(end-start)}')

# modelCosts = Costs(simpleModel)

# uniCosts = pd.DataFrame(modelCosts.U_Costs).transpose()
# uniCosts.columns = ['Total Cost', 'Printer To Warehouse', 'Warehouse to University']

# print(uniCosts)
# print(f'Total Costs from all Universities = {round(uniCosts["Total Cost"].sum(),0)}')
# print(f'Total Model Costs = {round(modelCosts.modelCost,0)}')


## 1.2 Allocate Costs ##

# shapleyValues_UB = allocateCost(demandData.U)
# print(shapleyValues_UB.shapleyValues)


## 2.1 Collaboration ##

#shapelys = collaboration(demandData,vCost,fCost)


# 2.2 Competition ##

# bestResponse = Competition()
# bestResponse.bestResponseUBFirst()
