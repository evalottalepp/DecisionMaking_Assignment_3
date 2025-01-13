from DataLoading import *
from InitialCostModel import costModel_complete
from Initial_Cost_Model_simple import costModel_PW_WU
from CostsCalc import Costs

demandData = demandFile('./given_data/demanddata.xlsx')
vCost = varCost('./given_data/variablecosts.xlsx')
fCost = fixedCost('./given_data/fixedcosts.xlsx') 
# demandData.printFile()

demandData

costs = {}

for u in demandData.U:
    simpleModel = costModel_PW_WU(
        W = demandData.W[:2],  
        P = demandData.P,
        cap = demandData.capacity,
        U = [u],   
        K = demandData.K,
        c = vCost.varCost,
        f = fCost.fixedCost,
        demand = demandData.demand,
        supply = demandData.supply
    )

    model  = simpleModel.model()

    costs[f'Univserity {u}'] = model.objVal

totalcost = 0
for item in costs.values():
    totalcost += item

costs[f'Sum of Costs'] = totalcost

simpleModel = costModel_PW_WU(
    W = demandData.W[:2],  
    P = demandData.P,
    cap = demandData.capacity,
    U = demandData.U,   
    K = demandData.K,
    c = vCost.varCost,
    f = fCost.fixedCost,
    demand = demandData.demand,
    supply = demandData.supply
)

model  = simpleModel.model()
costs[f'All University'] = model.objVal


for key, value in costs.items():
    print(key,round(value,0))