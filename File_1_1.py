from DataLoading import *
from costModel import costModel_PW_WU
from CostsCalc import Costs
from allocateCosts import AllocateCost
from Collab_2_1_b_c import collaboration
from compete_2_2 import Competition

import itertools
from tabulate import tabulate
import matplotlib.pyplot as plt 

demandData = demandFile('./given_data/demanddata.xlsx')
vCost = varCost('./given_data/variablecosts.xlsx')
fCost = fixedCost('./given_data/fixedcosts.xlsx') 
# demandData.printFile()

model_UB = costModel_PW_WU(
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


model  = model_UB.model()

model_UB.visualize_network(model)

modelCosts = Costs(model_UB)

uniCosts = pd.DataFrame(modelCosts.U_Costs).transpose()
uniCosts.columns = ['Total Cost', 'Printer To Warehouse', 'Warehouse to University']

print(uniCosts)
print(f'Total Costs from all Universities = {round(uniCosts["Total Cost"].sum(),0)}')
print(f'Total Model Costs = {round(modelCosts.modelCost,0)}')