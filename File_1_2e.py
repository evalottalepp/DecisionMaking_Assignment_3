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


# """
# 1.2e - cost allocation for Book Import SE
# """
print('---------------1.2e------------------')
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


model  = model_BI.model()
# model_BI.summarize_results()

# model_BI.visualize_network(model)

modelCosts_BI = Costs(model_BI)

BI_costs_table = distributeCosts('BI', model_BI)


universities = ["U1", "U2", "U3", "U4", "U5"]

x = np.arange(len(universities))  # Positions for universities
width = 0.3  # Width of the bars

fig, ax = plt.subplots(figsize=(10, 6))

uni_books = UB_costs_table['Shapley Cost']
book_import = BI_costs_table['Shapley Cost']
# Bars for Company A and Company B
bar1 = ax.bar(x - width/2, uni_books, width, label='Uni Books B.V.', color='skyblue', alpha=0.7)
bar2 = ax.bar(x + width/2, book_import, width, label='Book Import SE', color='lightcoral', alpha=0.7)

ax.set_xlabel("University")
ax.set_ylabel("Shapley Costs")
ax.set_xticks(x)
ax.set_xticklabels(universities)
ax.legend()

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('figures/company_price_comparison.png')
plt.show()
