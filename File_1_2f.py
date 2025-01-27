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


model_BI = costModel_PW_WU(
    W = demandData.W[2:],  # Keep only cross-docks
    P = demandData.P,
    cap = demandData.capacity,
    U = demandData.U,
    K = demandData.K,
    c = vCost.varCost,
    f = fCost.fixedCost,
    demand = demandData.demand,
    supply = demandData.supply
)

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


print('---------------1.2f------------------')
BI_customers = [10, 12] # Universities U3 and U5
UB_customers = [8, 9, 11] # Universities U1, U2 and U4

model_BI.set_U(BI_customers)
model_UB.set_U(UB_customers)

model_gurobi_BI = model_BI.model()
mode_gurobi_UB = model_UB.model()

#model_BI.visualize_network(model_gurobi_BI)
#model_UB.visualize_network(mode_gurobi_UB)

modelCosts_BI = Costs(model_BI)

BI_costs_table = distributeCosts('BI', model_BI)

modelCosts_UB = Costs(model_UB)

UB_costs_table = distributeCosts('UB', model_UB)

shapleyValues_UB = AllocateCost(demandData.U,company='UB')
print(f'Shapley Values of : {shapleyValues_UB.getShapleyValues()}')
