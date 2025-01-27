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

print('---------------1.2d------------------')
U = model_UB.U
all_single_flow_labels = {}
all_single_links = []
for u in U:
    model_UB.set_U([u])
    single_u_model = model_UB.model()
    single_flow_labels = model_UB.visualize_network(single_u_model, plot=False)
    single_links = list(single_flow_labels.keys())
    for key, value in single_flow_labels.items():
        if key in all_single_flow_labels:
            for book_type, count in value.items():
                all_single_flow_labels[key][book_type] = (
                    all_single_flow_labels[key].get(book_type, 0) + count
                )
        else:
            all_single_flow_labels[key] = value
    all_single_links = all_single_links + single_links

model_UB.set_U(U)
coalition_model = model_UB.model()
together_flow_labels = model_UB.visualize_network(coalition_model, plot=False)
together_links = list(together_flow_labels.keys())

# print(all_single_flow_labels)
# print(all_single_links)
# print(together_flow_labels)
# print(together_links)
model_UB.network_comparison(all_single_flow_labels, together_flow_labels, all_single_links, together_links)
