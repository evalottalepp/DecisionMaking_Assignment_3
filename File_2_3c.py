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