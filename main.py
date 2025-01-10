from DataLoading import *
from InitialCostModel import costModel_complete
from Initial_Cost_Model_simple import costModel_PW_WU
from CostsCalc import Costs

demandData = demandFile('./given_data/demanddata.xlsx')
vCost = varCost('./given_data/variablecosts.xlsx')
fCost = fixedCost('./given_data/fixedcosts.xlsx') 
# demandData.printFile()

demandData

simpleModel = costModel_PW_WU(
    W = demandData.W,
    P = demandData.P,
    cap = demandData.capacity,
    U = demandData.U,
    K = demandData.K,
    c = vCost.varCost,
    f = fCost.fixedCost,
    demand = demandData.demand,
    supply = demandData.supply
)


model  = simpleModel.model()

# simpleModel.visualize_results()

# simpleModel.summarize_results()

modelCosts = Costs(simpleModel)

uniCosts = pd.DataFrame(modelCosts.U_Costs).transpose()
uniCosts.columns = ['Total Cost', 'Printer To Warehouse', 'Warehouse to University']

print(uniCosts)
print(f'Total Costs from all Universities = {round(uniCosts["Total Cost"].sum(),0)}')
print(f'Total Model Costs = {round(modelCosts.modelCost,0)}')
