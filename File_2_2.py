from DataLoading import *
from costModel import costModel_PW_WU
from CostsCalc import Costs
from allocateCosts import AllocateCost
from Collab_2_1_b_c import collaboration
from compete_2_2 import Competition

import itertools
from tabulate import tabulate
import matplotlib.pyplot as plt 


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

