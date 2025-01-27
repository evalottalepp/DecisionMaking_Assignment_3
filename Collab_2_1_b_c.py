from costModel import costModel_PW_WU

class collaboration():
    def __init__(self,demandData,vCost,fCost):
        self.demandData = demandData
        self.vCost = vCost
        self.fCost = fCost
        self.price = 6
        self.totalRevenue = self.price * (self.demandData.demand.sum())
        
        self.UB_W = self.demandData.W[:2]
        self.SE_C = self.demandData.W[2:]

        self.UB_model = self.makeUB_model()
        self.SE_model = self.makeSE_model()
        self.bothModel = self.makeCombineModel()

        self.shapley = self.getAllocatedProfits()

    def makeUB_model(self):
        model = costModel_PW_WU(
            W = self.UB_W,  
            P = self.demandData.P,
            cap = self.demandData.capacity,
            U = self.demandData.U,  
            K = self.demandData.K,
            c = self.vCost.varCost,
            f = self.fCost.fixedCost,
            demand = self.demandData.demand,
            supply = self.demandData.supply
        )
        return model

    def makeSE_model(self):
        model = costModel_PW_WU(
            W = self.SE_C,  
            P = self.demandData.P,
            cap = self.demandData.capacity,
            U = self.demandData.U,  
            K = self.demandData.K,
            c = self.vCost.varCost,
            f = self.fCost.fixedCost,
            demand = self.demandData.demand,
            supply = self.demandData.supply
        )
        return model
    
    def makeCombineModel(self):
        model = costModel_PW_WU(
            W = self.demandData.W,  
            P = self.demandData.P,
            cap = self.demandData.capacity,
            U = self.demandData.U,  
            K = self.demandData.K,
            c = self.vCost.varCost,
            f = self.fCost.fixedCost,
            demand = self.demandData.demand,
            supply = self.demandData.supply
        )
        return model
    
    def getTotalProfit(self):

        costModel = self.bothModel.model()
        totalCosts = costModel.objVal

        jointProfit = self.totalRevenue - totalCosts

        return jointProfit


    def getAllocatedProfits(self):
        UBcostModel = self.UB_model.model()
        SEcostModel = self.SE_model.model()

        UBcost,SEcost = UBcostModel.objVal, SEcostModel.objVal

        UB_profit, SE_profit = self.totalRevenue - UBcost, self.totalRevenue - SEcost

        jointProfit = self.getTotalProfit()

        UB_Shapley = 0.5 * (UB_profit + (jointProfit - SE_profit))
        SE_Shapley = 0.5 * (SE_profit + (jointProfit - UB_profit))

        
        print(f'Individual Profits - UB:{round(UB_profit)}, SE:{round(SE_profit)}, joint profit of {round(jointProfit)}')
        print(f'Shapley Values - UB:{round(UB_Shapley)}, SE:{round(SE_Shapley)}, out of a joint profit of {round(jointProfit)}')
        return {'UB':UB_Shapley, 'SE': SE_Shapley}

