from DataLoading import *
from costModel import costModel_PW_WU
from CostsCalc import Costs
from allocateCosts import AllocateCost
from Collab_2_1_b_c import collaboration
from compete_2_2 import Competition
import time
import itertools
from tabulate import tabulate
import matplotlib.pyplot as plt 

demandData = demandFile('./given_data/demanddata.xlsx')
vCost = varCost('./given_data/variablecosts.xlsx')
fCost = fixedCost('./given_data/fixedcosts.xlsx') 
# demandData.printFile()

print('---------------1.1------------------')

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


## 1.2 Allocate Costs ##

# """
# # 1.2c - Fairly distribute savings accross all universities
# # """
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

# """
# 1.2d - path changes for single university vs coalition
# """
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

# """
# 1.2f - Each university is served by the company offering cheaper costs
# """
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
print(shapleyValues_UB.getShapleyValues())


# ## 2.1 Collaboration ##
print('---------------2.1------------------')

shapelys = collaboration(demandData,vCost,fCost)


# ## 2.2 Competition ##
print('---------------2.2------------------')
print('Profit values are formated as [UB Profit, SE Profit]')
result ={}
bestResponse = Competition()

UB_First = bestResponse.bestResponse(bestResponse.demandData.W[:2],whoFirst='UB')
SE_First = bestResponse.bestResponse(bestResponse.demandData.W[:2],whoFirst='SE')

UB_First = [round(x) for x in UB_First]
SE_First= [round(x) for x in SE_First]

result['Compitition Case'] = [UB_First,SE_First]
print(result)



# # # 2.3 
print('---------------2.3------------------')
# a)

fewerWarehouses = Competition()

for w in fewerWarehouses.demandData.W[:2]:

    UB_First = fewerWarehouses.bestResponse([w],whoFirst='UB')
    SE_First = fewerWarehouses.bestResponse([w],whoFirst='SE')

    UB_First[0] = round(UB_First[0] + 200) 
    SE_First[0] = round(SE_First[0] + 200)

    UB_First = [round(x) for x in UB_First]
    SE_First= [round(x) for x in SE_First]

    result[w] = [UB_First,SE_First]

result = pd.DataFrame(result)
result.columns = ['Base Case','Close Warehouse 0','Close Warehouse 1']

print(result)

# b)
print('---------------2.3b------------------')
differentPrice = {}

changingPrice = Competition()

for price in range(8,48,1):
    price = price/4
    # print(price)
    UB_First = changingPrice.bestResponse(changingPrice.demandData.W[:2],whoFirst='UB',price=price)
    SE_First = changingPrice.bestResponse(changingPrice.demandData.W[:2],whoFirst='SE',price=price)

    UB_First = [round(x) for x in UB_First]
    SE_First= [round(x) for x in SE_First]

    differentPrice[price] = [UB_First,SE_First]

differentPrice = pd.DataFrame(differentPrice).transpose()
differentPrice.columns = ['UB First','SE_First']
print(differentPrice)

prices = differentPrice.index  
profits = differentPrice['UB First'].tolist()  

UB_Profit = [val[0] for val in profits]  
SE_Profit = [val[1] for val in profits]  
max_UB = max(UB_Profit)
max_UB_price = prices[UB_Profit.index(max_UB)]

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(prices, UB_Profit, color='blue', label='UB Profit')
plt.plot(prices, SE_Profit, color='green', label='SE Profit')
plt.axhline(y=max_UB, color='red', linestyle='--', label=f'Max UB Profit (€{round(max_UB)} @ €{round(max_UB_price,2)})')

plt.xlabel('UB Price (€)')
plt.ylabel('Profit (€)')
plt.title('Effect on Profit by Price')
plt.legend()
plt.show()

# c)
print('---------------2.3c------------------')
specificBooks = Competition()

books = specificBooks.demandData.K
bookResult = {}
for r in range(1,len(books)+1):
    # print(r)
    bookSubset = list(itertools.combinations(books,r=r))
    for combination in bookSubset:
        UB_First = specificBooks.bestResponse(specificBooks.demandData.W[:2],whoFirst='UB',UB_Books=combination)
        SE_First = specificBooks.bestResponse(specificBooks.demandData.W[:2],whoFirst='SE',UB_Books=combination)

        UB_First = [round(x) for x in UB_First]
        SE_First= [round(x) for x in SE_First]

        bookResult[str(combination)] = [UB_First,SE_First]

smallerOffer = pd.DataFrame(bookResult).transpose()
smallerOffer.columns = ['UB First','SE_First']
print(tabulate(smallerOffer, 
               headers=["Book Offer", "UB First", "SE_First"]))