from DataLoading import *
from InitialCostModel import costModel_complete
from Initial_Cost_Model_simple import costModel_PW_WU
from CostsCalc import Costs
from allocateCosts import allocateCost
from Collab_2_1_b_c import collaboration
from compete_2_2 import Competition
import time
import matplotlib.pyplot as plt

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

"""
1.2a - COMPARE INDIVIDUAL UNIVERSITIES WITH THE SOLUTION OF ALL UNIVERSITIES
"""
U = simpleModel.U
uni_costs = {key: 0 for key in U + ['Total']}
for u in U:
    simpleModel.set_U([u])
    model_one_uni = simpleModel.model()
    obj = model_one_uni.ObjVal
    uni_costs[u] = obj

uni_costs['Total'] = model.objVal

uni_numbers = [key for key in uni_costs if isinstance(key, int)]
uni_values = [uni_costs[key] for key in uni_numbers]
uni_numbers = [simpleModel.map_pwu(num) for num in uni_numbers]
total_cost = uni_costs['Total']
average_cost = total_cost / len(uni_numbers)

# Plotting
plt.figure(figsize=(10,5))

# Bar plot for university costs
bars = plt.bar(uni_numbers, uni_values, color='skyblue', label='Cost per Customer')

# Dashed line for average cost
plt.axhline(y=average_cost, color='red', linestyle='--', linewidth=2, label=f'Average Cost ({average_cost:.2f})')

# Add data labels for deviation
for bar, cost in zip(bars, uni_values):
    deviation = cost - average_cost
    deviation_label = f'{cost:.2f} ({deviation:+.2f})'
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5, deviation_label, 
             ha='center', va='bottom', fontsize=10, color='black')

# Adding labels and title
plt.xlabel('University', fontsize=12)
plt.ylabel('Cost', fontsize=12)
plt.xticks(uni_numbers, fontsize=10)
plt.yticks(fontsize=10)

ax = plt.gca()

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.legend(fontsize=10)

# Show grid for better visualization
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show the plot
plt.tight_layout()
plt.savefig('figures/universities_of_total.png')
plt.show()
# simpleModel.set_U(U)
# # simpleModel.summarize_results()

# #simpleModel.visualize_results()
# simpleModel.visualize_network(model)

# end = time.time()

# print(f'Time for Model: {(end-start)}')

# modelCosts = Costs(simpleModel)

# uniCosts = pd.DataFrame(modelCosts.U_Costs).transpose()
# uniCosts.columns = ['Total Cost', 'Printer To Warehouse', 'Warehouse to University']

# print(uniCosts)
# print(f'Total Costs from all Universities = {round(uniCosts["Total Cost"].sum(),0)}')
# print(f'Total Model Costs = {round(modelCosts.modelCost,0)}')


# # 1.2 Allocate Costs ##

# shapleyValues_UB = allocateCost(demandData.U)
# print(shapleyValues_UB.shapleyValues)


## 2.1 Collaboration ##

#shapelys = collaboration(demandData,vCost,fCost)


# 2.2 Competition ##

bestResponse = Competition()
bestResponse.bestResponseUBFirst()