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

result ={}
bestResponse = Competition()

UB_First = bestResponse.bestResponse(bestResponse.demandData.W[:2],whoFirst='UB')
SE_First = bestResponse.bestResponse(bestResponse.demandData.W[:2],whoFirst='SE')

UB_First = [round(x) for x in UB_First]
SE_First= [round(x) for x in SE_First]

result['Compitition Case'] = [UB_First,SE_First]

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