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

print('---------------1.2c------------------')
def distributeCosts(company, model,printer=False):
    shapleyValues = AllocateCost(model.U, company,printer=printer)
    print(shapleyValues.shapleySavings)

    data = pd.DataFrame({
        "University": [model.map_pwu(u) for u in model.U],
        "Initial Cost": list(shapleyValues.aloneCosts.values()),
        "Shapley Cost": list(shapleyValues.shapleyCosts.values()),
        "Demand": list(sum(model.demand[u]) for u in model.U)
    })
    data["Savings"] = data["Initial Cost"] - data["Shapley Cost"]
    data["% Savings"] = (data["Savings"] / data["Initial Cost"]) * 100

    print(data.round(2))

    return data

UB_costs_table = distributeCosts('UB', model_UB,printer=True)   ### We did not want to print all these values but it was requested in the question
