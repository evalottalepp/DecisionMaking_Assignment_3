

class Costs():
    def __init__(self,modelClass):
        self.modelClass = modelClass
        self.model = modelClass.solvedModel
        self.modelCost = self.model.objVal
        
        self.X_PW = self.modelClass.x_pw_values_all
        self.X_WU = self.modelClass.x_wu_values_all
        self.Y_PW = self.modelClass.y_pw_values_all
        self.Y_WU = self.modelClass.y_wu_values_all


        self.U_Costs = {} 
        for u in self.modelClass.U:
            PW_Cost,WU_Cost = self.calculateCostPerUniversity(u)
            totalUCost = PW_Cost+WU_Cost

            self.U_Costs[u] = [round(totalUCost,2),round(PW_Cost,2),round(WU_Cost,2)]


        

    
    def calculateCostPerUniversity(self,u):

        PW_Cost = 0
        WU_Cost = 0 

        for w in self.modelClass.W:
            # Printers
            for p in self.modelClass.P:
                fixedCost = self.modelClass.f[p,w] * self.Y_PW[p,w]
                varCost = 0
                for k in self.modelClass.K:
                    varCost += self.X_PW[p,w,k]
                varCost = varCost * self.modelClass.c[p,w]

                PW_Cost += fixedCost + varCost

            # University
            fixedCost = self.modelClass.f[w,u] * self.Y_WU[w,u]
            varCost = 0
            for k in self.modelClass.K:
                varCost += self.X_WU[w,u,k]
            varCost = varCost * self.modelClass.c[w,u]

            WU_Cost += fixedCost + varCost
            
        return PW_Cost,WU_Cost

         
    