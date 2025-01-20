from DataLoading import *
from InitialCostModel import costModel_complete
from Initial_Cost_Model_simple import costModel_PW_WU
from CostsCalc import Costs
from allocateCosts import AllocateCost
from Collab_2_1_b_c import collaboration
from compete_2_2 import Competition
import time
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
model_UB.summarize_results()

model_UB.visualize_network(model)

"""
1.2a - COMPARE INDIVIDUAL UNIVERSITIES WITH THE SOLUTION OF ALL UNIVERSITIES
"""
U = model_UB.U
modelCosts = Costs(model_UB)
uni_costs = {key: 0 for key in U}
for u in U:
    obj = modelCosts.calculateCostPerUniversity(u)
    uni_costs[u] = obj

modelCosts.costs_per_uni = uni_costs


uni_numbers = [key for key in uni_costs]
uni_values = [uni_costs[key] for key in uni_numbers]
uni_numbers = [model_UB.map_pwu(num) for num in uni_numbers]
total_cost = model.objVal
average_cost = total_cost / len(uni_numbers)

# Plotting the single university costs and comparing them to total_cost*0.2 (i.e. expected average)
plt.rcParams.update({'font.size': 16})

plt.figure(figsize=(10,6))
bars = plt.bar(uni_numbers, uni_values, color='skyblue', label='Cost per Customer', width=0.5)
plt.axhline(y=average_cost, color='red', linestyle='--', linewidth=2, label=f'Average Cost ({average_cost:.2f})')

for bar, cost in zip(bars, uni_values):
    deviation = cost - average_cost
    deviation_label = f'{cost:.2f} ({deviation:+.2f})'
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5, deviation_label, 
             ha='center', va='bottom', fontsize=10, color='black')

plt.xlabel('University')
plt.ylabel('Cost')
plt.xticks(uni_numbers, fontsize=12)
plt.yticks(fontsize=12)

ax = plt.gca()

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.legend(fontsize=12)

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('figures/universities_of_total.png')
plt.show()

model_UB.set_U(U)

"""
# 1.2c - Fairly distribute savings accross all universities
# """
# def distributeCosts(company, model):
#     shapleyValues = AllocateCost(demandData.U, company)
#     print(shapleyValues.shapleySavings)

#     data = pd.DataFrame({
#         "University": [model.map_pwu(u) for u in demandData.U],
#         "Initial Cost": list(shapleyValues.aloneCosts.values()),
#         "Shapley Cost": list(shapleyValues.shapleyCosts.values())
#     })
#     data["Savings"] = data["Initial Cost"] - data["Shapley Cost"]
#     data["% Savings"] = (data["Savings"] / data["Initial Cost"]) * 100

#     print(data.round(2))

#     return data

# UB_costs_table = distributeCosts('UB', model_UB)


# """
# 1.2e - cost allocation for Book Import SE
# """
# model_BI = costModel_PW_WU(
#     W = demandData.W[2:],  # Keep only cross-docks
#     P = demandData.P,
#     cap = demandData.capacity,
#     U = demandData.U,
#     K = demandData.K,
#     c = vCost.varCost,
#     f = fCost.fixedCost,
#     demand = demandData.demand,
#     supply = demandData.supply
# )

# model  = model_BI.model()
# model_BI.summarize_results()

# model_BI.visualize_network(model)

# modelCosts_BI = Costs(model_BI)

# BI_costs_table = distributeCosts('BI', model_BI)


# universities = ["U1", "U2", "U3", "U4", "U5"]

# x = np.arange(len(universities))  # Positions for universities
# width = 0.3  # Width of the bars

# fig, ax = plt.subplots(figsize=(10, 6))

# uni_books = UB_costs_table['Shapley Cost']
# book_import = BI_costs_table['Shapley Cost']
# # Bars for Company A and Company B
# bar1 = ax.bar(x - width/2, uni_books, width, label='Uni Books B.V.', color='skyblue', alpha=0.7)
# bar2 = ax.bar(x + width/2, book_import, width, label='Book Import SE', color='lightcoral', alpha=0.7)

# ax.set_xlabel("University")
# ax.set_ylabel("Shapley Costs")
# ax.set_xticks(x)
# ax.set_xticklabels(universities)
# ax.legend()

# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)

# plt.tight_layout()
# plt.savefig('figures/company_price_comparison.png')
# plt.show()
## 2.1 Collaboration ##

#shapelys = collaboration(demandData,vCost,fCost)


# 2.2 Competition ##

#bestResponse = Competition()
#bestResponse.bestResponseUBFirst()