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